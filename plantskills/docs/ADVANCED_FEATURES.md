# Advanced Features Guide

> Phase 5 features for power users.

---

## 1. MS Light Training (Agent Lightning)

### Reward Emission

Train the system to learn your preferences:

```python
# When user approves a decision
emit_reward(1.0)  # Positive reinforcement

# When user corrects a decision
emit_reward(0.0)  # Learning signal
update_memory({"correction": "Use Vue instead of React"})
```

### Span Logging

Track agent decisions for analysis:

```python
emit_annotation({
    "agent": "frontend-specialist",
    "skill": "react-best-practices",
    "decision": "Client-side rendering"
})
```

### Dashboard

Access the training dashboard:
- URL: `http://localhost:3000` (MS Light dashboard)
- View rollouts, spans, and rewards
- Analyze routing accuracy over time

---

## 2. Custom Skill Creation

### Using `/synthesize`

```
/synthesize create skill for Supabase integration
```

### Manual Creation

1. Create directory: `.agent/skills/my-custom-skill/`
2. Add `SKILL.md`:

```markdown
---
name: my-custom-skill
description: Description of what this skill does
---

# My Custom Skill

## Capabilities
- Capability 1
- Capability 2

## Patterns
[Document patterns here]

## Examples
[Provide code examples]
```

3. Register in agent frontmatter:

```yaml
skills: clean-code, my-custom-skill
```

---

## 3. CI/CD Integration

### GitHub Actions Workflow

```yaml
name: Antigravity Checks

on: [push, pull_request]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Security Scan
        run: python .agent/skills/vulnerability-scanner/scripts/security_scan.py .
      
      - name: Lint Check
        run: python .agent/skills/lint-and-validate/scripts/lint_runner.py .
      
      - name: Full Checklist
        run: python .agent/scripts/checklist.py .
```

---

## 4. Knowledge Item (KI) Generation

### Capturing Project Learnings

```
/synthesize KI from this authentication implementation
```

Output: Knowledge Item saved to `knowledge/` directory.

### KI Structure

```
knowledge/
├── auth-patterns/
│   ├── metadata.json
│   └── artifacts/
│       ├── best-practices.md
│       └── common-pitfalls.md
```

---

## 5. Custom Workflow Creation

### Creating a New Workflow

1. Create `.agent/workflows/my-workflow.md`:

```markdown
# /my-workflow - Custom Workflow

$ARGUMENTS

---

## Purpose
[Describe what this workflow does]

## Steps
1. Step 1
2. Step 2
3. Step 3

## Output
[Describe expected output]
```

2. The workflow is immediately available via `/my-workflow`.

---

## 6. Agent Customization

### Adding Skills to an Agent

Edit agent file frontmatter:

```yaml
---
name: frontend-specialist
skills: clean-code, react-best-practices, my-new-skill
---
```

### Creating a New Agent

1. Create `.agent/agents/my-agent.md`
2. Follow agent template structure
3. Register skills in frontmatter
