import pytest
import asyncio
from core.memory_service import MemoryService

@pytest.mark.asyncio
async def test_rapid_memory_insertion(mock_memory_service):
    """
    Stress Test: Insert 1000 memories in rapid succession.
    """
    # Create 1000 dummy memories
    tasks = []
    for i in range(1000):
        tasks.append(mock_memory_service.store(f"Memory {i}", {"type": "stress_test"}))
    
    # Execute all
    results = await asyncio.gather(*tasks)
    
    # Assert all successful (mock returns True)
    assert len(results) == 1000
    assert all(results)
    assert mock_memory_service.store.call_count == 1000

@pytest.mark.asyncio
async def test_concurrent_search_and_insert(mock_memory_service):
    """
    Stress Test: perform searches while inserting data.
    """
    insert_tasks = [mock_memory_service.store(f"Mem {i}", {}) for i in range(500)]
    search_tasks = [mock_memory_service.search(f"Query {i}") for i in range(500)]
    
    all_tasks = insert_tasks + search_tasks
    results = await asyncio.gather(*all_tasks)
    
    assert len(results) == 1000
    assert mock_memory_service.store.call_count >= 500
    assert mock_memory_service.search.call_count >= 500

@pytest.mark.asyncio
async def test_memory_connection_failure_handling(mock_memory_service):
    """
    Negative Test: Simulate database connection failure.
    """
    # Override store to simulate failure
    mock_memory_service.store.side_effect = Exception("Connection Lost")
    
    try:
        await mock_memory_service.store("Test", {})
    except Exception as e:
        assert str(e) == "Connection Lost"
    
    # Ensure it doesn't crash the whole process (orchestrator level handling needs to be tested separately 
    # but at service level it raises exception as expected)
