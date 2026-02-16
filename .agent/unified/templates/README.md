# Template Organization Schema

This document describes the standardized directory structure for all templates in the unified agent system. The organization follows a logical grouping by component type and functionality to ensure maintainability and discoverability.

## Directory Structure

```
templates/
├── agents/                    # AI agent templates
│   ├── architecture/          # System architecture and design agents
│   ├── development/           # Development tool and debugging agents
│   ├── programming/           # Language-specific programming agents
│   └── specialized/           # Specialized domain agents
├── commands/                  # Command implementations
│   ├── automation/            # Workflow and automation commands
│   └── development/           # Development utility commands
├── hooks/                     # Hook implementations
│   ├── development/           # Development process hooks
│   ├── monitoring/            # System monitoring hooks
│   └── post-tool/             # Post-execution hooks
├── mcp/                       # Model Context Protocol
│   └── integrations/          # MCP integrations and connectors
├── settings/                  # Statusline and configuration
│   └── statuslines/           # Statusline implementations
└── skills/                    # Specialized skills
    ├── ai-research/           # AI and ML research skills
    ├── canvas/                  # Canvas and design skills
    └── development/             # Development utility skills
```

## Component Categories

### Agents (`agents/`)

**Architecture** (`agents/architecture/`)
- System design and architecture agents
- Machine learning engineers
- Infrastructure specialists

**Development** (`agents/development/`)
- Debugging and troubleshooting agents
- Performance analysis agents
- Tool integration specialists
- Command experts

**Programming** (`agents/programming/`)
- Language-specific programming agents
- Language experts (JavaScript, Rust, Go, C/C++, C#)
- Code optimization specialists

**Specialized** (`agents/specialized/`)
- Domain-specific specialists
- Mobile developers (iOS, Android, Flutter)
- Security specialists
- Performance optimization experts
- Specialized framework experts

### Commands (`commands/`)

**Automation** (`commands/automation/`)
- Workflow orchestration
- Session management
- Memory optimization
- Batch processing commands

**Development** (`commands/development/`)
- Utility commands for development
- Memory usage optimization
- Changelog generation
- Development workflow tools

### Hooks (`hooks/`)

**Development** (`hooks/development/`)
- Code formatting hooks
- Test execution hooks
- Development process automation

**Monitoring** (`hooks/monitoring/`)
- Performance monitoring
- Command logging
- System health checks

**Post-Tool** (`hooks/post-tool/`)
- Post-execution cleanup
- Result processing
- Output formatting

### Model Context Protocol (`mcp/`)

**Integrations** (`mcp/integrations/`)
- Memory system integrations
- External service connectors
- Protocol implementations

### Settings (`settings/`)

**Statuslines** (`settings/statuslines/`)
- Command status indicators
- Performance monitors
- Project dashboards
- Multi-environment status displays

### Skills (`skills/`)

**AI Research** (`skills/ai-research/`)
- Machine learning model serving
- Fine-tuning utilities
- Optimization techniques
- Tokenization systems

**Canvas** (`skills/canvas/`)
- Design and visualization tools
- Canvas-based interfaces
- Graphics and rendering

**Development** (`skills/development/`)
- Scientific computing tools
- Resource management
- Session handling
- Metrics and analytics

## Component Structure

Each component directory contains:
- `*.json` - Component metadata and configuration
- `*.md` - Template documentation (for agents)
- `*.js` - Implementation files (for commands/hooks)
- `tests.ps1` - PowerShell test scripts

## Migration Notes

This structure consolidates previously scattered components into logical groupings:

- **Agents**: Consolidated from `development-tools/`, `programming-languages/`, `data-ai/`, `development-team/`, `expert-advisors/`, `performance-testing/`, `realtime/`, and `security/` directories
- **Commands**: Consolidated from `automation/`, `performance/`, `team/`, and `deployment/` directories
- **Hooks**: Consolidated from `development-tools/`, `performance/`, and `post-tool/` directories
- **Skills**: Consolidated from `ai-research/`, `enterprise-communication/`, `railway/`, and `scientific/` directories

## Usage Guidelines

1. **Component Placement**: Place new components in the most specific appropriate category
2. **Naming Conventions**: Use kebab-case for directory names and component files
3. **Cross-References**: Document dependencies between components in their respective README files
4. **Testing**: All components must include comprehensive PowerShell test scripts
5. **Documentation**: Include clear documentation for complex components

## Maintenance

This structure is designed to be:
- **Scalable**: New categories can be added as needed
- **Discoverable**: Logical grouping makes components easy to find
- **Maintainable**: Related components are co-located
- **Extensible**: New component types can be accommodated

Regular audits should be performed to ensure components remain in their appropriate categories and the structure continues to serve the project's needs.