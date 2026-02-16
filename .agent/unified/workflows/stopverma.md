---
description: Stop the Verma AI System (Docker Stack)
---

This workflow completely shuts down the MR.VERMA intelligence core and removes all containers.

// turbo-all

1. Stop All Core Containers
   - Command: `docker compose -f e:\ABHINAV\MR.VERMA\agent-lightning-local\docker-compose.yml down --remove-orphans`

2. Verify No Containers Are Running
   - Command: `docker ps --filter "name=agl-" --format "table {{.Names}}\t{{.Status}}"`

3. Notify User
   - "🛑 MR.VERMA Singularity Hibernated. All containers removed. Sovereignty maintained."
