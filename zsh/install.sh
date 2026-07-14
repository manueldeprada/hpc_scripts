#!/bin/sh
# ============================================================================
#  hpc_scripts one-command zsh setup
#  https://github.com/manueldeprada/hpc_scripts
#
#  Usage (on any machine, new or existing):
#    curl -fsSL https://raw.githubusercontent.com/manueldeprada/hpc_scripts/main/zsh/install.sh | sh
#
#  What it does:
#    1. Clones (or updates) the repo to ~/.hpc_scripts
#    2. Installs starship if missing
#    3. Rewrites ~/.zshrc to source the synced config near the top, keeping your
#       machine-specific lines below it (a full backup is saved first)
#
#  After this, every shell start auto-pulls the latest config over HTTPS once a
#  day, so all your machines stay in sync. Your machine-specific config lives
#  below the `source` line in ~/.zshrc and is never synced or overwritten, so
#  tool installers (conda, gcloud, uv, ...) that append to ~/.zshrc just work.
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
    echo "!!  starship install failed; prompt will fall back to plain zsh."
    echo "!!  Re-run later: curl -sS https://starship.rs/install.sh | sh"
  fi
fi

# 3. Set up ~/.zshrc ----------------------------------------------------------
#    The synced config is sourced near the TOP of ~/.zshrc; everything below it
#    is your machine-local config. Because ~/.zshrc itself is the local file
#    (never synced, never overwritten by updates), installers that append here
#    just land in the local section and work.
header() {
  cat <<EOF
# hpc_scripts managed zsh: https://github.com/manueldeprada/hpc_scripts
# The line below loads the cloud-synced config (antidote, starship, PATH,
# keybindings, daily auto-update over HTTPS). Run \`zsync\` to update now.
#
# Put machine-specific config BELOW this line. This file is never synced and
# never overwritten by updates, so tool installers that append here just work.
export HPC_ZSH_DIR="$HPC_ZSH_DIR"
source "\$HPC_ZSH_DIR/zsh/zshrc"

# ===== machine-local config below =====
EOF
}

if grep -q 'HPC_ZSH_DIR' "$HOME/.zshrc" 2>/dev/null; then
  echo "--> ~/.zshrc already loads the managed config; leaving your local section as-is"
elif [ -f "$HOME/.zshrc" ]; then
  # Existing machine: keep the local lines, strip the bits now managed by the
  # synced config (antidote bootstrap, powerlevel10k, the Alt+arrow bindkeys,
  # the ~/.local/bin/env line). A full untouched backup is always saved.
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

  { header; awk -f "$awkf" "$HOME/.zshrc" | cat -s; } > "$HOME/.zshrc.hpc-new"
  mv "$HOME/.zshrc.hpc-new" "$HOME/.zshrc"
  rm -f "$awkf"
  echo "--> managed config prepended; your machine-specific lines kept below it"
else
  header > "$HOME/.zshrc"
  echo "--> wrote a fresh ~/.zshrc"
fi

echo ""
echo "Done. Start a new shell or run:  exec zsh"
echo "Machine-specific tweaks go below the 'source' line in ~/.zshrc"
