# 常见错误

> **遇到新的错误模式时，Planner 应追加到此文件。**
> Worker、Reviewer、Planner 均应在工作前 `Read ${CLAUDE_PLUGIN_ROOT}/mistakes.md` 了解已知问题。

---

## 已知错误模式

| # | 错误 | 后果 | 正确做法 |
|---|------|------|----------|
| 1 | 格式化前不运行 `format.sh` | 代码规范扣分 | 写完代码后立即执行 `${CLAUDE_PLUGIN_ROOT}/format.sh` |
| 2 | 编译时空闲等待 | 浪费时间 | 编译期间可派发独立任务的 Worker/Reviewer |
| 3 | 同时启动两个相同 Worker | 重复工作、冲突 | 一个任务只派一个 Worker |
| 4 | 忘记 git add/commit 就返回 | Reviewer 看不到变更 | Worker 必须 git add + commit 后再返回 |
| 5 | 代码注释中提及 V8/Maglev | 违反代码规范 | V8 对应关系只在项目文档中记录，代码中禁止出现 |
| 6 | 先写实现再补测试 | 违反 TDD，测试可能无效 | 严格按 TDD：先写测试 → 再写实现 |
| 7 | 使用 `.cc` 后缀而非 `.cpp` | 不符合 ets_runtime 规范 | 统一使用 `.cpp` |
| 8 | kebab-case 文件名/目录名 | 不符合 ets_runtime 规范 | 使用 `snake_case` |

---

<!-- Planner: 在此行下方追加新的错误模式 -->
