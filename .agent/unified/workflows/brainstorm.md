---
description: Structured brainstorming for projects and features. Explores multiple options before implementation.
---

# /brainstorm - Structured Idea Exploration

$ARGUMENTS: Topic or problem to explore

---

## 🤖 Applied Agent: `orchestrator` (Supreme Entity)

This workflow activates BRAINSTORM mode for structured idea exploration before committing to implementation.

## 🧠 Supreme Entity Integration

When `/brainstorm` is triggered, the Supreme Entity applies 5W1H:

| Dimension | Analysis |
|-----------|----------|
| **WHAT** | User wants to explore options before deciding |
| **WHO** | Orchestrator as facilitator, domain experts for validation |
| **HOW** | `brainstorming` skill, `architecture` skill |
| **WHY** | Reduce risk by evaluating alternatives |

---

## 🛠️ Step-by-Step Execution

### 1. Pre-Check
- Does a PLAN.md already exist for this topic?
- If yes, reference it for context.
- If no, proceed fresh.

### 2. Understand the Goal
- What problem are we solving?
- Who is the user/stakeholder?
- What constraints exist?

### 3. Generate Options
- Provide **at least 3** different approaches
- Each with **pros** and **cons**
- Consider unconventional solutions
- Include effort estimates

### 4. Compare and Recommend
- Summarize trade-offs
- Give a recommendation with reasoning
- Optionally, suggest next workflow (`/plan` or `/blueprint`)

---

## 🚦 Output Format

```markdown
## 🧠 Brainstorm: [Topic]

### Context
[Brief problem statement]

---

### Option A: [Name]
[Description]

✅ **Pros:**
- [benefit 1]
- [benefit 2]

❌ **Cons:**
- [drawback 1]

📊 **Effort:** Low | Medium | High
🎯 **Best For:** [Use case]

---

### Option B: [Name]
[Description]

✅ **Pros:**
- [benefit 1]

❌ **Cons:**
- [drawback 1]
- [drawback 2]

📊 **Effort:** Low | Medium | High
🎯 **Best For:** [Use case]

---

### Option C: [Name]
[Description]

✅ **Pros:**
- [benefit 1]

❌ **Cons:**
- [drawback 1]

📊 **Effort:** Low | Medium | High
🎯 **Best For:** [Use case]

---

## 💡 Recommendation

**Option [X]** because [reasoning].

### Suggested Next Steps
- [ ] `/plan` to create detailed task breakdown
- [ ] `/blueprint` for architecture design
- [ ] Proceed directly with implementation

What direction would you like to explore?
```

---

## 🔗 Workflow Chaining

After brainstorming, Supreme Entity may recommend:

| Decision | Next Workflow |
|----------|---------------|
| Architecture needed | `/blueprint` |
| Ready to build | `/plan` → `/create` |
| More research needed | Continue brainstorm |
| Security concerns | `/secure-audit` first |

---

## Examples

```
/brainstorm authentication system
/brainstorm state management for complex form
/brainstorm database schema for social app
/brainstorm caching strategy
/brainstorm mobile vs web approach
```

---

## Key Principles

- **No code** — this is about ideas, not implementation
- **Visual when helpful** — use diagrams for architecture
- **Honest trade-offs** — don't hide complexity
- **Defer to user** — present options, let them decide
- **Chain-ready** — prepare for next workflow in chain

## 🕸️ Spider Web Sync
- **Integrated Optimizations**: Apply `@[/poweruseage]` Level 3 + `@[/memory-optimization]`.
- **Related Triggers**: `/frontend-specialist`, `/database-architect`, `/security-auditor`, `/mobile-developer`, `/plan`.
