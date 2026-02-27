# Plan 输出模板

Planner 在步骤 1 输出 Plan 时使用此模板：

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

**Tests:** TS / C++ / TS + C++

**Step 1: Write failing test**
[完整测试代码]

**Step 2: Write minimal implementation**
[完整实现代码]

**Step 3: Commit**
`feat(scope): description`
```
