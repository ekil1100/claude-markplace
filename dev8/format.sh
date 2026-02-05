#!/bin/bash
# 格式化 git 工作区中已修改的 C/C++ 文件
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
git diff --name-only --diff-filter=ACMR -- '*.h' '*.cpp' \
  | xargs -r clang-format-14 -i --style="file:${SCRIPT_DIR}/.clang-format"
