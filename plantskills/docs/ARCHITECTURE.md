# Antigravity Kit - System Architecture

> **Version**: 2.0.0 (Project Symbiote)  
> **Last Updated**: 2026-02-06

---

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    USER REQUEST                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              SUPREME ENTITY ORCHESTRATOR                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │  5W1H       │  │  Workflow   │  │  Agent      │          │
│  │  Analysis   │  │  Detection  │  │  Selection  │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│    AGENTS       │  │    SKILLS       │  │   WORKFLOWS     │
│    (27)         │  │    (123)        │  │    (19)         │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

---

## Component Registry

### Agents (27)

| Category | Count | Agents |
|----------|-------|--------|
| Core | 3 | orchestrator, project-planner, explorer-agent |
| Frontend | 2 | frontend-specialist, mobile-developer |
| Backend | 2 | backend-specialist, database-architect |
| Security | 2 | security-auditor, penetration-tester |
| Quality | 4 | test-engineer, qa-automation-engineer, debugger, agent-perfectionist |
| DevOps | 2 | devops-engineer, cloud-native-expert |
| Performance | 1 | performance-optimizer |
| Content | 3 | documentation-writer, seo-specialist, knowledge-expert |
| Specialized | 4 | game-developer, ai-researcher, data-science-agent, code-archaeologist |
| Strategy | 4 | product-manager, product-owner, business-architect, antigravity-platform-expert |

### Skills (123)

| Category | Count |
|----------|-------|
| Core | 5 |
| Frontend | 15 |
| Backend | 12 |
| Mobile | 8 |
| Security | 8 |
| Testing | 10 |
| AI & Data | 8 |
| DevOps | 6 |
| Documentation | 6 |
| Memory | 8 |
| Platform | 4 |
| Other | 33 |

### Workflows (19)

| Category | Workflows |
|----------|-----------|
| Planning | /brainstorm, /blueprint, /plan |
| Building | /create, /enhance |
| Quality | /audit, /test, /debug |
| Deployment | /deploy, /preview, /status |
| Premium | /launch-mobile, /ai-feature, /secure-audit, /optimize-stack |
| Utility | /orchestrate, /synthesize, /platform, /ui-ux-pro-max |

---

## Directory Structure

```
.agent/
├── agents/                  # 27 agent definitions
│   ├── orchestrator.md      # Supreme Entity
│   ├── frontend-specialist.md
│   ├── backend-specialist.md
│   └── ...
├── skills/                  # 123 skills
│   ├── supreme-entity-routing/
│   ├── intelligent-routing/
│   ├── frontend-design/
│   └── ...
├── workflows/               # 19 workflows
│   ├── brainstorm.md
│   ├── plan.md
│   ├── orchestrate.md
│   └── ...
├── docs/                    # Documentation
│   ├── USER_GUIDE.md
│   ├── WORKFLOW_REFERENCE.md
│   ├── SKILL_REFERENCE.md
│   └── ARCHITECTURE.md
├── scripts/                 # Utility scripts
│   ├── checklist.py
│   └── verify_all.py
└── GEMINI.md                # Platform rules
```

---

## Decision Flow

### 5W1H Framework

```
User Request
    │
    ▼
┌─── WHEN ───┐
│ Urgent?    │ → Priority
└────────────┘
    │
    ▼
┌─── WHERE ──┐
│ Scope?     │ → Boundaries
└────────────┘
    │
    ▼
┌─── WHAT ───┐
│ Goal?      │ → Workflow
└────────────┘
    │
    ▼
┌─── HOW ────┐
│ Tools?     │ → Skills
└────────────┘
    │
    ▼
┌─── WHY ────┐
│ Business?  │ → Strategy
└────────────┘
    │
    ▼
┌─── WHO ────┐
│ Expertise? │ → Agent
└────────────┘
```

---

## Integration Points

### MS Light (Agent Lightning)

```python
# Reward emission for learning
emit_reward(1.0)  # User approved
emit_reward(0.0)  # User corrected

# Span logging
emit_annotation({"agent": "frontend-specialist"})
emit_message("Routing decision made")
```

### Scripts

| Script | Skill | Trigger |
|--------|-------|---------|
| security_scan.py | vulnerability-scanner | /audit, /deploy |
| checklist.py | scripts | /audit full_system |
| lint_runner.py | lint-and-validate | /test |
| playwright_runner.py | webapp-testing | /test e2e |

---

## Security Model

- **Agent Boundaries**: Agents can only modify files in their domain
- **Pre-flight Checks**: Security scan before deployment
- **Verification Scripts**: Automated quality gates

---

## Performance Considerations

- **Skill Loading**: On-demand based on task
- **Agent Invocation**: Sequential or parallel based on workflow
- **Caching**: Conversation context retained
