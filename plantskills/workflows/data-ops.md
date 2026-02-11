---
description: Database & Analytics command center. Activates database-architect, database-optimizer, and analytics-tracking.
---

# /data-ops - Data Command Center

$ARGUMENTS: [task_description]

## 🤖 Applied Agents: `database-architect`, `backend-specialist`

This workflow manages the entire data lifecycle: design, optimization, migration, and analysis.

## 🛠️ Skills Activated
- **Design:** `database-design`, `schema-validator`
- **Optimization:** `database-optimizer`, `cost-optimization`
- **Integration:** `convex`, `firebase`, `prisma`
- **Analytics:** `analytics-tracking`, `rag-pipeline`

## 📋 Step-by-Step Execution

1.  **Schema Engineering**
    - Agent: `database-architect`
    - Action: Design or modify schema using `database-design` principles.
    - Check: Normalization vs Denormalization tradeoffs.

2.  **Performance Tuning**
    - Agent: `database-architect`
    - Action: Apply `database-optimizer` tactics (Indexing, Partitioning).
    - Tool: Run `explain analyze` logic on complex queries.

3.  **Migration Management**
    - Agent: `backend-specialist`
    - Action: Generate safe migration scripts using `deployment-procedures` safety checks.

4.  **Verification**
    - Script: `python .agent/scripts/schema_validator.py`
    - Check: Data integrity and consistent types.

---

## 🚦 Output Format
Produces optimized database schemas, migration scripts, or performance analysis reports.
