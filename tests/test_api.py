import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_chat_agent_not_initialized():
    # If the app starts without running lifespan, agent_graph is None.
    # The client does not run lifespan by default unless used as context manager:
    # with TestClient(app) as client: ...
    # So this should hit the 503 error.
    response = client.post("/chat", json={"question": "Test"})
    assert response.status_code == 503
    assert response.json()["detail"] == "Agent not initialized."

@pytest.mark.asyncio
async def test_chat_success(mocker):
    # Mock the internal invoke agent call
    mock_invoke = mocker.patch("app.main._invoke_agent", return_value={"answer": "Test answer", "tools_used": [], "data": None})
    
    # We must use context manager to trigger lifespan so agent_graph is not None
    # Wait, we can also mock agent_graph to just be a truthy value
    mocker.patch("app.main.agent_graph", True)
    
    response = client.post("/chat", json={"question": "Test question?"})
    assert response.status_code == 200
    assert response.json()["answer"] == "Test answer"
