"""MR.VERMA Agents Package."""

"""MR.VERMA Agents Package."""

from .base_agent import BaseAgent
from .frontend_cluster import FrontendSpecialist, MobileDeveloper, UIDesigner
from .intelligence_cluster import AIMLEngineer, DataScientist, ResearchAnalyst
from .platform_cluster import ProductionOrchestrator, SecurityArchitect
from .swarm_node import UnifiedSwarmNode

__all__ = [
    "BaseAgent",
    "UnifiedSwarmNode",
    # Intelligence Cluster
    "DataScientist",
    "ResearchAnalyst",
    "AIMLEngineer",
    # Platform Cluster
    "ProductionOrchestrator",
    "SecurityArchitect",
    # Frontend Cluster
    "UIDesigner",
    "FrontendSpecialist",
    "MobileDeveloper",
]
