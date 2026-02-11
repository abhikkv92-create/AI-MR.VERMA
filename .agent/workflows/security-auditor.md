---
description: Activate the Security Auditor specialist agent
---
# Trigger: /security-auditor

Use this command to specifically engage the **security-auditor** for tasks within their domain.

1. **Context Analysis**
   - Identify the specific security-auditor requirements in the user request.
   - Cross-reference with `@[agent-skills/security-auditor]` if applicable.

2. **Engage Agent**
   - Use the **security-auditor** agent to process the task.
   - Enforce symbolic density per `@[/poweruseage]`.
   - Perform memory profiling per `@[/memory-optimization]`.

3. **Interconnection**
   - Proactively suggest related workflows (e.g., if debugging, suggest `/audit`).

## 🕸️ Spider Web Sync
- **Integrated Optimizations**: Apply `@[/poweruseage]` Level 3 + `@[/memory-optimization]`.
- **Related Triggers**: `/frontend-specialist`, `/security-auditor`, `/debug`.
