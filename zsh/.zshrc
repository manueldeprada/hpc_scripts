# Clone antidote if necessary.
[[ -e ${ZDOTDIR:-~}/.antidote ]] ||
  git clone https://github.com/mattmc3/antidote.git ${ZDOTDIR:-~}/.antidote

autoload -Uz compinit
compinit

# Source antidote.
source ${ZDOTDIR:-~}/.antidote/antidote.zsh
