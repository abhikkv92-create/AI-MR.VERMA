---
description: Activate the Documentation Writer specialist agent
---
# Trigger: /documentation-writer

Use this command to specifically engage the **documentation-writer** for tasks within their domain.

1. **Context Analysis**
   - Identify the specific documentation-writer requirements in the user request.
   - Cross-reference with `@[agent-skills/documentation-writer]` if applicable.

2. **Engage Agent**
   - Use the **documentation-writer** agent to process the task.
   - Enforce symbolic density per `@[/poweruseage]`.
   - Perform memory profiling per `@[/memory-optimization]`.

3. **Interconnection**
   - Proactively suggest related workflows (e.g., if debugging, suggest `/audit`).

## 🕸️ Spider Web Sync
- **Integrated Optimizations**: Apply `@[/poweruseage]` Level 3 + `@[/memory-optimization]`.
- **Related Triggers**: `/frontend-specialist`, `/debug`.
