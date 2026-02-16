# MR.VERMA API Integration Documentation

## Table of Contents

1. [Overview](#overview)
2. [Core API Architecture](#core-api-architecture)
3. [Authentication & Security](#authentication--security)
4. [Skill Execution API](#skill-execution-api)
5. [Agent Management API](#agent-management-api)
6. [Workflow Orchestration API](#workflow-orchestration-api)
7. [Cross-Platform Integration](#cross-platform-integration)
8. [Real-time Communication (SSE)](#real-time-communication)
9. [Swarm Dispatcher API](#swarm-dispatcher-api)
10. [Error Handling](#error-handling)
11. [Rate Limiting](#rate-limiting)
12. [SDKs and Client Libraries](#sdks-and-client-libraries)
13. [API Versioning](#api-versioning)

## Overview

The MR.VERMA API provides a comprehensive interface for interacting with the Supreme Entity Orchestrator and its ecosystem of 27 specialized agents, 123 skills, and 19 workflows. The API follows RESTful principles with WebSocket support for real-time communication.

### Base URLs

- **Production**: `https://api.mrverma.ai/v1`
- **Staging**: `https://staging-api.mrverma.ai/v1`
- **Local Development**: `http://localhost:8550` (Collector / SSE)

### 2.0 Real-time Extensions

MR.VERMA 2.0 introduces **Server-Sent Events (SSE)** for high-frequency data distribution.

### API Standards

- **Protocol**: HTTPS (TLS 1.3)
- **Data Format**: JSON (UTF-8)
- **Content-Type**: `application/json`
- **Rate Limit**: 100 requests/minute (authenticated), 20 requests/minute (anonymous)
- **Timeout**: 30 seconds (default), 300 seconds (long-running operations)

## Core API Architecture

### Request Flow Architecture

```python
class APIRequestHandler:
    """Central API request processor"""
    
    def __init__(self):
        self.auth_validator = AuthValidator()
        self.rate_limiter = RateLimiter()
        self.request_router = RequestRouter()
        self.response_formatter = ResponseFormatter()
    
    async def handle_request(self, request: APIRequest) -> APIResponse:
        """Process incoming API request through validation pipeline"""
        
        # 1. Authentication validation
        auth_result = await self.auth_validator.validate(request)
        if not auth_result.is_valid:
            return APIResponse.error(auth_result.error, status=401)
        
        # 2. Rate limiting check
        rate_check = self.rate_limiter.check_limit(request.client_id)
        if rate_check.exceeded:
            return APIResponse.error("Rate limit exceeded", status=429)
        
        # 3. Request routing
        route = self.request_router.find_route(request.path, request.method)
        if not route:
            return APIResponse.error("Endpoint not found", status=404)
        
        # 4. Execute handler
        try:
            result = await route.handler(request)
            return self.response_formatter.format_success(result)
        except Exception as e:
            return self.response_formatter.format_error(e)
```

### Response Format Standard

```json
{
  "success": true,
  "data": {
    "request_id": "req_1234567890",
    "timestamp": "2024-01-15T10:30:00Z",
    "result": {}
  },
  "metadata": {
    "version": "1.0.0",
    "processing_time_ms": 1250
  }
}
```

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "SKILL_EXECUTION_FAILED",
    "message": "Skill execution failed with timeout",
    "details": {
      "skill_name": "code_analyzer",
      "timeout_seconds": 30,
      "suggestion": "Increase timeout or optimize skill implementation"
    }
  },
  "metadata": {
    "request_id": "req_1234567890",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

## Authentication & Security

### API Key Authentication

```python
class APIKeyAuth:
    """API Key-based authentication"""
    
    def __init__(self):
        self.key_validator = KeyValidator()
        self.permission_checker = PermissionChecker()
    
    async def authenticate(self, api_key: str) -> AuthResult:
        """Validate API key and return authentication result"""
        
        # Validate key format and existence
        key_info = await self.key_validator.validate_key(api_key)
        if not key_info.is_valid:
            return AuthResult.fail("Invalid API key")
        
        # Check permissions
        permissions = await self.permission_checker.get_permissions(key_info.user_id)
        
        return AuthResult.success(
            user_id=key_info.user_id,
            permissions=permissions,
            rate_limit_tier=key_info.tier
        )
```

### JWT Token Authentication

```python
class JWTAuth:
    """JWT token-based authentication"""
    
    def __init__(self):
        self.jwt_secret = settings.JWT_SECRET
        self.token_blacklist = TokenBlacklist()
    
    def generate_token(self, user_id: str, permissions: List[str]) -> str:
        """Generate JWT token with user claims"""
        
        payload = {
            "user_id": user_id,
            "permissions": permissions,
            "exp": datetime.utcnow() + timedelta(hours=24),
            "iat": datetime.utcnow(),
            "jti": str(uuid.uuid4())
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")
    
    async def validate_token(self, token: str) -> AuthResult:
        """Validate JWT token and return authentication result"""
        
        try:
            # Check blacklist
            if await self.token_blacklist.is_blacklisted(token):
                return AuthResult.fail("Token has been revoked")
            
            # Decode and validate token
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            
            return AuthResult.success(
                user_id=payload["user_id"],
                permissions=payload["permissions"]
            )
        
        except jwt.ExpiredSignatureError:
            return AuthResult.fail("Token has expired")
        except jwt.InvalidTokenError:
            return AuthResult.fail("Invalid token")
```

### Security Headers

```python
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'",
    "Referrer-Policy": "strict-origin-when-cross-origin"
}
```

## Skill Execution API

### Execute Skill Endpoint

**POST** `/v1/skills/execute`

#### Request Body

```json
{
  "skill_name": "code_analyzer",
  "parameters": {
    "code": "def hello_world():\n    print('Hello, World!')",
    "language": "python",
    "analysis_type": "security"
  },
  "context": {
    "project_id": "proj_123",
    "user_id": "user_456",
    "timeout_seconds": 30
  }
}
```

#### Response

```json
{
  "success": true,
  "data": {
    "execution_id": "exec_789",
    "skill_name": "code_analyzer",
    "status": "completed",
    "result": {
      "security_issues": [],
      "code_quality_score": 8.5,
      "recommendations": [
        "Consider adding type hints for better code clarity",
        "Add docstring to explain function purpose"
      ]
    },
    "execution_time_ms": 1250
  }
}
```

### Skill Execution Handler

```python
class SkillExecutionAPI:
    """API handler for skill execution"""
    
    def __init__(self):
        self.skill_registry = SkillRegistry()
        self.execution_engine = ExecutionEngine()
        self.result_cache = ResultCache()
    
    async def execute_skill(self, request: SkillExecutionRequest) -> SkillExecutionResponse:
        """Execute a skill with given parameters"""
        
        # Validate skill exists
        skill = self.skill_registry.get_skill(request.skill_name)
        if not skill:
            raise SkillNotFoundError(f"Skill '{request.skill_name}' not found")
        
        # Check permissions
        if not self.has_permission(request.user_id, request.skill_name):
            raise PermissionDeniedError("Insufficient permissions for skill execution")
        
        # Check cache for identical requests
        cache_key = self.generate_cache_key(request)
        cached_result = await self.result_cache.get(cache_key)
        if cached_result and not request.context.get('force_refresh'):
            return cached_result
        
        # Execute skill
        execution_id = str(uuid.uuid4())
        try:
            result = await self.execution_engine.execute(
                skill=skill,
                parameters=request.parameters,
                context=request.context,
                timeout=request.context.get('timeout_seconds', 30)
            )
            
            # Cache result
            response = SkillExecutionResponse(
                execution_id=execution_id,
                skill_name=request.skill_name,
                status="completed",
                result=result,
                execution_time_ms=result.execution_time
            )
            
            await self.result_cache.set(cache_key, response, ttl=300)
            return response
            
        except TimeoutError:
            raise SkillExecutionError(f"Skill execution timed out after {request.context.get('timeout_seconds', 30)} seconds")
        except Exception as e:
            raise SkillExecutionError(f"Skill execution failed: {str(e)}")
```

### Batch Skill Execution

**POST** `/v1/skills/batch-execute`

#### Request Body

```json
{
  "executions": [
    {
      "skill_name": "code_analyzer",
      "parameters": {"code": "print('test')", "language": "python"},
      "execution_id": "batch_1"
    },
    {
      "skill_name": "documentation_generator",
      "parameters": {"content": "function example() {}", "format": "markdown"},
      "execution_id": "batch_2"
    }
  ],
  "parallel": true,
  "max_concurrent": 5
}
```

## Agent Management API

### List Agents

**GET** `/v1/agents`

#### Query Parameters

- `category` (optional): Filter by agent category (e.g., "development", "analysis")
- `status` (optional): Filter by agent status ("active", "idle", "busy")
- `limit` (optional): Maximum results (default: 50, max: 200)

#### Response

```json
{
  "success": true,
  "data": {
    "agents": [
      {
        "agent_id": "agent_dev_001",
        "name": "Frontend Specialist",
        "category": "development",
        "status": "idle",
        "capabilities": ["react", "vue", "typescript", "css"],
        "current_task": null,
        "performance_metrics": {
          "tasks_completed": 156,
          "average_rating": 4.8,
          "success_rate": 0.95
        }
      }
    ],
    "total_count": 27,
    "filtered_count": 15
  }
}
```

### Agent Registration

**POST** `/v1/agents/register`

#### Request Body

```json
{
  "agent_config": {
    "name": "Custom Analyzer",
    "category": "analysis",
    "capabilities": ["python", "security", "performance"],
    "max_concurrent_tasks": 3,
    "specialization": {
      "primary": "code_analysis",
      "secondary": ["security_scanning", "performance_profiling"]
    }
  },
  "deployment_config": {
    "image": "mrverma/agent-analyzer:latest",
    "resources": {
      "cpu": "2",
      "memory": "4Gi",
      "gpu": "optional"
    },
    "scaling": {
      "min_instances": 1,
      "max_instances": 5,
      "target_cpu_utilization": 0.7
    }
  }
}
```

### Agent Task Assignment

**POST** `/v1/agents/{agent_id}/assign-task`

#### Request Body

```json
{
  "task": {
    "type": "code_review",
    "payload": {
      "code": "def complex_function(): pass",
      "language": "python",
      "requirements": ["security", "performance", "readability"]
    },
    "priority": "high",
    "deadline": "2024-01-15T15:00:00Z"
  },
  "context": {
    "project_id": "proj_123",
    "user_id": "user_456",
    "callback_url": "https://app.example.com/webhook/task-complete"
  }
}
```

## Workflow Orchestration API

### Start Workflow

**POST** `/v1/workflows/start`

#### Request Body

```json
{
  "workflow_name": "multi_agent_code_review",
  "parameters": {
    "repository_url": "https://github.com/example/repo.git",
    "branch": "main",
    "review_criteria": ["security", "performance", "maintainability"]
  },
  "orchestration_config": {
    "agent_selection": "auto",
    "parallel_agents": true,
    "max_agents": 5,
    "timeout_minutes": 60
  },
  "context": {
    "project_id": "proj_123",
    "user_id": "user_456",
    "priority": "normal"
  }
}
```

#### Response

```json
{
  "success": true,
  "data": {
    "workflow_id": "wf_789",
    "workflow_name": "multi_agent_code_review",
    "status": "running",
    "started_at": "2024-01-15T10:30:00Z",
    "estimated_completion": "2024-01-15T11:30:00Z",
    "agents_assigned": [
      "agent_security_001",
      "agent_performance_002",
      "agent_maintainability_003"
    ],
    "progress": {
      "current_phase": "analysis",
      "completed_tasks": 2,
      "total_tasks": 8,
      "percentage": 25
    }
  }
}
```

### Workflow Status

**GET** `/v1/workflows/{workflow_id}/status`

#### Response

```json
{
  "success": true,
  "data": {
    "workflow_id": "wf_789",
    "status": "completed",
    "phases": [
      {
        "name": "planning",
        "status": "completed",
        "started_at": "2024-01-15T10:30:00Z",
        "completed_at": "2024-01-15T10:35:00Z",
        "agents_involved": ["orchestrator"]
      },
      {
        "name": "execution",
        "status": "completed",
        "started_at": "2024-01-15T10:35:00Z",
        "completed_at": "2024-01-15T11:25:00Z",
        "agents_involved": [
          "agent_security_001",
          "agent_performance_002",
          "agent_maintainability_003"
        ]
      }
    ],
    "results": {
      "security_score": 8.5,
      "performance_score": 7.8,
      "maintainability_score": 9.2,
      "overall_recommendation": "APPROVED_WITH_MINOR_CHANGES",
      "detailed_report": "https://reports.mrverma.ai/wf_789"
    }
  }
}
```

### Workflow Orchestrator Implementation

```python
class WorkflowOrchestrationAPI:
    """API handler for workflow orchestration"""
    
    def __init__(self):
        self.orchestrator = SupremeEntityOrchestrator()
        self.workflow_registry = WorkflowRegistry()
        self.execution_tracker = ExecutionTracker()
    
    async def start_workflow(self, request: WorkflowStartRequest) -> WorkflowStartResponse:
        """Start a new workflow execution"""
        
        # Validate workflow exists
        workflow = self.workflow_registry.get_workflow(request.workflow_name)
        if not workflow:
            raise WorkflowNotFoundError(f"Workflow '{request.workflow_name}' not found")
        
        # Validate user permissions
        if not self.has_workflow_permission(request.user_id, request.workflow_name):
            raise PermissionDeniedError("Insufficient permissions for workflow execution")
        
        # Create orchestration plan
        plan = await self.orchestrator.create_plan(
            workflow=workflow,
            parameters=request.parameters,
            config=request.orchestration_config,
            context=request.context
        )
        
        # Start workflow execution
        workflow_id = str(uuid.uuid4())
        execution = await self.execution_tracker.start_workflow(
            workflow_id=workflow_id,
            plan=plan,
            user_id=request.user_id
        )
        
        return WorkflowStartResponse(
            workflow_id=workflow_id,
            workflow_name=request.workflow_name,
            status="running",
            started_at=datetime.utcnow(),
            estimated_completion=execution.estimated_completion,
            agents_assigned=plan.assigned_agents,
            progress=execution.get_progress()
        )
```

## Cross-Platform Integration

### Platform Authentication

```python
class PlatformIntegrationAPI:
    """API for cross-platform integrations"""
    
    def __init__(self):
        self.platform_connectors = {
            'trae_ai': TRAEAIConnector(),
            'antigravity': AntigravityConnector(),
            'open_code': OpenCodeConnector()
        }
        self.sync_manager = SyncManager()
    
    async def authenticate_platform(self, platform: str, credentials: dict) -> PlatformAuthResult:
        """Authenticate with external platform"""
        
        connector = self.platform_connectors.get(platform)
        if not connector:
            raise PlatformNotSupportedError(f"Platform '{platform}' not supported")
        
        try:
            auth_result = await connector.authenticate(credentials)
            
            # Store platform connection
            await self.store_platform_connection(
                platform=platform,
                user_id=credentials['user_id'],
                auth_token=auth_result.token,
                refresh_token=auth_result.refresh_token
            )
            
            return PlatformAuthResult(
                success=True,
                platform=platform,
                permissions=auth_result.permissions,
                connection_id=auth_result.connection_id
            )
            
        except AuthenticationError as e:
            return PlatformAuthResult(
                success=False,
                platform=platform,
                error=str(e)
            )
```

### Cross-Platform Sync

**POST** `/v1/sync/cross-platform`

#### Request Body

```json
{
  "sync_type": "bidirectional",
  "platforms": ["trae_ai", "antigravity"],
  "sync_config": {
    "direction": "both",
    "conflict_resolution": "timestamp_wins",
    "sync_interval_seconds": 300,
    "batch_size": 100
  },
  "data_types": ["projects", "skills", "workflows", "user_preferences"],
  "context": {
    "user_id": "user_123",
    "priority": "normal"
  }
}
```

#### Response

```json
{
  "success": true,
  "data": {
    "sync_id": "sync_456",
    "status": "initiated",
    "platforms": {
      "trae_ai": {
        "status": "connected",
        "last_sync": "2024-01-15T10:25:00Z",
        "items_synced": 45
      },
      "antigravity": {
        "status": "connected",
        "last_sync": "2024-01-15T10:20:00Z",
        "items_synced": 38
      }
    },
    "conflicts_detected": 2,
    "conflicts_resolved": 2,
    "estimated_completion": "2024-01-15T10:35:00Z"
  }
}

## Real-time Communication (SSE)

The `/api/stream` endpoint provides a permanent connection for high-frequency updates.

### GET `/api/stream`
**Description**: Server-Sent Events provider.
**Events**:
- `telemetry`: CPU/RAM usage.
- `kernel_log`: Real-time agent logs.
- `thermal_status`: i9-13900H thermal and throttling data.
- `security_status`: Integrity and mutation alerts.

## Swarm Dispatcher API

### POST `/api/swarm/dispatch`
**Description**: Dispatch complex commands to the 27-agent swarm.
**Request Body**:
```json
{
  "command": "/scan"
}
```

**Supported Commands**:

- `/scan`: Trigger vulnerability check.
- `/heal`: Run auto-remediation.
- `/status`: Return detailed agent health.

---
*Documentation updated for MR.VERMA 2.0*

## Real-time Communication

### WebSocket Connection

```javascript
// Client-side WebSocket connection
const ws = new WebSocket('wss://api.mrverma.ai/v1/realtime');

ws.onopen = function(event) {
    // Authenticate connection
    ws.send(JSON.stringify({
        type: 'auth',
        token: 'your_jwt_token'
    }));
};

ws.onmessage = function(event) {
    const message = JSON.parse(event.data);
    
    switch(message.type) {
        case 'workflow_update':
            handleWorkflowUpdate(message.data);
            break;
        case 'skill_completion':
            handleSkillCompletion(message.data);
            break;
        case 'agent_status_change':
            handleAgentStatusChange(message.data);
            break;
    }
};

// Subscribe to workflow updates
ws.send(JSON.stringify({
    type: 'subscribe',
    channels: ['workflow_updates', 'agent_status'],
    filter: {
        project_id: 'proj_123',
        user_id: 'user_456'
    }
}));
```

### Real-time Event Handler

```python
class RealtimeEventHandler:
    """Handle real-time events for WebSocket connections"""
    
    def __init__(self):
        self.connections = {}
        self.subscriptions = {}
    
    async def handle_connection(self, websocket, user_id: str):
        """Handle new WebSocket connection"""
        
        connection_id = str(uuid.uuid4())
        self.connections[connection_id] = {
            'websocket': websocket,
            'user_id': user_id,
            'connected_at': datetime.utcnow()
        }
        
        try:
            await self.send_initial_state(connection_id, user_id)
            
            async for message in websocket:
                await self.handle_message(connection_id, message)
                
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.cleanup_connection(connection_id)
    
    async def broadcast_event(self, event_type: str, data: dict, filter_criteria: dict = None):
        """Broadcast event to subscribed connections"""
        
        for connection_id, connection in self.connections.items():
            if filter_criteria and not self.matches_filter(connection, filter_criteria):
                continue
            
            try:
                await connection['websocket'].send(json.dumps({
                    'type': event_type,
                    'data': data,
                    'timestamp': datetime.utcnow().isoformat()
                }))
            except Exception as e:
                logger.error(f"Failed to send event to {connection_id}: {e}")
                await self.cleanup_connection(connection_id)
```

## Error Handling

### Error Categories

```python
class APIErrorCategories:
    """Categorized API errors"""
    
    CLIENT_ERRORS = {
        'INVALID_REQUEST': {'code': 4001, 'status': 400},
        'UNAUTHORIZED': {'code': 4010, 'status': 401},
        'FORBIDDEN': {'code': 4030, 'status': 403},
        'NOT_FOUND': {'code': 4040, 'status': 404},
        'RATE_LIMITED': {'code': 4290, 'status': 429},
        'VALIDATION_ERROR': {'code': 4220, 'status': 422}
    }
    
    SERVER_ERRORS = {
        'INTERNAL_ERROR': {'code': 5000, 'status': 500},
        'SERVICE_UNAVAILABLE': {'code': 5030, 'status': 503},
        'TIMEOUT': {'code': 5040, 'status': 504}
    }
    
    SKILL_ERRORS = {
        'SKILL_NOT_FOUND': {'code': 4100, 'status': 404},
        'SKILL_EXECUTION_FAILED': {'code': 4200, 'status': 500},
        'SKILL_TIMEOUT': {'code': 4201, 'status': 504},
        'INVALID_SKILL_PARAMETERS': {'code': 4202, 'status': 400}
    }
```

### Error Handler Implementation

```python
class APIErrorHandler:
    """Centralized error handling"""
    
    def __init__(self):
        self.error_loggers = {}
        self.error_handlers = {}
    
    async def handle_error(self, error: Exception, request: APIRequest) -> APIResponse:
        """Handle API errors and return appropriate response"""
        
        error_type = type(error).__name__
        
        # Log error with context
        await self.log_error(error, request)
        
        # Find appropriate error handler
        handler = self.error_handlers.get(error_type, self.default_error_handler)
        
        return await handler(error, request)
    
    async def log_error(self, error: Exception, request: APIRequest):
        """Log error with full context"""
        
        error_context = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'request_id': request.request_id,
            'user_id': request.user_id,
            'endpoint': f"{request.method} {request.path}",
            'timestamp': datetime.utcnow().isoformat(),
            'stack_trace': traceback.format_exc() if settings.DEBUG else None
        }
        
        logger.error(f"API Error: {error_context}")
        
        # Send to monitoring system
        await self.send_to_monitoring(error_context)
```

## Rate Limiting

### Rate Limiter Implementation

```python
class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.limits = {
            'anonymous': {'requests': 20, 'window': 60},  # 20 requests per minute
            'basic': {'requests': 100, 'window': 60},     # 100 requests per minute
            'premium': {'requests': 500, 'window': 60},   # 500 requests per minute
            'enterprise': {'requests': 2000, 'window': 60} # 2000 requests per minute
        }
    
    def check_limit(self, client_id: str, tier: str = 'anonymous') -> RateLimitResult:
        """Check if request is within rate limit"""
        
        limit = self.limits.get(tier, self.limits['anonymous'])
        key = f"rate_limit:{client_id}:{tier}"
        
        try:
            current = self.redis_client.incr(key)
            if current == 1:
                self.redis_client.expire(key, limit['window'])
            
            if current > limit['requests']:
                ttl = self.redis_client.ttl(key)
                return RateLimitResult(
                    allowed=False,
                    exceeded=True,
                    reset_time=datetime.utcnow() + timedelta(seconds=ttl),
                    retry_after=ttl
                )
            
            return RateLimitResult(
                allowed=True,
                exceeded=False,
                remaining=limit['requests'] - current,
                reset_time=datetime.utcnow() + timedelta(seconds=limit['window'])
            )
            
        except redis.RedisError:
            # Fail open if Redis is unavailable
            return RateLimitResult(allowed=True, exceeded=False)
```

## SDKs and Client Libraries

### Python SDK

```python
# Installation: pip install mrverma-api

from mrverma import MRVerseAPI

# Initialize client
client = MRVerseAPI(
    api_key="your_api_key",
    base_url="https://api.mrverma.ai/v1"
)

# Execute a skill
result = client.skills.execute(
    skill_name="code_analyzer",
    parameters={
        "code": "def hello(): print('world')",
        "language": "python"
    }
)

print(f"Security score: {result['security_score']}")

# Start a workflow
workflow = client.workflows.start(
    workflow_name="multi_agent_code_review",
    parameters={
        "repository_url": "https://github.com/example/repo.git",
        "branch": "main"
    }
)

# Monitor progress
while workflow.status != "completed":
    status = client.workflows.get_status(workflow.id)
    print(f"Progress: {status.progress.percentage}%")
    time.sleep(5)
```

### JavaScript SDK

```javascript
// Installation: npm install mrverma-api

const { MRVerseAPI } = require('mrverma-api');

// Initialize client
const client = new MRVerseAPI({
    apiKey: 'your_api_key',
    baseURL: 'https://api.mrverma.ai/v1'
});

// Execute skill with async/await
async function analyzeCode() {
    try {
        const result = await client.skills.execute({
            skillName: 'code_analyzer',
            parameters: {
                code: 'console.log("Hello World");',
                language: 'javascript'
            }
        });
        
        console.log('Analysis complete:', result);
    } catch (error) {
        console.error('Analysis failed:', error);
    }
}

// Real-time WebSocket connection
client.realtime.connect({
    token: 'your_jwt_token',
    onWorkflowUpdate: (update) => {
        console.log('Workflow updated:', update);
    },
    onSkillCompletion: (result) => {
        console.log('Skill completed:', result);
    }
});
```

### cURL Examples

```bash
# Execute a skill
curl -X POST https://api.mrverma.ai/v1/skills/execute \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill_name": "code_analyzer",
    "parameters": {
      "code": "print(\"Hello World\")",
      "language": "python"
    }
  }'

# Start a workflow
curl -X POST https://api.mrverma.ai/v1/workflows/start \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_name": "multi_agent_code_review",
    "parameters": {
      "repository_url": "https://github.com/example/repo.git"
    }
  }'

# Check workflow status
curl -X GET https://api.mrverma.ai/v1/workflows/wf_123/status \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## API Versioning

### Version Strategy

```python
class APIVersionManager:
    """Manage API versioning and compatibility"""
    
    def __init__(self):
        self.current_version = "1.0.0"
        self.supported_versions = ["1.0.0", "0.9.0"]
        self.deprecation_schedule = {
            "0.9.0": "2024-06-01",
            "0.8.0": "2024-03-01"
        }
    
    def validate_version(self, version: str) -> bool:
        """Check if API version is supported"""
        return version in self.supported_versions
    
    def get_deprecation_info(self, version: str) -> dict:
        """Get deprecation information for version"""
        if version in self.deprecation_schedule:
            return {
                'deprecated': True,
                'sunset_date': self.deprecation_schedule[version],
                'migration_guide': f'https://docs.mrverma.ai/migration/{version}'
            }
        return {'deprecated': False}
    
    def transform_request(self, request: dict, from_version: str, to_version: str) -> dict:
        """Transform request between API versions"""
        
        if from_version == to_version:
            return request
        
        # Apply transformation rules
        transformer = self.get_transformer(from_version, to_version)
        return transformer.transform(request)
```

### Version Header

```http
GET /v1/agents HTTP/1.1
Host: api.mrverma.ai
Authorization: Bearer YOUR_API_KEY
API-Version: 1.0.0
Accept-Version: 1.0.0
```

### Deprecation Response Headers

```http
HTTP/1.1 200 OK
Content-Type: application/json
API-Version: 1.0.0
X-API-Deprecation-Date: 2024-06-01
X-API-Sunset-Date: 2024-12-01
X-API-Deprecation-Link: https://docs.mrverma.ai/deprecation/0.9.0
```

---

This API documentation provides a comprehensive guide for integrating with the MR.VERMA system. For additional support, please contact the development team or refer to the interactive API explorer at <https://api.mrverma.ai/docs>.
