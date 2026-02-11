---
name: supreme-entity-routing
description: Meta-intelligence skill for the Supreme Orchestrator. Provides 5W1H decision framework, global asset registry, and auto-initiation rules for agents, skills, and workflows.
version: 1.0.0
---

# Supreme Entity Routing

> **The Orchestrator's Brain** — Automatically determines WHEN, WHERE, WHAT, HOW, WHY, and WHO for every request.

## Core Philosophy

The Supreme Entity operates on two principles:
1.  **Zero-Friction Initiation**: The right asset (agent/skill/workflow) is selected without user intervention.
2.  **Transparent Reasoning**: Every decision is explainable via the 5W1H framework.

---

## 5W1H Decision Framework

Before responding to ANY complex request, apply this framework:

| Dimension | Question | Determines |
|-----------|----------|------------|
| **WHEN** | Is this urgent? Is it a new request or continuation? | **Priority** & **Context** |
| **WHERE** | What part of the codebase/system is affected? | **Scope** & **Agent Boundaries** |
| **WHAT** | What is the user trying to achieve? | **Goal** & **Workflow Selection** |
| **HOW** | What tools, scripts, or patterns are needed? | **Skill Selection** |
| **WHY** | What is the underlying motivation/business goal? | **Strategy** & **Trade-offs** |
| **WHO** | Which agent(s) have the expertise for this? | **Agent Selection** |

### Decision Tree

```mermaid
graph TD
    A[User Request] --> B{WHAT: Analyze Intent}
    B -->|Build/Create| C[/plan → /create]
    B -->|Improve/Add| D[/enhance]
    B -->|Review/Audit| E[/audit or /secure-audit]
    B -->|Explore Options| F[/brainstorm]
    B -->|Design System| G[/blueprint]
    B -->|Debug/Fix| H[@debugger]
    B -->|Deploy| I[/deploy]
    B -->|Complex/Multi| J[@orchestrator → Multi-Agent]
    
    C --> K{WHO: Agent Assignment}
    D --> K
    E --> K
    F --> K
    G --> K
    H --> K
    I --> K
    J --> K
    
    K --> L[HOW: Load Skills]
    L --> M[Execute with Context]
```

---

## Global Asset Registry

### Agents (27 Total)

| Agent | Domain | Trigger Keywords |
|-------|--------|------------------|
| `orchestrator` | Coordination | "comprehensive", "multi-perspective", "complex" |
| `project-planner` | Planning | "plan", "roadmap", "milestones", "breakdown" |
| `frontend-specialist` | UI/UX | "react", "vue", "component", "css", "tailwind" |
| `backend-specialist` | API/Server | "api", "node", "express", "fastapi", "server" |
| `mobile-developer` | Mobile | "flutter", "react native", "ios", "android" |
| `database-architect` | Database | "schema", "prisma", "sql", "migration" |
| `security-auditor` | Security | "auth", "security", "owasp", "vulnerability" |
| `penetration-tester` | Red Team | "pentest", "exploit", "red team" |
| `test-engineer` | Testing | "test", "jest", "playwright", "coverage" |
| `devops-engineer` | DevOps | "deploy", "docker", "ci/cd", "pm2" |
| `debugger` | Debugging | "bug", "error", "not working", "crash" |
| `performance-optimizer` | Performance | "slow", "optimize", "profiling", "cache" |
| `seo-specialist` | SEO | "seo", "meta", "analytics", "sitemap" |
| `ai-researcher` | AI/LLM | "prompt", "llm", "rag", "gemini", "ai" |
| `explorer-agent` | Discovery | "explore", "map", "structure", "find" |
| `product-manager` | Requirements | "user story", "requirements", "backlog" |
| `business-architect` | Strategy | "blueprint", "strategy", "feasibility" |
| `documentation-writer` | Docs | "readme", "docs", "documentation" |
| `game-developer` | Games | "unity", "godot", "game", "phaser" |
| `api-designer` | API Design | "openapi", "graphql", "rest" |
| `knowledge-expert` | Knowledge | "synthesis", "wiki", "research" |
| `agent-perfectionist` | Quality | "audit", "perfection", "ceo", "coo" |
| `antigravity-platform-expert` | Platform | "antigravity", "agent core", "rules" |
| `cloud-native-expert` | Cloud | "kubernetes", "aws", "terraform" |
| `data-science-agent` | Data | "pandas", "ml", "visualization" |
| `qa-automation-engineer` | QA | "automation", "regression", "e2e" |
| `tech-writer` | Writing | "technical writing", "api docs" |

### Workflows (19 Total)

