# ekil-marketplace

Claude Code / OpenCode 插件市场。

## 添加市场

**Claude Code：**

```bash
/plugin marketplace add ekil1100/claude-markplace
```

**OpenCode：**

OpenCode 没有市场命令，通过手动复制 skill 文件安装（见各插件说明）。

## 插件

### planning-with-files

Manus 风格持久化规划与进度跟踪。

```bash
# Claude Code
/plugin install planning-with-files@ekil-marketplace

# OpenCode（复制到项目或全局 skills 目录）
git clone https://github.com/ekil1100/claude-markplace.git /tmp/ekil-marketplace
cp -r /tmp/ekil-marketplace/planning-with-files/skills/* .opencode/skills/
```

### ai-assisted-case-study

AI 辅助工作案例文档生成。将 AI 辅助研发过程沉淀为可验证的案例文档，用于团队分享和知识沉淀。

**依赖：** [episodic-memory](#episodic-memory)

```bash
# Claude Code
/plugin install ai-assisted-case-study@ekil-marketplace

# OpenCode
cp -r /tmp/ekil-marketplace/ai-assisted-case-study/skills/* .opencode/skills/
```

### dev8

V8 参考源码驱动的 TDD 开发插件，用于参考 V8 源码实现 ets_runtime 功能。三角色协作（Planner / Worker / Reviewer），含代码审查评分机制。

```bash
# Claude Code
/plugin install dev8@ekil-marketplace

# OpenCode
cp -r /tmp/ekil-marketplace/dev8/skills/* .opencode/skills/
cp -r /tmp/ekil-marketplace/dev8/agents/* .opencode/agents/
```

### devark

ets_runtime 通用 TDD 开发插件。三角色协作（Planner / Worker / Reviewer），含 5 项代码审查评分机制。

```bash
# Claude Code
/plugin install devark@ekil-marketplace

# OpenCode
cp -r /tmp/ekil-marketplace/devark/skills/* .opencode/skills/
cp -r /tmp/ekil-marketplace/devark/agents/* .opencode/agents/
```

**依赖：** `clang-format`。插件会优先使用系统中的 `clang-format`，找不到时再尝试 repo `prebuilts/` 里的可执行文件。

**OpenCode 全局安装：**

```bash
cp -r /tmp/ekil-marketplace/devark/skills/* ~/.config/opencode/skills/
cp -r /tmp/ekil-marketplace/devark/agents/* ~/.config/opencode/agents/
```

**其他 agent 工具：** 将 `devark/skills/` 和 `devark/agents/` 复制到对应工具的技能/agent 发现目录即可。

### commit-push

提交所有更改并推送到远程。

```bash
# Claude Code
/plugin install commit-push@ekil-marketplace
```

> OpenCode 不支持：commit-push 是 Claude Code slash command，无对应 skill 文件。

## 依赖

### episodic-memory

GitHub: https://github.com/obra/episodic-memory

```bash
# 添加 superpowers 市场
/plugin marketplace add obra/superpowers-marketplace

# 安装 episodic-memory
/plugin install episodic-memory@superpowers-marketplace
```

## 许可证

各插件保留原始许可证，详见插件目录。
