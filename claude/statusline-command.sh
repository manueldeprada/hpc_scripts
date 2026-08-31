#!/bin/bash
# Claude Code status line: current directory, context usage, rate limits.

input=$(cat)

cwd=$(echo "$input" | jq -r '.workspace.current_dir')
dir_display="${cwd/#$HOME/~}"

used=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
ctx=""
[ -n "$used" ] && ctx=$(printf "Ctx: %.0f%%" "$used")

five=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')
week=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty')
rate=""
[ -n "$five" ] && rate="5h:$(printf '%.0f' "$five")%"
if [ -n "$week" ]; then
  week_fmt="7d:$(printf '%.0f' "$week")%"
  [ -n "$rate" ] && rate="$rate $week_fmt" || rate="$week_fmt"
fi

line="$dir_display"
[ -n "$ctx" ] && line="$line | $ctx"
[ -n "$rate" ] && line="$line | $rate"

printf "\033[2m%s\033[0m\n" "$line"
