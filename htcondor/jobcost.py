#!/usr/bin/env python3
"""Running HTCondor jobs with live cost/hr, escalation steps, queue pressure,
runtime, exact spend so far, the job command, balance + runway -- then the last
few finished jobs' charges.

Usage:  jobcost.py [username] [--history [N]]   (no history unless --history; bare = 5)

Columns:
  JOB NODE GPU CU $/CU HIKES COST/HR QPRESS RAN BURNT CMD
    $/CU    = live running price per CU (== the second price you pay); floor if no ticket
    HIKES   = round(log(price/floor)/log(1.1)) 10%/hr steps above floor, else FLOOR
    COST/HR = price * slot_weight
    QPRESS  = second-price ceiling: highest *competing* idle bid (other users)
              that could land on this node's GPU; 0 if <= your $/CU.
    RAN     = wall-clock since JobCurrentStartDate
    BURNT   = exact cluster$ charged so far (GetQueueStatus.charged, == the
              banking ledger). Falls back to an escalation estimate (~) w/o a ticket.
    CMD     = basename of the job executable

Then BALANCE / BURN/hr / RUNWAY. With --history [N] (off by default), also the last
N movements from the LastMovements ledger: job charges (Cmd from condor_history,
excluding running/fee-only jobs, small same-day same-command charges <1000 grouped
per line) and money transfers (shown as "→/← counterparty", "(by X)" when a third
party ordered it; "+" prefix marks incoming).

Cost model: CU = max(cores, mem_GB/16) + 24*GPUs; bid = JobPrio + 1000.

Data sources (all banking calls via curl, which does the Kerberos/Negotiate auth):
  GetQueueStatus  ~0.05s  live price + slot weight + exact `charged` per job
  GetBalances     ~0.2s   balance
  LastMovements   ~3s     the spend ledger -- SLOW, so it's fetched in a background
                          thread while the fast stuff is computed, and printed last.
condor_status/condor_q supply node, Cmd, start time, and competitor bids.
`condor_bank jobs`/`GetRunningJobs` (the old ~6s call) are no longer used --
GetQueueStatus returns the same `charged` figure ~100x faster.
"""
import json
import math
import os
import re
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta

API = "https://logger.cluster.is.localnet/htcondor/API"

# args:  jobcost.py [username] [--history [N]]   (no history unless --history; bare=5)
me = os.environ.get("USER", "")
want_history = False
hist_n = 5
_args = sys.argv[1:]
_i = 0
while _i < len(_args):
    a = _args[_i]
    if a == "--history":
        want_history = True
        nxt = _args[_i + 1] if _i + 1 < len(_args) else None
        if nxt and nxt.isdigit():
            hist_n = int(nxt)
            _i += 1
    elif a.startswith("--history="):
        want_history = True
        v = a.split("=", 1)[1]
        if v.isdigit():
            hist_n = int(v)
    elif not a.startswith("-"):
        me = a
    _i += 1
hist_n = max(1, hist_n)


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def curl_api(endpoint, body):
    """POST to a banking API endpoint via curl (handles Kerberos/Negotiate).
    Returns the parsed JSON, or None on auth failure / non-JSON / error."""
    r = run(["curl", "-s", "--negotiate", "-u", ":", "-m", "30", "-X", "POST",
             f"{API}/{endpoint}", "-H", "Content-Type: application/json",
             "-d", json.dumps(body)])
    try:
        return json.loads(r.stdout)
    except ValueError:
        return None                          # 401 HTML page, timeout, etc.


