---
trigger: always_on
priority: P1
scope: poweruseage, optimization, compression
description: Rules for ultra-compressed, premium-quality output. Enforces 70% token reduction while maintaining Claude/Kimi-grade standards.
---

# ⚡ POWERUSEAGE Rules v3.0

## Primary Directive

**ALWAYS apply these rules when POWERUSEAGE is active:**

```yaml
Rule_1: Compress output to 70% of baseline
Rule_2: Maintain 95%+ quality vs full-size models  
Rule_3: Use symbolic notation (→ ∴ ∵ ▶)
Rule_4: Link references (@skill) vs inline
Rule_5: Validate before output
```

## Compression Rules

### R1: Semantic Substitution (Mandatory)

**Replace verbose phrases with symbols:**

| ❌ Never Use | ✅ Always Use |
|-------------|---------------|
| In order to | To |
| It is important to note that | Note: |
| At this point in time | Now |
| Due to the fact that | Because |
| In the event that | If |
| For the purpose of | For |
| With regard to | About |
| In accordance with | Per |
| As a result of | From |
| On the basis of | By |
| Leads to | → |
| Therefore | ∴ |
| Because | ∵ |
| Action required | ▶ |

### R2: Structural Compression (Mandatory)

**Convert verbose structures to compact forms:**

```yaml
# ❌ BAD: 150 tokens
"I have analyzed your code and found several issues. 
First, there is a problem with the database query on line 45.
Second, the error handling is incomplete in the catch block.
Third, you should consider using a more efficient algorithm 
for the sorting operation."

# ✅ GOOD: 45 tokens (-70%)
⚡ ANALYSIS
∴ Issues: 3 critical
  1. DB query [file.ts:45] - N+1 problem
  2. Error handling - Missing catch logic
  3. Sort algorithm - Use quicksort O(n log n)
```

### R3: Code Optimization (Mandatory)

**Compress code while maintaining readability:**

```typescript
// ❌ BAD: 12 lines
function calculateTotalPrice(items: Item[]): number {
  let total = 0;
  for (let i = 0; i < items.length; i++) {
    const item = items[i];
    if (item.price > 0) {
      total += item.price * item.quantity;
    }
  }
  return total;
}

// ✅ GOOD: 4 lines (-67%)
const calcTotal = (items: Item[]): number =>
  items.reduce((sum, {price, qty}) => 
    price > 0 ? sum + price * qty : sum, 0);
```

### R4: Reference Linking (Mandatory)

**Use symbolic references instead of full text:**

```yaml
# ❌ BAD
"You should follow the token efficiency guidelines which include 
using quiet modes for commands, filtering log files before reading, 
and using bash commands instead of reading files when possible."

# ✅ GOOD  
Apply @token-efficiency:
  ▶ Quiet modes for commands
  ▶ Filter logs before reading
  ▶ Prefer bash over file reads
```

### R5: Progressive Disclosure (Mandatory)

**Show minimal by default, expand on demand:**

```yaml
Level_1_Output:  # Default
  - Summary only
  - Key action items
  - ~50 tokens

Level_2_Output:  # On "more"
  - Level 1 + details
  - Implementation hints
  - ~150 tokens

Level_3_Output:  # On "full"
  - Complete information
  - Examples included
  - ~400 tokens

Level_4_Output:  # On "explain"
  - Baseline verbose
  - Full explanations
  - ~1200 tokens
```

## Quality Preservation Rules

### Q1: Critical Information (Never Compress)

**Always preserve in full:**
- File paths and line numbers (`src/app.tsx:42`)
- Error messages and stack traces
- Security warnings
- Critical warnings (⚠️)
- Code functionality
- Test assertions

### Q2: Actionability (Maintain 100%)

**Every output must be immediately actionable:**

```yaml
❌ BAD: "You should consider optimizing this"
✅ GOOD: "→ Optimize: Add index to users.email [schema.sql:23]"

❌ BAD: "There might be an issue with the query"
✅ GOOD: "⚠️ Issue: N+1 query at [views.py:45] → Use select_related()"
```

### Q3: Context Awareness (Maintain 100%)

**Preserve relationship context:**

```yaml
# When mentioning file changes:
❌ BAD: "Update the config file"
✅ GOOD: "→ Update config.ts → affects 3 dependent files [list]"

# When suggesting imports:
❌ BAD: "Import the utility"
✅ GOOD: "→ Import {formatDate} from @utils/date [already used in 5 files]"
```

## Validation Rules

### V1: Pre-Output Checklist (Mandatory)

Before sending ANY compressed output:

