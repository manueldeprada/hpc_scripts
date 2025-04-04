# hpc_scripts
My HPC cheatsheet. I share here some of my favorite scripts and commands.

## General
### Copy ssh pubkey
`ssh-copy-id -i ~/.ssh/id_xx.pub u@server`

### launch vscode on a login node
```bash
ssh -t -L 8080:localhost:8080 user@eu-login-xx.euler.ethz.ch 'module load stack code-server/4.89.1 && code-server --bind-addr 0.0.0.0:8080'
```
### zsh quicksetup
```
dnf install zsh git curl util-linux-user
chsh -s $(which zsh)
wget https://raw.githubusercontent.com/manueldeprada/hpc_scripts/main/zsh/.zshrc
wget https://raw.githubusercontent.com/manueldeprada/hpc_scripts/main/zsh/.zsh_plugins.txt
```
### Set zsh as default shell
```bash
# .bash_profile
if [ -t 1 ] && [ -x /cluster/software/stacks/2024-06/sfos/zsh ]; then
    exec /cluster/software/stacks/2024-06/sfos/zsh
fi
```

## Slurm and GPU jobs
### Scancel all your jobs
`squeue -o '%i' --noheader | sed -z 's/\n/ /g; s/ $/\n/' | xargs scancel`

### Resource avaliability script
This script displays the availability of CPUs, memory, and GPUs, allowing you to make targeted requests to SLURM. For instance, you can optimize the number of cores, amount of memory, or types of GPUs you request.

The script is tailored for ETH's Euler system but should work on any SLURM setup with minor adjustments, primarily by updating the gpus_alias variable.

Please note that a node may have unusable free GPUs, if the node lacks available CPUs or if the node is DOWN, DRAINED or RESERVED. In that case, the GPUs will show in red and won't be included in the count.

**update 7/3/24:** the script now displays the state of nodes.

Example (first column is the node name):
![image](https://github.com/manueldeprada/hpc_scripts/assets/6536835/0dea520e-e7f0-480a-90dc-f0c9e2e0cad1)

### nvitop
`pip3 install nvitop`: great tool to monitor your GPU usage inside multigpu jobs

### ssh into running job
`srun --interactive --jobid <jobid> --pty bash`
**update 4/2025:** since the Ubuntu update, `ssh node` also works.
### direct ssh into a running node through a login node from your machine (i.e. to redirect ports)
```bash
ssh -J ssh -J user@euler.ethz.ch user@node.euler.ethz.ch
```
### get an interactive gpu session
`srun --pty --ntasks=1 --cpus-per-task=2 -t 3:59:00 --mem-per-cpu=15G --gpus=1 --gres=gpumem:24g bash`

## Troubleshooting
### Prioritize conda env packages over user pip dir
```
export PYTHONPATH=$(find $CONDA_PREFIX -type d -name "site-packages" | head -n 1)
```
