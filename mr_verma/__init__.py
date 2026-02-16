"""MR.VERMA - Multi-agent AI Platform."""

__version__ = "5.0.0"

from agents import (
    AIMLEngineer,
    BaseAgent,
    DataScientist,
    FrontendSpecialist,
    MobileDeveloper,
    ProductionOrchestrator,
    ResearchAnalyst,
    SecurityArchitect,
    UIDesigner,
    UnifiedSwarmNode,
)
from core import global_task_queue, kernel_pu, security_service

__all__ = [
    "__version__",
    # Core components
    "global_task_queue",
    "kernel_pu",
    "security_service",
    # Agents
    "BaseAgent",
    "UnifiedSwarmNode",
    "DataScientist",
    "ResearchAnalyst",
    "AIMLEngineer",
    "ProductionOrchestrator",
    "SecurityArchitect",
    "UIDesigner",
    "FrontendSpecialist",
    "MobileDeveloper",
]
