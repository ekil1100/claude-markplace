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
| `format.sh` | 格式化 git 工作区中已修改的 C/C++ 文件 |
| `ets_runtime.md` | ets_runtime 编译、测试、运行参考（按需读取） |

---

## 执行流程

### 0. 需求确认

在写任何代码之前，必须先完成需求确认：

1. **质疑需求合理性**：是否真的需要参考 V8？有没有更简单的方案？
2. **确认 V8 参考范围**：用户需要提供具体的 V8 源文件路径
3. **确认 V8 源码根路径**：如果用户前面没提到，主动询问（如 `/path/to/v8/`）
4. **明确实现范围**：哪些功能需要实现、哪些可以简化或跳过
5. **识别差异风险**：V8 和 ets_runtime 的架构差异可能导致的问题

使用 `AskUserQuestion` 工具完成确认。

### 1. 输出 Plan

需求确认后，输出实现计划（用户可提修改意见，迭代直到确认）：

```markdown
# [功能名] Implementation Plan

**Goal:** [一句话目标]
**Architecture:** [2-3 句方案描述]
**V8 Reference:** [参考的 V8 源文件列表]

---

### Task 1: [组件名]

**Files:**
- Create: `exact/path/to/file.h`
- Modify: `exact/path/to/existing.cpp:123-145`
- Test: `tests/exact/path/to/test.cpp`

**Step 1: Write failing test**
[完整测试代码]

**Step 2: Write minimal implementation**
[完整实现代码]

**Step 3: Commit**
`feat(scope): description`
```

**⚠️ 用户确认 Plan 后才能进入下一步。**

### 2. 派发 Worker

```
Task(dev8-worker, run_in_background=True, max_turns=50):
  "实现 [Task 描述]。
   V8 参考：[V8 源文件路径]
   V8 源码根路径：[v8_root]
   项目根路径：[project_root]
   文档目录：[docs_dir]
   **禁止编译**"
```

Worker 完成后会执行 `${CLAUDE_PLUGIN_ROOT}/format.sh` 格式化代码。

### 3. 派发 Reviewer

```
Task(dev8-reviewer, run_in_background=True):
  "审查最新提交。
   V8 参考：[V8 源文件路径]
   V8 源码根路径：[v8_root]
   任务描述：[Task 描述]"
```

**Review 结果处理**：

| 结果 | 动作 |
|------|------|
| ≥90 分 | 通过，进入下一步 |
| <90 分（第 1-3 轮） | 将 Reviewer 的修复建议附给 Worker，重新派发 |
| <90 分（第 3 轮后） | 升级给用户决策 |

### 4. 编译验证（可选）

问用户是否需要编译验证。先 `Read ${CLAUDE_PLUGIN_ROOT}/ets_runtime.md` 获取完整的构建/测试/运行命令参考。

**自动检测工作目录**：

- **如果在 ets_runtime 目录下**（路径包含 `arkcompiler/ets_runtime`）：
  - 令 `OHOS_ROOT` 为 ets_runtime 往上两级目录（即包含 `ark.py` 的目录）
  - GN 构建测试：`cd ${OHOS_ROOT} && python3 ark.py x64.debug {test_name}{Mode}Action`
  - 直接用二进制快速验证：见 `ets_runtime.md` 第 2 节
- **否则**：
  - 询问用户构建/测试命令

编译失败 → 将错误信息附给 Worker，重新派发修复。

### 5. DONE

所有 Task 完成、Review 通过、编译验证通过（或跳过）后，汇总报告结果。

---

## 并行规则

- Review 期间可派发其他**独立** Task 的 Worker/Reviewer
- 不要同时启动两个相同 Worker（重复工作）
- 不要派发依赖当前 Task 的工作

---

## 错误追加

工作过程中如果发现新的错误模式（Worker 或 Reviewer 反复犯的错），应追加到 `${CLAUDE_PLUGIN_ROOT}/mistakes.md`。

---

## 重要约束

- Worker **禁止编译**，编译由 Planner 在步骤 4 统一执行
- Reviewer **禁止编译**，只做代码审查
- **代码注释中禁止提及 V8、Maglev 或任何外部项目来源**
- V8 路径、项目路径等由 Planner 在 dispatch 时注入，不要硬编码
