# ekil-marketplace

Claude Code 插件市场。

## 添加市场

```bash
/plugin marketplace add ekil1100/claude-markplace
```

## 插件

### planning-with-files

Manus 风格持久化规划与进度跟踪。

```bash
/plugin install planning-with-files@ekil-marketplace
```

### ai-assisted-case-study

AI 辅助工作案例文档生成。将 AI 辅助研发过程沉淀为可验证的案例文档，用于团队分享和知识沉淀。

**依赖：** [episodic-memory](#episodic-memory)

```bash
/plugin install ai-assisted-case-study@ekil-marketplace
```

### dev8

V8 参考源码驱动的 TDD 开发插件，用于参考 V8 源码实现 ets_runtime 功能。三角色协作（Planner / Worker / Reviewer），含代码审查评分机制。

```bash
/plugin install dev8@ekil-marketplace
```

### commit-push

提交所有更改并推送到远程。

```bash
/plugin install commit-push@ekil-marketplace
```

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
