---
name: devark
description: "General-purpose ets_runtime development orchestrator for feature work, bug fixes, refactors, and tests under arkcompiler/ets_runtime. Use when Codex should clarify requirements, persist a plan and task list, coordinate implementation/review loops, and finish with build verification for ets_runtime changes."
---

# devark — ets_runtime Development Orchestrator

负责把 ets_runtime 开发任务拆成可恢复、可审查的原子任务，并协调实现、评审、编译验证。

## SKILL_ROOT 定位

启动时先确定 `SKILL_ROOT`（devark 资源目录，包含 `review.md`、`format.sh` 等文件）：

1. 从项目根目录搜索 `**/devark/review.md`
2. 将 `review.md` 所在目录作为 `SKILL_ROOT`
3. 如果找不到，向用户确认已安装的 devark 资源路径

后续所有 `SKILL_ROOT/` 引用均指此路径。

## 共享资源路径

以下文件位于 `SKILL_ROOT/`，按需读取，不要一次性全部加载：

| 文件 | 用途 |
|------|------|
| `review.md` | 5 项评分标准 |
| `mistakes.md` | 常见错误模式（可追加） |
| `.clang-format` | 代码格式化配置 |
| `format.sh` | 格式化 git 工作区中已修改的 C/C++ 文件（仅修改行） |
| `ets_runtime.md` | ets_runtime 编译、测试、运行参考（按需读取） |
| `states.md` | Task 状态定义 |
| `plan-template.md` | Plan 输出模板 |
| `tasks-template.md` | tasks.md 模板 |

Task 状态定义详见 `SKILL_ROOT/states.md`。

---

## 执行流程

### 恢复检查

在开始需求确认之前，先检查当前分支是否有已存在的 plan/tasks：

1. 获取当前分支名：`git branch --show-current`
2. 检查 `.agents/devark/<branch-name>/plan.md` 是否存在
3. **如果存在**：读取 `plan.md` 和 `tasks.md`，询问用户是继续未完成的任务，还是开始新任务覆盖旧文件
4. **如果不存在**：进入正常的需求确认流程

### 0. 创建分支

先与用户确认工作分支：
- **新建分支**：询问分支名和基于哪个分支创建（默认当前分支），执行 `git checkout -b <branch-name> <base-branch>`
- **在当前分支工作**：不做任何操作

### 1. 需求确认

在写任何代码之前，必须先完成需求确认：

1. **质疑需求合理性**：是否真的需要？有没有更简单的方案？
2. **明确实现范围**：哪些功能需要实现、哪些可以简化或跳过
3. **识别风险**：架构差异、依赖关系等可能导致的问题
4. **确认参考资料**：如有参考代码或设计文档，确认具体路径

只在会影响设计或验证结果的点上追问用户，避免把简单任务问成访谈。

### 2. 输出 Plan

需求确认后，参照 `SKILL_ROOT/plan-template.md` 输出实现计划，并立即持久化：

1. 获取当前分支名：`git branch --show-current`
2. 创建目录：`.agents/devark/<branch-name>/`
3. 创建目录：`.agents/devark/<branch-name>/docs/`
4. 写入 `.agents/devark/<branch-name>/plan.md`：保存完整 Plan 内容
5. 写入 `.agents/devark/<branch-name>/tasks.md`：参照 `SKILL_ROOT/tasks-template.md` 生成

**⚠️ 持久化后先让用户确认 Plan 没有问题，再进入下一步。**

### 2.5 无命名 agent 时的本地 fallback

如果当前环境不支持按名称派发 `devark-worker` / `devark-reviewer`，Planner 仍要维护**同一套状态机、产物位置和提交边界**，不要退化成临时手工流程。

- **本地执行 Worker 时**，严格按 `devark-worker` 的 contract 自行完成：
  1. 先把当前 Task 状态改为 `in_progress`
  2. 参考 `SKILL_ROOT/review.md`、`mistakes.md`、`states.md`，按 TDD 顺序完成测试和实现
  3. 把任务文档写到 `.agents/devark/<branch-name>/docs/`，不要把这类工作文档写到源码目录或 repo 根目录
  4. 优先使用仓库正式测试布局（如 `test/jittest/...`），不要用临时 C++ harness、repo-local 草稿文档或一次性脚本代替最终交付；若临时验证文件确实必要，验证后删除，不能留在最终工作区状态里
  5. 执行 `SKILL_ROOT/format.sh`
  6. 更新 `tasks.md`：完成后置为 `in_review`，阻塞时置为 `blocked`
  7. `git add` 代码、文档和任务跟踪文件；**首轮创建 Task commit，后续返工、review/build 元数据更新都通过 `git commit --amend` 折叠回同一个 Task commit**。不要把变更留在未提交状态下进入 Review 或结束任务，也不要为同一 Task 追加 `persist review/build state` 之类的 follow-up commit

