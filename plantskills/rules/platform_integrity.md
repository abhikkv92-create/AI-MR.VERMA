---
priority: P1
trigger: always_on
---

# 🛡️ Platform Integrity Protocol

> **Purpose**: Maintain the structural and functional integrity of the Antigravity workspace.

## 1. File Persistence
- **GEMINI.md**: MUST exist in `.agent/GEMINI.md`. If missing, recreate immediately.
- **ARCHITECTURE.md**: MUST be kept up-to-date with agent/skill changes.

## 2. Component Modularity
- **Max File Size**: Components > 300 lines MUST be refactored.
- **Colocation**: Keep related styles/types with the component or in strictly defined shared folders.

## 3. Orchestration Enforcement
- **Minimum Agents**: Orchestration requires 3+ distinct agents.
- **Verification**: Always run `checklist.py` before marking a task complete.
