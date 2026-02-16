---
description: Activate the Database Architect specialist agent
---
# Trigger: /database-architect

Use this command to specifically engage the **database-architect** for tasks within their domain.

1. **Context Analysis**
   - Identify the specific database-architect requirements in the user request.
   - Cross-reference with `@[agent-skills/database-architect]` if applicable.

2. **Engage Agent**
   - Use the **database-architect** agent to process the task.
   - Enforce symbolic density per `@[/poweruseage]`.
   - Perform memory profiling per `@[/memory-optimization]`.

3. **Interconnection**
   - Proactively suggest related workflows (e.g., if debugging, suggest `/audit`).

## 🕸️ Spider Web Sync
- **Integrated Optimizations**: Apply `@[/poweruseage]` Level 3 + `@[/memory-optimization]`.
- **Related Triggers**: `/frontend-specialist`, `/database-architect`, `/debug`.
