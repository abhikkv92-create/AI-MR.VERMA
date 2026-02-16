---
description: Activate the Game Developer specialist agent
---
# Trigger: /game-developer

Use this command to specifically engage the **game-developer** for tasks within their domain.

1. **Context Analysis**
   - Identify the specific game-developer requirements in the user request.
   - Cross-reference with `@[agent-skills/game-developer]` if applicable.

2. **Engage Agent**
   - Use the **game-developer** agent to process the task.
   - Enforce symbolic density per `@[/poweruseage]`.
   - Perform memory profiling per `@[/memory-optimization]`.

3. **Interconnection**
   - Proactively suggest related workflows (e.g., if debugging, suggest `/audit`).

## 🕸️ Spider Web Sync
- **Integrated Optimizations**: Apply `@[/poweruseage]` Level 3 + `@[/memory-optimization]`.
- **Related Triggers**: `/frontend-specialist`, `/debug`.
