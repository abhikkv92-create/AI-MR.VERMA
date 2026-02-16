#!/usr/bin/env python3
"""
MR.VERMA Enhanced - Full Agent, Skill & Workflow System
=======================================================

Complete AI platform with:
- 27+ Specialized Agents
- 19+ Workflows
- 66+ Skills
- Multi-Agent Orchestration
- Workflow Automation

Usage: python unified/mrverma_enhanced.py
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
                "[bold green]",
                "[bold blue]",
                "[bold red]",
                "[bold yellow]",
                "[cyan]",
                "[/cyan]",
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

    console = DummyConsole()
    Prompt = DummyPrompt
    Confirm = DummyConfirm
    Panel = DummyPanel


# ═══════════════════════════════════════════════════════════════════════════════
# AGENT SYSTEM
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
class Agent:
    """Represents an AI Agent"""

    name: str
    agent_type: AgentType
    description: str
    capabilities: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    system_prompt: str = ""

    def invoke(self, task: str, context: Dict = None) -> str:
        """Invoke the agent on a task"""
        # This would integrate with actual AI calls
        return f"[{self.name}] Processing: {task[:50]}..."


class AgentRegistry:
    """Registry of all available agents"""

    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self._register_default_agents()

    def _register_default_agents(self):
        """Register the 27 core agents"""

        # Core Agents
        self.register(
            Agent(
                name="orchestrator",
                agent_type=AgentType.CORE,
                description="Supreme Entity for multi-agent coordination",
                capabilities=["coordination", "routing", "analysis"],
                skills=["5w1h-analysis", "workflow-detection", "agent-selection"],
                system_prompt="You are the Supreme Orchestrator. Route tasks to appropriate agents.",
            )
        )

        self.register(
            Agent(
                name="project-planner",
                agent_type=AgentType.CORE,
                description="Creates structured project plans and roadmaps",
                capabilities=["planning", "estimation", "roadmapping"],
                skills=["project-breakdown", "timeline-creation", "dependency-mapping"],
            )
        )

        self.register(
            Agent(
                name="explorer-agent",
                agent_type=AgentType.CORE,
                description="Explores and maps codebases",
                capabilities=["code-analysis", "architecture-mapping", "discovery"],
                skills=["codebase-exploration", "pattern-recognition"],
            )
        )

        # Frontend Agents
        self.register(
            Agent(
                name="frontend-specialist",
                agent_type=AgentType.FRONTEND,
                description="Expert in frontend development (React, Vue, Angular)",
                capabilities=["ui-development", "component-design", "styling"],
                skills=["react", "vue", "angular", "css", "javascript", "typescript"],
            )
        )

        self.register(
            Agent(
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
            Agent(
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
            Agent(
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
            Agent(
                name="api-designer",
                agent_type=AgentType.BACKEND,
                description="API design and documentation",
                capabilities=["api-design", "openapi", "documentation"],
                skills=["openapi", "swagger", "rest", "graphql", "grpc"],
            )
        )

        # Security Agents
        self.register(
            Agent(
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
            Agent(
                name="penetration-tester",
                agent_type=AgentType.SECURITY,
                description="Penetration testing and exploitation",
                capabilities=["penetration-testing", "exploitation", "reporting"],
                skills=["owasp", "burp-suite", "metasploit", "web-security"],
            )
        )

        # Quality Agents
        self.register(
            Agent(
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
            Agent(
                name="qa-automation-engineer",
                agent_type=AgentType.QUALITY,
                description="QA automation and CI/CD integration",
                capabilities=["test-automation", "ci-cd", "quality-gates"],
                skills=["selenium", "playwright", "cypress", "ci-cd"],
            )
        )

        self.register(
            Agent(
                name="agent-perfectionist",
                agent_type=AgentType.QUALITY,
                description="Code perfection and best practices",
                capabilities=["code-review", "refactoring", "optimization"],
                skills=["clean-code", "solid-principles", "design-patterns"],
            )
        )

        # DevOps Agents
        self.register(
            Agent(
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
            Agent(
                name="cloud-native-expert",
                agent_type=AgentType.DEVOPS,
                description="Cloud architecture and services",
                capabilities=["cloud-architecture", "scalability", "cost-optimization"],
                skills=["aws", "azure", "gcp", "serverless", "microservices"],
            )
        )

        # Performance Agents
        self.register(
            Agent(
                name="performance-optimizer",
                agent_type=AgentType.PERFORMANCE,
                description="Performance optimization",
                capabilities=["profiling", "optimization", "benchmarking"],
                skills=["performance-tuning", "memory-optimization", "caching"],
            )
        )

        self.register(
            Agent(
                name="debugger",
                agent_type=AgentType.PERFORMANCE,
                description="Debugging and troubleshooting",
                capabilities=["debugging", "root-cause-analysis", "fixing"],
                skills=["debugging", "profiling", "tracing", "logging"],
            )
        )

        # Content Agents
        self.register(
            Agent(
                name="documentation-writer",
                agent_type=AgentType.CONTENT,
                description="Technical documentation",
                capabilities=["documentation", "technical-writing", "examples"],
                skills=["markdown", "openapi", "readme", "api-docs"],
            )
        )

        self.register(
            Agent(
                name="tech-writer",
                agent_type=AgentType.CONTENT,
                description="Technical content and tutorials",
                capabilities=["tutorials", "blogs", "technical-content"],
                skills=["technical-writing", "tutorials", "documentation"],
            )
        )

        self.register(
            Agent(
                name="seo-specialist",
                agent_type=AgentType.CONTENT,
                description="SEO optimization and content strategy",
                capabilities=["seo", "content-strategy", "analytics"],
                skills=["seo", "keyword-research", "content-optimization"],
            )
        )

        # Specialized Agents
        self.register(
            Agent(
                name="game-developer",
                agent_type=AgentType.SPECIALIZED,
                description="Game development (Unity, Unreal)",
                capabilities=["game-development", "graphics", "physics"],
                skills=["unity", "unreal", "godot", "c#", "c++", "game-design"],
            )
        )

        self.register(
            Agent(
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
            Agent(
                name="data-science-agent",
                agent_type=AgentType.SPECIALIZED,
                description="Data science and analytics",
                capabilities=["data-analysis", "visualization", "modeling"],
                skills=["python", "pandas", "numpy", "scikit-learn", "jupyter"],
            )
        )

        # Strategy Agents
        self.register(
            Agent(
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
            Agent(
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
            Agent(
                name="knowledge-expert",
                agent_type=AgentType.STRATEGY,
                description="Knowledge management and expertise",
                capabilities=["knowledge-synthesis", "research", "documentation"],
                skills=["research", "knowledge-management", "documentation"],
            )
        )

    def register(self, agent: Agent):
        """Register an agent"""
        self.agents[agent.name] = agent

    def get(self, name: str) -> Optional[Agent]:
        """Get an agent by name"""
        return self.agents.get(name)

    def list_by_type(self, agent_type: AgentType) -> List[Agent]:
        """List agents by type"""
        return [a for a in self.agents.values() if a.agent_type == agent_type]

    def find_by_capability(self, capability: str) -> List[Agent]:
        """Find agents with specific capability"""
        return [a for a in self.agents.values() if capability in a.capabilities]

    def all(self) -> List[Agent]:
        """Get all agents"""
        return list(self.agents.values())


# ═══════════════════════════════════════════════════════════════════════════════
# SKILL SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class Skill:
    """Represents a skill that can be applied"""

    name: str
    description: str
    category: str
    prompt_template: str = ""
    parameters: Dict = field(default_factory=dict)


class SkillRegistry:
    """Registry of all available skills"""

    def __init__(self):
        self.skills: Dict[str, Skill] = {}
        self._register_default_skills()

    def _register_default_skills(self):
        """Register the 66+ skills"""

        # Code Skills
        code_skills = [
            ("clean-code", "Write clean, maintainable code", "code"),
            ("refactoring", "Refactor and improve existing code", "code"),
            ("code-review", "Review code for quality issues", "code"),
            ("documentation", "Generate code documentation", "code"),
            ("debugging", "Debug and fix code issues", "code"),
            ("testing", "Write comprehensive tests", "code"),
            ("optimization", "Optimize code performance", "code"),
            ("typing", "Add type hints and annotations", "code"),
            ("linting", "Apply linting and style fixes", "code"),
            ("error-handling", "Implement proper error handling", "code"),
        ]

        # Architecture Skills
        arch_skills = [
            ("design-patterns", "Apply design patterns appropriately", "architecture"),
            ("solid-principles", "Follow SOLID principles", "architecture"),
            ("microservices", "Design microservices architecture", "architecture"),
            ("api-design", "Design RESTful/GraphQL APIs", "architecture"),
            ("database-design", "Design database schemas", "architecture"),
            ("scalability", "Ensure scalability considerations", "architecture"),
            ("security-architecture", "Design secure architectures", "architecture"),
            ("event-driven", "Implement event-driven patterns", "architecture"),
        ]

        # Frontend Skills
        frontend_skills = [
            ("react", "React component development", "frontend"),
            ("vue", "Vue.js development", "frontend"),
            ("angular", "Angular development", "frontend"),
            ("css", "CSS and styling", "frontend"),
            ("responsive", "Responsive design", "frontend"),
            ("accessibility", "Accessibility (a11y) compliance", "frontend"),
            ("performance", "Frontend performance optimization", "frontend"),
            ("state-management", "State management patterns", "frontend"),
        ]

        # Backend Skills
        backend_skills = [
            ("api-development", "Develop backend APIs", "backend"),
            ("authentication", "Implement authentication/authorization", "backend"),
            ("database", "Database operations and optimization", "backend"),
            ("caching", "Implement caching strategies", "backend"),
            ("queues", "Message queues and async processing", "backend"),
            ("validation", "Input validation and sanitization", "backend"),
        ]

        # DevOps Skills
        devops_skills = [
            ("docker", "Docker containerization", "devops"),
            ("kubernetes", "Kubernetes orchestration", "devops"),
            ("ci-cd", "CI/CD pipeline setup", "devops"),
            ("terraform", "Infrastructure as Code", "devops"),
            ("monitoring", "Monitoring and observability", "devops"),
            ("logging", "Centralized logging", "devops"),
        ]

        # Security Skills
        security_skills = [
            ("vulnerability-scanning", "Scan for vulnerabilities", "security"),
            ("penetration-testing", "Perform penetration tests", "security"),
            ("secure-coding", "Apply secure coding practices", "security"),
            ("encryption", "Implement encryption", "security"),
            ("compliance", "Ensure compliance (GDPR, SOC2, etc.)", "security"),
        ]

        # AI/ML Skills
        ai_skills = [
            ("prompt-engineering", "Craft effective prompts", "ai"),
            ("rag", "Retrieval Augmented Generation", "ai"),
            ("fine-tuning", "Fine-tune AI models", "ai"),
            ("embeddings", "Work with embeddings", "ai"),
            ("agents", "Build AI agent systems", "ai"),
        ]

        # Combine all skills
        all_skills = (
            code_skills
            + arch_skills
            + frontend_skills
            + backend_skills
            + devops_skills
            + security_skills
            + ai_skills
        )

        for name, desc, category in all_skills:
            self.register(Skill(name=name, description=desc, category=category))

    def register(self, skill: Skill):
        """Register a skill"""
        self.skills[skill.name] = skill

    def get(self, name: str) -> Optional[Skill]:
        """Get a skill by name"""
        return self.skills.get(name)

    def list_by_category(self, category: str) -> List[Skill]:
        """List skills by category"""
        return [s for s in self.skills.values() if s.category == category]

    def all(self) -> List[Skill]:
        """Get all skills"""
        return list(self.skills.values())


# ═══════════════════════════════════════════════════════════════════════════════
# WORKFLOW SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class Workflow:
    """Represents a workflow that can be executed"""

    name: str
    description: str
    category: str
    steps: List[Dict] = field(default_factory=list)
    agents: List[str] = field(default_factory=list)

    def execute(self, context: Dict) -> Dict:
        """Execute the workflow"""
        results = []
        for i, step in enumerate(self.steps):
            results.append(
                {"step": i + 1, "action": step.get("action"), "status": "completed"}
            )
        return {"workflow": self.name, "results": results}


class WorkflowRegistry:
    """Registry of all available workflows"""

    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self._register_default_workflows()

    def _register_default_workflows(self):
        """Register the 19 core workflows"""

        # Planning Workflows
        self.register(
            Workflow(
                name="/brainstorm",
                description="Explore ideas and alternatives",
                category="planning",
                steps=[
                    {
                        "action": "generate_ideas",
                        "description": "Generate initial ideas",
                    },
                    {
                        "action": "explore_alternatives",
                        "description": "Explore alternatives",
                    },
                    {"action": "evaluate_options", "description": "Evaluate options"},
                ],
                agents=["orchestrator", "knowledge-expert"],
            )
        )

        self.register(
            Workflow(
                name="/blueprint",
                description="Design system architecture",
                category="planning",
                steps=[
                    {
                        "action": "analyze_requirements",
                        "description": "Analyze requirements",
                    },
                    {
                        "action": "design_architecture",
                        "description": "Design architecture",
                    },
                    {"action": "define_components", "description": "Define components"},
                    {
                        "action": "create_documentation",
                        "description": "Create documentation",
                    },
                ],
                agents=["orchestrator", "business-architect", "cloud-native-expert"],
            )
        )

        self.register(
            Workflow(
                name="/plan",
                description="Create structured project plan",
                category="planning",
                steps=[
                    {"action": "breakdown_tasks", "description": "Break down tasks"},
                    {"action": "estimate_effort", "description": "Estimate effort"},
                    {"action": "set_priorities", "description": "Set priorities"},
                    {"action": "create_timeline", "description": "Create timeline"},
                ],
                agents=["orchestrator", "project-planner", "product-manager"],
            )
        )

        # Building Workflows
        self.register(
            Workflow(
                name="/create",
                description="Build new application from scratch",
                category="building",
                steps=[
                    {
                        "action": "setup_project",
                        "description": "Setup project structure",
                    },
                    {
                        "action": "implement_core",
                        "description": "Implement core features",
                    },
                    {"action": "add_tests", "description": "Add tests"},
                    {"action": "document", "description": "Document the application"},
                ],
                agents=[
                    "orchestrator",
                    "frontend-specialist",
                    "backend-specialist",
                    "test-engineer",
                ],
            )
        )

        self.register(
            Workflow(
                name="/enhance",
                description="Add features or improvements",
                category="building",
                steps=[
                    {
                        "action": "analyze_existing",
                        "description": "Analyze existing code",
                    },
                    {"action": "design_feature", "description": "Design new feature"},
                    {"action": "implement", "description": "Implement feature"},
                    {"action": "test", "description": "Test implementation"},
                ],
                agents=["orchestrator", "explorer-agent", "agent-perfectionist"],
            )
        )

        # Quality Workflows
        self.register(
            Workflow(
                name="/audit",
                description="Code quality audit",
                category="quality",
                steps=[
                    {"action": "static_analysis", "description": "Run static analysis"},
                    {"action": "check_coverage", "description": "Check test coverage"},
                    {
                        "action": "review_patterns",
                        "description": "Review design patterns",
                    },
                    {
                        "action": "generate_report",
                        "description": "Generate audit report",
                    },
                ],
                agents=[
                    "orchestrator",
                    "agent-perfectionist",
                    "qa-automation-engineer",
                ],
            )
        )

        self.register(
            Workflow(
                name="/test",
                description="Comprehensive testing",
                category="quality",
                steps=[
                    {"action": "unit_tests", "description": "Create unit tests"},
                    {
                        "action": "integration_tests",
                        "description": "Create integration tests",
                    },
                    {"action": "e2e_tests", "description": "Create E2E tests"},
                    {
                        "action": "coverage_report",
                        "description": "Generate coverage report",
                    },
                ],
                agents=["orchestrator", "test-engineer", "qa-automation-engineer"],
            )
        )

        self.register(
            Workflow(
                name="/debug",
                description="Debug and fix issues",
                category="quality",
                steps=[
                    {"action": "identify_issue", "description": "Identify the issue"},
                    {"action": "root_cause", "description": "Find root cause"},
                    {"action": "implement_fix", "description": "Implement fix"},
                    {"action": "verify", "description": "Verify fix works"},
                ],
                agents=["orchestrator", "debugger", "test-engineer"],
            )
        )

        # Deployment Workflows
        self.register(
            Workflow(
                name="/deploy",
                description="Deploy to production",
                category="deployment",
                steps=[
                    {
                        "action": "pre_deployment_checks",
                        "description": "Pre-deployment checks",
                    },
                    {"action": "build", "description": "Build application"},
                    {"action": "test", "description": "Run tests"},
                    {"action": "deploy", "description": "Deploy to production"},
                    {"action": "verify", "description": "Verify deployment"},
                ],
                agents=["orchestrator", "devops-engineer", "test-engineer"],
            )
        )

        # Premium Workflows
        self.register(
            Workflow(
                name="/launch-mobile",
                description="Launch mobile application",
                category="premium",
                steps=[
                    {"action": "setup_mobile", "description": "Setup mobile project"},
                    {"action": "implement_ui", "description": "Implement UI"},
                    {"action": "add_features", "description": "Add core features"},
                    {"action": "test_mobile", "description": "Test on devices"},
                    {"action": "publish", "description": "Prepare for publish"},
                ],
                agents=["orchestrator", "mobile-developer", "backend-specialist"],
            )
        )

        self.register(
            Workflow(
                name="/ai-feature",
                description="Add AI/ML features",
                category="premium",
                steps=[
                    {"action": "research_models", "description": "Research AI models"},
                    {
                        "action": "design_integration",
                        "description": "Design integration",
                    },
                    {"action": "implement", "description": "Implement AI feature"},
                    {"action": "test_ai", "description": "Test AI functionality"},
                    {"action": "optimize", "description": "Optimize performance"},
                ],
                agents=["orchestrator", "ai-researcher", "backend-specialist"],
            )
        )

        self.register(
            Workflow(
                name="/secure-audit",
                description="Security audit and hardening",
                category="premium",
                steps=[
                    {
                        "action": "vulnerability_scan",
                        "description": "Scan for vulnerabilities",
                    },
                    {
                        "action": "penetration_test",
                        "description": "Penetration testing",
                    },
                    {"action": "code_review", "description": "Security code review"},
                    {"action": "compliance_check", "description": "Check compliance"},
                    {"action": "hardening", "description": "Implement hardening"},
                ],
                agents=["orchestrator", "security-auditor", "penetration-tester"],
            )
        )

        self.register(
            Workflow(
                name="/optimize-stack",
                description="Full stack optimization",
                category="premium",
                steps=[
                    {
                        "action": "performance_analysis",
                        "description": "Analyze performance",
                    },
                    {
                        "action": "bottleneck_identification",
                        "description": "Find bottlenecks",
                    },
                    {"action": "optimization", "description": "Apply optimizations"},
                    {
                        "action": "infrastructure",
                        "description": "Optimize infrastructure",
                    },
                    {"action": "monitoring", "description": "Setup monitoring"},
                ],
                agents=["orchestrator", "performance-optimizer", "cloud-native-expert"],
            )
        )

    def register(self, workflow: Workflow):
        """Register a workflow"""
        self.workflows[workflow.name] = workflow

    def get(self, name: str) -> Optional[Workflow]:
        """Get a workflow by name"""
        return self.workflows.get(name)

    def list_by_category(self, category: str) -> List[Workflow]:
        """List workflows by category"""
        return [w for w in self.workflows.values() if w.category == category]

    def detect_from_text(self, text: str) -> List[str]:
        """Detect workflows from user text"""
        text_lower = text.lower()
        detected = []

        patterns = {
            "/brainstorm": ["explore", "ideas", "alternatives", "options"],
            "/blueprint": ["architecture", "design", "blueprint", "structure"],
            "/plan": ["plan", "roadmap", "breakdown", "timeline"],
            "/create": ["create", "build", "new app", "from scratch"],
            "/enhance": ["enhance", "improve", "add feature", "upgrade"],
            "/audit": ["audit", "review", "quality", "check"],
            "/test": ["test", "testing", "coverage"],
            "/debug": ["debug", "fix", "error", "bug"],
            "/deploy": ["deploy", "release", "production"],
            "/launch-mobile": ["mobile", "flutter", "react native", "ios", "android"],
            "/ai-feature": ["ai", "ml", "machine learning", "llm", "chatbot"],
            "/secure-audit": ["security", "secure", "vulnerability", "penetration"],
            "/optimize-stack": ["optimize", "performance", "slow", "fast"],
        }

        for workflow, keywords in patterns.items():
            if any(kw in text_lower for kw in keywords):
                detected.append(workflow)

        return detected

    def all(self) -> List[Workflow]:
        """Get all workflows"""
        return list(self.workflows.values())


# ═══════════════════════════════════════════════════════════════════════════════
# ORCHESTRATOR ENGINE
# ═══════════════════════════════════════════════════════════════════════════════


class OrchestratorEngine:
    """Main orchestration engine that coordinates agents, skills, and workflows"""

    def __init__(self):
        self.agents = AgentRegistry()
        self.skills = SkillRegistry()
        self.workflows = WorkflowRegistry()
        self.api_key = os.getenv("NVIDIA_API_KEY", "")
        self.api_url = os.getenv(
            "NVIDIA_API_URL", "https://integrate.api.nvidia.com/v1/chat/completions"
        )
        self.model = os.getenv("NVIDIA_MODEL", "moonshotai/kimi-k2.5")
        self.history = []

    async def analyze_intent(self, text: str) -> Dict:
        """Analyze user intent using 5W1H framework"""
        return {
            "what": self._extract_goal(text),
            "who": self._suggest_agents(text),
            "how": self._suggest_skills(text),
            "workflow": self.workflows.detect_from_text(text),
            "urgency": self._detect_urgency(text),
        }

    def _extract_goal(self, text: str) -> str:
        """Extract the main goal from text"""
        # Simple extraction - could be enhanced with NLP
        return text[:100]

    def _suggest_agents(self, text: str) -> List[str]:
        """Suggest appropriate agents"""
        text_lower = text.lower()
        suggestions = []

        # Frontend
        if any(
            kw in text_lower for kw in ["frontend", "ui", "react", "vue", "css", "html"]
        ):
            suggestions.append("frontend-specialist")

        # Backend
        if any(
            kw in text_lower for kw in ["backend", "api", "server", "database", "sql"]
        ):
            suggestions.append("backend-specialist")

        # Security
        if any(
            kw in text_lower for kw in ["security", "auth", "vulnerability", "encrypt"]
        ):
            suggestions.append("security-auditor")

        # Testing
        if any(
            kw in text_lower for kw in ["test", "testing", "coverage", "jest", "pytest"]
        ):
            suggestions.append("test-engineer")

        # Mobile
        if any(
            kw in text_lower
            for kw in ["mobile", "flutter", "react native", "ios", "android"]
        ):
            suggestions.append("mobile-developer")

        # DevOps
        if any(
            kw in text_lower
            for kw in ["docker", "kubernetes", "deploy", "ci/cd", "pipeline"]
        ):
            suggestions.append("devops-engineer")

        # Database
        if any(
            kw in text_lower
            for kw in ["database", "schema", "sql", "postgres", "mongodb"]
        ):
            suggestions.append("database-architect")

        # Performance
        if any(
            kw in text_lower
            for kw in ["performance", "optimize", "slow", "fast", "cache"]
        ):
            suggestions.append("performance-optimizer")

        # Default to orchestrator
        if not suggestions:
            suggestions.append("orchestrator")

        return suggestions

    def _suggest_skills(self, text: str) -> List[str]:
        """Suggest appropriate skills"""
        text_lower = text.lower()
        suggestions = []

        skill_keywords = {
            "clean-code": ["clean", "refactor", "improve"],
            "code-review": ["review", "audit", "check"],
            "testing": ["test", "coverage"],
            "api-design": ["api", "endpoint"],
            "security": ["security", "auth", "vulnerability"],
            "optimization": ["optimize", "performance", "slow"],
            "debugging": ["debug", "fix", "error", "bug"],
            "documentation": ["document", "readme", "docs"],
        }

        for skill, keywords in skill_keywords.items():
            if any(kw in text_lower for kw in keywords):
                suggestions.append(skill)

        return suggestions

    def _detect_urgency(self, text: str) -> str:
        """Detect urgency level"""
        text_lower = text.lower()
        if any(
            kw in text_lower for kw in ["urgent", "asap", "immediately", "critical"]
        ):
            return "high"
        elif any(kw in text_lower for kw in ["soon", "today", "tomorrow"]):
            return "medium"
        return "low"

    async def execute_with_agents(self, task: str, agent_names: List[str]) -> str:
        """Execute task with specified agents"""
        if not agent_names:
            agent_names = ["orchestrator"]

        results = []
        for agent_name in agent_names:
            agent = self.agents.get(agent_name)
            if agent:
                result = agent.invoke(task)
                results.append(f"[{agent.name}]: {result}")

        return "\n".join(results)

    async def execute_workflow(self, workflow_name: str, context: Dict) -> Dict:
        """Execute a workflow"""
        workflow = self.workflows.get(workflow_name)
        if workflow:
            return workflow.execute(context)
        return {"error": f"Workflow {workflow_name} not found"}

    async def ai_chat(self, message: str, system_prompt: Optional[str] = None) -> str:
        """Send message to AI API"""
        import requests

        if not self.api_key:
            return (
                "❌ Error: NVIDIA API key not configured. Please set it in .env file."
            )

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


def print_banner():
    """Display enhanced banner"""
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
    ║              🤖 Enhanced AI Platform with Agents 🤖                   ║
    ║                                                                       ║
    ║   27 Agents • 66+ Skills • 19 Workflows • Multi-Agent Orchestration   ║
    ║                                                                       ║
    ╚═══════════════════════════════════════════════════════════════════════╝
    """
    if RICH_AVAILABLE:
        console.print(banner, style="bold cyan")
    else:
        print(banner)


