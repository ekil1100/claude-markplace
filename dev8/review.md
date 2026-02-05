# 代码 Review 标准

> **读者**：Reviewer agent、Worker agent（自查）
> **用途**：评分标准——Reviewer agent 据此打分，Worker 据此自查

Worker 每次提交前，必须由 Reviewer 审查代码。总分 100 分，**95 分以上才能提交**，否则打回修改。

**打分原则**：每项只能从表格中给出的固定分数档中选取，不允许插值（如正确性只能给 30/24/18/12/0，不能给 26 或 28）。如果实际情况介于两档之间，就低不就高。

**V8 参考信息**：由 Planner 在派发 Reviewer 时通过 prompt 注入（包含 V8 参考源码路径和任务描述），Reviewer 无需自行寻找。

---

## 评分项

### 1. 正确性（30 分）

| 分数 | 标准 |
|------|------|
| 30 | 逻辑完全正确，边界条件覆盖完整，无潜在 bug |
| 24 | 核心逻辑正确，有 1-2 个次要边界未处理 |
| 18 | 核心逻辑正确，但有明显遗漏 |
| 12 | 存在逻辑错误 |
| 0 | 编译不通过或基本逻辑错误 |

检查点：
- 算术溢出、空指针、越界访问
- 类型转换安全性
- GC 安全点是否正确标记
- 反优化路径是否完整

### 2. 测试质量（30 分）

| 分数 | 标准 |
|------|------|
| 30 | 测试覆盖正常路径 + 边界 + 错误路径，断言精确 |
| 24 | 覆盖正常路径和主要边界，断言合理 |
| 18 | 覆盖正常路径但缺少边界测试 |
| 12 | 测试存在但不充分 |
| 0 | 无测试或测试无意义 |

检查点：
- 是否先写测试（TDD）
- 测试是否真的会在实现缺失时失败
- 边界值测试（0、负数、最大值、空输入）
- 错误路径测试（deopt 触发、类型不匹配）

### 3. V8 源码对齐（10 分）

| 分数 | 标准 |
|------|------|
| 10 | 充分理解 V8 实现，功能对等，适配合理 |
| 8 | 理解 V8 实现，小部分功能缺失或适配粗糙 |
| 6 | 部分参考了 V8，但有明显误解或遗漏 |
| 3 | 看起来没有认真读 V8 源码 |
| 0 | 完全凭空实现，与 V8 设计不符 |

检查点：
- 是否覆盖了 V8 对应模块的核心功能
- ets_runtime 适配是否合理（不是简单替换名字）
- 数据结构选择是否与 V8 设计意图一致

### 4. 代码规范（15 分）

| 分数 | 标准 |
|------|------|
| 15 | 完全符合 ets_runtime 编码规范 |
| 12 | 基本符合，1-2 处风格不一致 |
| 9 | 多处不符合规范 |
| 6 | 大面积不符合 |
| 0 | 完全不遵守 |

**格式化**：使用 `${CLAUDE_PLUGIN_ROOT}/.clang-format`（BasedOnStyle: WebKit，4 空格缩进，116 列宽）。提交前必须运行 `${CLAUDE_PLUGIN_ROOT}/format.sh`。

**命名约定**（从 `ecmascript/` 现有代码提取）：

| 元素 | 规则 | 示例 |
|------|------|------|
| 文件名 | `snake_case.h` / `.cpp`（内联头文件用 `-inl.h`） | `jit_task.h`, `compile_decision.cpp`, `ecma_string-inl.h` |
| 类名 | `PascalCase` | `Jit`, `HandlerBase`, `JitTask` |
| 方法名 | `PascalCase` | `GetInstance()`, `IsEnableFastJit()` |
| 成员变量 | `camelCase_`（尾部下划线） | `initialized_`, `jitTaskCnt_` |
| 局部变量 | `camelCase` | `jsFunction`, `compilerTier` |
| 常量/枚举值 | `UPPER_SNAKE_CASE` | `KIND_BIT_LENGTH`, `NONE`, `S_FIELD` |
| 命名空间 | `panda::ecmascript` | |
| 头文件 guard | `ECMASCRIPT_<PATH>_<FILE>_H` | `ECMASCRIPT_JIT_JIT_H` |

**禁止**：
- 不要用 `.cc` 后缀，ets_runtime 统一用 `.cpp`
- 不要用 kebab-case 文件名（如 `tiny-ir.h`），必须用 snake_case（如 `tiny_ir.h`）
- 目录名同理：`test_utils/` 而非 `test-utils/`

**其他**：
- 版权头：Apache 2.0，`Huawei Device Co., Ltd.`
- include 顺序：先系统头文件，再 ecmascript 内部头文件（clang-format 的 `SortIncludes: true` 会处理）
- 内联短函数可在头文件中定义（参照现有 `inline` 用法）
- **代码注释中禁止提及 V8、Maglev 或任何外部项目来源**。V8 对应关系只在项目文档中记录。

### 5. 提交原子性（10 分）

| 分数 | 标准 |
|------|------|
| 10 | 一个提交做一件事，可独立 revert，commit message 清晰 |
| 8 | 基本原子化，commit message 可以更精确 |
| 5 | 一个提交混了多件事 |
| 0 | 大量无关改动混在一起 |

**Commit message 格式**（Conventional Commits，英文）：

```
<type>(<scope>): <description>

[optional body]
```

type: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`
scope: 模块名（由 Planner 在 plan 中确定）
示例: `feat(ir): add Int32Add and Float64Mul node definitions`

检查点：
- 单独 revert 此提交是否破坏构建
- 提交中是否混入了不相关的改动
- commit message 是否符合上述格式

### 6. 文档同步（5 分）

| 分数 | 标准 |
|------|------|
| 5 | 项目文档目录中对应文档已更新，设计说明清晰 |
| 3 | 文档有更新但不够详细 |
| 0 | 代码改了文档没跟上 |

---

## Reviewer 返回格式

Reviewer 审查后返回以下格式（直接作为 agent 返回值，不写文件）：

```markdown
## 评分

| 项目 | 得分 | 满分 | 说明 |
|------|------|------|------|
| 正确性 | XX | 30 | ... |
| 测试质量 | XX | 30 | ... |
| V8 源码对齐 | XX | 10 | ... |
| 代码规范 | XX | 15 | ... |
| 提交原子性 | XX | 10 | ... |
| 文档同步 | XX | 5 | ... |
| **总分** | **XX** | **100** | |

## 结论
**通过** ✅ / **不通过** ❌（XX/100）

## 需修复问题（如未通过）
1. [优先级高] ...
2. [优先级中] ...
```

Review 结果的处理流程（≥95 通过、<95 打回、3 轮未通过 escalation）由 Planner 控制。
