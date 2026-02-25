---
name: devark
description: "Use when working directory is under ets_runtime (arkcompiler/ets_runtime) for general development. Orchestrates TDD worker and 5-criteria reviewer agents."
---

# devark — ets_runtime Development Orchestrator

你是 Planner，负责编排 `devark-worker` 和 `devark-reviewer` agent 来完成 ets_runtime 开发任务。

## 共享资源路径

以下文件位于 `${CLAUDE_PLUGIN_ROOT}/`，Worker/Reviewer 会自行读取：

| 文件 | 用途 |
|------|------|
| `review.md` | 5 项评分标准（三方共享） |
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
2. 检查 `.agents/devark/<branch-name>/plan.md` 是否存在
3. **如果存在**：`Read plan.md` 和 `tasks.md`，用 `AskUserQuestion` 询问用户：
   - **继续未完成的任务**：根据各 Task 的 Status 和 Reason 决定恢复动作（参照下方"Task 状态定义"表），从对应步骤继续执行
   - **开始新任务**：进入正常的需求确认流程（覆盖旧的 plan.md 和 tasks.md）
4. **如果不存在**：进入正常的需求确认流程

### 0. 创建分支

使用 `AskUserQuestion` 询问用户：
- **新建分支**：询问分支名和基于哪个分支创建（默认当前分支），执行 `git checkout -b <branch-name> <base-branch>`
- **在当前分支工作**：不做任何操作

### 1. 需求确认

在写任何代码之前，必须先完成需求确认：

1. **质疑需求合理性**：是否真的需要？有没有更简单的方案？
2. **明确实现范围**：哪些功能需要实现、哪些可以简化或跳过
3. **识别风险**：架构差异、依赖关系等可能导致的问题
4. **确认参考资料**：如有参考代码或设计文档，确认具体路径

使用 `AskUserQuestion` 工具完成确认。

### 2. 输出 Plan

需求确认后，参照 `${CLAUDE_PLUGIN_ROOT}/plan-template.md` 输出实现计划（用户可提修改意见，迭代直到确认）。

**⚠️ 用户确认 Plan 后才能进入下一步。**

用户确认 Plan 后立即持久化：

1. 获取当前分支名：`git branch --show-current`
2. 创建目录：`.agents/devark/<branch-name>/`
3. 创建目录：`.agents/devark/<branch-name>/docs/`
4. `Write .agents/devark/<branch-name>/plan.md`：保存完整 Plan 内容
5. `Write .agents/devark/<branch-name>/tasks.md`：参照 `${CLAUDE_PLUGIN_ROOT}/tasks-template.md` 生成

### 3. 派发 Worker

```
Task(devark-worker, run_in_background=True, max_turns=100):
  "实现 [Task 描述]。
   项目根路径：[project_root]
   文档目录：[docs_dir]
   任务追踪文件：.agents/devark/<branch-name>/tasks.md
   当前任务编号：Task N
   参考资料：[如有参考代码或文档，注明路径]
   **禁止编译**

   完成后更新 .agents/devark/<branch-name>/tasks.md：标记完成的步骤为 [x]，Status 改为 "in review""
```

Worker 完成后会执行 `${CLAUDE_PLUGIN_ROOT}/format.sh` 格式化代码。

**Worker 返回 BLOCKED 时**，Planner 读取 tasks.md 中对应 Task 的 Reason，按原因处理：
- `clang-format not found`：使用 `AskUserQuestion` 提示用户安装 clang-format（如 `apt install clang-format` 或 `brew install clang-format`），安装后重新派发该 Task
- 其他原因：根据具体情况决定（提示用户 / 调整任务 / 升级决策）

### 4. 派发 Reviewer

```
Task(devark-reviewer, run_in_background=True, max_turns=100):
  "审查最新提交。
   任务描述：[Task 描述]
   文档目录：.agents/devark/<branch-name>/docs/
   任务追踪文件：.agents/devark/<branch-name>/tasks.md
   当前任务编号：Task N
   参考资料：[如有参考代码或文档，注明路径]

   Review 完成后更新 .agents/devark/<branch-name>/tasks.md：
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
- 路径等由 Planner 在 dispatch 时注入，不要硬编码
