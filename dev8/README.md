# dev8 — V8-Referenced TDD Development Plugin

Claude Code 插件，用于参考 V8 源码实现 ets_runtime 功能的 TDD 编排。

## 架构

三角色协作：

| 角色 | 职责 |
|------|------|
| **Planner**（SKILL.md） | 需求确认、任务拆分、派发 Worker/Reviewer、编译验证、状态管理 |
| **Worker**（dev8-worker） | 读 V8 源码 → TDD 写测试和实现 → 格式化 → 提交 |
| **Reviewer**（dev8-reviewer） | 6 项评分标准审查代码，≥95 分通过，<95 分打回 |

## 依赖

- **clang-format**：代码格式化（`brew install clang-format` 或 `apt install clang-format`）

## 使用方式

在 Claude Code 中使用 `/dev8` 触发，或在 ets_runtime 项目目录下讨论"参考 V8 实现"时自动触发。

## 评分标准

| 项目 | 满分 |
|------|------|
| 正确性 | 30 |
| 测试质量 | 30 |
| V8 源码对齐 | 10 |
| 代码规范 | 15 |
| 提交原子性 | 10 |
| 文档同步 | 5 |
| **总分** | **100** |

通过阈值：**95 分**。未通过最多打回 3 轮，之后升级给用户决策。

## 文件结构

```
dev8/
├── README.md              # 本文件
├── skills/dev8/SKILL.md   # Planner 主流程
├── agents/
│   ├── dev8-worker.md     # Worker agent
│   └── dev8-reviewer.md   # Reviewer agent
├── review.md              # 评分标准详情
├── states.md              # Task 状态定义
├── mistakes.md            # 已知错误模式
├── format.sh              # clang-format 包装脚本
├── .clang-format          # 格式化配置
├── ets_runtime.md         # ets_runtime 编译/测试参考
├── plan-template.md       # Plan 输出模板
└── tasks-template.md      # tasks.md 模板
```
