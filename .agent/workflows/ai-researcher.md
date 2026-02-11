---
description: Activate the Ai Researcher specialist agent
---
# Trigger: /ai-researcher

Use this command to specifically engage the **ai-researcher** for tasks within their domain.

1. **Context Analysis**
   - Identify the specific ai-researcher requirements in the user request.
   - Cross-reference with `@[agent-skills/ai-researcher]` if applicable.

2. **Engage Agent**
   - Use the **ai-researcher** agent to process the task.
   - Enforce symbolic density per `@[/poweruseage]`.
   - Perform memory profiling per `@[/memory-optimization]`.

3. **Interconnection**
   - Proactively suggest related workflows (e.g., if debugging, suggest `/audit`).

## 🕸️ Spider Web Sync
- **Integrated Optimizations**: Apply `@[/poweruseage]` Level 3 + `@[/memory-optimization]`.
- **Related Triggers**: `/frontend-specialist`, `/debug`.