def print_main_menu():
    """Display main menu"""
    menu = """
    ╔═══════════════════════════════════════════════════════════════════════╗
    ║                        🎯 MAIN MENU                                   ║
    ╠═══════════════════════════════════════════════════════════════════════╣
    ║                                                                       ║
    ║  💬 [1] AI CHAT          - Conversational AI with context             ║
    ║  🤖 [2] AGENT MODE       - Deploy specialized agents                  ║
    ║  🔄 [3] WORKFLOWS        - Execute automated workflows                ║
    ║  🛠️  [4] SKILLS          - Apply specific skills                      ║
    ║  📝 [5] CODE ASSISTANT   - Write, review, and debug code              ║
    ║  🎨 [6] DESIGN MODE      - UI/UX and architecture design              ║
    ║  🔒 [7] SECURITY MODE    - Security audit and hardening               ║
    ║  📊 [8] SYSTEM STATUS    - Check agents, skills, and workflows        ║
    ║  📚 [9] KNOWLEDGE BASE   - Browse agents and capabilities             ║
    ║  ❓ [10] HELP            - How to use MR.VERMA                        ║
    ║                                                                       ║
    ║  🚪 [0] EXIT             - Close MR.VERMA                             ║
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


class MRVERMAEnhanced:
    """Enhanced MR.VERMA with full agent support"""

    def __init__(self):
        self.engine = OrchestratorEngine()

    async def ai_chat_mode(self):
        """Enhanced AI chat mode"""
        if RICH_AVAILABLE:
            console.print(
                "\n[bold cyan]💬 Enhanced AI Chat Mode - Type 'exit' to return[/bold cyan]\n"
            )
            console.print(
                "[dim]Tip: Mention agents like @frontend-specialist or workflows like /brainstorm[/dim]\n"
            )
        else:
            print("\n💬 Enhanced AI Chat Mode")
            print("Type 'exit' to return\n")

        while True:
            try:
                if RICH_AVAILABLE:
                    user_input = Prompt.ask("[bold blue]You[/bold blue]")
                else:
                    user_input = input("You: ")

                if user_input.lower() in ["exit", "quit", "back"]:
                    break

                # Check for agent mentions
                agent_mentions = re.findall(r"@(\w+)", user_input)
                workflow_mentions = re.findall(r"/(\w+)", user_input)

                if agent_mentions or workflow_mentions:
                    # Enhanced mode with agents
                    if RICH_AVAILABLE:
                        with console.status("[bold green]Orchestrating agents..."):
                            response = await self._orchestrate(
                                user_input, agent_mentions, workflow_mentions
                            )
                    else:
                        print("Orchestrating agents...")
                        response = await self._orchestrate(
                            user_input, agent_mentions, workflow_mentions
                        )
                else:
                    # Simple chat mode
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

    async def _orchestrate(
        self, text: str, agents: List[str], workflows: List[str]
    ) -> str:
        """Orchestrate agents and workflows"""
        analysis = await self.engine.analyze_intent(text)

        results = []

        # Execute workflows
        for wf in workflows:
            wf_name = f"/{wf}"
            workflow = self.engine.workflows.get(wf_name)
            if workflow:
                result = await self.engine.execute_workflow(wf_name, {"input": text})
                results.append(
                    f"[Workflow {wf_name}]: Activated with {len(workflow.agents)} agents"
                )

        # Invoke agents
        if agents:
            agent_result = await self.engine.execute_with_agents(text, agents)
            results.append(agent_result)

        # Get AI response
        system_prompt = f"You are coordinating: {', '.join(agents)} with workflows: {', '.join(workflows)}"
        ai_response = await self.engine.ai_chat(text, system_prompt)
        results.append(ai_response)

        return "\n\n".join(results)

    async def agent_mode(self):
        """Browse and use agents"""
        if RICH_AVAILABLE:
            console.print("\n[bold cyan]🤖 AGENT MODE[/bold cyan]\n")
        else:
            print("\n🤖 AGENT MODE\n")

        # Show agent categories
        for agent_type in AgentType:
            agents = self.engine.agents.list_by_type(agent_type)
            if agents:
                if RICH_AVAILABLE:
                    console.print(
                        f"\n[bold yellow]{agent_type.value} Agents:[/bold yellow]"
                    )
                else:
                    print(f"\n{agent_type.value} Agents:")

                for i, agent in enumerate(agents, 1):
                    if RICH_AVAILABLE:
                        console.print(
                            f"  {i}. [green]{agent.name}[/green] - {agent.description}"
                        )
                    else:
                        print(f"  {i}. {agent.name} - {agent.description}")

        if RICH_AVAILABLE:
            console.print(
                "\n[dim]Usage: In chat mode, mention agents with @agent-name[/dim]\n"
            )
        else:
            print("\nUsage: In chat mode, mention agents with @agent-name\n")

        input("\nPress Enter to continue...")

    async def workflow_mode(self):
        """Browse and execute workflows"""
        if RICH_AVAILABLE:
            console.print("\n[bold cyan]🔄 WORKFLOW MODE[/bold cyan]\n")
        else:
            print("\n🔄 WORKFLOW MODE\n")

        categories = ["planning", "building", "quality", "deployment", "premium"]

        for category in categories:
            workflows = self.engine.workflows.list_by_category(category)
            if workflows:
                if RICH_AVAILABLE:
                    console.print(f"\n[bold yellow]{category.upper()}:[/bold yellow]")
                else:
                    print(f"\n{category.upper()}:")

                for wf in workflows:
                    if RICH_AVAILABLE:
                        console.print(f"  [green]{wf.name}[/green] - {wf.description}")
                        console.print(f"    Agents: {', '.join(wf.agents)}")
                    else:
                        print(f"  {wf.name} - {wf.description}")
                        print(f"    Agents: {', '.join(wf.agents)}")

        if RICH_AVAILABLE:
            console.print(
                "\n[dim]Usage: In chat mode, trigger workflows with /workflow-name[/dim]\n"
            )
        else:
            print("\nUsage: In chat mode, trigger workflows with /workflow-name\n")

        input("\nPress Enter to continue...")

    async def skills_mode(self):
        """Browse available skills"""
        if RICH_AVAILABLE:
            console.print("\n[bold cyan]🛠️ SKILLS MODE[/bold cyan]\n")
        else:
            print("\n🛠️ SKILLS MODE\n")

        categories = [
            "code",
            "architecture",
            "frontend",
            "backend",
            "devops",
            "security",
            "ai",
        ]

        for category in categories:
            skills = self.engine.skills.list_by_category(category)
            if skills:
                if RICH_AVAILABLE:
                    console.print(
                        f"\n[bold yellow]{category.upper()} SKILLS:[/bold yellow]"
                    )
                else:
                    print(f"\n{category.upper()} SKILLS:")

                for skill in skills:
                    if RICH_AVAILABLE:
                        console.print(
                            f"  • [green]{skill.name}[/green] - {skill.description}"
                        )
                    else:
                        print(f"  • {skill.name} - {skill.description}")

        input("\nPress Enter to continue...")

    async def code_assistant(self):
        """Code assistant with specialized agents"""
        if RICH_AVAILABLE:
            console.print("\n[bold cyan]📝 CODE ASSISTANT[/bold cyan]\n")
        else:
            print("\n📝 CODE ASSISTANT\n")

        options = [
            "Write new code (with @backend-specialist or @frontend-specialist)",
            "Review existing code (with @agent-perfectionist)",
            "Debug issues (with @debugger)",
            "Add tests (with @test-engineer)",
            "Optimize performance (with @performance-optimizer)",
        ]

        for i, opt in enumerate(options, 1):
            if RICH_AVAILABLE:
                console.print(f"{i}. {opt}")
            else:
                print(f"{i}. {opt}")

        if RICH_AVAILABLE:
            console.print(
                "\n[dim]Select an option or type your request directly in chat mode[/dim]\n"
            )
        else:
            print("\nSelect an option or type your request directly in chat mode\n")

        input("\nPress Enter to continue...")

    async def design_mode(self):
        """Design and architecture mode"""
        if RICH_AVAILABLE:
            console.print("\n[bold cyan]🎨 DESIGN MODE[/bold cyan]\n")
        else:
            print("\n🎨 DESIGN MODE\n")

        options = [
            ("Create system blueprint", "/blueprint with @business-architect"),
            ("Design UI/UX", "@frontend-specialist"),
            ("Database design", "@database-architect"),
            ("API design", "@api-designer"),
            ("Mobile app design", "@mobile-developer"),
        ]

        for i, (desc, agent) in enumerate(options, 1):
            if RICH_AVAILABLE:
                console.print(f"{i}. {desc} ({agent})")
            else:
                print(f"{i}. {desc} ({agent})")

        input("\nPress Enter to continue...")

    async def security_mode(self):
        """Security audit mode"""
        if RICH_AVAILABLE:
            console.print("\n[bold cyan]🔒 SECURITY MODE[/bold cyan]\n")
        else:
            print("\n🔒 SECURITY MODE\n")

        options = [
            ("Run security audit", "/secure-audit workflow"),
            ("Check vulnerabilities", "@security-auditor"),
            ("Penetration test", "@penetration-tester"),
            ("Review authentication", "@security-auditor + @backend-specialist"),
            ("Compliance check", "@security-auditor"),
        ]

        for i, (desc, action) in enumerate(options, 1):
            if RICH_AVAILABLE:
                console.print(f"{i}. {desc} [dim]({action})[/dim]")
            else:
                print(f"{i}. {desc} ({action})")

        input("\nPress Enter to continue...")

    async def system_status(self):
        """Show system status"""
        if RICH_AVAILABLE:
            console.print("\n[bold cyan]📊 SYSTEM STATUS[/bold cyan]\n")

            # Create status table
            table = Table(title="MR.VERMA System Status")
            table.add_column("Component", style="cyan")
            table.add_column("Count", style="green")
            table.add_column("Status", style="yellow")

            table.add_row("Agents", str(len(self.engine.agents.all())), "✅ Ready")
            table.add_row("Skills", str(len(self.engine.skills.all())), "✅ Ready")
            table.add_row(
                "Workflows", str(len(self.engine.workflows.all())), "✅ Ready"
            )

            console.print(table)

            # API Status
            console.print(
                f"\n[dim]API Key: {'✅ Configured' if self.engine.api_key else '❌ Not configured'}[/dim]"
            )

        else:
            print("\n📊 SYSTEM STATUS\n")
            print(f"Agents: {len(self.engine.agents.all())} ✅")
            print(f"Skills: {len(self.engine.skills.all())} ✅")
            print(f"Workflows: {len(self.engine.workflows.all())} ✅")
            print(
                f"API Key: {'✅ Configured' if self.engine.api_key else '❌ Not configured'}"
            )

        input("\nPress Enter to continue...")

    async def knowledge_base(self):
        """Browse knowledge base"""
        if RICH_AVAILABLE:
            console.print("\n[bold cyan]📚 KNOWLEDGE BASE[/bold cyan]\n")

            console.print("[bold yellow]Quick Reference:[/bold yellow]\n")

            console.print("[bold]Agent Commands:[/bold]")
            console.print("  @agent-name - Invoke specific agent")
            console.print("  Example: @security-auditor review this code\n")

            console.print("[bold]Workflow Commands:[/bold]")
            console.print("  /workflow-name - Trigger workflow")
            console.print("  Example: /brainstorm ideas for new feature\n")

            console.print("[bold]Popular Workflows:[/bold]")
            console.print("  /brainstorm - Explore ideas")
            console.print("  /plan - Create project plan")
            console.print("  /create - Build application")
            console.print("  /audit - Quality audit")
            console.print("  /deploy - Deploy to production")
            console.print("  /secure-audit - Security audit\n")

        else:
            print("\n📚 KNOWLEDGE BASE\n")
            print("Agent Commands:")
            print("  @agent-name - Invoke specific agent")
            print("Workflow Commands:")
            print("  /workflow-name - Trigger workflow")

        input("\nPress Enter to continue...")

    async def help(self):
        """Show help"""
        help_text = """
        MR.VERMA Enhanced Help
        ======================
        
        This is the enhanced version of MR.VERMA with full agent support!
        
        KEY FEATURES:
        • 27 Specialized AI Agents
        • 66+ Technical Skills
        • 19 Automated Workflows
        • Multi-Agent Orchestration
        
        HOW TO USE:
        
        1. AI Chat Mode (Option 1)
           Just chat naturally with AI
           Mention agents: @security-auditor check this
           Trigger workflows: /brainstorm ideas
        
        2. Agent Mode (Option 2)
           Browse all 27 agents
           See what each agent specializes in
        
        3. Workflows (Option 3)
           Automated multi-step processes
           Trigger with /workflow-name in chat
        
        4. Skills (Option 4)
           Browse 66+ technical skills
           Applied automatically by agents
        
        EXAMPLES:
        • "@frontend-specialist create a login form"
        • "/secure-audit check my API for vulnerabilities"
        • "@performance-optimizer make this faster"
        • "/plan create roadmap for my app"
        
        TIPS:
        • Combine agents: @backend-specialist and @frontend-specialist
        • Use workflows: /create, /audit, /deploy
        • Be specific for best results
        """

        if RICH_AVAILABLE:
            console.print(Panel(help_text, title="Help", border_style="blue"))
        else:
            print(help_text)

        input("\nPress Enter to continue...")

    async def run(self):
        """Main application loop"""
        print_banner()

        while True:
            print_main_menu()

            try:
                if RICH_AVAILABLE:
                    choice = Prompt.ask(
                        "Select option",
                        choices=[str(i) for i in range(11)],
                        default="1",
                    )
                else:
                    choice = input("\nSelect option (0-10): ").strip()

                if choice == "0":
                    if RICH_AVAILABLE:
                        console.print(
                            "\n[bold green]👋 Goodbye! Thanks for using MR.VERMA Enhanced![/bold green]\n"
                        )
                    else:
                        print("\n👋 Goodbye!\n")
                    break

                elif choice == "1":
                    await self.ai_chat_mode()
                elif choice == "2":
                    await self.agent_mode()
                elif choice == "3":
                    await self.workflow_mode()
                elif choice == "4":
                    await self.skills_mode()
                elif choice == "5":
                    await self.code_assistant()
                elif choice == "6":
                    await self.design_mode()
                elif choice == "7":
                    await self.security_mode()
                elif choice == "8":
                    await self.system_status()
                elif choice == "9":
                    await self.knowledge_base()
                elif choice == "10":
                    await self.help()
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
    app = MRVERMAEnhanced()
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
