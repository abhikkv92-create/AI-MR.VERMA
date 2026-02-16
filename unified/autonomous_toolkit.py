import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from unified.platform_adapters import BasePlatformAdapter, PlatformFactory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Tool:
    """Definition of an autonomous tool."""
    name: str
    description: str
    func: Callable
    parameters: Dict[str, Any] = field(default_factory=dict)

class ToolRegistry:
    """Registry for autonomous tools."""
    
    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register_tool(self, name: str, description: str, func: Callable, parameters: Dict[str, Any] = None):
        """Register a new tool."""
        tool = Tool(name, description, func, parameters or {})
        self._tools[name] = tool
        logger.info(f"Registered tool: {name}")

    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools."""
        return [
            {"name": t.name, "description": t.description, "parameters": t.parameters}
            for t in self._tools.values()
        ]

    def invoke_tool(self, name: str, **kwargs) -> Any:
        """Invoke a tool by name."""
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found")
        
        logger.info(f"Invoking tool: {name} with args: {kwargs}")
        try:
            return tool.func(**kwargs)
        except Exception as e:
            logger.error(f"Tool invocation failed: {e}")
            return f"Error: {str(e)}"

class AgentOrchestrator:
    """Orchestrates agent activities across platforms."""

    def __init__(self, platform_adapter: BasePlatformAdapter, tool_registry: ToolRegistry):
        self.adapter = platform_adapter
        self.registry = tool_registry
        self.context = {}

    def execute_goal(self, goal: str) -> str:
        """Execute a high-level goal using the platform and tools."""
        logger.info(f"Executing goal: {goal}")
        
        # 1. Plan (Simplified for now)
        # In a real system, this would use the LLM to breakdown the goal into steps/tools
        plan_prompt = f"Plan for goal: {goal}\nAvailable tools: {[t['name'] for t in self.registry.list_tools()]}"
        
        # Simulate planning via adapter
        plan_response = self.adapter.generate_code(plan_prompt, language="text")
        logger.info(f"Generated plan: {plan_response}")

        # 2. Execute (Mock execution logic)
        # Depending on the plan, call tools. 
        # For this implementation, we'll pretend to execute a simple loop.
        
        result_log = []
        result_log.append(f"Goal: {goal}")
        result_log.append(f"Plan: {plan_response}")
        
        # Example self-correction/feedback loop simulation
        result_log.append("Executing step 1... Done.")
        result_log.append("Executing step 2... Done.")
        
        final_result = "\n".join(result_log)
        return final_result

    def run_workflow(self, workflow_name: str, parameters: Dict[str, Any]) -> str:
        """Run a predefined workflow."""
        # This could load workflow definitions from files
        return f"Running workflow '{workflow_name}' with {parameters}"

def autonomous_agent(platform_name: str = "antigravity") -> AgentOrchestrator:
    """Create a fully configured autonomous agent."""
    registry = ToolRegistry()
    
    # Register default tools
    from unified.document_generation import DocumentAgent
    doc_agent = DocumentAgent()
    
    registry.register_tool(
        "create_document", 
        "Create rich documents (docx, pptx, xlsx)", 
        doc_agent.create_document
    )
    
    if doc_agent.vector_store:
        registry.register_tool(
            "search_knowledge",
            "Search vector knowledge base",
            doc_agent.vector_store.search
        )

    adapter = PlatformFactory.get_adapter(platform_name)
    if not adapter:
        raise ValueError(f"Could not create adapter for {platform_name}")

    return AgentOrchestrator(adapter, registry)
