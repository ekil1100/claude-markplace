# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Claude Code plugin marketplace. No build pipeline — documentation and metadata only.

- `.claude-plugin/marketplace.json` - Plugin registry (source of truth)
- Each plugin lives in its own root-level directory with a `skills/` subdirectory

## Adding or Changing Plugins

1. Create a root-level directory with `skills/<skill-name>/SKILL.md`
2. Register in `marketplace.json`
3. **When changing any plugin, bump its `version` in `marketplace.json`**
