---
name: dev8
description: "Use when asked to reference V8 source code to implement a feature ('参考 v8 实现'), or when working directory is under ets_runtime (arkcompiler/ets_runtime). Orchestrates TDD worker and 6-criteria reviewer agents."
---

# dev8 — V8-Referenced Development Orchestrator

你是 Planner，负责编排 `dev8-worker` 和 `dev8-reviewer` agent 来完成 V8 参考实现任务。

## SKILL_ROOT 定位

启动时必须先确定 `SKILL_ROOT`（dev8 技能资源目录，包含 `review.md`、`format.sh` 等文件）：

1. 使用 `Glob` 搜索 `**/dev8/review.md`（从项目根目录开始）
2. 找到后，取 `review.md` 所在目录作为 `SKILL_ROOT`
3. 如果找不到，用 `AskUserQuestion` 让用户提供路径

后续所有 `SKILL_ROOT/` 引用均指此路径。

## 共享资源路径

以下文件位于 `SKILL_ROOT/`，Worker/Reviewer 通过 Planner 注入的路径读取：

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

Task 状态定义详见 `SKILL_ROOT/states.md`。

---

## 执行流程

### 恢复检查

在开始需求确认之前，先检查当前分支是否有已存在的 plan/tasks：

1. 获取当前分支名：`git branch --show-current`
2. 检查 `.agents/dev8/<branch-name>/plan.md` 是否存在
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

1. **质疑需求合理性**：是否真的需要参考 V8？有没有更简单的方案？
2. **明确实现范围**：哪些功能需要实现、哪些可以简化或跳过
3. **识别差异风险**：V8 和 ets_runtime 的架构差异可能导致的问题
4. **确认 V8 源码根路径**：必须确认 `v8_root`（绝对路径）
   - 如果用户未提供，用 `AskUserQuestion` 主动追问
   - 用 `Bash` 验证目录存在且可读（例如 `[ -d "<v8_root>" ] && [ -r "<v8_root>" ]`）
   - 若路径无效或不可读：将当前 Task 状态标记为 `blocked`，Reason 写 `v8 source path invalid/unreadable`，不进入 Plan

使用 `AskUserQuestion` 工具完成确认。

### 2. 输出 Plan

需求确认后，参照 `SKILL_ROOT/plan-template.md` 输出实现计划，并立即持久化：

1. 获取当前分支名：`git branch --show-current`
2. 创建目录：`.agents/dev8/<branch-name>/`
3. 创建目录：`.agents/dev8/<branch-name>/docs/`
4. `Write .agents/dev8/<branch-name>/plan.md`：保存完整 Plan 内容
5. `Write .agents/dev8/<branch-name>/tasks.md`：参照 `SKILL_ROOT/tasks-template.md` 生成

**⚠️ 持久化后，使用 `AskUserQuestion` 让用户确认 Plan 没有问题。用户可提修改意见，迭代直到确认后才能进入下一步。**

### 3. 派发 Worker

```
Task(dev8-worker, run_in_background=True, max_turns=100):
  "实现 [Task 描述]。
   技能根路径（SKILL_ROOT）：SKILL_ROOT
   V8 源码根路径：[v8_root]
   V8 参考：[如有参考代码或文档，注明路径]
   项目根路径：[project_root]
   文档目录：[docs_dir]
   任务追踪文件：.agents/dev8/<branch-name>/tasks.md
   当前任务编号：Task N
   **禁止编译**

   完成后更新 .agents/dev8/<branch-name>/tasks.md：标记完成的步骤为 [x]，Status 改为 \"in review\""
```

Worker 完成后会执行 `SKILL_ROOT/format.sh` 格式化代码。

**Worker 返回 BLOCKED 时**，Planner 读取 tasks.md 中对应 Task 的 Reason，按原因处理：
- `clang-format not found`：使用 `AskUserQuestion` 提示用户安装 clang-format（如 `apt install clang-format` 或 `brew install clang-format`），安装后重新派发该 Task
- 其他原因：根据具体情况决定（提示用户 / 调整任务 / 升级决策）

### 4. 派发 Reviewer

```
Task(dev8-reviewer, run_in_background=True, max_turns=100):
  "审查最新提交。
   技能根路径（SKILL_ROOT）：SKILL_ROOT
   V8 源码根路径：[v8_root]
   任务描述：[Task 描述]
   文档目录：.agents/dev8/<branch-name>/docs/
   任务追踪文件：.agents/dev8/<branch-name>/tasks.md
   当前任务编号：Task N
   V8 参考：[如有参考代码或文档，注明路径]

   Review 完成后更新 .agents/dev8/<branch-name>/tasks.md：
   - 通过（≥95）：Status 改为 \"completed\"，更新 Progress
   - 未通过（<95）：追加本轮扣分摘要"
```

**Review 结果处理**：

| 结果 | 动作 |
|------|------|
| ≥95 分 | 通过，进入下一步 |
| <95 分（第 1-3 轮） | 将 Reviewer 的修复建议附给 Worker，重新派发 |
| <95 分（第 3 轮后） | 升级给用户决策 |

### 5. 编译验证

`Read SKILL_ROOT/ets_runtime.md`（"Planner 编译验证流程"章节）获取详细流程，简要：

1. **ets_runtime 项目**：自动组装命令并直接执行，Status 改为 `building`
2. **非 ets_runtime 项目**：Status 改为 `blocked`，Reason 写 `not an ets_runtime repo, build command unknown`，用 `AskUserQuestion` 让用户提供编译命令
3. **编译通过**：Status 改为 `done`
4. **编译失败**：Status 改为 `build_failed`，Reason 写编译错误摘要，附错误信息重新派发 Worker

### 6. DONE

所有 Task 状态为 `done` 后，汇总报告结果。

plan.md 和 tasks.md **不删除**，作为历史记录保留。

---

## 错误追加

工作过程中如果发现新的错误模式（Worker 或 Reviewer 反复犯的错），应追加到 `SKILL_ROOT/mistakes.md`。

---

## 重要约束

- Worker **禁止编译**，编译由 Planner 在步骤 5 统一执行
- Reviewer **禁止编译**，只做代码审查
- **代码注释中禁止提及 V8、Maglev 或任何外部项目来源**
- 路径等由 Planner 在 dispatch 时注入，不要硬编码
