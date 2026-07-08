import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app
from app.models.roadmap import RoadmapResponse, Task, Subtask
from app.models.project import ProjectResponse
from app.models.chat import ChatResponse
from app.dependencies import AppState

@pytest.fixture(autouse=True)
def setup_app_state():
    """Ensure AppState is initialized for tests without lifespan."""
    app.state.app_state = AppState()
    yield

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_generate_structured():
    with patch('app.api.endpoints.generate_structured', new_callable=AsyncMock) as mock:
        yield mock

@pytest.fixture
def mock_index_roadmap():
    with patch('app.api.endpoints.index_roadmap', new_callable=AsyncMock) as mock:
        yield mock

@pytest.fixture
def mock_retrieve():
    with patch('app.api.endpoints.retrieve', new_callable=AsyncMock) as mock:
        yield mock

@pytest.fixture
def sample_roadmap_response():
    return RoadmapResponse(
        estimated_hours=100,
        skills=["Python"],
        tasks=[
            Task(
                title="Learn Python Basics",
                estimated_hours=20,
                subtasks=[Subtask(title="Variables")]
            )
        ]
    )

@pytest.fixture
def sample_project_response():
    return ProjectResponse(
        project_title="CLI App",
        description="A command line tool",
        required_skills=["Python"],
        complexity="Beginner"
    )

@pytest.fixture
def sample_chat_response():
    return ChatResponse(
        response="Here is the answer based on the roadmap.",
        follow_up_questions=["Any other questions?"],
        session_id="test-session-id"
    )
