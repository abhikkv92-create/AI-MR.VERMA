# 📁 Directory Restructure Plan for MR.VERMA

## Current Issues Identified:

### 1. Duplicate Components
- `settings/command-statusline/` vs `statusline/command-statusline/` (identical)
- `automation/workflow-orchestrator/` vs `commands/workflow-orchestrator/` (duplicate)
- `performance/optimize-memory-usage/` vs `commands/optimize-memory-usage/` (duplicate)

### 2. Scattered Organization
- Component types mixed across directories
- No logical grouping by functionality
- Inconsistent naming conventions

### 3. Proposed New Structure:

```
templates/
├── agents/                    # AI agent templates
│   ├── development/
│   │   ├── tooling-engineer/
│   │   ├── debugger/
│   │   ├── performance-engineer/
│   │   └── command-expert/
│   ├── programming/
│   │   ├── javascript-pro/
│   │   ├── python-pro/
│   │   ├── rust-pro/
│   │   ├── golang-pro/
│   │   └── csharp-developer/
│   ├── architecture/
│   │   ├── cloud-architect/
│   │   ├── database-architect/
│   │   └── graphql-architect/
│   └── specialized/
│       ├── mobile-developer/
│       ├── game-developer/
│       └── ui-ux-designer/
│
├── commands/                   # Command implementations
│   ├── automation/
│   │   ├── workflow-orchestrator/
│   │   ├── memory-spring-cleaning/
│   │   └── session-learning-capture/
│   ├── development/
│   │   ├── changelog-demo-command/
│   │   └── optimize-memory-usage/
│   └── system/
│       └── (reserved for future system commands)
│
├── hooks/                     # Hook implementations
│   ├── development/
│   │   ├── format-python-files/
│   │   └── test-runner/
│   ├── monitoring/
│   │   ├── performance-monitor/
│   │   └── command-logger/
│   └── post-tool/
│       └── format-python-files/ (consolidated)
│
├── settings/                  # Statusline and configuration
│   └── statuslines/
│       ├── command-statusline/
│       ├── game-performance-monitor-statusline/
│       ├── unity-project-dashboard-statusline/
│       └── vercel-multi-env-status/
│
├── skills/                    # Specialized skills
│   ├── ai-research/
│   │   ├── agent-memory-systems/
│   │   ├── crewai/
│   │   ├── fine-tuning-peft/
│   │   └── inference-serving-vllm/
│   ├── canvas/
│   │   └── canvas-design/
│   ├── documentation/
│   │   └── docx/
│   └── development/
│       ├── docker-expert/
│       └── cto-advisor/
│
└── mcp/                      # Model Context Protocol
    └── integrations/
        └── memory-integration/
```

## Consolidation Actions:

1. **Remove Duplicates:**
   - Keep `commands/workflow-orchestrator/` (remove from automation/)
   - Keep `commands/optimize-memory-usage/` (remove from performance/)
   - Consolidate all statusline components into `settings/statuslines/`

2. **Logical Grouping:**
   - Group agents by function (development, programming, architecture, specialized)
   - Group commands by purpose (automation, development, system)
   - Group hooks by trigger type (development, monitoring, post-tool)

3. **Naming Convention:**
   - Use kebab-case consistently
   - Use descriptive but concise names
   - Follow type-specific suffixes (-engineer, -developer, -architect)

## Implementation Steps:

1. Create new directory structure
2. Move components to appropriate locations
3. Update all references and imports
4. Remove empty directories
5. Validate with QA framework
6. Update documentation