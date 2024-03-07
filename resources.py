#!/usr/bin/env python3
import subprocess
import argparse
import re
import json

def get_args():
    parser = argparse.ArgumentParser(description="Display nodes and their usage.")
    parser.add_argument("--only-gpus", action="store_true", help="Show only nodes with GPUs")
    parser.add_argument("--gpu-filter", type=str, default="", help="Filter nodes by GPU alias (partial names accepted).")
    parser.add_argument("--print-failed-nodes", action="store_true", help="Print which nodes failed to be parsed.")
    return parser.parse_args()

def get_slurm_info():
    process = subprocess.run(
        "scontrol --json show nodes",
        stdout=subprocess.PIPE, shell=True
    )
    output = process.stdout.decode().strip()
    if not output:
        raise Exception("No nodes found")
    data = json.loads(output)["nodes"]
    return data

def parse_properties(fields):
    return {k: (v if 'res' in k.lower() else float(v) if '.' in v else int(v)) for k, v in (field.split("=", 1) for field in fields)}

def parse_gpu_availability(gres, alloc_tres, aliases):
    gpu_info, gpu_counts = {}, {}
    for gpu_type, count in re.findall(r'gpu:([a-zA-Z0-9_\-]+):(\d+)', gres):
        alias = aliases.get(gpu_type, gpu_type)
        gpu_info[alias] = gpu_counts[alias] = {'total': int(count), 'allocated': 0}
    for gpu_type, count in re.findall(r'.*gpu:([a-zA-Z0-9_\-]+):(\d+)', alloc_tres):
        alias = aliases.get(gpu_type, gpu_type)
        if alias in gpu_info:
            gpu_info[alias]['allocated'] = gpu_counts[alias]['allocated'] = int(count)
    return 'gpu_avail: ' + ', '.join(f"{gpu}({counts['total'] - counts['allocated']}/{counts['total']})" for gpu, counts in gpu_info.items()), gpu_counts

state_color_map = {
    # 'ALLOCATED': '\033[98m', # orange
    'MIXED': '\033[93m', # yellow
    'IDLE': '\033[92m', # green
    'DRAIN': '\033[91m', # red
    'DOWN': '\033[91m', # red
    'FAIL': '\033[91m', # red
    'NOT_RESPONDING': '\033[91m', # red
    'MAINTENANCE': '\033[91m', # red
    'RESERVED': '\033[91m', # red
    'PLANNED': '\033[91m', # red
}
    
    

def print_node_usage(data, only_gpus, gpu_filter, aliases):
    gpu_aggregate = {}
    for node in data:
        name = node['name']
        node_state = node['state']
        color = '\033[0m'
        for c in state_color_map: # apply colors by severity order
            if c in node_state:
                color = state_color_map[c]
        name = f"{color}{name}"
        gpu_info, gpu_counts = parse_gpu_availability(node["gres"], node["gres_used"], aliases)
        cpu_avail = node['cpus'] - node['alloc_cpus']
        if cpu_avail > 0 and ('IDLE' in node_state or 'MIXED' in node_state or 'ALLOCATED' in node_state) and 'RESERVED' not in node_state and 'PLANNED' not in node_state:
            for gpu, counts in gpu_counts.items():
                if gpu in gpu_aggregate:
                    gpu_aggregate[gpu] += counts['total'] - counts['allocated']
                else:
                    gpu_aggregate[gpu] = counts['total'] - counts['allocated']
        if only_gpus and node["gres"] == '' or gpu_filter and not any(gpu_filter in gpu for gpu in node.get('gres', '').split(', ')):
           continue
        mem, mem_avail = node['real_memory'] / 1000.0, node['real_memory'] / 1000.0 - node['alloc_memory'] / 1000.0
        mem_used = (mem - node['free_mem']['number'] / 1000.0) / (node['alloc_memory'] / 1000.0 + 0.00001)
        mem_used = 0.0 if mem_used > 1 else mem_used
        free_gpus = -1
        if len(gpu_counts) > 0:
            gpu_counts = next(iter(gpu_counts.values()), 0)
            free_gpus = gpu_counts['total'] - gpu_counts['allocated']
        gpu_avail_text = f"\033[91m{gpu_info}\033[0m" if cpu_avail == 0 or free_gpus == 0 else gpu_info
        print(f"{name}\tcpu_aval:{cpu_avail:>2}/{node['cpus']:>2}  \t"
              f"mem_aval:{mem_avail:>6.2f}/{mem:>6.2f}GB\tcpu_use:{node['cpu_load']['number']/100.0:>5.2f}\t"
              f"mem_use:{int(mem_used * 100):>3}%\t{gpu_avail_text}\tstate:{','.join(node_state)}")
    inv_dict = {v: k for k, v in aliases.items()}
    print("\nAggregate of available GPUs:", *(f"{gpu}: {count}      \t slurm_code:{inv_dict[gpu]}" for gpu, count in gpu_aggregate.items()), sep="\n")

def main():
    args = get_args()
    aliases = {
        "nvidia_v100-sxm2-32gb": "v100_32G", "nvidia_a100-pcie-40gb": "a100_40G",
        "quadro_rtx_6000": "Qrtx6000_24G", "nvidia_titan_rtx": "titanrtx_24G",
        "nvidia_geforce_rtx_3090": "rtx3090_24G", "nvidia_geforce_rtx_4090": "rtx4090_24G",
        "tesla_v100-sxm2-32gb": "v100_32G", "nvidia_a100_80gb_pcie": "a100_80G",
        "nvidia_geforce_rtx_2080_ti": "rtx2080ti_11G", "nvidia_geforce_gtx_1080_ti": "gtx1080ti_11G"
    }
    data = get_slurm_info()
    print_node_usage(data, args.only_gpus, args.gpu_filter, aliases)
    if args.print_failed_nodes:
        print(f"\nNodes failed to be parsed: {data['failed_nodes']}")

if __name__ == "__main__":
    main()

