# ekil-marketplace

Claude Code 插件市场。

## 添加市场

```bash
# 终端
claude marketplace add https://github.com/ekil1100/claude-markplace/raw/main/marketplace.json

# Claude Code 内
/plugin marketplace add ekil1100/claude-markplace
```

## 插件

### planning-with-files

Manus 风格持久化规划与进度跟踪。

```bash
# 终端
claude plugin install planning-with-files@ekil-marketplace

# Claude Code 内
/plugin install planning-with-files@ekil-marketplace
```

### ai-assisted-case-study

AI 辅助工作案例文档生成。将 AI 辅助研发过程沉淀为可验证的案例文档，用于团队分享和知识沉淀。

**依赖：** [superpowers](#superpowers) 的 `episodic-memory:search-conversations`

```bash
# 终端
claude plugin install ai-assisted-case-study@ekil-marketplace

# Claude Code 内
/plugin install ai-assisted-case-study@ekil-marketplace
```

## 依赖

### Superpowers

```bash
# 终端
claude plugin install superpowers --url https://github.com/anthropics/claude-code-superpowers/raw/main/.claude-plugin

# Claude Code 内
/plugin install superpowers --url https://github.com/anthropics/claude-code-superpowers/raw/main/.claude-plugin
```

## 许可证

各插件保留原始许可证，详见插件目录。
