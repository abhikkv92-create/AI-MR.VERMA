---
description: Ultra-optimized power usage workflow. Delivers premium Claude/Kimi-grade quality with 70% smaller footprint. Use for any task requiring maximum efficiency without sacrificing quality.
triggers: poweruseage, optimize, compress, efficiency, reduce tokens
version: 3.0.0
---

# ⚡ /poweruseage Workflow

> **Ultra-compression mode activated. Premium quality maintained.**

## Quick Start

```bash
/poweruseage <action> [target] [options]
```

## Actions

| Command | Description | Use Case |
|---------|-------------|----------|
| `compress` | Reduce token usage by 70% | Large contexts, verbose content |
| `optimize` | Performance + size optimization | Codebases, applications |
| `premium` | Maximum quality, minimal size | Critical implementations |
| `analyze` | Efficiency audit with recommendations | Identify waste |
| `batch` | Process multiple files | Large-scale optimization |

## Options

```yaml
--level, -l:      1|2|3 (basic|aggressive|maximum)
--quality, -q:    standard|premium (default: premium)
--target, -t:     file|directory|code_block
--validate, -v:   Enable quality gates (default: true)
--cache, -c:      Use smart caching (default: true)
```

## Execution Flow

### Phase 1: Intent Classification (10ms)
```python
if action == 'compress':
    strategy = CompressionStrategy.AGGRESSIVE
    quality_threshold = 0.95
elif action == 'premium':
    strategy = CompressionStrategy.SELECTIVE
    quality_threshold = 0.98
```

### Phase 2: Smart Analysis
1. **Size Assessment**: Calculate current token count
2. **Content Mapping**: Identify compressible vs critical sections
3. **Strategy Selection**: Match compression level to content type
4. **Cache Check**: Load pre-computed patterns if available

### Phase 3: Optimization Engine

**Compression Pipeline:**
```
Input → Semantic Analysis → Pattern Matching → 
Symbol Substitution → Structure Optimization → 
Quality Validation → Compressed Output
```

**Key Transformations:**
- Text: Verbose → Symbolic (→ ∴ ∵)
- Structure: Paragraphs → Bullets
- Code: Minified but readable
- References: Inline → Linked (@skill)

### Phase 4: Quality Assurance

**Automated Checks:**
- [ ] Token reduction ≥ target%
- [ ] Critical information preserved
- [ ] Output is actionable
- [ ] No ambiguity introduced
- [ ] Ready for immediate use

**Validation Score:**
```yaml
score = (information_preserved * 0.4 + 
         actionability * 0.3 + 
         clarity * 0.2 + 
         completeness * 0.1)
         
Required: score >= quality_threshold (0.95-0.98)
```

## Usage Examples

### Example 1: Compress Large Response
```bash
/poweruseage compress --level=3 --target="previous_output"
```

**Before:** 850 tokens of verbose explanation
**After:** 
```markdown
⚡ COMPRESSED OUTPUT

∴ Objective: Optimize database queries
∵ Issues: 3 N+1 queries, missing indexes
→ Actions:
  1. Add `user_id` index [schema.sql:42]
  2. Use `select_related()` [views.py:28]
  3. Cache frequent lookups
✅ Savings: 450ms → 45ms (-90%)
```
**Result:** 180 tokens (-79%)

### Example 2: Premium Implementation
```bash
/poweruseage premium --target="feature_request"
```

Output characteristics:
- Production-ready code
- Type-safe throughout
- Error handling complete
- Security reviewed
- **Compressed format**: No filler, maximum density

### Example 3: Batch Optimization
```bash
/poweruseage batch --dir=./src --pattern="*.ts" --level=2
```

Generates:
- Summary report (all files)
- Individual optimizations
- Combined savings calculation
- Deployment-ready output

### Example 4: Efficiency Audit
```bash
/poweruseage analyze --report=detailed
```

Reports:
```yaml
Current_State:
  Total_Files: 45
  Avg_File_Size: 12KB
  Total_Tokens: 15,000
  
Optimization_Opportunities:
  - 12 files: Remove dead code (-2,100 tokens)
  - 8 files: Compress comments (-890 tokens)
  - 5 files: Inline small functions (-450 tokens)
  
Projected_Savings:
  Tokens: -3,440 (-23%)
  Size: -45KB (-8%)
  Load_Time: -12%
```

## Integration with Other Workflows

**Chain with `/audit`:**
```bash
/audit → Identify issues
/poweruseage optimize → Fix with compression
```

**Chain with `/create`:**
```bash
/create → Generate application  
/poweruseage compress --level=2 → Optimize output
```

**Chain with `/debug`:**
```bash
/debug → Find issues
/poweruseage premium → Concise fix with max quality
```

## Output Formats

### Format 1: Minimal (Level 3)
```markdown
⚡ [Action]
∴ [Objective]
→ [Solution in 3 bullets]
✅ [Validation]
```
~50 tokens

### Format 2: Standard (Level 2)
```markdown
⚡ [Action] [Target]

∴ Objective: [One line]
∵ Context: [2 bullets]
→ Implementation:
  - [Step 1]
  - [Step 2]
  - [Step 3]
✅ Validation: [Checks]
📊 Metrics: [Before/After]
```
~120 tokens

### Format 3: Premium (Level 1)
```markdown
⚡ [Action] - Premium Quality

[Compressed but complete explanation]
[Production-ready code]
[Comprehensive validation]
```
~300 tokens (vs 1000+ baseline)

## Performance Characteristics

```yaml
Latency:
  Intent_Classification: <10ms
  Content_Analysis: 20-50ms
  Compression: 30-100ms
  Validation: 10-30ms
  Total: 70-190ms

Throughput:
  Text: ~10,000 tokens/second
  Code: ~5,000 tokens/second
  Mixed: ~7,000 tokens/second

Efficiency:
  Compression_Ratio: 70-85%
  Quality_Retention: 95-98%
  Cache_Hit_Rate: 60-80%
```

## Smart Features

**1. Adaptive Compression**
```python
if content.contains('code'):
    preserve_readability = True
    compress_comments = True
elif content.contains('explanation'):
    use_symbols = True
    bullet_conversion = True
```

**2. Context Memory**
```python
# Learn from user preferences
if user.expands_output:
    compression_level -= 1
if user.asks_clarification:
    add_context += 20%
```

**3. Predictive Optimization**
```python
# Pre-compute likely next steps
if optimizing_api:
    preload(['caching-strategies', 'rate-limiting'])
if optimizing_ui:
    preload(['lazy-loading', 'code-splitting'])
```

## Quality Guarantees

**Premium Mode:**
- 98%+ information retention
- 100% code functionality preserved
- Zero ambiguity in critical sections
- Immediate actionability

**Aggressive Mode:**
- 95%+ information retention
- All file:line references preserved
- Expandable on demand
- Core logic intact

## Troubleshooting

| Symptom | Solution |
|---------|----------|
| Output too terse | Increase level: `--level=1` |
| Missing context | Use premium mode: `--quality=premium` |
| Need expansion | Reply "expand" for full version |
| Unclear symbols | Request clarification |
| Quality concerns | Auto-rollback to less aggressive |

## Best Practices

1. **Start aggressive**: Use Level 3, adjust if needed
2. **Validate early**: Check first output before continuing
3. **Use symbols**: Train users on symbolic notation
4. **Link references**: @skill-name vs full text
5. **Cache patterns**: Reuse common optimizations
6. **Batch similar**: Group related optimizations

---

**Workflow Version**: 3.0.0 | **Efficiency**: 70% token reduction | **Quality**: Premium Grade
