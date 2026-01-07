# Reference: Manus Context Engineering Principles

This document explains the underlying principles from Manus AI that inform the planning-with-files workflow.

## The Core Problem

AI agents face several challenges during complex tasks:

1. **Context window limits** - Can't hold everything in memory
2. **Attention drift** - Original goals fade as conversation grows
3. **Error amnesia** - Mistakes are forgotten and repeated
4. **Information overload** - Too much context degrades performance

## The Solution: Files as External Memory

Manus's key insight: **Use the filesystem as working memory.**

Instead of keeping everything in the context window, store information in files and read them when needed. This:

- Frees up context space
- Creates persistent records
- Enables goal refreshing
- Builds error knowledge

## The 6 Principles

### Principle 1: Maintain Information Across Contexts

**Problem:** Context resets lose critical information.

**Solution:** Write important information to files immediately. Don't assume you'll remember it.

```
Bad:  "I'll remember the API key format"
Good: Write api_notes.md with the format documented
```

### Principle 2: Manipulate Attention Strategically

**Problem:** As context grows, early information fades from "attention."

**Solution:** Re-read plan files before major decisions. This brings goals back into the attention window.

```
Before deciding: Read task_plan.md
Then: Make the decision with fresh goals
```

### Principle 3: Store Errors Persistently

**Problem:** Errors are fixed but forgotten, leading to repeated mistakes.

**Solution:** Log every error to the plan file. Build a knowledge base of what went wrong.

```markdown
## Errors Encountered
- [Error]: API timeout on large requests
  [Resolution]: Batch requests into chunks of 100
```

### Principle 4: Use Progressive File Disclosure

**Problem:** Loading all information at once wastes context.

**Solution:** Create multiple files, read only what's needed for current task.

```
task_plan.md    <- Read for goals
notes.md        <- Read for research
deliverable.md  <- Read for final output
```

### Principle 5: Optimize Context Window

**Problem:** Large outputs consume valuable context space.

**Solution:** Write large outputs to files, keep only paths in memory.

```
Bad:  Keep entire API response in context
Good: Write to api_response.json, keep path in context
```

### Principle 6: Create Before Execute

**Problem:** Jumping into execution leads to scope creep and forgotten goals.

**Solution:** Always create a plan file before starting work.

```
1. Receive task
2. Create task_plan.md (FIRST!)
3. Begin execution
4. Update plan after each phase
```

## Why This Works

The key insight is that **reading a file brings its contents into the attention window**.

When you read `task_plan.md`:
- Goals become prominent in context
- Progress is visible
- Errors are remembered
- Next steps are clear

This is why Manus can handle 50+ tool calls without losing focus - the plan file acts as an "attention anchor."

## Comparison to TodoWrite

| TodoWrite | Planning with Files |
|-----------|---------------------|
| In-memory only | Persisted to disk |
| Lost on context reset | Survives context resets |
| No error history | Full error log |
| Single list | Multiple organized files |
| Limited visibility | Files can be reviewed later |

## Source

These principles are derived from analysis of Manus AI's context engineering approach, as documented in various technical discussions about their architecture.
