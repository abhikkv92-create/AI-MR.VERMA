---
name: memory-enhanced-workflows
description: Enables workflows to recall past successful executions, common pitfalls, and optimized patterns from the Agent Lightning store.
skills: [agent-memory, agent-memory-systems]
---

# Memory Enhanced Workflows

> **Purpose**: Give the AI "Long-Term Procedural Memory" to stop repeating mistakes and start replicating success.

## Core Concept

Instead of starting from zero every time a workflow runs, this skill allows the agent to:
1. **Query** the LightningStore for similar past spans.
2. **Analyze** which past execution had the highest reward.
3. **Adopt** the strategies that led to that success.

## 🛠️ Usage Protocol

### 1. Recall Phase (Before Execution)

Retrieve "Wisdom" from the store.

```python
from agentlightning.store import LightningStore
from agentlightning.analysis import PatternMatcher

store = LightningStore()
matcher = PatternMatcher(store)

# "How did we successfully build a login page last time?"
similar_spans = matcher.find_similar(
    task_type="frontend_build",
    query="login page",
    min_reward=0.8
)

if similar_spans:
    best_practice = similar_spans[0].attributes["strategy"]
    print(f"💡 Suggestion: Last time, {best_practice} worked perfectly.")
```

### 2. Adaptation Phase (During Execution)

Adjust strategy based on recall.

- **If past attempts failed**: Avoid the paths with `reward=0.0`.
- **If past attempts succeeded**: bias towards agents/skills used in `reward=1.0` spans.

### 3. Consolidation Phase (After Execution)

Save new learnings.

```python
# Did this specific variation work even better?
if current_reward > historical_average:
    store.mark_as_new_best_practice(span_id, task_type)
```

## Integrated Workflows

This skill is automatically active for:
- `/brainstorm` (Recalls creative patterns)
- `/debug` (Recalls fix strategies)
- `/orchestrate` (Recalls effective team compositions)

## 🧠 Memory Types

| Type | Source | Use Case |
|------|--------|----------|
| **Procedural** | Workflow Spans | "How do I do X?" |
| **Episodic** | Traces | "What happened last Tuesday?" |
| **Semantic** | Knowledge Items | "What is the Project TPV architecture?" |
