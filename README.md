# hpc_scripts
My HPC cheatsheet. I share here some of my favorite scripts and commands.

## General
### Copy ssh pubkey
`ssh-copy-id -i ~/.ssh/id_xx.pub u@server`

### launch vscode on a login node
```bash
ssh -t -L 8080:localhost:8080 user@eu-login-xx.euler.ethz.ch 'module load stack code-server/4.89.1 && code-server --bind-addr 0.0.0.0:8080'
```
### zsh quicksetup, one command
On any machine, new or one you already use (zsh must be installed, see below):
```bash
curl -fsSL https://raw.githubusercontent.com/manueldeprada/hpc_scripts/main/zsh/install.sh | sh
exec zsh
```
This clones the repo to `~/.hpc_scripts`, installs [starship](https://starship.rs)
(replaces powerlevel10k), and rewrites `~/.zshrc` to source the synced config near
the top. Plugins are managed by [antidote](https://github.com/mattmc3/antidote).

**Auto-sync:** every shell start checks GitHub for updates (throttled to once a
day, in the background) and pulls the latest config **over HTTPS**, never SSH, so a
machine without an SSH key can never hang on a key prompt. Push a change to this
repo and it lands on all your machines. The synced `bin/` scripts (`rtmux`, `duh`)
and the starship prompt update the same way. Run **`zsync`** to force an update now
and reload the shell instead of waiting for the daily check.

**Per-machine config:** put anything machine-specific (conda/mamba init, gpg-agent,
`module load`s, gcloud, ...) **below the `source` line in `~/.zshrc`**. That part is
never synced or overwritten, and it is exactly where tool installers append their
own lines, so `conda init`, `gcloud`, `uv`, and friends just work with no extra
setup. The synced config only owns the small block above.

**Migrating a machine you already use:** run the same install command. Your existing
`~/.zshrc` is backed up to `~/.zshrc.pre-hpc.<timestamp>`, the `source` line is added
at the top, and the old managed bits (antidote bootstrap, powerlevel10k, the
Alt+arrow bindkeys, the `~/.local/bin/env` line) are stripped since the synced config
now provides them. Everything else you had stays put as your local section.

**Global Claude config:** `~/.claude/CLAUDE.md` is synced too. The canonical copy
is `claude/CLAUDE.md` in this repo; each shell start copies it into place. If a
machine's local `~/.claude/CLAUDE.md` was edited by hand, the sync does not
overwrite it, it prints a loud warning so you can either discard the local change
or promote it into `claude/CLAUDE.md` and push. The repo is public, so keep that
file free of anything private.

**zsh not on PATH:** on clusters where zsh is loaded from a module directory that
is not on `$PATH` (so antidote fails with `command not found: zsh`), the config
adds the running zsh binary's directory to `$PATH` automatically.

Install zsh first if needed:
```bash
# Fedora/RHEL
dnf install zsh git curl util-linux-user
# Debian/Ubuntu
apt install zsh git curl
chsh -s "$(which zsh)"   # make zsh the default shell (see Euler note below if chsh is unavailable)
```

### fedora gpu quick bring-up
```
sudo dnf config-manager addrepo --from-repofile https://developer.download.nvidia.com/compute/cuda/repos/fedora42/x86_64/cuda-fedora42.repo
sudo dnf -y install cuda-toolkit-13-0 nvidia-open patch htop
sudo mkdir /var/swap
sudo btrfs filesystem mkswapfile --size 32G /var/swap/swapfile
sudo swapon /var/swap/swapfile
code tunnel service install
chmod 600 ~/.ssh/id_ed25519
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Set zsh as default shell in Euler
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
```bash
srun --interactive --jobid <jobid> --pty bash
```
**update 4/2025:** since the Ubuntu update, `ssh node` also works.
### direct ssh into a running node through a login node from your machine (i.e. to redirect ports)
```bash
ssh -J ssh -J user@euler.ethz.ch user@node.euler.ethz.ch
```
### get an interactive gpu session
```bash
srun --pty --ntasks=1 --cpus-per-task=2 -t 3:59:00 --mem-per-cpu=15G --gpus=1 --gres=gpumem:24g bash
```

## Troubleshooting
### Prioritize conda env packages over user pip dir
```bash
export PYTHONPATH=$(find $CONDA_PREFIX -type d -name "site-packages" | head -n 1)
```
