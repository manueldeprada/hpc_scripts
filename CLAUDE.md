# hpc_scripts

An HPC cheatsheet plus a cloud-synced zsh and dotfiles setup that keeps every
machine (laptop, HPC login nodes, personal servers) in sync from this repo.

## Two different CLAUDE.md files (do not confuse them)

- `CLAUDE.md` (this file, repo root): project instructions for working ON this
  repo. Auto-loaded by Claude Code.
- `claude/CLAUDE.md`: a canonical copy of the user's GLOBAL `~/.claude/CLAUDE.md`,
  distributed to every machine by the zsh sync. It is a payload, not instructions
  for this repo. To change global prefs, edit it, commit, push, then copy it to
  `~/.claude/CLAUDE.md` so this machine stays in sync.

## Layout

- `README.md` - user-facing HPC cheatsheet and zsh setup docs.
- `zsh/install.sh` - one-command installer: `curl -fsSL .../zsh/install.sh | sh`.
  Opt-out flags after `-s --`: `--no-update`, `--no-scripts`, `--no-claude-sync`,
  `--no-tmux-sync`. Each writes an `export HPC_ZSH_NO_*=1` line into `~/.zshrc`.
- `zsh/zshrc` - the managed, cloud-synced config, sourced near the top of
  `~/.zshrc`. Does: daily background auto-update, PATH, antidote, starship,
  keybindings, dotfile sync, and a zsh-on-PATH fallback for clusters that load
  zsh from a module dir.
- `zsh/.zsh_plugins.txt` - antidote plugin list. `zsh/.zsh_plugins.zsh` is
  antidote's compiled cache: gitignored, machine-specific, regenerated per host.
- `zsh/starship.toml` - starship prompt (gruvbox-rainbow preset, restructured:
  os/dir/git on the left, env + language versions + `user@host` on the right).
- `zsh/bin/{rtmux,duh}` - scripts put on PATH and synced. rtmux = reconnecting
  tmux over ssh (autossh); duh = incremental `du -sh | sort`.
- `claude/CLAUDE.md`, `tmux/tmux.conf` - synced dotfile payloads (see above).
- `resources.py`, `torch_compile.sh`, `verbose_FindCUDA.cmake`, `htcondor/` -
  assorted HPC helpers.

## How the sync works

- Install clones the repo to `~/.hpc_scripts` and rewrites `~/.zshrc` to
  `source "$HPC_ZSH_DIR/zsh/zshrc"` near the top. Machine-local config lives BELOW
  that source line in `~/.zshrc` (never synced, and where tool installers like
  conda/gcloud/uv append).
- Auto-update: throttled daily background `git pull --ff-only` from the HTTPS URL
  `HPC_ZSH_REMOTE` (never SSH, so no key prompt can hang it). `zsync` forces it now
  and reloads.
- Dotfile sync: `_hpc_sync_file <repo-path> <dest> <cache-key>` copies repo to
  home, storing a baseline hash in `~/.cache/hpc_<key>_base`. If the home copy
  diverged from that baseline, it warns instead of overwriting.
- On this dev Mac, `HPC_ZSH_DIR=$HOME/hpc_scripts` (this working checkout), so
  edits are live. Deployed machines use `~/.hpc_scripts`.

## Editing gotchas

- starship.toml powerline glyphs: the Write/Edit tools drop private-use-area
  characters in U+E000..U+F8FF, which includes the powerline caps
  (U+E0B6 left-semicircle, U+E0B0 right-triangle, U+E0B4 right-semicircle) and
  many nerd-font icons (git branch, language symbols). Rewriting those lines
  leaves empty `[]` and blank `symbol = ""` values and breaks the prompt. Only
  edit lines that contain NO such glyph. To regenerate the file, generate it with
  Python (which preserves the bytes), pulling icon bytes from
  `starship preset gruvbox-rainbow` and injecting the caps by codepoint. Higher
  plane icons (U+F0000 and up, e.g. the `Macos` os symbol) survive Write. Verify:
  `grep -m1 'color_orange)' zsh/starship.toml | hexdump -C` must show
  `5b ee 82 b6 5d`, not `5b 5d`.

## Conventions

- Global rules in `~/.claude/CLAUDE.md` apply (lowercase few-word commit subjects,
  no AI attribution/trailers, American English, no em dashes).
- The user verifies changes themselves. Keep to a quick syntax check
  (`zsh -n zsh/zshrc`, `sh -n zsh/install.sh`, `STARSHIP_CONFIG=... starship print-config`);
  do not build elaborate test harnesses.
- To change a synced dotfile, edit the repo copy, commit, push, and copy it to the
  home path. Editing the home copy directly triggers the divergence warning.
