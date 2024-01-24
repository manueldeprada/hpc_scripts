# hpc_scripts
I will share here some of my personal scripts for slurm and other HPC helpers.

## resources.py
This script displays the availability of CPUs, memory, and GPUs, allowing you to make targeted requests to SLURM. For instance, you can optimize the number of cores, amount of memory, or types of GPUs you request.


The script is tailored for ETH's Euler system but should work on any SLURM setup with minor adjustments, primarily by updating the gpus_alias variable.

Please note that a node may have available GPUs, but they can be unrequestable if the node lacks available CPUs. In that case, they will be red and won't be included in the count.

Example (first column is the node name):
![image](https://github.com/manueldeprada/hpc_scripts/assets/6536835/b808c146-9a77-4b76-a7ea-ad8d16e02282)

