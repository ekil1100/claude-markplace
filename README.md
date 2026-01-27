# ekil-marketplace

Claude Code 插件市场。

## 插件列表

| 插件 | 描述 | 依赖 |
|------|------|------|
| [planning-with-files](./planning-with-files/) | Manus 风格持久化规划与进度跟踪 | - |
| [ai-assisted-case-study](./ai-assisted-case-study/) | AI 辅助工作案例文档生成 | [superpowers](#依赖安装) |

## 安装

### 1. 添加市场

```bash
# 终端
claude marketplace add https://github.com/ekil1100/claude-markplace/raw/main/marketplace.json

# Claude Code 内
/plugin marketplace add ekil1100/claude-markplace
```

### 2. 安装插件

```bash
# 终端
claude plugin install <插件名>@ekil-marketplace

# Claude Code 内
/plugin install <插件名>@ekil-marketplace
```

## 依赖安装

### Superpowers

`ai-assisted-case-study` 依赖 superpowers 的 `episodic-memory:search-conversations` 搜索历史对话。

```bash
# 终端
claude plugin install superpowers --url https://github.com/anthropics/claude-code-superpowers/raw/main/.claude-plugin

# Claude Code 内
/plugin install superpowers --url https://github.com/anthropics/claude-code-superpowers/raw/main/.claude-plugin
```

## 许可证

各插件保留原始许可证，详见插件目录。
