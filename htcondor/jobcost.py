#!/usr/bin/env python3
"""Running HTCondor jobs with live cost/hr, escalation steps, queue pressure
(the second-price ceiling your $/CU is climbing toward), and the job command.

Usage:  jobcost.py [username]   (defaults to $USER)

Columns:
  JOB NODE GPU CU $/CU HIKES COST/HR QPRESS CMD
    $/CU    = live running price per CU (condor_bank jobs); floor if no ticket
    HIKES   = round(log(price/floor)/log(1.1)) 10%/hr steps above floor, else FLOOR
    COST/HR = price * slot_weight
    QPRESS  = second-price ceiling: highest *competing* idle bid (other users)
              that could land on this node's GPU. 0 if that bid <= your $/CU
              (no upward pressure); otherwise the bid itself (where you're headed).
    CMD     = basename of the job executable

Cost model: CU = max(cores, mem_GB/16) + 24*GPUs; bid = JobPrio + 1000.
"""
import math
import os
import re
import subprocess
import sys

me = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("USER", "")


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


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

# --- live running price (condor_bank jobs) -----------------------------------
bank, bank_down = {}, False
r = run(["condor_bank", "jobs"])
if re.search(r"kerberos|keystore|permission", (r.stdout + r.stderr), re.I):
    bank_down = True
else:
    for line in r.stdout.splitlines():
        p = line.split()
        if len(p) >= 4 and p[0].isdigit():
            try:
                bank[p[0]] = (float(p[1]), float(p[2]), float(p[3]))
            except ValueError:
                pass

# --- idle competitors (all users, other than me) ----------------------------
# NOTE: `-af Requirements` returns "undefined" for many jobs (Requirements is
# materialized lazily), so we parse the long form (`-l`), which shows the real
# expression with the GPU device-name whitelist. One call, parsed into blocks.
# each: (bid, owner, req_gpus, requirements_text)
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
    # no explicit device-name whitelist -> capability-only or any-GPU
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


# --- my running jobs ---------------------------------------------------------
rows = []
for line in run(["condor_q", me, "-run", "-af",
                 "ClusterId", "ProcId",
                 'split(split(RemoteHost,"@")[1],".")[0]',
                 "RequestGpus", "RequestCpus", "RequestMemory",
                 "MachineAttrMinRunningPrice0", "Cmd"]).stdout.splitlines():
    p = line.split()
    if len(p) < 8:
        continue
    cl, pr, node, g, c, m, floor = p[:7]
    cmd = os.path.basename(p[7]) if len(p) > 7 else "?"
    try:
        g, c, m, floor = float(g), float(c), float(m), float(floor)
    except ValueError:
        continue
    cu = max(c, m / 16000.0) + 24 * g
    gpu_name, node_cap = nodes.get(node, ("?", 8))
    rows.append(dict(job=f"{cl}.{int(float(pr))}", node=node, gpu=int(g), cu=cu,
                     floor=floor, gpu_name=gpu_name, node_cap=node_cap or 8,
                     live=bank.get(f"{cl}{pr}"), cmd=cmd))

if not rows:
    print(f"No running jobs for {me!r}.")
    sys.exit(0)

# --- render ------------------------------------------------------------------
H = (f"{'JOB':<12}{'NODE':<6}{'GPU':>4}{'CU':>5}{'$/CU':>7}{'HIKES':>8}"
     f"{'COST/HR':>9}{'QPRESS':>8}  CMD")
print(H)
print("-" * len(H))
total = 0.0
for x in rows:
    if x["live"] is not None:
        _, price, weight = x["live"]
    else:
        price, weight = x["floor"], x["cu"]
    cost = price * weight
    total += cost
    if x["floor"] > 0 and price > x["floor"] * 1.0001:
        hikes = f"+{round(math.log(price / x['floor']) / math.log(1.1))}x10%"
    else:
        hikes = "FLOOR"
    qp = ceiling(x["gpu_name"], x["node_cap"], price)
    qtxt = f"{qp:.0f}" if qp > 0 else "0"
    pcu = (f"{price:.1f}" if x["live"] is not None else f"~{price:.0f}")
    print(f"{x['job']:<12}{x['node']:<6}{x['gpu']:>4}{x['cu']:>5.0f}{pcu:>7}"
          f"{hikes:>8}{cost:>9.0f}{qtxt:>8}  {x['cmd']}")
print("-" * len(H))
print(f"{'TOTAL':<36}{total:>9.0f}  cluster$/hr")
if bank_down:
    print("\n!! condor_bank unreadable (Kerberos) - $/CU are FLOOR estimates. Run: kinit")
