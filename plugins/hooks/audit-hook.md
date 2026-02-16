---
name: audit-hook
type: lifecycle-hook
event: post-commit
target: security-fortress
description: Automatically triggers a security sweep after any file modification.
---

import os
import logging
from core.mcp_hub import mcp_hub

log = logging.getLogger("Hook.Audit")

async def run(context):
    """
    Hook execution logic.
    Triggers the Security Fortress to verify the integrity of the latest change.
    """
    modified_files = context.get("files", [])
    log.info(f"Post-commit hook triggered for: {modified_files}")

    # Standardized MCP tool call to the security scanner
    result = await mcp_hub.call_tool("security_scan", {"paths": modified_files})
    
    if result.get("high_risk_vulnerabilities", 0) > 0:
        log.warning("FALLBACK: High-risk vulnerability detected by Hook. Blocking auto-deploy.")
        return {"status": "BLOCK", "reason": "Security Alert"}
        
    return {"status": "PASS"}
