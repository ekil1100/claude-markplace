#!/bin/bash
# 格式化 git 工作区中已修改的 C/C++ 文件（仅格式化修改的部分）
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
STYLE="file:${SCRIPT_DIR}/.clang-format"

if ! command -v clang-format &>/dev/null; then
  echo "Error: clang-format not found. Please install it (e.g., apt install clang-format)." >&2
  exit 1
fi

git diff --name-only --diff-filter=ACMR -- '*.h' '*.cpp' | while IFS= read -r file; do
  [ -f "$file" ] || continue

  lines_args=""
  while IFS= read -r hunk; do
    if [[ "$hunk" =~ \+([0-9]+)(,([0-9]+))? ]]; then
      start="${BASH_REMATCH[1]}"
      count="${BASH_REMATCH[3]:-1}"
      [ "$count" -eq 0 ] && continue  # 纯删除，无需格式化
      end=$((start + count - 1))
      lines_args="$lines_args --lines=${start}:${end}"
    fi
  done < <(git diff -U0 -- "$file" | grep '^@@')

  if [ -n "$lines_args" ]; then
    clang-format -i --style="$STYLE" $lines_args "$file"
  fi
done
