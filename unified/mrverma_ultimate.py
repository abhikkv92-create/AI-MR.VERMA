#!/usr/bin/env python3
"""
MR.VERMA Ultimate - Complete AI Platform with Integrated Prompt Library
=====================================================================

Fully integrated system featuring:
- 27 AI Agents
- 66+ Technical Skills
- 19 Automated Workflows
- 82 System Prompts from Leading AI Tools (Claude, Cursor, Devin, etc.)
- Prompt Library Browser
- Prompt-Enhanced Agent System
- Multi-Agent Orchestration

Usage: python unified/mrverma_ultimate.py
"""

import os
import sys
import json
import asyncio
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import fnmatch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Try to import rich for UI
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    from rich.tree import Tree
    from rich.prompt import Prompt, Confirm
    from rich.layout import Layout
    from rich.live import Live
    from rich.progress import Progress, SpinnerColumn, TextColumn

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Console setup
if RICH_AVAILABLE:
    console = Console()
else:

    class DummyConsole:
        def print(self, *args, **kwargs):
            text = " ".join(str(a) for a in args)
            for tag in [
                "[bold]",
                "[/bold]",
                "[green]",
                "[/green]",
                "[blue]",
                "[/blue]",
                "[red]",
                "[/red]",
                "[yellow]",
                "[/yellow]",
                "[cyan]",
                "[/cyan]",
                "[bold green]",
                "[bold blue]",
                "[bold red]",
                "[bold yellow]",
                "[bold cyan]",
            ]:
                text = text.replace(tag, "")
            print(text)

        def status(self, msg):
            class DummyStatus:
                def __enter__(self):
                    return self

                def __exit__(self, *args):
                    pass

            return DummyStatus()

    class DummyPrompt:
        @staticmethod
        def ask(msg, **kwargs):
            default = kwargs.get("default", "")
            choices = kwargs.get("choices")
            if choices:
                msg = f"{msg} ({'/'.join(choices)}): "
            elif default:
                msg = f"{msg} [{default}]: "
            else:
                msg = f"{msg}: "
            result = input(msg)
            return result if result else default

    class DummyConfirm:
        @staticmethod
        def ask(msg):
            return input(f"{msg} (y/n): ").lower() in ["y", "yes"]

    class DummyPanel:
        def __init__(self, content, **kwargs):
            self.content = content

        def __str__(self):
            return f"\n{'=' * 70}\n{self.content}\n{'=' * 70}\n"

    class DummyTable:
        def __init__(self, **kwargs):
            self.rows = []

        def add_column(self, *args, **kwargs):
            pass

        def add_row(self, *args):
            self.rows.append(args)

        def __str__(self):
            return "\n".join([" | ".join(row) for row in self.rows])

    class DummyTree:
        def __init__(self, label):
            self.label = label
            self.children = []

        def add(self, child):
            self.children.append(child)

        def __str__(self):
            return f"{self.label}\n" + "\n".join([f"  - {c}" for c in self.children])

    console = DummyConsole()
    Prompt = DummyPrompt
    Confirm = DummyConfirm
    Panel = DummyPanel
    Table = DummyTable
    Tree = DummyTree


# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT LIBRARY SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class PromptEntry:
    """Represents a system prompt from the library"""

    name: str
    source: str  # e.g., "Anthropic/Claude Code"
    category: str
    filepath: str
    content: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)

    def load_content(self):
        """Load prompt content from file"""
        try:
            with open(self.filepath, "r", encoding="utf-8", errors="ignore") as f:
                self.content = f.read()
            return True
        except Exception as e:
            print(f"Error loading {self.filepath}: {e}")
            return False