| Workflow | Trigger Intent | Description |
|----------|----------------|-------------|
| `/brainstorm` | Explore ideas | Structured idea exploration |
| `/blueprint` | Design system | Business → Technical translation |
| `/plan` | Plan project | Task breakdown, no code |
| `/create` | Build new app | Full-stack app creation |
| `/enhance` | Add features | Iterative development |
| `/debug` | Fix bugs | Systematic debugging |
| `/deploy` | Release | Production deployment |
| `/orchestrate` | Coordinate | Multi-agent tasks |
| `/audit` | Quality check | Executive quality audit |
| `/test` | Generate tests | Test creation |
| `/preview` | Local server | Dev server management |
| `/status` | Check progress | Project status |
| `/ui-ux-pro-max` | Design UI | Premium UI design |
| `/launch-mobile` | Mobile app | Mobile accelerator |
| `/ai-feature` | AI integration | LLM feature pipeline |
| `/secure-audit` | Security sweep | Deep security review |
| `/optimize-stack` | Performance | Full-stack optimization |
| `/synthesize` | Knowledge | Document synthesis |
| `/platform` | Admin | Platform research |

### Skills (66+ Total)

Grouped by domain:

**Frontend**: `react-best-practices`, `nextjs-best-practices`, `tailwind-patterns`, `frontend-design`, `superdesign`, `remotion`, `agent-ui`, `angular-component`

**Backend**: `nodejs-best-practices`, `api-patterns`, `python-patterns`, `mcp-builder`

**Security**: `vulnerability-scanner`, `red-team-tactics`, `api-security-best-practices`, `better-auth-best-practices`

**Testing**: `testing-patterns`, `webapp-testing`, `tdd-workflow`

**Database**: `database-design`, `database-optimizer`

**DevOps**: `deployment-procedures`, `server-management`, `docker-expert`, `pnpm`

**AI/ML**: `ai-sdk`, `ai-rag-pipeline`, `langchain-architecture`, `gemini-token-optimization`

**Planning**: `plan-writing`, `brainstorming`, `c4-architecture`, `writing-plans`

**Core**: `clean-code`, `architecture`, `intelligent-routing`, `parallel-agents`, `behavioral-modes`

---

## Auto-Initiation Rules

### Rule 1: Workflow Selection by Intent

| User Intent Pattern | Auto-Initiate | Condition |
|---------------------|---------------|-----------|
| "I want to build..." | `/plan` → `/create` | New project |
| "Add feature X to..." | `/enhance` | Existing project |
| "Review/Check/Audit..." | `/audit` | Quality focus |
| "Explore options for..." | `/brainstorm` | Decision needed |
| "Design the architecture..." | `/blueprint` | System design |
| "Debug/Fix/Error..." | `/debug` | Bug investigation |
| "Deploy/Release..." | `/deploy` | Production push |

### Rule 2: Agent Selection by Domain

```
IF request.domains.length === 1:
    → Auto-select single domain agent
ELSE IF request.domains.length === 2:
    → Chain agents sequentially
ELSE:
    → Invoke orchestrator for coordination
```

### Rule 3: Skill Loading

```
WHEN agent is selected:
    → Read agent's frontmatter `skills:` field
    → Load SKILL.md for each skill
    → Apply skill principles to response
```

### Rule 4: Adaptive Routing (Agent Lightning)

**Query history to optimize selection:**

```python
from agentlightning.store import LightningStore

store = LightningStore()

# 1. Fetch performance stats for potential agents
stats = store.get_agent_performance(
    agents=["frontend-specialist", "backend-specialist"],
    task_type="api_implementation"
)

# 2. Re-weight selection based on success rate
# Example: If 'backend-specialist' has 98% success vs 85% for others
selected_agent = max(stats, key=lambda x: x.success_rate)
```

**Feedback Loop:**
- AFTER task completion:
- `emit_reward(1.0)` → reinforces this routing decision
- `emit_reward(0.0)` → penalizes this choice


---

## Response Protocol

When the Supreme Entity makes a decision, it announces:

```markdown
🧠 **Supreme Entity Routing**

| Dimension | Decision |
|-----------|----------|
| **WHAT** | [User's goal] |
| **WHO** | `@[agent-name]` |
| **HOW** | [Skills being applied] |
| **WHY** | [Reasoning] |

---

🤖 **Applying knowledge of `@[agent-name]`...**

[Specialized response]
```

---

## Integration Points

### With `intelligent-routing` Skill
- Supreme Entity uses intelligent-routing as a sub-module for agent selection.

### With `parallel-agents` Skill
- For multi-agent tasks, Supreme Entity leverages parallel-agents patterns.

### With MS Light (Agent Lightning)
- All decisions are logged as spans.
- Rewards are emitted post-completion.

---

## Edge Cases

### Case 1: User Explicitly Mentions Agent
```
User: "@security-auditor review this"
→ Override auto-selection
→ Use explicitly mentioned agent
```

### Case 2: Ambiguous Request
```
User: "Make it better"
→ Ask 1-2 clarifying questions via Socratic Gate
→ Then apply 5W1H
```

### Case 3: Conflicting Domains
```
User: "Add mobile support to the web app"
→ Ask: "Do you want responsive web or native mobile?"
→ Route based on answer
```

---

## Summary

The `supreme-entity-routing` skill transforms the orchestrator from a passive coordinator into an **intelligent meta-controller** that:

✅ Automatically detects user intent  
✅ Selects optimal agents, skills, and workflows  
✅ Applies 5W1H reasoning to every decision  
✅ Learns from user feedback via MS Light  
✅ Maintains transparency through structured announcements
