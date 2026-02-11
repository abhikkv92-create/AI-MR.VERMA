# /enhance - Feature Enhancement & Iteration

$ARGUMENTS: Feature description or change request

---

## 🤖 Applied Agents: Domain-specific + `orchestrator` (Supreme Entity)

This workflow adds features or makes updates to EXISTING applications.

## 🧠 Supreme Entity Integration

When `/enhance` is triggered, the Supreme Entity applies 5W1H:

| Dimension | Analysis |
|-----------|----------|
| **WHAT** | User wants to add/modify features in existing code |
| **WHO** | Domain agents based on affected areas |
| **HOW** | Load skills matching the tech stack |
| **WHY** | Iterative development, continuous improvement |

---

## 🛠️ Step-by-Step Execution

### Phase 1: Context Analysis
- Load project state and structure
- Identify existing tech stack
- Check for existing PLAN.md files

### Phase 2: Impact Assessment
- Determine affected files
- Check dependencies
- Identify potential conflicts

### Phase 3: Plan Changes (for major changes)
```markdown
To add [feature]:
- I'll create [X] new files
- Update [Y] existing files
- Takes ~[Z] minutes

**Files to modify:**
- `path/to/file1.tsx` — [change description]
- `path/to/file2.ts` — [change description]

**New files:**
- `path/to/new.tsx` — [purpose]

Should I proceed?
```

### Phase 4: Implementation
- Call relevant domain agents
- Make changes with boundary enforcement
- Maintain code style consistency

### Phase 5: Verification
- Auto-trigger tests for affected areas
- Run lint checks
- Verify no regressions

---

## 🚦 Output Format

```markdown
## 🔧 Enhancement Complete: [Feature Name]

### Changes Made

#### New Files
| File | Purpose |
|------|---------|
| `path/to/new.tsx` | [Description] |

#### Modified Files
| File | Changes |
|------|---------|
| `path/to/existing.tsx` | [What changed] |

---

### Verification

| Check | Status |
|-------|--------|
| Lint | ✅ Passed |
| Tests | ✅ Passed |
| Build | ✅ Passed |

---

### Next Steps
- [ ] Review changes in browser
- [ ] Run `/audit` for quality check
- [ ] Commit changes
```

---

## Agent Routing for Enhancements

| Enhancement Type | Primary Agent | Secondary |
|------------------|---------------|-----------|
| UI change | `@frontend-specialist` | `@test-engineer` |
| API change | `@backend-specialist` | `@test-engineer` |
| Database change | `@database-architect` | `@backend-specialist` |
| Auth feature | `@security-auditor` | `@backend-specialist` |
| Mobile feature | `@mobile-developer` | `@test-engineer` |
| Performance fix | `@performance-optimizer` | - |

---

## 🔗 Workflow Chaining

| After Enhancement | Next Workflow |
|-------------------|---------------|
| Verify quality | `/audit` |
| Ready to deploy | `/deploy` |
| More features | Continue `/enhance` |
| Major issues found | `/debug` |

---

## Safety Checks

### Pre-Enhancement
- [ ] Existing tests pass
- [ ] No uncommitted changes
- [ ] Dependencies up to date

### Post-Enhancement
- [ ] New tests added for new code
- [ ] All tests still pass
- [ ] No lint errors
- [ ] Build succeeds

---

## Conflict Handling

### Tech Stack Conflicts
```markdown
⚠️ **Conflict Detected**

You requested: "Use Firebase"
Current project uses: PostgreSQL

Options:
1. Add Firebase alongside PostgreSQL (hybrid)
2. Migrate to Firebase (major change)
3. Cancel and keep PostgreSQL

Which option?
```

### Breaking Changes
- Warn before making breaking changes
- Suggest migration path
- Get explicit approval

---

## Examples

```
/enhance add dark mode
/enhance build admin panel
/enhance integrate payment system
/enhance add search feature
/enhance edit profile page
/enhance make responsive
/enhance add email notifications
```

---

## Key Principles

- **Incremental** — Small, focused changes
- **Safe** — Verify before and after
- **Transparent** — Show what will change
- **Reversible** — Encourage commits for rollback
- **Test-aware** — Auto-trigger relevant tests