- **本地执行 Reviewer 时**，严格按 `devark-reviewer` 的 contract 自行完成：
  1. 基于 `git show HEAD` 审查最近一次提交，而不是审查未提交工作区
  2. 按 `review.md` 固定档位打分，并对照 `mistakes.md`
  3. 把 review 记录写到 `.agents/devark/<branch-name>/docs/review_round_<N>.md`（或等价命名）
  4. 通过则把 Task 置为 `completed`，不通过则置为 `rework`
  5. 如果当前没有可审查的提交，先回到 Worker 流程完成 commit，再进入 Review
  6. 如果 review 记录、`tasks.md` 或后续 build 记录导致工作区再次变脏，`git add` 这些 workflow 文件并执行 `git commit --amend --no-edit`，把状态变化折叠回当前 Task commit；不要再追加 `chore(devark): persist review/build state for task N` 这类 follow-up commit

### 3. 派发 Worker

优先将每个原子任务委派给 `devark-worker`；如果当前环境不支持命名 worker，就按上面的本地 fallback 规则自行实现。

委派时提供以下上下文：
- 技能根路径（`SKILL_ROOT`）
- 项目根路径（`project_root`）
- 文档目录（`docs_dir`）
- 任务追踪文件（`.agents/devark/<branch-name>/tasks.md`）
- 当前任务编号（`Task N`）
- 参考资料路径（如有）
- `禁止编译`

Worker 完成后会执行 `SKILL_ROOT/format.sh` 格式化代码。本地 fallback 也必须执行同样的格式化、任务状态更新和 commit，并保证**同一 Task 最终只保留一个 commit**。

**Worker 返回 `BLOCKED` 时**，读取 tasks.md 中对应 Task 的 `Reason`，按原因处理：
- `clang-format not found`：提示用户安装 `clang-format`（如 `apt install clang-format` 或 `brew install clang-format`），安装后重新派发该 Task
- 其他原因：根据具体情况提示用户、调整任务或升级决策

### 4. 派发 Reviewer

优先将代码审查委派给 `devark-reviewer`；如果当前环境不支持命名 reviewer，就按上面的本地 fallback 规则执行一次完整 Review。

委派时提供以下上下文：
- 技能根路径（`SKILL_ROOT`）
- 任务描述
- 文档目录（`.agents/devark/<branch-name>/docs/`）
- 任务追踪文件（`.agents/devark/<branch-name>/tasks.md`）
- 当前任务编号（`Task N`）
- 参考资料路径（如有）

**Review 结果处理**：

| 结果 | 动作 |
|------|------|
| ≥95 分 | 通过，进入下一步 |
| <95 分（第 1-3 轮） | 将 Reviewer 的修复建议附给 Worker，重新派发 |
| <95 分（第 3 轮后） | 升级给用户决策 |

返工轮继续沿用当前 Task commit，修复后通过 `git commit --amend` 更新；不要为同一 Task 叠加新的代码 commit。

### 5. 编译验证

`Read SKILL_ROOT/ets_runtime.md`（"Planner 编译验证流程"章节）获取详细流程，简要：

1. **ets_runtime 项目**：自动组装命令并直接执行，Status 改为 `building`
2. **非 ets_runtime 项目**：Status 改为 `blocked`，Reason 写 `not an ets_runtime repo, build command unknown`，向用户询问编译命令
3. **编译通过**：Status 改为 `done`
4. **编译失败**：Status 改为 `build_failed`，Reason 写编译错误摘要，附错误信息重新派发 Worker

本地 fallback 完成编译验证后，如果 `tasks.md`、review/build 文档或其他 workflow 元数据发生变化，也要把这些变化持久化；持久化方式应为 `git commit --amend --no-edit` 折叠回当前 Task commit，不要只把代码提交掉而把状态文件留在未提交状态，也不要再追加单独的 workflow commit。

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
- **每个 Task 最终只保留一个 commit**；review/build/workflow 元数据通过 amend 折叠进该 Task commit，禁止追加 `persist review/build state` 一类独立 commit
- 本地 fallback 也要遵守 Worker / Reviewer 的职责边界，不能因为没有命名 agent 就跳过 `.agents/devark/<branch>/docs/`、`tasks.md` 或 commit
- 路径等由 Planner 在 dispatch 时注入，不要硬编码
