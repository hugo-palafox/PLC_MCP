---
name: changelog
description: Automatically track and document all changes made to the codebase in a centralized changelog.md file.
---

# Changelog Skill

This skill ensures that every significant change, implementation, or refactoring in the project is documented in the `changelog.md` file located at the project root.

## Instructions

1. **When to Update**: Every time you complete a task, fix a bug, or implement a new feature.
2. **Format**: Use standard Keep A Changelog format (Log date, category like [Added], [Changed], [Fixed]).
3. **Execution**:
    - Open `changelog.md`.
    - Add a new entry under the current date.
    - Be specific about what was changed and why.

## Example Entry

### [2026-02-13]
#### Added
- `MockDriver.py` for simulated real-time data.
- `.agent/skills/changelog/SKILL.md` to track project evolution.
