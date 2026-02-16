---
description: Activate the Data Science Agent specialist agent
---
# Trigger: /data-science-agent

Use this command to specifically engage the **data-science-agent** for tasks within their domain.

1. **Context Analysis**
   - Identify the specific data-science-agent requirements in the user request.
   - Cross-reference with `@[agent-skills/data-science-agent]` if applicable.

2. **Engage Agent**
   - Use the **data-science-agent** agent to process the task.
   - Enforce symbolic density per `@[/poweruseage]`.
   - Perform memory profiling per `@[/memory-optimization]`.

3. **Interconnection**
   - Proactively suggest related workflows (e.g., if debugging, suggest `/audit`).

## 🕸️ Spider Web Sync
- **Integrated Optimizations**: Apply `@[/poweruseage]` Level 3 + `@[/memory-optimization]`.
- **Related Triggers**: `/frontend-specialist`, `/debug`.