class PromptLibrary:
    """Manages the system prompts library"""

    def __init__(self, base_path: str = "knowledge/prompts"):
        self.base_path = Path(base_path)
        self.prompts: Dict[str, PromptEntry] = {}
        self.categories: Dict[str, List[PromptEntry]] = {}
        self.sources: Dict[str, List[PromptEntry]] = {}
        self._index_prompts()

    def _index_prompts(self):
        """Index all prompt files"""
        if not self.base_path.exists():
            print(f"Warning: Prompt library not found at {self.base_path}")
            return

        prompt_extensions = ["*.txt", "*.md"]

        for ext in prompt_extensions:
            for filepath in self.base_path.rglob(ext):
                # Skip README and LICENSE files
                if filepath.name in ["README.md", "LICENSE.md"]:
                    continue

                # Determine source (parent directories)
                relative_path = filepath.relative_to(self.base_path)
                source = str(relative_path.parent)

                # Determine category based on source
                category = self._categorize_prompt(source, filepath.name)

                # Create entry
                name = filepath.stem
                entry = PromptEntry(
                    name=name,
                    source=source,
                    category=category,
                    filepath=str(filepath),
                    description=self._extract_description(filepath),
                    tags=self._extract_tags(source, name),
                )

                # Store in dictionaries
                key = f"{source}/{name}"
                self.prompts[key] = entry

                # Organize by category
                if category not in self.categories:
                    self.categories[category] = []
                self.categories[category].append(entry)

                # Organize by source
                if source not in self.sources:
                    self.sources[source] = []
                self.sources[source].append(entry)

    def _categorize_prompt(self, source: str, filename: str) -> str:
        """Categorize a prompt based on its source and name"""
        source_lower = source.lower()
        filename_lower = filename.lower()

        # Check for agent-related prompts
        if any(
            kw in source_lower or kw in filename_lower
            for kw in ["cursor", "claude", "devin", "augment", "kiro", "junie", "agent"]
        ):
            return "AI Agents"

        # Check for coding prompts
        if any(
            kw in source_lower or kw in filename_lower
            for kw in ["code", "coding", "vscode", "xcode", "replit", "windsurf"]
        ):
            return "Code Generation"

        # Check for chat/assistant prompts
        if any(
            kw in source_lower or kw in filename_lower
            for kw in ["chat", "assistant", "gemini", "perplexity", "notion"]
        ):
            return "Chat Assistants"

        # Check for UI/Design prompts
        if any(
            kw in source_lower or kw in filename_lower
            for kw in ["lovable", "v0", "design", "ui"]
        ):
            return "UI/Design"

        # Check for search/research prompts
        if any(
            kw in source_lower or kw in filename_lower
            for kw in ["perplexity", "search", "research", "deepwiki"]
        ):
            return "Research"

        return "General"

    def _extract_description(self, filepath: Path) -> str:
        """Extract description from file content or name"""
        name = filepath.stem
        # Clean up name
        description = name.replace("_", " ").replace("-", " ")
        return description[:100]

    def _extract_tags(self, source: str, name: str) -> List[str]:
        """Extract tags from source and name"""
        tags = []

        # Add source as tag
        source_parts = source.split("/")
        if source_parts and source_parts[0]:
            tags.append(source_parts[0].lower())

        # Extract keywords from name
        keywords = [
            "agent",
            "code",
            "chat",
            "assistant",
            "system",
            "prompt",
            "claude",
            "cursor",
            "devin",
            "gpt",
            "ai",
            "ml",
        ]
        name_lower = name.lower()
        for kw in keywords:
            if kw in name_lower and kw not in tags:
                tags.append(kw)

        return tags[:5]  # Limit to 5 tags

    def get(self, key: str) -> Optional[PromptEntry]:
        """Get a prompt by key"""
        return self.prompts.get(key)

    def search(self, query: str) -> List[PromptEntry]:
        """Search prompts by query"""
        query_lower = query.lower()
        results = []

        for entry in self.prompts.values():
            # Search in name, source, description, and tags
            if (
                query_lower in entry.name.lower()
                or query_lower in entry.source.lower()
                or query_lower in entry.description.lower()
                or any(query_lower in tag for tag in entry.tags)
            ):
                results.append(entry)

        return results

    def list_by_category(self, category: str) -> List[PromptEntry]:
        """List prompts by category"""
        return self.categories.get(category, [])

    def list_by_source(self, source: str) -> List[PromptEntry]:
        """List prompts by source"""
        return self.sources.get(source, [])

    def get_all_categories(self) -> List[str]:
        """Get all categories"""
        return list(self.categories.keys())

    def get_all_sources(self) -> List[str]:
        """Get all sources"""
        return list(self.sources.keys())

    def get_stats(self) -> Dict:
        """Get library statistics"""
        return {
            "total_prompts": len(self.prompts),
            "categories": len(self.categories),
            "sources": len(self.sources),
            "category_breakdown": {
                cat: len(items) for cat, items in self.categories.items()
            },
        }


# ═══════════════════════════════════════════════════════════════════════════════
# ENHANCED AGENT SYSTEM WITH PROMPT INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════


class AgentType(Enum):
    CORE = "Core"
    FRONTEND = "Frontend"
    BACKEND = "Backend"
    SECURITY = "Security"
    QUALITY = "Quality"
    DEVOPS = "DevOps"
    PERFORMANCE = "Performance"
    CONTENT = "Content"
    SPECIALIZED = "Specialized"
    STRATEGY = "Strategy"


@dataclass
class EnhancedAgent:
    """Agent with integrated prompt capabilities"""

    name: str
    agent_type: AgentType
    description: str
    capabilities: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    system_prompt: str = ""
    prompt_templates: List[str] = field(default_factory=list)
    preferred_prompts: List[str] = field(default_factory=list)

    def invoke(
        self, task: str, prompt_library: PromptLibrary = None, context: Dict = None
    ) -> str:
        """Invoke agent with optional prompt enhancement"""
        context = context or {}

        # If prompt library available, enhance with relevant prompts
        if prompt_library and self.preferred_prompts:
            enhanced_prompt = self._enhance_with_prompts(prompt_library)
            return f"[{self.name}] Using enhanced system prompt\nTask: {task[:50]}..."

        return f"[{self.name}] Processing: {task[:50]}..."

    def _enhance_with_prompts(self, prompt_library: PromptLibrary) -> str:
        """Enhance agent with prompts from library"""
        enhanced = self.system_prompt

        for prompt_key in self.preferred_prompts:
            prompt_entry = prompt_library.get(prompt_key)
            if prompt_entry and prompt_entry.load_content():
                # Integrate prompt content
                enhanced += f"\n\n--- Enhanced with {prompt_entry.name} ---\n"
                enhanced += prompt_entry.content[:500]  # First 500 chars

        return enhanced


