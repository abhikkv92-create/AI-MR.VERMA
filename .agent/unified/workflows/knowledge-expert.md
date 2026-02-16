---
description: Activate the Knowledge Expert specialist agent
---
# Trigger: /knowledge-expert

Use this command to specifically engage the **knowledge-expert** for tasks within their domain.

1. **Context Analysis**
   - Identify the specific knowledge-expert requirements in the user request.
   - Cross-reference with `@[agent-skills/knowledge-expert]` if applicable.

2. **Engage Agent**
   - Use the **knowledge-expert** agent to process the task.
   - Enforce symbolic density per `@[/poweruseage]`.
   - Perform memory profiling per `@[/memory-optimization]`.

3. **Interconnection**
   - Proactively suggest related workflows (e.g., if debugging, suggest `/audit`).

## 🕸️ Spider Web Sync
- **Integrated Optimizations**: Apply `@[/poweruseage]` Level 3 + `@[/memory-optimization]`.
- **Related Triggers**: `/frontend-specialist`, `/debug`.
