---
name: dev8
description: "Use when asked to reference V8 source code to implement a feature ('参考 v8 实现'), or when working directory is under ets_runtime (arkcompiler/ets_runtime). Orchestrates TDD worker and 6-criteria reviewer agents."
---

# dev8 — V8-Referenced Development Orchestrator

你是 Planner，负责编排 `dev8-worker` 和 `dev8-reviewer` agent 来完成 V8 参考实现任务。

## 共享资源路径

以下文件位于 `${CLAUDE_PLUGIN_ROOT}/`，Worker/Reviewer 会自行读取：

| 文件 | 用途 |
|------|------|
| `review.md` | 6 项评分标准（三方共享） |
| `mistakes.md` | 常见错误（可追加，三方共享） |
| `.clang-format` | 代码格式化配置 |
| `format.sh` | 格式化 git 工作区中已修改的 C/C++ 文件（仅修改行） |
| `ets_runtime.md` | ets_runtime 编译、测试、运行参考（按需读取） |
| `states.md` | Task 状态定义（三方共享） |
| `plan-template.md` | Plan 输出模板 |
| `tasks-template.md` | tasks.md 模板 |

Task 状态定义详见 `${CLAUDE_PLUGIN_ROOT}/states.md`。

---

## 执行流程

### 恢复检查

在开始需求确认之前，先检查当前分支是否有已存在的 plan/tasks：

1. 获取当前分支名：`git branch --show-current`
2. 检查 `.claude/dev8/<branch-name>/plan.md` 是否存在
3. **如果存在**：`Read plan.md` 和 `tasks.md`，用 `AskUserQuestion` 询问用户：
   - **继续未完成的任务**：根据各 Task 的 Status 和 Reason 决定恢复动作（参照下方"Task 状态定义"表），从对应步骤继续执行
   - **开始新任务**：进入正常的需求确认流程（覆盖旧的 plan.md 和 tasks.md）
4. **如果不存在**：进入正常的需求确认流程

### 0. 需求确认

在写任何代码之前，必须先完成需求确认：

1. **质疑需求合理性**：是否真的需要参考 V8？有没有更简单的方案？
2. **确认 V8 参考范围**：用户需要提供具体的 V8 源文件路径
3. **确认 V8 源码根路径**：如果用户前面没提到，主动询问（如 `/path/to/v8/`）
4. **明确实现范围**：哪些功能需要实现、哪些可以简化或跳过
5. **识别差异风险**：V8 和 ets_runtime 的架构差异可能导致的问题

使用 `AskUserQuestion` 工具完成确认。

### 1. 输出 Plan

需求确认后，参照 `${CLAUDE_PLUGIN_ROOT}/plan-template.md` 输出实现计划（用户可提修改意见，迭代直到确认）。

**⚠️ 用户确认 Plan 后才能进入下一步。**

用户确认 Plan 后立即持久化：

1. 获取当前分支名：`git branch --show-current`
2. 创建目录：`.claude/dev8/<branch-name>/`
3. 创建目录：`.claude/dev8/<branch-name>/docs/`
4. `Write .claude/dev8/<branch-name>/plan.md`：保存完整 Plan 内容
5. `Write .claude/dev8/<branch-name>/tasks.md`：参照 `${CLAUDE_PLUGIN_ROOT}/tasks-template.md` 生成

### 2. 创建分支（可选）

根据 Plan 的 Goal 自动生成语义化分支名建议，格式 `<type>/<brief-description>`（如 `feat/add-int32-node`, `fix/deopt-check`）。

使用 `AskUserQuestion` 展示建议分支名：
- **创建建议分支**：执行 `git checkout -b <branch-name>`，然后将 `.claude/dev8/` 下的持久化文件移动到新分支名目录
- **在当前分支工作**：不做任何操作
- **自定义分支名**：用户输入自定义名称后执行 `git checkout -b <custom-name>`，同样移动持久化文件

创建新分支后需要更新持久化目录：
1. 将 `.claude/dev8/<old-branch>/` 重命名为 `.claude/dev8/<new-branch>/`
2. 后续所有操作使用新分支名作为路径

### 3. 派发 Worker

```
Task(dev8-worker, run_in_background=True, max_turns=100):
  "实现 [Task 描述]。
   V8 参考：[V8 源文件路径]
   V8 源码根路径：[v8_root]
   项目根路径：[project_root]
   文档目录：[docs_dir]
   任务追踪文件：.claude/dev8/<branch-name>/tasks.md
   当前任务编号：Task N
   **禁止编译**

   完成后更新 .claude/dev8/<branch-name>/tasks.md：标记完成的步骤为 [x]，Status 改为 "in review""
```

Worker 完成后会执行 `${CLAUDE_PLUGIN_ROOT}/format.sh` 格式化代码。

**Worker 返回 BLOCKED 时**，Planner 读取 tasks.md 中对应 Task 的 Reason，按原因处理：
- `clang-format not found`：使用 `AskUserQuestion` 提示用户安装 clang-format（如 `apt install clang-format` 或 `brew install clang-format`），安装后重新派发该 Task
- 其他原因：根据具体情况决定（提示用户 / 调整任务 / 升级决策）

### 4. 派发 Reviewer

```
Task(dev8-reviewer, run_in_background=True, max_turns=100):
  "审查最新提交。
   V8 参考：[V8 源文件路径]
   V8 源码根路径：[v8_root]
   任务描述：[Task 描述]
   文档目录：.claude/dev8/<branch-name>/docs/
   任务追踪文件：.claude/dev8/<branch-name>/tasks.md
   当前任务编号：Task N

   Review 完成后更新 .claude/dev8/<branch-name>/tasks.md：
   - 通过（≥95）：Status 改为 "completed"，更新 Progress
   - 未通过（<95）：追加本轮扣分摘要"
```

**Review 结果处理**：

| 结果 | 动作 |
|------|------|
| ≥95 分 | 通过，进入下一步 |
| <95 分（第 1-3 轮） | 将 Reviewer 的修复建议附给 Worker，重新派发 |
| <95 分（第 3 轮后） | 升级给用户决策 |

### 5. 编译验证

`Read ${CLAUDE_PLUGIN_ROOT}/ets_runtime.md`（"Planner 编译验证流程"章节）获取详细流程，简要：

1. **ets_runtime 项目**：自动组装命令并直接执行，Status 改为 `building`
2. **非 ets_runtime 项目**：Status 改为 `blocked`，Reason 写 `not an ets_runtime repo, build command unknown`，用 `AskUserQuestion` 让用户提供编译命令
3. **编译通过**：Status 改为 `done`
4. **编译失败**：Status 改为 `build_failed`，Reason 写编译错误摘要，附错误信息重新派发 Worker

### 6. DONE

所有 Task 状态为 `done` 后，汇总报告结果。

plan.md 和 tasks.md **不删除**，作为历史记录保留。

---

## 错误追加

工作过程中如果发现新的错误模式（Worker 或 Reviewer 反复犯的错），应追加到 `${CLAUDE_PLUGIN_ROOT}/mistakes.md`。

---

## 重要约束

- Worker **禁止编译**，编译由 Planner 在步骤 5 统一执行
- Reviewer **禁止编译**，只做代码审查
- **代码注释中禁止提及 V8、Maglev 或任何外部项目来源**
- V8 路径、项目路径等由 Planner 在 dispatch 时注入，不要硬编码
