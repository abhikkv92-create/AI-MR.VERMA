---
description: Activate the Debugger specialist agent
---
# Trigger: /debugger

Use this command to specifically engage the **debugger** for tasks within their domain.

1. **Context Analysis**
   - Identify the specific debugger requirements in the user request.
   - Cross-reference with `@[agent-skills/debugger]` if applicable.

2. **Engage Agent**
   - Use the **debugger** agent to process the task.
   - Enforce symbolic density per `@[/poweruseage]`.
   - Perform memory profiling per `@[/memory-optimization]`.

3. **Interconnection**
   - Proactively suggest related workflows (e.g., if debugging, suggest `/audit`).

## 🕸️ Spider Web Sync
- **Integrated Optimizations**: Apply `@[/poweruseage]` Level 3 + `@[/memory-optimization]`.
- **Related Triggers**: `/frontend-specialist`, `/debug`.
