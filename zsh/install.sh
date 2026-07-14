#!/bin/sh
# ============================================================================
#  hpc_scripts — one-command zsh setup
#  https://github.com/manueldeprada/hpc_scripts
#
#  Usage (on any new machine):
#    curl -fsSL https://raw.githubusercontent.com/manueldeprada/hpc_scripts/main/zsh/install.sh | sh
#
#  What it does:
#    1. Clones (or updates) the repo to ~/.hpc_scripts
#    2. Installs starship if missing
#    3. Backs up any existing ~/.zshrc to ~/.zshrc.local (machine-local config)
#    4. Writes a tiny ~/.zshrc that sources the managed config
#
#  After this, every shell start auto-pulls the latest config (once a day),
#  so all your machines stay in sync. Machine-specific config lives in
#  ~/.zshrc.local and is never touched by the sync.
# ============================================================================
set -eu

REPO_URL="https://github.com/manueldeprada/hpc_scripts.git"
HPC_ZSH_DIR="${HPC_ZSH_DIR:-$HOME/.hpc_scripts}"

echo "==> hpc_scripts zsh setup"

# 1. Clone or update the repo -------------------------------------------------
if [ -d "$HPC_ZSH_DIR/.git" ]; then
  echo "--> updating existing checkout at $HPC_ZSH_DIR"
  git -C "$HPC_ZSH_DIR" pull --ff-only --quiet || true
else
  echo "--> cloning into $HPC_ZSH_DIR"
  git clone --depth=1 "$REPO_URL" "$HPC_ZSH_DIR"
fi

# 2. Install starship if missing ---------------------------------------------
if command -v starship >/dev/null 2>&1; then
  echo "--> starship already installed"
else
  echo "--> installing starship into ~/.local/bin"
  mkdir -p "$HOME/.local/bin"
  if ! curl -sS https://starship.rs/install.sh | sh -s -- -y -b "$HOME/.local/bin"; then
    echo "!!  starship install failed — prompt will fall back to plain zsh."
    echo "!!  Re-run later: curl -sS https://starship.rs/install.sh | sh"
  fi
fi

# 3. Migrate any existing (non-managed) ~/.zshrc into ~/.zshrc.local -----------
#    Strips the bits now handled by the synced config (antidote bootstrap,
#    powerlevel10k, the Alt+arrow bindkeys, the ~/.local/bin/env line) and keeps
#    only your machine-specific lines. A full, untouched backup is always saved,
#    and existing ~/.zshrc.local content is appended to, never overwritten.
if [ -f "$HOME/.zshrc" ] && ! grep -q "HPC_ZSH_DIR" "$HOME/.zshrc" 2>/dev/null; then
  backup="$HOME/.zshrc.pre-hpc.$(date +%s)"
  cp "$HOME/.zshrc" "$backup"
  echo "--> full backup saved: $backup"

  awkf="$(mktemp)"
  cat > "$awkf" <<'AWK'
/^if \[\[ -r .*p10k-instant-prompt/ { skip = 1; next }
skip && /^fi[[:space:]]*$/ { skip = 0; next }
skip { next }
/antidote/ { next }
/^[[:space:]]*autoload -Uz compinit/ { next }
/^[[:space:]]*compinit[[:space:]]*$/ { next }
/p10k/ { next }
/\.local\/bin\/env/ { next }
/bindkey.*forward-word/ { next }
/bindkey.*backward-word/ { next }
/# Clone antidote if necessary/ { next }
/# Source antidote/ { next }
/# Enable Powerlevel10k instant prompt/ { next }
/require console input/ { next }
/everything else may go below/ { next }
/# To customize prompt, run/ { next }
{ print }
AWK

  {
    echo "# ~/.zshrc.local — machine-specific config (NOT synced)."
    echo "# Sourced at the end of the hpc_scripts managed config. Bits now managed"
    echo "# (antidote, starship, bindkeys, PATH) were stripped. Full backup: $backup"
    echo ""
    awk -f "$awkf" "$HOME/.zshrc" | cat -s
  } >> "$HOME/.zshrc.local"
  rm -f "$awkf"
  echo "--> machine-specific lines -> ~/.zshrc.local"
fi

# 4. Write the managed stub ~/.zshrc -----------------------------------------
echo "--> writing ~/.zshrc"
cat > "$HOME/.zshrc" <<EOF
# hpc_scripts managed zsh — https://github.com/manueldeprada/hpc_scripts
# Machine-specific config goes in ~/.zshrc.local (auto-sourced), not here.
export HPC_ZSH_DIR="$HPC_ZSH_DIR"
source "\$HPC_ZSH_DIR/zsh/zshrc"
EOF

echo ""
echo "Done. Start a new shell or run:  exec zsh"
echo "Machine-specific tweaks go in:   ~/.zshrc.local"
