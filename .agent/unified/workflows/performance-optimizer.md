---
description: Activate the Performance Optimizer specialist agent
---
# Trigger: /performance-optimizer

Use this command to specifically engage the **performance-optimizer** for tasks within their domain.

1. **Context Analysis**
   - Identify the specific performance-optimizer requirements in the user request.
   - Cross-reference with `@[agent-skills/performance-optimizer]` if applicable.

2. **Engage Agent**
   - Use the **performance-optimizer** agent to process the task.
   - Enforce symbolic density per `@[/poweruseage]`.
   - Perform memory profiling per `@[/memory-optimization]`.

3. **Interconnection**
   - Proactively suggest related workflows (e.g., if debugging, suggest `/audit`).

## 🕸️ Spider Web Sync
- **Integrated Optimizations**: Apply `@[/poweruseage]` Level 3 + `@[/memory-optimization]`.
- **Related Triggers**: `/frontend-specialist`, `/performance-optimizer`, `/debug`.
