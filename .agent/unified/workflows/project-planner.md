---
description: Activate the Project Planner specialist agent
---
# Trigger: /project-planner

Use this command to specifically engage the **project-planner** for tasks within their domain.

1. **Context Analysis**
   - Identify the specific project-planner requirements in the user request.
   - Cross-reference with `@[agent-skills/project-planner]` if applicable.

2. **Engage Agent**
   - Use the **project-planner** agent to process the task.
   - Enforce symbolic density per `@[/poweruseage]`.
   - Perform memory profiling per `@[/memory-optimization]`.

3. **Interconnection**
   - Proactively suggest related workflows (e.g., if debugging, suggest `/audit`).

## 🕸️ Spider Web Sync
- **Integrated Optimizations**: Apply `@[/poweruseage]` Level 3 + `@[/memory-optimization]`.
- **Related Triggers**: `/frontend-specialist`, `/plan`, `/debug`.
