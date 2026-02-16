---
description: Activate the Product Owner specialist agent
---
# Trigger: /product-owner

Use this command to specifically engage the **product-owner** for tasks within their domain.

1. **Context Analysis**
   - Identify the specific product-owner requirements in the user request.
   - Cross-reference with `@[agent-skills/product-owner]` if applicable.

2. **Engage Agent**
   - Use the **product-owner** agent to process the task.
   - Enforce symbolic density per `@[/poweruseage]`.
   - Perform memory profiling per `@[/memory-optimization]`.

3. **Interconnection**
   - Proactively suggest related workflows (e.g., if debugging, suggest `/audit`).

## 🕸️ Spider Web Sync
- **Integrated Optimizations**: Apply `@[/poweruseage]` Level 3 + `@[/memory-optimization]`.
- **Related Triggers**: `/frontend-specialist`, `/debug`.
