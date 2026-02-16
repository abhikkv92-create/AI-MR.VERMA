import pytest
import asyncio
import sys
import os
from unittest.mock import AsyncMock, MagicMock, patch
from dotenv import load_dotenv

# Load env vars for tests
load_dotenv()

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.ai.vision_engine import VisionAIEngine
from core.memory_service import MemoryService
from core.orchestrator import SupremeOrchestrator

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_vision_engine():
    with patch("core.ai.vision_engine.VisionAIEngine.analyze") as mock_analyze:
        # Default behavior: Return a standard response
        mock_analyze.return_value = "A generated description of the scene."
        yield mock_analyze

@pytest.fixture
def mock_memory_service():
    with patch("core.memory_service.memory_service") as mock_service:
        mock_service.store = AsyncMock(return_value=True)
        mock_service.store_visual_memory = AsyncMock(return_value=True)
        mock_service.search = AsyncMock(return_value=[])
        mock_service.connect = MagicMock(return_value=True)
        yield mock_service

@pytest.fixture
def orchestrator(mock_vision_engine, mock_memory_service):
    # Initialize orchestrator with mocked dependencies where possible
    # We patch the internal engines of the orchestrator instance
    orch = SupremeOrchestrator()
    orch.vision_engine.analyze = mock_vision_engine
    
    # Mock Vision Queue submission
    async def mock_submit(func, *args, **kwargs):
        if asyncio.iscoroutinefunction(func):
             res = await func(*args, **kwargs)
        else:
             res = func(*args, **kwargs)
        f = asyncio.Future()
        f.set_result(res)
        return f
        
    orch.vision_queue = MagicMock()
    orch.vision_queue.submit = mock_submit
    
    return orch

@pytest.fixture
def huge_dummy_image(tmp_path):
    # Create a 10MB dummy file
    p = tmp_path / "huge_image.png"
    p.write_bytes(b"\x00" * (10 * 1024 * 1024))
    return str(p)

@pytest.fixture
def corrupt_dummy_image(tmp_path):
    p = tmp_path / "corrupt.png"
    p.write_bytes(b"Not an image")
    return str(p)
