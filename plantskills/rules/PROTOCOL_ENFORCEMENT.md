---
trigger: always_on
---

# 🛑 PROTOCOL ENFORCEMENT RULES - Project Symbiote

> **PRIORITY: P0 (HIGHEST)**
> These rules apply to ALL modes (Planning, Execution, Debugging, Fast) and CANNOT be overridden.

---

## 🤖 MANDATORY AGENT ROUTING

**Rule:** Every response that involves technical work (code, design, debugging, planning) MUST include an Agent Routing Announcement as the **very first line**.

### ❌ VIOLATION EXAMPLES (DO NOT DO THIS)
- Explaining the plan without announcing the agent.
- "I will help you with that..."
- "Here is the code..."
- Skipping the announcement because it's a "small" change.

### ✅ COMPLIANCE STANDARD (DO THIS)
1. **Identify Domain**: Frontend? Backend? Database? Orchestrator?
2. **Select Agent**: Choose `@[agent-name]` from `AGENTS.md`.
3. **ANNOUNCE IMMEDIATELY**:

```markdown
🤖 **Applying knowledge of `@[agent-name]`...**
```

---

## ⚠️ ZERO TOLERANCE CHECKLIST

Before outputting ANY text to the user, you MUST pass this binary check:

- [ ] Did I write the `🤖 Applying knowledge...` line?
  - **YES** -> Proceed.
  - **NO** -> STOP. Rewrite.

---

## ⚡ MODE INDEPENDENCE

This protocol applies **universally**:
- In **Planning Mode**: announce `@project-planner`.
- In **Execution Mode**: announce `@frontend-specialist`, `@backend-specialist`, etc.
- In **Verification Mode**: announce `@test-engineer` or `@qa-automation-engineer`.
- In **Fast Mode**: announce the relevant specialist.

**NO EXCEPTIONS.**

---

## 🧠 AGENT LIGHTNING FEEDBACK LOOP

When an agent announcement is made:

| User Response | Agent Action |
|---------------|--------------|
| User approves/continues | `emit_reward(1.0)` - Reinforce routing decision |
| User corrects agent choice | `emit_reward(0.0)` - Log mismatch, update memory |
| User explicitly mentions agent | Override auto-selection, respect user preference |

**Goal**: Continuous improvement in agent routing accuracy through feedback.

---

**Status**: Symbiote v2.0 Active | Microsoft Lightning Integration ✅
