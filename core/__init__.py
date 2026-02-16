"""Core package initialization."""

from core.processing_unit import kernel_pu
from core.security_orchestrator import security_service
from core.task_queue import VisionTaskQueue

# Create global task queue instance
global_task_queue = VisionTaskQueue(concurrency=5)

__all__ = [
    "VisionTaskQueue",
    "global_task_queue",
    "kernel_pu",
    "security_service",
]