# --- kick off the slow ledger fetch in the background ------------------------
# LastMovements is ~3s; it hits the banking server (not the schedd), so it's safe
# to overlap with the fast queries. We print the main table before joining it.
_now = datetime.now()
HFROM = (_now - timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%S")
HTO = (_now + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S")
hist = {"data": None, "cmd": {}}


def fetch_history():
    # fetch extra rows: we drop running + fee-only jobs before taking hist_n
    length = hist_n + 25
    obj = curl_api("LastMovements",
                   {"query": {"from": HFROM, "to": HTO, "start": 0, "length": length}})
    hist["data"] = obj.get("data") if obj else None
    if not hist["data"]:
        return
    # enrich with Cmd from condor_history. Runs *after* LastMovements (~3s in),
    # by when the main-thread condor_q calls are done -> no schedd contention.
    cmap = {}
    for line in run(["condor_history", me, "-limit", str(max(40, length + 40)),
                     "-af", "ClusterId", "ProcId", "Cmd"]).stdout.splitlines():
        q = line.split()
        if len(q) >= 3:
            cmap[f"{q[0]}{q[1]}"] = os.path.basename(" ".join(q[2:]))
    hist["cmd"] = cmap


hist_thread = threading.Thread(target=fetch_history, daemon=True)
if want_history:
    hist_thread.start()


# capability by GPU family (for capability-only competitor requirements)
CAP = [("B200", 10.0), ("H100", 9.0), ("A100", 8.0),
       ("RTX 6000", 7.5), ("2080", 7.5), ("V100", 7.0)]


def gpu_token(name):
    """Distinctive substring used to match a device name inside Requirements."""
    if "B200" in name:
        return "B200"
    if "H100" in name:
        return "H100"
    if "A100-SXM4-40GB" in name:
        return "A100-SXM4-40GB"
    if "A100-SXM4-80GB" in name:
        return "A100-SXM4-80GB"
    return name.replace("NVIDIA ", "").strip()


def gpu_cap(name):
    for key, c in CAP:
        if key in name:
            return c
    return 8.0


def fmt_dur(secs):
    """Compact human duration: 47m / 6.9h / 2d3h."""
    if secs is None:
        return "?"
    h = secs / 3600.0
    if h < 1:
        return f"{h * 60:.0f}m"
    if h < 24:
        return f"{h:.1f}h"
    d = int(h // 24)
    return f"{d}d{h - d * 24:.0f}h"


def fmt_money(x, prefix=""):
    """Compact cluster$: 1840 / 18.3k / 1.2M (sign preserved)."""
    if x is None:
        return "?"
    a = abs(x)
    if a >= 1e6:
        return f"{prefix}{x / 1e6:.1f}M"
    if a >= 1e4:
        return f"{prefix}{x / 1e3:.1f}k"
    return f"{prefix}{x:.0f}"


def short_date(ts):
    """'Jun 17, 2026' -> 'Jun 17' (drop the redundant year)."""
    return re.sub(r",\s*\d{4}\s*$", "", ts) if ts else (ts or "")


def parse_transfer(concept):
    """Classify a ledger Concept that is a money transfer (not a job charge).
    Returns (direction, counterparty, orderer) where direction is 'to'
    (outgoing, Amount<0) or 'from' (incoming, Amount>0); None if not a transfer.
        'Transfer to Jana Zeller (ordered by Manuel De Prada Corral).'
        'Transfer from Jana Zeller (ordered by Jana Zeller).'
    """
    m = re.match(r"Transfer (to|from) (.+?) \(ordered by (.+?)\)\.?\s*$",
                 concept or "")
    return (m.group(1), m.group(2), m.group(3)) if m else None


# --- node -> (gpu device name, total gpus) -----------------------------------
nodes = {}
for line in run(["condor_status", "-af", "Machine", "GPUs_DeviceName",
                 "TotalGpus"]).stdout.splitlines():
    p = line.split()
    if len(p) < 2:
        continue
    short = p[0].split(".")[0].split("@")[-1]
    gpu = " ".join(p[1:-1]) if len(p) > 2 else p[1]
    try:
        tot = int(float(p[-1]))
    except ValueError:
        tot = 8
    if "NVIDIA" in gpu or "Quadro" in gpu or "RTX" in gpu:
        g, t = nodes.get(short, ("", 0))
        nodes[short] = (gpu, max(t, tot))

# --- live price + exact charge (GetQueueStatus; ~0.05s) ----------------------
# qstatus[key] = dict(price, weight, charged); key = f"{clusterID}{procID}"
qstatus, bank_down = {}, False
qs = curl_api("GetQueueStatus",
              {"query": {"start": 0, "length": 500, "allUsers": False}})
if qs is None:
    bank_down = True                         # no ticket / API unreachable
else:
    for j in qs.get("jobs", []):
        key = f"{j['clusterID']}{j['procID']}"
        ch = j.get("charged")
        qstatus[key] = dict(price=float(j.get("runningPrice") or 0.0),
                            weight=float(j.get("slotWeight") or 0.0),
                            charged=float(ch) if ch is not None else None)

# --- balance (GetBalances) ---------------------------------------------------
balance = None
if not bank_down:
    b = curl_api("GetBalances", {"users": [me]})
    if b and b.get("balances"):
        balance = float(b["balances"][0]["value"])

# --- idle competitors (all users, other than me) ----------------------------
# NOTE: `-af Requirements` returns "undefined" for many jobs (Requirements is
# materialized lazily), so we parse the long form (`-l`), which shows the real
# expression with the GPU device-name whitelist. One call, parsed into blocks.
comp = []
cq = run(["condor_q", "-allusers", "-l",
          "-constraint", "JobStatus==1 && RequestGPUs>0"])
for block in cq.stdout.split("\n\n"):
    if "JobPrio" not in block:
        continue
    mo = re.search(r'Owner\s*=\s*"([^"]+)"', block)
    mp = re.search(r'\bJobPrio\s*=\s*(-?\d+)', block)
    mg = re.search(r'\bRequestG[pP][uU]s\s*=\s*(\d+)', block)
    mr = re.search(r'\bRequirements\s*=\s*(.+)', block)
    if not (mo and mp):
        continue
    owner = mo.group(1)
    if owner == me:
        continue
    bid = float(mp.group(1)) + 1000.0
    rgpu = int(mg.group(1)) if mg else 1
    req = mr.group(1) if mr else ""
    comp.append((bid, owner, rgpu, req))


def accepts(req, token, cap):
    """Would a job with this Requirements run on a GPU of (token, capability)?"""
    if token in req:
        return True
    if "CUDADeviceName" not in req:
        caps = [float(x) for x in re.findall(r"CUDACapability\s*>=\s*([0-9.]+)", req)]
        if not caps:
            return True                      # any GPU accepted
        return min(caps) <= cap              # lowest threshold satisfiable
    return False


def ceiling(gpu_name, node_cap, my_price):
    """Highest competing bid that could land on this node; 0 if <= my_price."""
    tok, cap = gpu_token(gpu_name), gpu_cap(gpu_name)
    best = 0.0
    for bid, _o, rgpu, req in comp:
        if rgpu <= node_cap and accepts(req, tok, cap):
            best = max(best, bid)
    return best if best > my_price else 0.0


# --- my running jobs (condor_q supplies node, Cmd, start time) ---------------
now = time.time()
rows, running_keys = [], set()
for line in run(["condor_q", me, "-run", "-af",
                 "ClusterId", "ProcId",
                 'split(split(RemoteHost,"@")[1],".")[0]',
                 "RequestGpus", "RequestCpus", "RequestMemory",
                 "MachineAttrMinRunningPrice0", "JobCurrentStartDate",
                 "Cmd"]).stdout.splitlines():
    p = line.split()
    if len(p) < 9:
        continue
    cl, pr, node, g, c, m, floor, start = p[:8]
    cmd = os.path.basename(" ".join(p[8:]))
    try:
        g, c, m, floor = float(g), float(c), float(m), float(floor)
    except ValueError:
        continue
    try:
        elapsed = now - float(start)
    except ValueError:
        elapsed = None
    cu = max(c, m / 16000.0) + 24 * g
    gpu_name, node_cap = nodes.get(node, ("?", 8))
    key = f"{cl}{pr}"
    running_keys.add(key)
    rows.append(dict(job=f"{cl}.{int(float(pr))}", node=node, gpu=int(g), cu=cu,
                     floor=floor, gpu_name=gpu_name, node_cap=node_cap or 8,
                     qs=qstatus.get(key), elapsed=elapsed, cmd=cmd))


def burnt_estimate(floor, price, weight, elapsed_h):
    """Fallback cluster$ spent ~ integral of the escalation curve (only used when
    GetQueueStatus.charged is unavailable, i.e. no ticket)."""
    if elapsed_h is None:
        return None
    if floor > 0 and price > floor * 1.0001:
        n = min(math.log(price / floor) / math.log(1.1), elapsed_h)
        return weight * (floor * max(elapsed_h - n, 0.0)
                         + (price - floor) / math.log(1.1))
    return price * weight * elapsed_h


def print_history():
    """Print the last hist_n ledger movements (only with --history): job charges
    plus money transfers. Small same-day, same-command job charges (<1000) collapse
    to one line; transfers always stand alone, shown with direction + counterparty."""
    if not want_history:
        return
    hist_thread.join(timeout=30)
    data = hist["data"]
    if not data:
        if not bank_down:
            print("\n(history unavailable)")
        return
    cmap = hist["cmd"]
    # my display name (GECOS), to drop the redundant "ordered by <me>" on my own
    # outgoing transfers while still flagging third-party (delegated) ones.
    gec = run(["getent", "passwd", me]).stdout
    my_name = gec.split(":")[4].strip() if gec.count(":") >= 5 else ""
    entries = []
    for mv in data:
        amt = mv.get("Amount") or 0.0
        concept = mv.get("Concept", "")
        tr = parse_transfer(concept)
        if tr:
            direction, counterparty, orderer = tr
            desc = f"{'→' if direction == 'to' else '←'} {counterparty}"
            if orderer != counterparty and orderer != my_name:
                desc += f" (by {orderer})"   # delegated: a third party moved it
            entries.append(dict(kind="transfer", head="transfer", amt=amt,
                                day=mv.get("Timestamp"), desc=desc))
        else:
            if abs(amt) < 0.5:
                continue                     # fee-only "-0" job (never really ran)
            mo = re.search(r"#(\d+)\.(\d+)", concept)
            key = (mo.group(1) + mo.group(2)) if mo else None
            if key in running_keys:
                continue                     # shown above as currently running
            jid = f"{mo.group(1)}.{mo.group(2)}" if mo else (concept or "?")
            entries.append(dict(kind="job", head=jid, amt=amt,
                                day=mv.get("Timestamp"), desc=cmap.get(key, "?")))
        if len(entries) >= hist_n:
            break
    if not entries:
        return
    # group small (<1000) job charges sharing the same day + command into one line;
    # transfers (and >=1000 charges) always get their own line.
    groups, index = [], {}
    for e in entries:
        if e["kind"] == "job" and abs(e["amt"]) < 1000:
            g = index.get((e["day"], e["desc"]))
            if g:
                g["count"] += 1
                g["total"] += e["amt"]
                continue
            g = dict(count=1, total=e["amt"], day=short_date(e["day"]),
                     desc=e["desc"], head=e["head"], kind="job")
            index[(e["day"], e["desc"])] = g
            groups.append(g)
        else:
            groups.append(dict(count=1, total=e["amt"], day=short_date(e["day"]),
                               desc=e["desc"], head=e["head"], kind=e["kind"]))
    n = sum(g["count"] for g in groups)
    print(f"\nLast {n} movements (small same-day/-cmd job charges grouped):")
    for g in groups:
        head = f"{g['count']}×" if g["count"] > 1 else g["head"]
        sign = "+" if (g["kind"] == "transfer" and g["total"] > 0) else ""
        print(f"  {head:<14}{fmt_money(g['total'], prefix=sign):>10}  "
              f"{g['day']:<13}  {g['desc']}")


# --- render ------------------------------------------------------------------
if not rows:
    # how many of my jobs are sitting idle in the queue?
    if qstatus:
        idle = len(qstatus)                  # no running jobs -> all are idle
    else:
        idle = sum(1 for t in run(["condor_q", me, "-af", "JobStatus"]).stdout.split()
                   if t == "1")
    msg = f"No running jobs for {me!r}."
    if idle:
        msg += f"  {idle} idle in queue."
    print(msg)
    if balance is not None:
        print(f"BALANCE {balance:,.0f} cluster$")
    sys.stdout.flush()
    print_history()
    sys.exit(0)

H = (f"{'JOB':<12}{'NODE':<6}{'GPU':>4}{'CU':>5}{'$/CU':>7}{'HIKES':>8}"
     f"{'COST/HR':>9}{'QPRESS':>8}{'RAN':>7}{'BURNT':>9}  CMD")
print(H)
print("-" * len(H))
total = 0.0
tot_burnt = 0.0
any_est = False
for x in rows:
    qsj = x["qs"]
    if qsj and qsj["price"] > 0:
        price, weight = qsj["price"], qsj["weight"]
    else:
        price, weight = x["floor"], x["cu"]
    cost = price * weight
    total += cost
    if qsj and qsj["charged"] is not None:
        burnt, exact = qsj["charged"], True              # exact charge
    else:
        eh = x["elapsed"] / 3600.0 if x["elapsed"] is not None else None
        burnt, exact = burnt_estimate(x["floor"], price, weight, eh), False
        any_est = True
    if burnt is not None:
        tot_burnt += burnt
    nh = (round(math.log(price / x["floor"]) / math.log(1.1))
          if x["floor"] > 0 and price > x["floor"] * 1.0001 else 0)
    hikes = f"+{nh}x10%" if nh >= 1 else "FLOOR"
    qp = ceiling(x["gpu_name"], x["node_cap"], price)
    qtxt = f"{qp:.0f}" if qp > 0 else "0"
    pcu = (f"{price:.1f}" if qsj and qsj["price"] > 0 else f"~{price:.0f}")
    btxt = fmt_money(burnt, prefix="" if exact else "~")
    print(f"{x['job']:<12}{x['node']:<6}{x['gpu']:>4}{x['cu']:>5.0f}{pcu:>7}"
          f"{hikes:>8}{cost:>9.0f}{qtxt:>8}{fmt_dur(x['elapsed']):>7}"
          f"{btxt:>9}  {x['cmd']}")
print("-" * len(H))
tb = fmt_money(tot_burnt, prefix="~" if any_est else "")
print(f"{'TOTAL':<42}{total:>9.0f}{'':>8}{'':>7}{tb:>9}  cluster$  (COST/HR | BURNT)")

print()
if balance is not None:
    if total > 0:
        h = balance / total
        rw = f"{h:,.0f}h (~{h / 24:.1f}d)"
    else:
        rw = "n/a (no running cost)"
    print(f"BALANCE {balance:,.0f} cluster$    BURN {total:,.0f}/hr"
          f"    RUNWAY @ current rate: {rw}")
else:
    print("BALANCE unavailable (no Kerberos ticket?) - run: kinit")
if bank_down:
    print("!! banking API unreadable (Kerberos) - $/CU & BURNT are FLOOR "
          "estimates. Run: kinit")

# main table is out; now wait on + print the slow ledger history
sys.stdout.flush()
print_history()
