# MR.VERMA API Documentation

## Overview

MR.VERMA provides a comprehensive multi-agent AI platform with RESTful API endpoints and programmatic Python interfaces.

---

## Core Components

### 1. SupremeOrchestrator

The main entry point for processing requests through the MR.VERMA system.

```python
from core.orchestrator import SupremeOrchestrator

orchestrator = SupremeOrchestrator()
result = await orchestrator.process_request("Your task here")
```

#### Methods

##### `process_request(prompt: str, **kwargs) -> dict`

Process a natural language request through the AI pipeline.

**Parameters:**
- `prompt` (str): The user request or instruction
- `image_path` (str, optional): Path to image for vision tasks
- `stream` (bool, optional): Whether to stream the response

**Returns:**
```python
{
    "status": "SUCCESS",
    "response": "AI generated response",
    "agents_invoked": ["Agent1", "Agent2"],
    "processing_time": 1.23
}
```

**Example:**
```python
result = await orchestrator.process_request(
    "Analyze this codebase for security vulnerabilities",
    stream=False
)
```

---

### 2. Agent Clusters

#### Intelligence Cluster

##### DataScientist

Specialized in data analysis and log processing.

```python
from agents import DataScientist

agent = DataScientist()
agent.start()

result = await agent.process_task({
    "mode": "ai_log_analysis",
    "log_file": "logs/system.log"
})
```

**Modes:**
- `ai_log_analysis`: Analyze log files for issues and patterns

##### ResearchAnalyst

Conducts research and data analysis.

```python
from agents import ResearchAnalyst

agent = ResearchAnalyst()
agent.start()

# Research mode
result = await agent.process_task({
    "mode": "research",
    "topic": "Latest developments in quantum computing"
})

# Analysis mode
result = await agent.process_task({
    "mode": "analyze",
    "data": "Your data here",
    "analysis_type": "sentiment"
})
```

##### AIMLEngineer

AI/ML engineering and model design.

```python
from agents import AIMLEngineer

agent = AIMLEngineer()
agent.start()

result = await agent.process_task({
    "mode": "model_design",
    "requirements": "Build a sentiment analysis model for social media"
})
```

#### Platform Cluster

##### ProductionOrchestrator

Handles production operations and self-healing.

```python
from agents import ProductionOrchestrator

agent = ProductionOrchestrator()
agent.start()

result = await agent.process_task({
    "mode": "self_heal",
    "auto_heal": True,
    "audit_log": "logs/audit.log"
})
```

##### SecurityArchitect

Security audits and vulnerability analysis.

```python
from agents import SecurityArchitect

agent = SecurityArchitect()
agent.start()

result = await agent.process_task({
    "mode": "ai_security_scan",
    "target_file": "path/to/code.py"
})
```

#### Frontend Cluster

##### UIDesigner

UI/UX design and layout generation.

```python
from agents import UIDesigner

agent = UIDesigner()
agent.start()

result = await agent.process_task({
    "mode": "design_muse",
    "prompt": "Modern dashboard for data analytics",
    "style": "modern",
    "framework": "tailwind"
})
```

---

### 3. Core Services

#### Task Queue

Async task queue for managing background operations.

```python
from core import global_task_queue

# Start the queue
await global_task_queue.start()

# Submit a task
future = await global_task_queue.submit(
    my_async_function,
    arg1, arg2,
    keyword_arg="value"
)

# Get result
result = await future

# Stop the queue
await global_task_queue.stop()
```

#### Security Orchestrator

Security management and audit logging.

```python
from core import security_service

# Generate authentication token
token = security_service.generate_token(
    agent_id="my_agent",
    permissions=["read", "write"]
)

# Log audit event
security_service.log_audit_event(
    agent_id="my_agent",
    action="TASK_COMPLETE",
    status="SUCCESS",
    details="Task completed successfully"
)
```

#### Processing Unit

CPU optimization and task scheduling.

