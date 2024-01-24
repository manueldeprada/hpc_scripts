#!/usr/bin/env python3
import subprocess
import argparse
import re

def get_args():
    parser = argparse.ArgumentParser(description="Display nodes and their usage.")
    parser.add_argument("--only-gpus", action="store_true", help="Show only nodes with GPUs")
    parser.add_argument("--gpu-filter", type=str, default="", help="Filter nodes by GPU alias (partial names accepted).")
    parser.add_argument("--print-failed-nodes", action="store_true", help="Print which nodes failed to be parsed.")
    return parser.parse_args()

def parse_nodes_output():
    process = subprocess.run(
        "scontrol -o show nodes | awk '{ print $1, $4, $6, $7, $24, $25, $26, $10, $40, $41}'",
        stdout=subprocess.PIPE, shell=True
    )
    return process.stdout.decode().strip().split("\n")

def parse_properties(fields):
    return {k: (v if 'res' in k.lower() else float(v) if '.' in v else int(v)) for k, v in (field.split("=", 1) for field in fields)}

def parse_gpu_availability(gres, alloc_tres, aliases):
    gpu_info, gpu_counts = {}, {}
    for gpu_type, count in re.findall(r'gpu:([a-zA-Z0-9_\-]+):(\d+)', gres):
        alias = aliases.get(gpu_type, gpu_type)
        gpu_info[alias] = gpu_counts[alias] = {'total': int(count), 'allocated': 0}
    for gpu_type, count in re.findall(r'gres/gpu:([a-zA-Z0-9_\-]+)=(\d+)', alloc_tres):
        alias = aliases.get(gpu_type, gpu_type)
        if alias in gpu_info:
            gpu_info[alias]['allocated'] = gpu_counts[alias]['allocated'] = int(count)
    return 'gpu_avail: ' + ', '.join(f"{gpu}({counts['total'] - counts['allocated']})" for gpu, counts in gpu_info.items()), gpu_counts

def build_data(nodes):
    data = {"failed_nodes": [], "nodes": {}}
    for node in nodes:
        fields = node.split(" ")
        node_name = fields.pop(0).split("=")[1]
        try:
            data["nodes"][node_name] = parse_properties(fields)
        except Exception:
            data["failed_nodes"].append(node_name)
    return data

def print_node_usage(data, only_gpus, gpu_filter, aliases):
    gpu_aggregate = {}
    for name, props in data["nodes"].items():
        gpu_info, gpu_counts = parse_gpu_availability(props.get('Gres', ''), props.get('AllocTRES', ''), aliases)
        cpu_avail = props['CPUTot'] - props['CPUAlloc']
        if cpu_avail > 0:
            for gpu, counts in gpu_counts.items():
                if gpu in gpu_aggregate:
                    gpu_aggregate[gpu] += counts['total'] - counts['allocated']
                else:
                    gpu_aggregate[gpu] = counts['total'] - counts['allocated']
        if only_gpus and props.get('Gres') == '(null)' or gpu_filter and not any(gpu_filter in gpu for gpu in props.get('Gres', '').split(', ')):
           continue
        mem, mem_avail = props['RealMemory'] / 1000.0, props['RealMemory'] / 1000.0 - props['AllocMem'] / 1000.0
        mem_used = (mem - props['FreeMem'] / 1000.0) / (props['AllocMem'] / 1000.0 + 0.00001)
        mem_used = 0.0 if mem_used > 1 else mem_used
        gpu_counts = next(iter(gpu_counts.values()), 0)
        free_gpus = gpu_counts['total'] - gpu_counts['allocated']
        gpu_avail_text = f"\033[91m{gpu_info}\033[0m" if cpu_avail == 0 or free_gpus == 0 else gpu_info
        print(f"{name:<15}cpu_aval:{cpu_avail:>2}/{props['CPUTot']:>2}\t"
              f"mem_aval:{mem_avail:>6.2f}/{mem:>6.2f}GB\tcpu_use:{props['CPULoad']:>5.2f}\t"
              f"mem_use:{int(mem_used * 100):>3}%\t{gpu_avail_text}")
    print("\nAggregate Available GPUs:", *(f"{gpu}: {count}" for gpu, count in gpu_aggregate.items()), sep="\n")

def main():
    args = get_args()
    aliases = {
        "nvidia_v100-sxm2-32gb": "v100_32G", "nvidia_a100-pcie-40gb": "a100_40G",
        "quadro_rtx_6000": "Qrtx6000_24G", "nvidia_titan_rtx": "titanrtx_24G",
        "nvidia_geforce_rtx_3090": "rtx3090_24G", "nvidia_geforce_rtx_4090": "rtx4090_24G",
        "tesla_v100-sxm2-32gb": "v100_32G", "nvidia_a100_80gb_pcie": "a100_80G",
        "nvidia_geforce_rtx_2080_ti": "rtx2080ti_11G", "nvidia_geforce_gtx_1080_ti": "gtx1080ti_11G"
    }
    data = build_data(parse_nodes_output())
    print_node_usage(data, args.only_gpus, args.gpu_filter, aliases)
    if args.print_failed_nodes:
        print(f"\nNodes failed to be parsed: {data['failed_nodes']}")

if __name__ == "__main__":
    main()
