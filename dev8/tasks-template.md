# tasks.md 模板

Planner 在用户确认 Plan 后，按此模板生成 `.claude/dev8/<branch-name>/tasks.md`：

```markdown
# Tasks

## Task 1: [组件名]
- [ ] Write failing test (TS / C++ / TS + C++)
- [ ] Write implementation
- [ ] Format & commit
- Status: pending
- Reason:

## Task 2: ...

---
Progress: 0/N completed
```

括号内测试类型为 `TS` / `C++` / `TS + C++` 之一，与 Plan 中对应 Task 的 `Tests` 字段一致。