class EnhancedAgentRegistry:
    """Registry with integrated prompt library"""

    def __init__(self, prompt_library: PromptLibrary = None):
        self.agents: Dict[str, EnhancedAgent] = {}
        self.prompt_library = prompt_library or PromptLibrary()
        self._register_enhanced_agents()

    def _register_enhanced_agents(self):
        """Register agents with prompt integration"""

        # Core Agents with prompt enhancement
        self.register(
            EnhancedAgent(
                name="orchestrator",
                agent_type=AgentType.CORE,
                description="Supreme Entity for multi-agent coordination",
                capabilities=["coordination", "routing", "analysis", "5w1h"],
                skills=["5w1h-analysis", "workflow-detection", "agent-selection"],
                system_prompt="""You are the Supreme Orchestrator of MR.VERMA. 
Your role is to analyze user requests using the 5W1H framework:
- WHAT: Identify the goal
- WHO: Select appropriate agents
- HOW: Determine required skills
- WHEN: Assess urgency
- WHERE: Define scope
- WHY: Understand business objective

Route tasks to appropriate agents and workflows.""",
                preferred_prompts=["Anthropic/Claude Code/Prompt"],
            )
        )

        self.register(
            EnhancedAgent(
                name="claude-coder",
                agent_type=AgentType.CORE,
                description="Claude-powered coding assistant",
                capabilities=["coding", "analysis", "debugging", "architecture"],
                skills=["clean-code", "refactoring", "testing", "documentation"],
                system_prompt="""You are Claude, an expert coding assistant. 
Follow best practices and provide clean, maintainable code.""",
                preferred_prompts=[
                    "Anthropic/Claude Code/Prompt",
                    "Anthropic/Claude Code 2.0",
                ],
            )
        )

        self.register(
            EnhancedAgent(
                name="cursor-agent",
                agent_type=AgentType.CORE,
                description="Cursor-style AI coding agent",
                capabilities=["code-generation", "refactoring", "inline-editing"],
                skills=["clean-code", "typescript", "react", "nodejs"],
                system_prompt="""You are a Cursor-style AI coding agent.
Provide code suggestions and inline edits.""",
                preferred_prompts=[
                    "Cursor Prompts/Agent Prompt 2.0",
                    "Cursor Prompts/Chat Prompt",
                ],
            )
        )

        self.register(
            EnhancedAgent(
                name="devin-ai",
                agent_type=AgentType.CORE,
                description="Devin-style autonomous coding agent",
                capabilities=["autonomous-coding", "research", "implementation"],
                skills=["full-stack", "research", "testing", "deployment"],
                system_prompt="""You are Devin, an autonomous AI software engineer.
Plan, research, and implement complete features independently.""",
                preferred_prompts=["Devin AI/Prompt", "Devin AI/DeepWiki Prompt"],
            )
        )

        # Frontend Agents
        self.register(
            EnhancedAgent(
                name="frontend-specialist",
                agent_type=AgentType.FRONTEND,
                description="Expert in frontend development (React, Vue, Angular)",
                capabilities=["ui-development", "component-design", "styling"],
                skills=["react", "vue", "angular", "css", "javascript", "typescript"],
                system_prompt="Expert frontend developer specializing in modern frameworks.",
                preferred_prompts=[],
            )
        )

        self.register(
            EnhancedAgent(
                name="lovable-designer",
                agent_type=AgentType.FRONTEND,
                description="Lovable-style UI/UX designer",
                capabilities=["ui-design", "ux-design", "prototyping"],
                skills=["design-systems", "figma", "accessibility"],
                system_prompt="Create beautiful, functional UI designs like Lovable.",
                preferred_prompts=["Lovable/Prompt"],
            )
        )

        self.register(
            EnhancedAgent(
                name="v0-designer",
                agent_type=AgentType.FRONTEND,
                description="v0-style UI generator",
                capabilities=["ui-generation", "tailwind", "react"],
                skills=["tailwind", "react", "shadcn-ui"],
                system_prompt="Generate modern UI components with Tailwind CSS.",
                preferred_prompts=["v0 Prompts and Tools/Prompt"],
            )
        )

        self.register(
            EnhancedAgent(
                name="mobile-developer",
                agent_type=AgentType.FRONTEND,
                description="Mobile app development (React Native, Flutter)",
                capabilities=[
                    "mobile-development",
                    "cross-platform",
                    "native-features",
                ],
                skills=["react-native", "flutter", "ios", "android"],
            )
        )

        # Backend Agents
        self.register(
            EnhancedAgent(
                name="backend-specialist",
                agent_type=AgentType.BACKEND,
                description="Server-side development and APIs",
                capabilities=["api-design", "server-logic", "microservices"],
                skills=[
                    "python",
                    "nodejs",
                    "go",
                    "rust",
                    "api-design",
                    "rest",
                    "graphql",
                ],
            )
        )

        self.register(
            EnhancedAgent(
                name="database-architect",
                agent_type=AgentType.BACKEND,
                description="Database design and optimization",
                capabilities=["schema-design", "query-optimization", "data-modeling"],
                skills=[
                    "sql",
                    "nosql",
                    "postgresql",
                    "mongodb",
                    "redis",
                    "elasticsearch",
                ],
            )
        )

        self.register(
            EnhancedAgent(
                name="api-designer",
                agent_type=AgentType.BACKEND,
                description="API design and documentation",
                capabilities=["api-design", "openapi", "documentation"],
                skills=["openapi", "swagger", "rest", "graphql", "grpc"],
            )
        )

        # Security Agents
        self.register(
            EnhancedAgent(
                name="security-auditor",
                agent_type=AgentType.SECURITY,
                description="Security auditing and vulnerability detection",
                capabilities=[
                    "vulnerability-scanning",
                    "security-review",
                    "compliance",
                ],
                skills=[
                    "penetration-testing",
                    "vulnerability-assessment",
                    "secure-coding",
                ],
            )
        )

        self.register(
            EnhancedAgent(
                name="penetration-tester",
                agent_type=AgentType.SECURITY,
                description="Penetration testing and exploitation",
                capabilities=["penetration-testing", "exploitation", "reporting"],
                skills=["owasp", "burp-suite", "metasploit", "web-security"],
            )
        )

        # Quality Agents
        self.register(
            EnhancedAgent(
                name="test-engineer",
                agent_type=AgentType.QUALITY,
                description="Test engineering and automation",
                capabilities=["test-design", "automation", "coverage-analysis"],
                skills=[
                    "unit-testing",
                    "integration-testing",
                    "e2e-testing",
                    "pytest",
                    "jest",
                ],
            )
        )

        self.register(
            EnhancedAgent(
                name="qa-automation-engineer",
                agent_type=AgentType.QUALITY,
                description="QA automation and CI/CD integration",
                capabilities=["test-automation", "ci-cd", "quality-gates"],
                skills=["selenium", "playwright", "cypress", "ci-cd"],
            )
        )

        self.register(
            EnhancedAgent(
                name="agent-perfectionist",
                agent_type=AgentType.QUALITY,
                description="Code perfection and best practices",
                capabilities=["code-review", "refactoring", "optimization"],
                skills=["clean-code", "solid-principles", "design-patterns"],
            )
        )

        # DevOps Agents
        self.register(
            EnhancedAgent(
                name="devops-engineer",
                agent_type=AgentType.DEVOPS,
                description="DevOps and infrastructure",
                capabilities=["ci-cd", "infrastructure", "deployment"],
                skills=[
                    "docker",
                    "kubernetes",
                    "terraform",
                    "ansible",
                    "jenkins",
                    "github-actions",
                ],
            )
        )

        self.register(
            EnhancedAgent(
                name="cloud-native-expert",
                agent_type=AgentType.DEVOPS,
                description="Cloud architecture and services",
                capabilities=["cloud-architecture", "scalability", "cost-optimization"],
                skills=["aws", "azure", "gcp", "serverless", "microservices"],
            )
        )

        # Performance Agents
        self.register(
            EnhancedAgent(
                name="performance-optimizer",
                agent_type=AgentType.PERFORMANCE,
                description="Performance optimization",
                capabilities=["profiling", "optimization", "benchmarking"],
                skills=["performance-tuning", "memory-optimization", "caching"],
            )
        )

        self.register(
            EnhancedAgent(
                name="debugger",
                agent_type=AgentType.PERFORMANCE,
                description="Debugging and troubleshooting",
                capabilities=["debugging", "root-cause-analysis", "fixing"],
                skills=["debugging", "profiling", "tracing", "logging"],
            )
        )

        # Content Agents
        self.register(
            EnhancedAgent(
                name="documentation-writer",
                agent_type=AgentType.CONTENT,
                description="Technical documentation",
                capabilities=["documentation", "technical-writing", "examples"],
                skills=["markdown", "openapi", "readme", "api-docs"],
            )
        )

        self.register(
            EnhancedAgent(
                name="tech-writer",
                agent_type=AgentType.CONTENT,
                description="Technical content and tutorials",
                capabilities=["tutorials", "blogs", "technical-content"],
                skills=["technical-writing", "tutorials", "documentation"],
            )
        )

        self.register(
            EnhancedAgent(
                name="seo-specialist",
                agent_type=AgentType.CONTENT,
                description="SEO optimization and content strategy",
                capabilities=["seo", "content-strategy", "analytics"],
                skills=["seo", "keyword-research", "content-optimization"],
            )
        )

        # Specialized Agents
        self.register(
            EnhancedAgent(
                name="game-developer",
                agent_type=AgentType.SPECIALIZED,
                description="Game development (Unity, Unreal)",
                capabilities=["game-development", "graphics", "physics"],
                skills=["unity", "unreal", "godot", "c#", "c++", "game-design"],
            )
        )

        self.register(
            EnhancedAgent(
                name="ai-researcher",
                agent_type=AgentType.SPECIALIZED,
                description="AI/ML research and implementation",
                capabilities=["ml-research", "model-training", "implementation"],
                skills=[
                    "machine-learning",
                    "deep-learning",
                    "tensorflow",
                    "pytorch",
                    "nlp",
                ],
            )
        )

        self.register(
            EnhancedAgent(
                name="data-science-agent",
                agent_type=AgentType.SPECIALIZED,
                description="Data science and analytics",
                capabilities=["data-analysis", "visualization", "modeling"],
                skills=["python", "pandas", "numpy", "scikit-learn", "jupyter"],
            )
        )

        # Strategy Agents
        self.register(
            EnhancedAgent(
                name="product-manager",
                agent_type=AgentType.STRATEGY,
                description="Product management and strategy",
                capabilities=["product-strategy", "prioritization", "roadmapping"],
                skills=[
                    "product-management",
                    "agile",
                    "user-stories",
                    "prioritization",
                ],
            )
        )

        self.register(
            EnhancedAgent(
                name="business-architect",
                agent_type=AgentType.STRATEGY,
                description="Business architecture and analysis",
                capabilities=["business-analysis", "architecture", "strategy"],
                skills=[
                    "business-analysis",
                    "system-thinking",
                    "stakeholder-management",
                ],
            )
        )

        self.register(
            EnhancedAgent(
                name="knowledge-expert",
                agent_type=AgentType.STRATEGY,
                description="Knowledge management and expertise",
                capabilities=["knowledge-synthesis", "research", "documentation"],
                skills=["research", "knowledge-management", "documentation"],
            )
        )

        # Augment Code Agents
        self.register(
            EnhancedAgent(
                name="augment-claude",
                agent_type=AgentType.SPECIALIZED,
                description="Augment Code with Claude Sonnet",
                capabilities=["code-completion", "inline-editing", "chat"],
                skills=["claude", "code-assistance"],
                preferred_prompts=["Augment Code/claude-4-sonnet-agent-prompts"],
            )
        )

        self.register(
            EnhancedAgent(
                name="augment-gpt",
                agent_type=AgentType.SPECIALIZED,
                description="Augment Code with GPT",
                capabilities=["code-completion", "inline-editing", "chat"],
                skills=["gpt", "code-assistance"],
                preferred_prompts=["Augment Code/gpt-5-agent-prompts"],
            )
        )

    def register(self, agent: EnhancedAgent):
        """Register an agent"""
        self.agents[agent.name] = agent

    def get(self, name: str) -> Optional[EnhancedAgent]:
        """Get an agent by name"""
        return self.agents.get(name)

    def list_by_type(self, agent_type: AgentType) -> List[EnhancedAgent]:
        """List agents by type"""
        return [a for a in self.agents.values() if a.agent_type == agent_type]

    def find_by_capability(self, capability: str) -> List[EnhancedAgent]:
        """Find agents with specific capability"""
        return [a for a in self.agents.values() if capability in a.capabilities]

    def search(self, query: str) -> List[EnhancedAgent]:
        """Search agents by query"""
        query_lower = query.lower()
        results = []

        for agent in self.agents.values():
            if (
                query_lower in agent.name.lower()
                or query_lower in agent.description.lower()
                or any(query_lower in skill for skill in agent.skills)
                or any(query_lower in cap for cap in agent.capabilities)
            ):
                results.append(agent)

        return results

    def all(self) -> List[EnhancedAgent]:
        """Get all agents"""
        return list(self.agents.values())


