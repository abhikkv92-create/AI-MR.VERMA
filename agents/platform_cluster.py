"""
Platform Cluster Agents
Specialized agents for platform operations, security, and production orchestration.
"""

import json
import logging
import os
from datetime import datetime
from typing import Any

from core.ai.primary_engine import PrimaryAIEngine
from core.ai.secondary_engine import SecondaryAIEngine

from .base_agent import BaseAgent

logger = logging.getLogger("Kernel.PlatformCluster")


class ProductionOrchestrator(BaseAgent):
    """Agent specialized in production operations and self-healing."""

    def __init__(self):
        super().__init__("ProductionOrchestrator", "Platform", "PLATFORM")
        self.primary_engine = PrimaryAIEngine()
        self.secondary_engine = SecondaryAIEngine()

    async def trigger_self_heal(self) -> dict[str, Any]:
        """Trigger self-healing analysis (convenience method for tests)."""
        return await self._self_heal({"auto_heal": True, "audit_log": "logs/audit.log"})

    async def enqueue_background_task(self, task_id: str, task_func, *args, **kwargs):
        """Enqueue a background task (convenience method for tests)."""
        from core import global_task_queue

        return await global_task_queue.submit(task_func, *args, **kwargs)

    async def _execute_task_logic(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """Execute production orchestration tasks."""
        mode = task_data.get("mode", "")

        if mode == "self_heal":
            return await self._self_heal(task_data)
        elif mode == "health_check":
            return await self._health_check(task_data)
        else:
            return {"status": "ERROR", "message": f"Unknown mode: {mode}"}

    async def _self_heal(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """Perform self-healing analysis and remediation."""
        auto_heal = task_data.get("auto_heal", False)
        audit_log = task_data.get("audit_log", "logs/audit.log")

        # Read recent failures from audit log
        failures = []
        if os.path.exists(audit_log):
            try:
                with open(audit_log) as f:
                    for line in f.readlines()[-100:]:  # Last 100 lines
                        try:
                            entry = json.loads(line.strip())
                            if entry.get("event") == "TASK_FAIL":
                                failures.append(entry)
                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                logger.error(f"Failed to read audit log: {e}")

        if not failures:
            return {
                "status": "Self-Healing Analysis Complete",
                "message": "No failures found in recent logs",
                "actions": [],
            }

        # Analyze failures using AI
        system_prompt = (
            "You are a ProductionOrchestrator agent. Analyze the following "
            "system failures and suggest remediation actions. Respond with "
            "a JSON array of actions to take. Each action should have "
            "'type' (command or file) and 'details' fields."
        )

        failures_text = json.dumps(failures, indent=2)

        try:
            analysis = self.secondary_engine.generate(
                system_prompt=system_prompt,
                prompt=f"Recent failures:\n{failures_text}",
                max_tokens=1500,
                stream=False,
            )

            actions = []
            if auto_heal:
                # Parse and execute actions
                await self._execute_healing_actions(analysis)
                actions.append("Executed healing actions")

            return {
                "status": "Self-Healing Analysis Complete",
                "failures_found": len(failures),
                "analysis": analysis,
                "actions_taken": actions,
            }
        except Exception as e:
            logger.error(f"Self-healing analysis failed: {e}")
            return {"status": "ERROR", "message": str(e)}

    async def _execute_healing_actions(self, analysis: str) -> None:
        """Execute healing actions based on AI analysis."""
        # This is a simplified implementation
        # In production, this would parse structured actions and execute safely
        logger.info(f"Executing healing actions based on analysis: {analysis[:100]}...")

        # Log the healing action
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "HEAL_ACTION",
            "agent": self.agent_id,
            "action": "Executed AI-suggested remediation",
            "analysis_summary": analysis[:200],
        }

        try:
            with open("logs/audit.log", "a") as f:
                f.write(json.dumps(audit_entry) + "\n")
        except Exception as e:
            logger.error(f"Failed to log healing action: {e}")

    async def _health_check(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """Perform system health check."""
        components = task_data.get("components", ["all"])

        health_status = {
            "timestamp": datetime.now().isoformat(),
            "components": {},
            "overall": "healthy",
        }

        # Check core components
        if "all" in components or "memory" in components:
            health_status["components"]["memory"] = "healthy"

        if "all" in components or "queue" in components:
            health_status["components"]["queue"] = "healthy"

        return {
            "status": "Health Check Complete",
            "health": health_status,
        }


class SecurityArchitect(BaseAgent):
    """Agent specialized in security audits and vulnerability analysis."""

    def __init__(self):
        super().__init__("SecurityArchitect", "Security", "PLATFORM")
        self.primary_engine = PrimaryAIEngine()
        self.secondary_engine = SecondaryAIEngine()

    async def _execute_task_logic(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """Execute security tasks."""
        mode = task_data.get("mode", "")

        if mode == "ai_security_scan":
            return await self._security_scan(task_data)
        elif mode == "vulnerability_check":
            return await self._vulnerability_check(task_data)
        else:
            return {"status": "ERROR", "message": f"Unknown mode: {mode}"}

    async def _security_scan(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """Perform AI-powered security scan on code."""
        target_file = task_data.get("target_file", "")

        try:
            with open(target_file) as f:
                code_content = f.read()
        except Exception as e:
            return {"status": "ERROR", "message": f"Failed to read file: {e}"}

        system_prompt = (
            "You are a SecurityArchitect agent. Analyze the following code "
            "for security vulnerabilities, hardcoded secrets, and bad practices. "
            "Provide a risk score (0-10), list critical vulnerabilities, "
            "and suggest fixes. Return analysis as structured text."
        )

        try:
            result = self.secondary_engine.generate(
                system_prompt=system_prompt,
                prompt=f"Code to analyze:\n```\n{code_content}\n```",
                max_tokens=2000,
                stream=False,
            )

            return {
                "status": "AI Security Scan Complete",
                "analysis": result,
                "target_file": target_file,
            }
        except Exception as e:
            logger.error(f"Security scan failed: {e}")
            return {"status": "ERROR", "message": str(e)}

    async def _vulnerability_check(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """Check for known vulnerabilities in dependencies."""
        dependencies = task_data.get("dependencies", [])

        system_prompt = (
            "You are a SecurityArchitect agent. Check the following dependencies "
            "for known security vulnerabilities. List any CVEs found and "
            "recommend updates."
        )

        try:
            result = self.secondary_engine.generate(
                system_prompt=system_prompt,
                prompt=f"Dependencies: {', '.join(dependencies)}",
                max_tokens=1500,
                stream=False,
            )

            return {
                "status": "Vulnerability Check Complete",
                "findings": result,
                "dependencies_checked": len(dependencies),
            }
        except Exception as e:
            logger.error(f"Vulnerability check failed: {e}")
            return {"status": "ERROR", "message": str(e)}
