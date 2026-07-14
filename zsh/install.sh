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

# 3. Preserve any existing (non-managed) ~/.zshrc as machine-local config -----
if [ -f "$HOME/.zshrc" ] && ! grep -q "HPC_ZSH_DIR" "$HOME/.zshrc" 2>/dev/null; then
  if [ ! -f "$HOME/.zshrc.local" ]; then
    echo "--> moving existing ~/.zshrc -> ~/.zshrc.local (kept as machine-local config)"
    mv "$HOME/.zshrc" "$HOME/.zshrc.local"
  else
    echo "--> ~/.zshrc.local already exists; saving old ~/.zshrc as ~/.zshrc.pre-hpc"
    mv "$HOME/.zshrc" "$HOME/.zshrc.pre-hpc"
  fi
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