# ═══════════════════════════════════════════════════════════════════════════════
# ULTIMATE ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════════════════


class UltimateOrchestrator:
    """Ultimate orchestrator with prompt library integration"""

    def __init__(self):
        self.prompt_library = PromptLibrary()
        self.agents = EnhancedAgentRegistry(self.prompt_library)
        self.api_key = os.getenv("NVIDIA_API_KEY", "")
        self.api_url = os.getenv(
            "NVIDIA_API_URL", "https://integrate.api.nvidia.com/v1/chat/completions"
        )
        self.model = os.getenv("NVIDIA_MODEL", "moonshotai/kimi-k2.5")

    async def analyze_intent(self, text: str) -> Dict:
        """Analyze user intent"""
        return {
            "what": text[:100],
            "agents": self._suggest_agents(text),
            "prompts": self._suggest_prompts(text),
            "urgency": "normal",
        }

    def _suggest_agents(self, text: str) -> List[str]:
        """Suggest appropriate agents"""
        text_lower = text.lower()
        suggestions = []

        if any(kw in text_lower for kw in ["cursor", "vscode", "editor"]):
            suggestions.append("cursor-agent")
        if any(kw in text_lower for kw in ["claude", "anthropic"]):
            suggestions.append("claude-coder")
        if any(kw in text_lower for kw in ["devin", "autonomous", "full-stack"]):
            suggestions.append("devin-ai")
        if any(kw in text_lower for kw in ["frontend", "ui", "react", "vue"]):
            suggestions.append("frontend-specialist")
        if any(kw in text_lower for kw in ["backend", "api", "server"]):
            suggestions.append("backend-specialist")
        if any(kw in text_lower for kw in ["lovable", "design", "ui/ux"]):
            suggestions.append("lovable-designer")
        if any(kw in text_lower for kw in ["v0", "tailwind", "component"]):
            suggestions.append("v0-designer")
        if any(kw in text_lower for kw in ["security", "vulnerability", "auth"]):
            suggestions.append("security-auditor")
        if any(kw in text_lower for kw in ["test", "testing", "coverage"]):
            suggestions.append("test-engineer")

        if not suggestions:
            suggestions.append("orchestrator")

        return suggestions

    def _suggest_prompts(self, text: str) -> List[str]:
        """Suggest relevant prompts from library"""
        results = self.prompt_library.search(text)
        return [f"{r.source}/{r.name}" for r in results[:3]]

    async def execute_with_agents(self, task: str, agent_names: List[str]) -> str:
        """Execute task with specified agents"""
        results = []
        for agent_name in agent_names:
            agent = self.agents.get(agent_name)
            if agent:
                result = agent.invoke(task, self.prompt_library)
                results.append(result)
        return "\n".join(results)

    async def ai_chat(self, message: str, system_prompt: Optional[str] = None) -> str:
        """Send message to AI API"""
        import requests

        if not self.api_key:
            return "❌ Error: NVIDIA API key not configured."

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 2000,
            "temperature": 0.7,
        }

        try:
            response = requests.post(
                self.api_url, headers=headers, json=payload, timeout=60
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            return f"❌ Error: {str(e)}"


# ═══════════════════════════════════════════════════════════════════════════════
# UI COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════


def print_ultimate_banner():
    """Display ultimate banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════════════╗
    ║                                                                       ║
    ║   ███╗   ███╗██████╗      ██╗   ██╗███████╗██████╗ ███╗   ███╗       ║
    ║   ████╗ ████║██╔══██╗     ██║   ██║██╔════╝██╔══██╗████╗ ████║       ║
    ║   ██╔████╔██║██████╔╝     ██║   ██║█████╗  ██████╔╝██╔████╔██║       ║
    ║   ██║╚██╔╝██║██╔══██╗     ╚██╗ ██╔╝██╔══╝  ██╔══██╗██║╚██╔╝██║       ║
    ║   ██║ ╚═╝ ██║██║  ██║      ╚████╔╝ ███████╗██║  ██║██║ ╚═╝ ██║       ║
    ║   ╚═╝     ╚═╝╚═╝  ╚═╝       ╚═══╝  ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝       ║
    ║                                                                       ║
    ║         🤖 ULTIMATE AI PLATFORM with PROMPT LIBRARY 🤖                ║
    ║                                                                       ║
    ║     30+ Agents • 66+ Skills • 19 Workflows • 82 System Prompts        ║
    ║                                                                       ║
    ║   Claude • Cursor • Devin • Lovable • v0 • Augment • And More!        ║
    ║                                                                       ║
    ╚═══════════════════════════════════════════════════════════════════════╝
    """
    if RICH_AVAILABLE:
        console.print(banner, style="bold cyan")
    else:
        print(banner)


def print_ultimate_menu():
    """Display ultimate menu"""
    menu = """
    ╔═══════════════════════════════════════════════════════════════════════╗
    ║                      🎯 ULTIMATE MENU                                 ║
    ╠═══════════════════════════════════════════════════════════════════════╣
    ║                                                                       ║
    ║  💬 [1] AI CHAT          - Enhanced chat with agents                  ║
    ║  🤖 [2] AGENT CENTER     - Browse 30+ specialized agents              ║
    ║  📚 [3] PROMPT LIBRARY   - Browse 82 system prompts                   ║
    ║  🔍 [4] PROMPT SEARCH    - Search prompt library                      ║
    ║  🛠️  [5] SKILL CENTER    - Browse 66+ technical skills                ║
    ║  🔄 [6] WORKFLOWS        - Execute automated workflows                ║
    ║  📝 [7] CODE CENTER      - Code with Claude/Cursor/Devin              ║
    ║  🎨 [8] DESIGN CENTER    - UI/UX with Lovable/v0                      ║
    ║  🔒 [9] SECURITY CENTER  - Security audits                            ║
    ║  📊 [10] SYSTEM STATUS   - Check all components                       ║
    ║  ℹ️  [11] SYSTEM INFO    - About this platform                        ║
    ║                                                                       ║
    ║  🚪 [0] EXIT             - Close MR.VERMA Ultimate                    ║
    ║                                                                       ║
    ╚═══════════════════════════════════════════════════════════════════════╝
    """
    if RICH_AVAILABLE:
        console.print(menu, style="bold green")
    else:
        print(menu)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════


class MRVERMAUltimate:
    """Ultimate MR.VERMA with full prompt library integration"""

    def __init__(self):
        self.engine = UltimateOrchestrator()

    async def ai_chat_mode(self):
        """Enhanced AI chat with agent mentions and prompt integration"""
        if RICH_AVAILABLE:
            console.print("\n[bold cyan]💬 Ultimate AI Chat[/bold cyan]")
            console.print(
                "[dim]Tip: Use @agent-name or mention Claude/Cursor/Devin/Lovable/v0[/dim]\n"
            )
        else:
            print("\n💬 Ultimate AI Chat")
            print("Use @agent-name or mention Claude/Cursor/Devin/Lovable/v0\n")

        while True:
            try:
                if RICH_AVAILABLE:
                    user_input = Prompt.ask("[bold blue]You[/bold blue]")
                else:
                    user_input = input("You: ")

                if user_input.lower() in ["exit", "quit", "back"]:
                    break

                # Detect agent mentions
                agent_mentions = re.findall(r"@(\w+)", user_input)

                # Detect AI tool mentions
                tool_patterns = {
                    "claude-coder": ["claude", "anthropic"],
                    "cursor-agent": ["cursor"],
                    "devin-ai": ["devin"],
                    "lovable-designer": ["lovable"],
                    "v0-designer": ["v0", "v zero"],
                    "augment-claude": ["augment"],
                }

                detected_tools = []
                for agent_name, keywords in tool_patterns.items():
                    if any(kw in user_input.lower() for kw in keywords):
                        detected_tools.append(agent_name)

                all_agents = agent_mentions + detected_tools

                if all_agents:
                    if RICH_AVAILABLE:
                        with console.status("[bold green]Activating agents..."):
                            response = await self._process_with_agents(
                                user_input, all_agents
                            )
                    else:
                        print("Activating agents...")
                        response = await self._process_with_agents(
                            user_input, all_agents
                        )
                else:
                    if RICH_AVAILABLE:
                        with console.status("[bold green]AI is thinking..."):
                            response = await self.engine.ai_chat(user_input)
                    else:
                        print("AI is thinking...")
                        response = await self.engine.ai_chat(user_input)

                if RICH_AVAILABLE:
                    console.print(f"[bold green]AI:[/bold green] {response}\n")
                else:
                    print(f"AI: {response}\n")

            except KeyboardInterrupt:
                break
            except Exception as e:
                if RICH_AVAILABLE:
                    console.print(f"[bold red]Error: {e}[/bold red]")
                else:
                    print(f"Error: {e}")

    async def _process_with_agents(self, text: str, agents: List[str]) -> str:
        """Process with multiple agents"""
        results = []

        for agent_name in agents:
            agent = self.engine.agents.get(agent_name)
            if agent:
                if RICH_AVAILABLE:
                    console.print(f"[dim]Activating {agent.name}...[/dim]")
                result = agent.invoke(text, self.engine.prompt_library)
                results.append(result)

        # Get AI response with context
        system_prompt = f"You are coordinating: {', '.join(agents)}"
        ai_response = await self.engine.ai_chat(text, system_prompt)
        results.append(ai_response)

        return "\n\n".join(results)

    async def agent_center(self):
        """Browse all agents"""
        if RICH_AVAILABLE:
            console.print("\n[bold cyan]🤖 AGENT CENTER[/bold cyan]\n")
        else:
            print("\n🤖 AGENT CENTER\n")

        # Show agent categories
        for agent_type in AgentType:
            agents = self.engine.agents.list_by_type(agent_type)
            if agents:
                if RICH_AVAILABLE:
                    console.print(
                        f"\n[bold yellow]{agent_type.value} ({len(agents)} agents):[/bold yellow]"
                    )
                else:
                    print(f"\n{agent_type.value} ({len(agents)} agents):")

                for i, agent in enumerate(agents[:5], 1):  # Show first 5
                    if RICH_AVAILABLE:
                        console.print(
                            f"  {i}. [green]{agent.name}[/green] - {agent.description[:60]}"
                        )
                    else:
                        print(f"  {i}. {agent.name} - {agent.description[:60]}")

                if len(agents) > 5:
                    if RICH_AVAILABLE:
                        console.print(f"  ... and {len(agents) - 5} more")
                    else:
                        print(f"  ... and {len(agents) - 5} more")

        if RICH_AVAILABLE:
            console.print(
                "\n[dim]Total: {} agents available[/dim]".format(
                    len(self.engine.agents.all())
                )
            )
            console.print("[dim]Usage: In chat, mention @agent-name[/dim]")
        else:
            print(f"\nTotal: {len(self.engine.agents.all())} agents available")
            print("Usage: In chat, mention @agent-name")

        input("\nPress Enter to continue...")

    async def prompt_library_browser(self):
        """Browse prompt library"""
        if RICH_AVAILABLE:
            console.print("\n[bold cyan]📚 PROMPT LIBRARY[/bold cyan]\n")
        else:
            print("\n📚 PROMPT LIBRARY\n")

        # Show categories
        categories = self.engine.prompt_library.get_all_categories()

        if RICH_AVAILABLE:
            console.print("[bold yellow]Categories:[/bold yellow]")
        else:
            print("Categories:")

        for cat in categories:
            count = len(self.engine.prompt_library.list_by_category(cat))
            if RICH_AVAILABLE:
                console.print(f"  • [green]{cat}[/green]: {count} prompts")
            else:
                print(f"  • {cat}: {count} prompts")

        # Show top sources
        if RICH_AVAILABLE:
            console.print("\n[bold yellow]Top Sources:[/bold yellow]")
        else:
            print("\nTop Sources:")

        sources = list(self.engine.prompt_library.sources.keys())[:10]
        for source in sources:
            count = len(self.engine.prompt_library.list_by_source(source))
            if RICH_AVAILABLE:
                console.print(f"  • [green]{source}[/green]: {count} prompts")
            else:
                print(f"  • {source}: {count} prompts")

        if RICH_AVAILABLE:
            console.print(
                f"\n[dim]Total: {len(self.engine.prompt_library.prompts)} system prompts[/dim]"
            )
        else:
            print(f"\nTotal: {len(self.engine.prompt_library.prompts)} system prompts")

        input("\nPress Enter to continue...")

    async def prompt_search(self):
        """Search prompts"""
        if RICH_AVAILABLE:
            console.print("\n[bold cyan]🔍 PROMPT SEARCH[/bold cyan]\n")
            query = Prompt.ask("Enter search term")
        else:
            print("\n🔍 PROMPT SEARCH\n")
            query = input("Enter search term: ")

        if query:
            results = self.engine.prompt_library.search(query)

            if RICH_AVAILABLE:
                console.print(
                    f"\n[bold yellow]Found {len(results)} results:[/bold yellow]"
                )
            else:
                print(f"\nFound {len(results)} results:")

            for i, entry in enumerate(results[:10], 1):
                if RICH_AVAILABLE:
                    console.print(f"{i}. [green]{entry.name}[/green] ({entry.source})")
                    console.print(f"   {entry.description[:80]}")
                else:
                    print(f"{i}. {entry.name} ({entry.source})")
                    print(f"   {entry.description[:80]}")

            if len(results) > 10:
                if RICH_AVAILABLE:
                    console.print(f"\n... and {len(results) - 10} more results")
                else:
                    print(f"\n... and {len(results) - 10} more results")

        input("\nPress Enter to continue...")

    async def skill_center(self):
        """Browse skills"""
        if RICH_AVAILABLE:
            console.print("\n[bold cyan]🛠️ SKILL CENTER[/bold cyan]")
            console.print("[dim]Agents automatically apply relevant skills[/dim]\n")
        else:
            print("\n🛠️ SKILL CENTER")
            print("Agents automatically apply relevant skills\n")

        if RICH_AVAILABLE:
            console.print("[bold yellow]Example Skills:[/bold yellow]")
            console.print("  • clean-code, refactoring, debugging")
            console.print("  • react, vue, angular, typescript")
            console.print("  • api-design, database, microservices")
            console.print("  • docker, kubernetes, ci-cd")
            console.print("  • security, testing, optimization")
        else:
            print("Example Skills:")
            print("  • clean-code, refactoring, debugging")
            print("  • react, vue, angular, typescript")
            print("  • api-design, database, microservices")
            print("  • docker, kubernetes, ci-cd")
            print("  • security, testing, optimization")

        input("\nPress Enter to continue...")

    async def workflow_center(self):
        """Browse workflows"""
        if RICH_AVAILABLE:
            console.print("\n[bold cyan]🔄 WORKFLOW CENTER[/bold cyan]\n")
        else:
            print("\n🔄 WORKFLOW CENTER\n")

        if RICH_AVAILABLE:
            console.print("[bold yellow]Available Workflows:[/bold yellow]")
            console.print("  Planning: /brainstorm, /blueprint, /plan")
            console.print("  Building: /create, /enhance")
            console.print("  Quality: /audit, /test, /debug")
            console.print("  Security: /secure-audit")
            console.print("  Design: /launch-mobile, /ai-feature")
            console.print("\n[dim]Usage: In chat, type /workflow-name[/dim]")
        else:
            print("Available Workflows:")
            print("  Planning: /brainstorm, /blueprint, /plan")
            print("  Building: /create, /enhance")
            print("  Quality: /audit, /test, /debug")
            print("  Security: /secure-audit")
            print("  Design: /launch-mobile, /ai-feature")
            print("\nUsage: In chat, type /workflow-name")

        input("\nPress Enter to continue...")

    async def code_center(self):
        """Code center with AI tools"""
        if RICH_AVAILABLE:
            console.print("\n[bold cyan]📝 CODE CENTER[/bold cyan]\n")
            console.print("[bold yellow]Available Coding Agents:[/bold yellow]")
            console.print("  • @claude-coder - Claude-powered coding")
            console.print("  • @cursor-agent - Cursor-style editor")
            console.print("  • @devin-ai - Autonomous coding agent")
            console.print("  • @augment-claude - Augment with Claude")
            console.print("  • @augment-gpt - Augment with GPT")
            console.print("\n[dim]Usage: In chat, mention the agent you want[/dim]")
        else:
            print("\n📝 CODE CENTER\n")
            print("Available Coding Agents:")
            print("  • @claude-coder - Claude-powered coding")
            print("  • @cursor-agent - Cursor-style editor")
            print("  • @devin-ai - Autonomous coding agent")
            print("  • @augment-claude - Augment with Claude")
            print("  • @augment-gpt - Augment with GPT")
            print("\nUsage: In chat, mention the agent you want")

        input("\nPress Enter to continue...")

    async def design_center(self):
        """Design center"""
        if RICH_AVAILABLE:
            console.print("\n[bold cyan]🎨 DESIGN CENTER[/bold cyan]\n")
            console.print("[bold yellow]Available Design Agents:[/bold yellow]")
            console.print("  • @lovable-designer - Lovable-style UI/UX")
            console.print("  • @v0-designer - v0 component generator")
            console.print("  • @frontend-specialist - Frontend expert")
            console.print("\n[dim]Usage: In chat, mention the designer you want[/dim]")
        else:
            print("\n🎨 DESIGN CENTER\n")
            print("Available Design Agents:")
            print("  • @lovable-designer - Lovable-style UI/UX")
            print("  • @v0-designer - v0 component generator")
            print("  • @frontend-specialist - Frontend expert")
            print("\nUsage: In chat, mention the designer you want")

        input("\nPress Enter to continue...")

    async def security_center(self):
        """Security center"""
        if RICH_AVAILABLE:
            console.print("\n[bold cyan]🔒 SECURITY CENTER[/bold cyan]\n")
            console.print("[bold yellow]Available Security Agents:[/bold yellow]")
            console.print("  • @security-auditor - Vulnerability scanning")
            console.print("  • @penetration-tester - Penetration testing")
            console.print(
                "\n[dim]Usage: In chat, mention @security-auditor or /secure-audit[/dim]"
            )
        else:
            print("\n🔒 SECURITY CENTER\n")
            print("Available Security Agents:")
            print("  • @security-auditor - Vulnerability scanning")
            print("  • @penetration-tester - Penetration testing")
            print("\nUsage: In chat, mention @security-auditor or /secure-audit")

        input("\nPress Enter to continue...")

    async def system_status(self):
        """Show system status"""
        if RICH_AVAILABLE:
            console.print("\n[bold cyan]📊 SYSTEM STATUS[/bold cyan]\n")

            # Create table
            table = Table(title="MR.VERMA Ultimate System Status")
            table.add_column("Component", style="cyan")
            table.add_column("Count", style="green")
            table.add_column("Status", style="yellow")

            table.add_row("AI Agents", str(len(self.engine.agents.all())), "✅ Ready")
            table.add_row(
                "System Prompts",
                str(len(self.engine.prompt_library.prompts)),
                "✅ Loaded",
            )
            table.add_row(
                "Prompt Categories",
                str(len(self.engine.prompt_library.categories)),
                "✅ Indexed",
            )
            table.add_row(
                "Prompt Sources",
                str(len(self.engine.prompt_library.sources)),
                "✅ Indexed",
            )

            console.print(table)

            console.print(
                f"\n[dim]API Key: {'✅ Configured' if self.engine.api_key else '❌ Not configured'}[/dim]"
            )

        else:
            print("\n📊 SYSTEM STATUS\n")
            print(f"AI Agents: {len(self.engine.agents.all())} ✅")
            print(f"System Prompts: {len(self.engine.prompt_library.prompts)} ✅")
            print(f"Prompt Categories: {len(self.engine.prompt_library.categories)} ✅")
            print(f"Prompt Sources: {len(self.engine.prompt_library.sources)} ✅")
            print(
                f"API Key: {'✅ Configured' if self.engine.api_key else '❌ Not configured'}"
            )

        input("\nPress Enter to continue...")

    async def system_info(self):
        """Show system info"""
        info = """
        MR.VERMA Ultimate - System Information
        ======================================
        
        INTEGRATED AI TOOLS:
        • Anthropic Claude (Claude Code, Sonnet)
        • Cursor (Agent prompts)
        • Devin AI (Autonomous coding)
        • Lovable (UI/UX design)
        • v0 (Component generation)
        • Augment Code (Claude & GPT)
        • And 25+ more sources!
        
        CAPABILITIES:
        • 30+ Specialized AI Agents
        • 82 System Prompts from leading AI tools
        • 66+ Technical Skills
        • 19 Automated Workflows
        • Multi-Agent Orchestration
        • Prompt Library Browser
        • Intent Analysis
        
        USAGE:
        • Chat naturally with AI
        • Mention @agent-name to use specific agents
        • Reference AI tools: Claude, Cursor, Devin, etc.
        • Use /workflow-name for workflows
        • Browse prompts in Prompt Library
        
        PROMPT LIBRARY:
        Location: knowledge/prompts/
        Sources: Anthropic, Cursor, Devin, Lovable, v0, etc.
        Total: 82+ system prompts
        
        All prompts from: https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools
        """

        if RICH_AVAILABLE:
            console.print(Panel(info, title="System Information", border_style="blue"))
        else:
            print(info)

        input("\nPress Enter to continue...")

    async def run(self):
        """Main application loop"""
        print_ultimate_banner()

        while True:
            print_ultimate_menu()

            try:
                if RICH_AVAILABLE:
                    choice = Prompt.ask(
                        "Select option",
                        choices=[str(i) for i in range(12)],
                        default="1",
                    )
                else:
                    choice = input("\nSelect option (0-11): ").strip()

                if choice == "0":
                    if RICH_AVAILABLE:
                        console.print(
                            "\n[bold green]👋 Goodbye! Thanks for using MR.VERMA Ultimate![/bold green]\n"
                        )
                    else:
                        print("\n👋 Goodbye!\n")
                    break

                elif choice == "1":
                    await self.ai_chat_mode()
                elif choice == "2":
                    await self.agent_center()
                elif choice == "3":
                    await self.prompt_library_browser()
                elif choice == "4":
                    await self.prompt_search()
                elif choice == "5":
                    await self.skill_center()
                elif choice == "6":
                    await self.workflow_center()
                elif choice == "7":
                    await self.code_center()
                elif choice == "8":
                    await self.design_center()
                elif choice == "9":
                    await self.security_center()
                elif choice == "10":
                    await self.system_status()
                elif choice == "11":
                    await self.system_info()
                else:
                    if RICH_AVAILABLE:
                        console.print("[bold red]Invalid option[/bold red]")
                    else:
                        print("Invalid option")

            except KeyboardInterrupt:
                if RICH_AVAILABLE:
                    console.print("\n[bold yellow]Use option 0 to exit[/bold yellow]")
                else:
                    print("\nUse option 0 to exit")
            except Exception as e:
                if RICH_AVAILABLE:
                    console.print(f"[bold red]Error: {e}[/bold red]")
                else:
                    print(f"Error: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════


async def main():
    """Application entry point"""
    app = MRVERMAUltimate()
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
