---
description: Activate the Code Archaeologist specialist agent
---
# Trigger: /code-archaeologist

Use this command to specifically engage the **code-archaeologist** for tasks within their domain.

1. **Context Analysis**
   - Identify the specific code-archaeologist requirements in the user request.
   - Cross-reference with `@[agent-skills/code-archaeologist]` if applicable.

2. **Engage Agent**
   - Use the **code-archaeologist** agent to process the task.
   - Enforce symbolic density per `@[/poweruseage]`.
   - Perform memory profiling per `@[/memory-optimization]`.

3. **Interconnection**
   - Proactively suggest related workflows (e.g., if debugging, suggest `/audit`).

## 🕸️ Spider Web Sync
- **Integrated Optimizations**: Apply `@[/poweruseage]` Level 3 + `@[/memory-optimization]`.
- **Related Triggers**: `/frontend-specialist`, `/debug`.
