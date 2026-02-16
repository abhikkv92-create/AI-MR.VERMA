# Integration Tests

## Overview

Integration tests verify that MR.VERMA components work correctly with real API connections and data.

---

## Prerequisites

Before running integration tests:

1. **Valid API Keys**: Ensure your `.env` file contains valid NVIDIA API keys
2. **Network Access**: Verify connectivity to NVIDIA API endpoints
3. **Test Data**: Some tests require sample files in `tests/fixtures/`

---

## Running Integration Tests

### Basic Integration Test

```bash
# Run with pytest
python -m pytest tests/integration/ -v

# Run specific test
python -m pytest tests/integration/test_nvidia_api.py -v
```

### Environment Setup

```bash
# Set test environment
export ENV=test
export NVIDIA_API_KEY=test_key_here

# Run tests
python -m pytest tests/integration/ --cov=mr_verma
```

---

## Test Categories

### 1. API Integration Tests

Tests for external API connectivity:

```python
# tests/integration/test_nvidia_api.py
import pytest
from core.ai.primary_engine import PrimaryAIEngine
from core.env_manager import load_env_file

@pytest.fixture
def engine():
    load_env_file()
    return PrimaryAIEngine()

@pytest.mark.integration
@pytest.mark.asyncio
async def test_nvidia_api_connection(engine):
    """Test basic connectivity to NVIDIA API."""
    result = await engine.generate(
        messages=[{"role": "user", "content": "Hello"}],
        stream=False
    )
    assert result is not None
    assert "choices" in result
```

### 2. Agent Integration Tests

Tests for agent functionality with real AI:

```python
# tests/integration/test_agents.py
import pytest
from agents import DataScientist, SecurityArchitect

@pytest.mark.integration
@pytest.mark.asyncio
async def test_data_scientist_log_analysis():
    """Test DataScientist agent with real log analysis."""
    agent = DataScientist()
    agent.start()
    
    # Create test log
    with open("logs/test.log", "w") as f:
        f.write("2026-02-16 ERROR: Database connection failed\n")
        f.write("2026-02-16 WARNING: High memory usage\n")
    
    result = await agent.process_task({
        "mode": "ai_log_analysis",
        "log_file": "logs/test.log"
    })
    
    assert result["status"] == "AI Log Analysis Complete"
    assert "analysis" in result
    agent.stop()
```

### 3. End-to-End Tests

Full workflow tests:

```python
# tests/integration/test_e2e.py
import pytest
from core.orchestrator import SupremeOrchestrator
from core.env_manager import load_env_file

@pytest.mark.integration
@pytest.mark.e2e
@pytest.mark.asyncio
async def test_full_workflow():
    """Test complete request processing workflow."""
    load_env_file()
    
    orchestrator = SupremeOrchestrator()
    
    result = await orchestrator.process_request(
        "Analyze this Python code for security issues",
        stream=False
    )
    
    assert result["status"] == "SUCCESS"
    assert "response" in result
    assert len(result["agents_invoked"]) > 0
```

---

## Test Configuration

### pytest.ini

```ini
[pytest]
testpaths = tests
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    unit: Unit tests (fast, no external deps)
    integration: Integration tests (requires API keys)
    e2e: End-to-end tests (full system)
    slow: Tests that take > 5 seconds

addopts =
    -v
    --tb=short
    --strict-markers
```

### conftest.py

```python
# tests/integration/conftest.py
import pytest
import asyncio

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def api_keys():
    """Load API keys for integration tests."""
    from core.env_manager import load_env_file
    load_env_file()
    return {
        "nvidia": os.environ.get("NVIDIA_API_KEY"),
        "nvidia_secondary": os.environ.get("NVIDIA_API_KEY_SECONDARY"),
    }
```

---

## Mock vs Real Tests

### When to Use Mocks

Use mocks for:
- Unit tests (fast feedback)
- CI/CD pipelines (no API costs)
- Testing error handling
- Offline development

### When to Use Real APIs

Use real APIs for:
- Integration tests (verify actual behavior)
- Before releases (validate production readiness)
- Performance testing
- Compatibility checks

### Hybrid Approach

```python
@pytest.mark.parametrize("use_real_api", [True, False])
async def test_with_option(use_real_api):
    if use_real_api:
        engine = PrimaryAIEngine()
    else:
        engine = MockEngine()
    
    result = await engine.generate(...)
    assert result is not None
```

---

## Performance Tests

### Response Time Tests

```python
import time

@pytest.mark.performance
@pytest.mark.asyncio
async def test_response_time():
    """Verify API response time is acceptable."""
    engine = PrimaryAIEngine()
    
    start = time.time()
    result = await engine.generate(
        messages=[{"role": "user", "content": "Hello"}],
        stream=False
    )
    elapsed = time.time() - start
    
    assert elapsed < 10.0, f"Response took {elapsed}s, expected < 10s"
```

### Load Tests

```python
@pytest.mark.stress
@pytest.mark.asyncio
async def test_concurrent_requests():
    """Test handling multiple concurrent requests."""
    engine = PrimaryAIEngine()
    
    tasks = [
        engine.generate(
            messages=[{"role": "user", "content": f"Request {i}"}],
            stream=False
        )
        for i in range(10)
    ]
    
    results = await asyncio.gather(*tasks)
    assert all(r is not None for r in results)
```

---

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/integration-tests.yml
name: Integration Tests

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio
      
      - name: Run integration tests
        env:
          NVIDIA_API_KEY: ${{ secrets.NVIDIA_API_KEY }}
        run: |
          pytest tests/integration/ -v --tb=short
```

---

## Troubleshooting

### Common Issues

**1. API Rate Limits**
```python
# Add rate limiting between tests
import time
time.sleep(1)  # Wait between requests
```

**2. Timeouts**
```python
# Increase timeout for slow tests
@pytest.mark.timeout(60)
async def test_slow_operation():
    ...
```

**3. Flaky Tests**
```python
# Retry flaky tests
@pytest.mark.flaky(reruns=3, reruns_delay=5)
async def test_network_dependent():
    ...
```

---

## Test Data Management

### Fixture Files

Store test data in `tests/fixtures/`:

```
tests/fixtures/
├── sample_code.py
├── sample_logs/
│   ├── system.log
│   └── error.log
├── images/
│   ├── test.png
│   └── test.jpg
└── configs/
    └── test.env
```

### Loading Fixtures

```python
import pytest
from pathlib import Path

@pytest.fixture
def sample_code():
    """Load sample code for testing."""
    return Path("tests/fixtures/sample_code.py").read_text()
```

---

## Best Practices

1. **Isolate Tests**: Each test should be independent
2. **Clean State**: Reset state between tests
3. **Use Markers**: Mark tests appropriately (unit, integration, e2e)
4. **Document**: Add docstrings explaining test purpose
5. **Monitor Costs**: Track API usage during integration tests
6. **Parallelize**: Use pytest-xdist for faster execution

---

## Running Tests by Category

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# Run specific marker combinations
pytest -m "integration and not slow"
```