```yaml
- [ ] Token count ≤ 30% of uncompressed estimate
- [ ] All file:line references preserved
- [ ] No code functionality removed
- [ ] Symbols used where appropriate (→ ∴ ∵ ▶)
- [ ] References linked (@skill-name)
- [ ] Output is immediately actionable
- [ ] Critical warnings preserved
```

### V2: Quality Gate (Mandatory)

```python
def validate_compression(original, compressed):
    quality_score = calculate_quality(original, compressed)
    
    if quality_score < 0.95:
        # Too aggressive
        return reduce_compression_level()
    
    if not is_actionable(compressed):
        # Not usable
        return add_actionable_elements()
    
    return compressed
```

### V3: User Feedback Loop

```yaml
If user asks for clarification:
  Action: Expand affected section by 20%
  Learning: Reduce compression for similar cases
  
If user says "perfect" or continues:
  Action: Reinforce compression pattern
  Learning: Maintain current level
  
If user corrects understanding:
  Action: Fix and reduce compression
  Learning: Preserve that context type
```

## Output Format Templates

### Template A: Code Change (Compressed)
```markdown
⚡ UPDATE [filename:line]

∴ Change: [One line]
∵ Reason: [Impact level] - [One line]
→ Code:
  ```diff
  - old
  + new
  ```
✅ Check: ▶ Tests ▶ Types ▶ Lint
```

### Template B: Implementation (Premium)
```markdown
⚡ IMPLEMENT

∴ Goal: [One line]
∵ Plan: [3 bullets max]
→ Code:
  ```[lang]
  // Production-ready implementation
  ```
✅ Quality: ▶ Typed ▶ Secure ▶ Tested ▶ Optimized
📊 Impact: [Before] → [After]
```

### Template C: Review (Ultra-Compressed)
```markdown
⚡ REVIEW

Files: [n] | Issues: [n critical, n warnings]

Critical:
1. [file:line]: [Issue] → [Fix]
2. [file:line]: [Issue] → [Fix]

Warnings:
- [file:line]: [Suggestion]

✅ Next: [Action]
```

## Smart Caching Rules

### C1: Pattern Cache

```yaml
Cache_Hot:  # Always loaded (~100 tokens)
  - Common compression patterns
  - User preferences
  - Recent context

Cache_Warm:  # Preload likely (~200 tokens)
  - Related skills
  - Adjacent files
  - Common fixes

Cache_Cold:  # Load on demand
  - Full documentation
  - Edge cases
  - Rare patterns
```

### C2: Predictive Loading

```python
if query_domain == 'api':
    preload(['api-patterns', 'error-handling'])
elif query_domain == 'ui':
    preload(['frontend-design', 'performance'])
elif query_domain == 'database':
    preload(['database-design', 'query-optimization'])
```

## Integration Rules

### I1: Agent Compatibility

**Works with all agents:**
- Announce: `⚡ POWERUSEAGE active with @[agent-name]`
- Apply compression to agent output
- Maintain agent's core principles

### I2: Skill Compatibility

**Chain with skills:**
```yaml
@token-efficiency: Compress output further
@performance-profiling: Include metrics
@clean-code: Maintain standards
```

### I3: Workflow Compatibility

**Use in workflows:**
```yaml
/create → /poweruseage compress
/audit → /poweruseage optimize  
/debug → /poweruseage premium
```

## Error Handling

### E1: Over-Compression Recovery

```yaml
Detection: Ambiguity score > threshold
Response: 
  1. Identify unclear section
  2. Expand minimally (+15% tokens)
  3. Add clarification
  4. Re-validate
```

### E2: Quality Degradation Recovery

```yaml
Detection: Quality score < 0.95
Response:
  1. Halt compression
  2. Restore critical details
  3. Apply selective compression only
  4. Prioritize accuracy
```

## Performance Targets

```yaml
Compression:
  Target: 70% reduction
  Acceptable: 65-75%
  Maximum: 80%

Quality:
  Target: 95% retention
  Minimum: 90%
  Premium: 98%

Speed:
  Target: <100ms latency
  Acceptable: <200ms
  Maximum: <500ms
```

## Enforcement

**These rules are MANDATORY when:**
- User invokes /poweruseage
- Token limits approaching
- Large context detected (>500 tokens)
- Explicit optimization request

**Violations:**
- ❌ Verbose output without compression
- ❌ Missing file:line references
- ❌ Unclear or ambiguous compressed text
- ❌ Quality below 90%

---

**Rule Set**: POWERUSEAGE v3.0 | **Status**: Enforced | **Priority**: P1
