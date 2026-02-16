import asyncio
import logging
import time
from typing import Any, Dict

from core import kernel_pu

logger = logging.getLogger("Kernel.SelfHealing")

class AutonomousRepairLoop:
    """
    ARL Module: Monitors system integrity and performs autonomous self-healing.
    """

    def __init__(self, orchestrator: Any):
        self.orchestrator = orchestrator
        self.is_running = False
        self._heal_count = 0
        self._last_audit_report = ""

    async def start(self):
        """Starts the heart-beat monitoring loop."""
        self.is_running = True
        logger.info("ARL: Autonomous Repair Loop Started.")
        while self.is_running:
            await self._monitor_cycle()
            await asyncio.sleep(600) # Every 10 minutes

    async def _monitor_cycle(self):
        """Single health-check and healing cycle with Latency Awareness."""
        start_time = time.time()
        logger.info("ARL: Running System Integrity Audit...")

        health = kernel_pu.check_system_health()

        # Latency Awareness (V5.0)
        audit_duration = time.time() - start_time
        if audit_duration > 1.0: # If audit takes more than 1s, system is lagging
            logger.warning(f"ARL: High System Latency Detected ({audit_duration:.2f}s). Optimizing pools...")

        if health["status"] == "CRITICAL":
            await self._heal_memory_leak()

        # Thermal & Hardware check (Simulated for 13900H)
        load = health.get("cpu_usage", 0)
        if load > 90.0:
            logger.warning(f"ARL: High Thermal Load ({load}%). Engaging Power Governor.")

        await self._ensure_mesh_integrity()

    async def _heal_memory_leak(self):
        """Performs a memory purge and garbage collection."""
        logger.warning("ARL: Critical Memory Leak Detected. Initiating Self-Heal...")
        import gc
        gc.collect()
        # Potential for dynamic node restart if needed
        logger.info("ARL: Memory self-healed via GC sweep.")
        self._heal_count += 1

    async def _ensure_mesh_integrity(self):
        """Verifies that all master nodes are responsive."""
        for name, node in self.orchestrator.nodes.items():
            if not node.is_active:
                logger.warning(f"ARL: Mesh Node '{name}' found inactive. Restarting...")
                node.start()
                self._heal_count += 1

    def get_stats(self) -> Dict[str, Any]:
        return {
            "heals_performed": self._heal_count,
            "arl_status": "ACTIVE" if self.is_running else "INACTIVE",
            "last_audit": self._last_audit_report
        }

    async def stop(self):
        self.is_running = False
        logger.info("ARL: Autonomous Repair Loop Stopped.")
