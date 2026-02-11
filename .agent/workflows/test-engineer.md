---
description: Activate the Test Engineer specialist agent
---
# Trigger: /test-engineer

Use this command to specifically engage the **test-engineer** for tasks within their domain.

1. **Context Analysis**
   - Identify the specific test-engineer requirements in the user request.
   - Cross-reference with `@[agent-skills/test-engineer]` if applicable.

2. **Engage Agent**
   - Use the **test-engineer** agent to process the task.
   - Enforce symbolic density per `@[/poweruseage]`.
   - Perform memory profiling per `@[/memory-optimization]`.

3. **Interconnection**
   - Proactively suggest related workflows (e.g., if debugging, suggest `/audit`).

## 🕸️ Spider Web Sync
- **Integrated Optimizations**: Apply `@[/poweruseage]` Level 3 + `@[/memory-optimization]`.
- **Related Triggers**: `/frontend-specialist`, `/test-engineer`, `/debug`.
