# Product Management Framework

This document outlines the product management framework for this project. The goal is to ensure every user prompt and idea is captured, prioritized, and systematically developed.

## The Workflow

1.  **Capture**: Every user prompt, idea, or request is first logged in `BACKLOG.md`.
2.  **Prioritize**: Items in the backlog are prioritized based on user impact and strategic alignment.
3.  **Plan**: High-priority items are moved to `task.md` for active development.
4.  **Execute**: The AI agent (or developer) implements the planned tasks.
5.  **Review**: Completed tasks are reviewed by the user.
6.  **Archive**: Completed items are marked as "Done" in `BACKLOG.md`.

## Artifacts

### BACKLOG.md
A comprehensive list of all potential work. It serves as the single source of truth for "what could be done."

**Format:**
```markdown
| ID | Status | Priority | Description | Notes |
| :--- | :--- | :--- | :--- | :--- |
| 001 | Todo | High | Implement user authentication | |
```

### task.md
The active to-do list for the current session or sprint. Items here are committed work.

**Format:**
```markdown
- [ ] Task description <!-- id: 0 -->
```

### VISION.md
The long-term strategic vision for the product. Backlog items should align with the vision.

## Roles and Responsibilities

-   **User**: Provides prompts, feedback, and strategic direction.
-   **AI Agent**: Captures prompts into the backlog, proposes plans, executes code, and updates documentation.
