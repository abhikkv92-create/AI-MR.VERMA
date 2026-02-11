---
name: brain-lightning-sync
description: Bidirectional synchronization between Antigravity Brain (Knowledge Items) and Agent Lightning (LightningStore).
skills: [memory-enhanced-workflows]
---

# Brain ↔ Lightning Sync

> **Purpose**: Bridge the gap between "Static Knowledge" (KIs) and "Dynamic Experience" (agent execution history).

## Core Concept

- **Brain (Antigravity)**: Stores structured, curated knowledge (e.g., "How to use Prisma").
- **Lightning (MS Light)**: Stores raw execution data & rewards (e.g., "Prisma migration failed 3 times yesterday").

This skill connects them so the agent learns from *experience* while following *structured guides*.

## 🛠️ Usage Protocol

### 1. Enrich Knowledge with Experience (Read)

When reading a Knowledge Item (KI), append recent performance stats.

```python
from agentlightning.store import LightningStore

def enrich_ki(topic: str, content: str) -> str:
    store = LightningStore()
    stats = store.get_topic_stats(topic)
    
    if stats.failure_rate > 0.5:
        warning = f"⚠️ WARNING: Recent executions for '{topic}' have high failure rate ({stats.failure_rate:.1%}). Check logs."
        return f"{warning}\n\n{content}"
    return content
```

### 2. Crystallize Experience into Knowledge (Write)

When a pattern consistently succeeds (Reward > 0.9), prompt the user to create a KI.

```python
if consistent_success(topic="params_validation"):
    return "💡 I've noticed 'Zod' validation works 100% of the time. Should I create a Knowledge Item for this?"
```

## Integration Points

### `/synthesize` Workflow
- **Before**: Only summarized docs.
- **After**: Checks LightningStore for "proven patterns" to include in synthesis.

### Agent Routing
- **Before**: Static rules.
- **After**: Checks if a KI exists for the specific domain *and* if it's working well.
