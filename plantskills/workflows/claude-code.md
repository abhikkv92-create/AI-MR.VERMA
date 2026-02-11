---
description: Claude Code CLI specialized workflow for agentic coding and project analysis.
---

# Claude Code CLI Workflow

Use this workflow to initiate and manage Claude Code sessions for advanced coding tasks, project analysis, and automated refactoring.

## Commands

### 1. Initialize Project Memory
Initialize or update the `CLAUDE.md` file to provide context for the CLI.
```bash
claude /init
```

### 2. Start Interactive Session
Launch the interactive terminal for pair programming.
```bash
claude
```

### 3. Non-Interactive Analysis
Run a prompt and get a direct response without entering the interactive shell.
```bash
claude -p "Analyze the current project structure and suggest optimizations"
```

### 4. Update Claude Code
Ensure you are on the latest version.
```bash
claude update
```

## Best Practices

- **Context Awareness**: Always mention the specific directories or files you want Claude to focus on.
- **Project Memory**: Maintain a comprehensive `CLAUDE.md` file for persistent rules and architecture patterns.
- **Cost Optimization**: Use specific prompts to avoid excessive token usage in large repositories.

## Troubleshooting

- **Authentication**: If you face login issues, run `claude` and follow the OAuth flow in your browser.
- **WSL vs PowerShell**: On Windows, PowerShell is supported, but WSL 2 is recommended for native Linux performance.
