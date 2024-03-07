# hpc_scripts
My HPC cheatsheet. I share here some of my favorite scripts and commands.

## Slurm and GPUs stuff
### Scancel all your jobs
`squeue -o '%i' --noheader | sed -z 's/\n/ /g; s/ $/\n/' | xargs scancel`

### Resource avaliability script
This script displays the availability of CPUs, memory, and GPUs, allowing you to make targeted requests to SLURM. For instance, you can optimize the number of cores, amount of memory, or types of GPUs you request.

The script is tailored for ETH's Euler system but should work on any SLURM setup with minor adjustments, primarily by updating the gpus_alias variable.

Please note that a node may have unusable free GPUs, if the node lacks available CPUs or if the node is DOWN, DRAINED or RESERVED. In that case, the GPUs will show in red and won't be included in the count.

**update 7/3/24:** the script now displays the state of nodes.

Example (first column is the node name):
![image](https://github.com/manueldeprada/hpc_scripts/assets/6536835/b808c146-9a77-4b76-a7ea-ad8d16e02282)

### nvitop
`pip3 install nvitop`: great tool to monitor your GPU usage inside multigpu jobs

### ssh into running job
`srun --interactive --jobid <jobid> --pty bash`

### get an interactive gpu session
`srun --pty --ntasks=1 --cpus-per-task=2 -t 3:59:00 --mem-per-cpu=15G --gpus=1 --gres=gpumem:24g bash`

## General stuff

### Copy ssh pubkey
`ssh-copy-id -i ~/.ssh/id_xx.pub u@server`

### zsh quickstart
```
dnf install zsh git curl
chsh -s $(which zsh)
wget https://raw.githubusercontent.com/manueldeprada/hpc_scripts/main/zsh/.zshrc
wget https://raw.githubusercontent.com/manueldeprada/hpc_scripts/main/zsh/.zsh_plugins.txt
```
