# devark — ets_runtime TDD Development Skill

ets_runtime 通用开发的 TDD 编排技能，支持 Claude Code、OpenCode 等 agent 工具。

## 架构

三角色协作：

| 角色 | 职责 |
|------|------|
| **Planner**（SKILL.md） | 需求确认、任务拆分、派发 Worker/Reviewer、编译验证、状态管理 |
| **Worker**（devark-worker） | TDD 写测试和实现 → 格式化 → 提交 |
| **Reviewer**（devark-reviewer） | 5 项评分标准审查代码，≥95 分通过，<95 分打回 |

## 依赖

- **clang-format**：代码格式化（`apt install clang-format` 或 `brew install clang-format`），也会自动在 repo 的 `prebuilts/` 目录下查找

## 安装

### OpenCode

将 skills 和 agents 复制到项目目录：

```bash
git clone https://github.com/ekil1100/claude-markplace.git /tmp/ekil-marketplace
cp -r /tmp/ekil-marketplace/devark/skills/* .opencode/skills/
cp -r /tmp/ekil-marketplace/devark/agents/* .opencode/agents/
```

或复制到全局目录：

```bash
cp -r /tmp/ekil-marketplace/devark/skills/* ~/.config/opencode/skills/
cp -r /tmp/ekil-marketplace/devark/agents/* ~/.config/opencode/agents/
```

### 其他 agent 工具

将 `skills/` 和 `agents/` 目录复制到对应工具的技能发现路径即可（如 `.agents/skills/`、`.agents/agents/`）。

