---
description: Start the Verma AI System (Docker Stack)
---

# MR.VERMA V5.0 Singularity Startup

This workflow starts the full MR.VERMA intelligence core (Collector + Trainer) and launches the CLI interface.

// turbo-all

1. Purging Legacy Artifacts (Singularity Hygiene)
   - Command: `python scripts/run_maintenance.py --purge`

2. Start Core Docker Stack (V5.0 Infrastructure)
   - Command: `docker compose -f e:\ABHINAV\MR.VERMA\agent-lightning-local\docker-compose.yml up -d --remove-orphans agl-collector agl-trainer`

3. Seed Singularity Brain (Codebase Scan)
   - Command: `python -c "import asyncio; from main_orchestrator import SupremeOrchestrator; orch = SupremeOrchestrator(); asyncio.run(orch.dep_graph.sync_to_brain())"`

4. Verify V5.0 Engine Health
   - Command: `docker ps --filter "name=agl-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"`

5. Launch Terminal Chat CLI
   - Command: `python e:\ABHINAV\MR.VERMA\agent-lightning-local\terminal_chat.py`

6. Notify User
   - "🌌 MR.VERMA V5.0 Singularity Started. Brain is Synced. Terminal Chat is live."
