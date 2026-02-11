# Workflow Reference Guide

> Complete documentation for all 19 Antigravity workflows with examples.

---

## Planning Workflows

### `/brainstorm`
**Purpose**: Explore multiple options before committing to implementation.

**Usage**:
```
/brainstorm authentication system
/brainstorm state management for complex form
/brainstorm database schema for social app
```

**Output Format**: 3+ options with pros/cons, effort estimate, and recommendation.

---

### `/blueprint`
**Purpose**: Architecture and system design for complex features.

**Usage**:
```
/blueprint e-commerce checkout system
/blueprint real-time notification service
/blueprint multi-tenant SaaS architecture
```

**Output**: C4 diagrams, stack recommendation, data flow, risk analysis.

---

### `/plan`
**Purpose**: Create structured task breakdown without writing code.

**Usage**:
```
/plan mobile fitness app
/plan add dark mode feature
/plan refactor authentication module
```

**Output**: `docs/PLAN-{slug}.md` with tasks, agent assignments, estimates.

---

## Building Workflows

### `/create`
**Purpose**: Build new applications from scratch.

**Usage**:
```
/create e-commerce site with cart
/create mobile app for fitness tracking
/create SaaS dashboard with analytics
```

**Agents**: project-planner → frontend/backend-specialist → test-engineer

---

### `/enhance`
**Purpose**: Add features or modify existing applications.

**Usage**:
```
/enhance add dark mode
/enhance build admin panel
/enhance integrate payment system
```

**Safety**: Warns before breaking changes, suggests migration path.

---

## Quality Workflows

### `/audit`
**Purpose**: Comprehensive quality assurance check.

**Arguments**: `backend | frontend | accessibility | security | full_system`

**Usage**:
```
/audit full_system
/audit frontend
/audit security
```

**Output**: GO/NO-GO deployment decision with severity-ranked findings.

---

### `/test`
**Purpose**: Generate and run test suites.

**Usage**:
```
/test unit tests for auth module
/test e2e for checkout flow
/test integration for API endpoints
```

**Scripts**: Uses `test_runner.py`, `playwright_runner.py`

---

### `/debug`
**Purpose**: Systematic problem investigation.

**Usage**:
```
/debug login not working
/debug memory leak in dashboard
/debug API returning 500
```

**Method**: Gather → Hypothesize → Test → Fix → Verify

---

## Deployment Workflows

### `/deploy`
**Purpose**: Production release with pre-flight checks.

**Usage**:
```
/deploy to production
/deploy to staging
```

**Pre-flight**: Security scan, lint check, test run, build verification.

---

### `/preview`
**Purpose**: Start/stop local development server.

**Usage**:
```
/preview start
/preview stop
/preview status
```

---

### `/status`
**Purpose**: Check overall project status.

**Usage**:
```
/status
```

**Output**: Build status, test coverage, last deploy, open issues.

---

## Premium Workflows

### `/launch-mobile`
**Purpose**: Mobile app accelerator for iOS/Android.

**Triggers**: ios, android, flutter, react native

**Agents**: mobile-developer + security-auditor + frontend-specialist

---

### `/ai-feature`
**Purpose**: AI/LLM feature integration.

**Triggers**: rag, llm, vector db, chatbot

**Agents**: ai-researcher + backend-specialist + frontend-specialist

---

### `/secure-audit`
**Purpose**: Deep security review with red team tactics.

**Triggers**: pentest, vulnerability, security audit

**Agents**: security-auditor + penetration-tester + devops-engineer

---

### `/optimize-stack`
**Purpose**: Full-stack performance optimization.

**Triggers**: slow, performance, scaling

**Agents**: database-architect + backend-specialist + frontend-specialist

---

## Utility Workflows

### `/orchestrate`
**Purpose**: Coordinate 3+ agents for complex multi-domain tasks.

**Usage**:
```
/orchestrate build complete e-commerce platform
/orchestrate security review and performance audit
```

**Requirement**: Minimum 3 agents must be invoked.

---

### `/synthesize`
**Purpose**: Knowledge distillation and documentation.

**Usage**:
```
/synthesize learnings from this project
/synthesize best practices for auth
```

---

### `/platform`
**Purpose**: System administration and platform updates.

**Usage**:
```
/platform update rules
/platform add new agent
```

---

### `/ui-ux-pro-max`
**Purpose**: Premium UI design with 50+ style options.

**Usage**:
```
/ui-ux-pro-max design landing page
/ui-ux-pro-max design dashboard
```

**Features**: Glassmorphism, gradients, animations, dark mode.