```python
from core import kernel_pu

# Submit task to high-priority pool
result = await kernel_pu.submit_high_priority(
    my_task_function,
    *args
)

# Submit task to standard pool
result = await kernel_pu.submit_standard(
    my_background_task,
    *args
)
```

---

### 4. AI Engines

#### Primary Engine

Main AI engine for complex reasoning tasks.

```python
from core.ai.primary_engine import PrimaryAIEngine

engine = PrimaryAIEngine()

completion = engine.generate(
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello!"}
    ],
    stream=False
)
```

#### Secondary Engine

Fallback engine for simpler tasks or when primary is unavailable.

```python
from core.ai.secondary_engine import SecondaryAIEngine

engine = SecondaryAIEngine()

response = engine.generate(
    system_prompt="You are an expert",
    user_prompt="Explain quantum computing",
    max_tokens=1000
)
```

#### Vision Engine

Image analysis and vision tasks.

```python
from core.ai.vision_engine import VisionAIEngine

engine = VisionAIEngine()

if engine.is_available():
    analysis = engine.analyze(
        media_files=["image1.png", "image2.jpg"],
        query="Describe what's in these images"
    )
```

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# NVIDIA AI APIs (Primary)
NVIDIA_API_KEY=your_nvidia_api_key_here
NVIDIA_API_URL=https://integrate.api.nvidia.com/v1
NVIDIA_MODEL=z-ai/glm5

# Secondary AI (Backup)
NVIDIA_API_KEY_SECONDARY=your_secondary_key_here

# Vision AI
NVIDIA_API_KEY_VISION=your_vision_key_here

# Optional: OpenRouter APIs
OPENROUTER_API_KEY_GENERATE_IMAGE=your_key
OPENROUTER_API_KEY_PERPLEXITY_SEARCH=your_key
```

### Loading Environment

```python
from core.env_manager import load_env_file

# Load from default .env file
load_env_file()

# Or specify custom path
load_env_file("config/production.env")
```

---

## Error Handling

All agents and core services use consistent error handling:

```python
try:
    result = await agent.process_task(task_data)
    if result["status"] == "ERROR":
        # Handle task failure
        print(f"Task failed: {result['message']}")
    else:
        # Process successful result
        print(f"Success: {result}")
except Exception as e:
    # Handle unexpected errors
    print(f"Unexpected error: {e}")
```

---

## Best Practices

### 1. Always Start Agents

```python
agent = DataScientist()
agent.start()  # Required before processing tasks
# ... use agent ...
agent.stop()   # Clean shutdown
```

### 2. Use Async Context Managers

```python
async with global_task_queue:
    # Queue is automatically started and stopped
    result = await process_tasks()
```

### 3. Handle Rate Limits

```python
from core.rate_limiter import RateLimiter

limiter = RateLimiter.get_limiter("my_api", capacity=10, refill_rate=1.0)
await limiter.acquire()  # Wait for rate limit slot
```

### 4. Log Security Events

```python
from core import security_service

security_service.log_audit_event(
    agent_id="my_agent",
    action="SENSITIVE_OPERATION",
    status="SUCCESS",
    details="Accessed user data"
)
```

---

## Examples

### Complete Workflow Example

```python
import asyncio
from agents import DataScientist, SecurityArchitect
from core.orchestrator import SupremeOrchestrator
from core.env_manager import load_env_file

async def main():
    # Load environment
    load_env_file()
    
    # Initialize orchestrator
    orchestrator = SupremeOrchestrator()
    
    # Process general request
    result = await orchestrator.process_request(
        "Analyze system logs and check for security issues"
    )
    print(f"Orchestrator result: {result}")
    
    # Use specific agents
    data_agent = DataScientist()
    data_agent.start()
    
    log_result = await data_agent.process_task({
        "mode": "ai_log_analysis",
        "log_file": "logs/system.log"
    })
    print(f"Log analysis: {log_result}")
    
    data_agent.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Support

For issues and feature requests, please refer to:
- Documentation: `/documentation/`
- Tests: `/tests/`
- Production Readiness Report: `PRODUCTION_READINESS_REPORT.md`
