import pytest
from app.main import app

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_roadmap_success(client, mock_generate_structured, mock_index_roadmap, sample_roadmap_response):
    mock_generate_structured.return_value = sample_roadmap_response
    
    payload = {
        "goal_title": "Backend Dev",
        "weekly_hours": 10,
        "known_skills": ["Python"]
    }
    response = client.post("/roadmap", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "roadmap_id" in data
    assert "roadmap" in data
    assert data["roadmap"]["estimated_hours"] == 100
    
    mock_generate_structured.assert_called_once()
    mock_index_roadmap.assert_called_once()

def test_project_dual_input_validation(client):
    # Missing both
    response = client.post("/project", json={})
    assert response.status_code == 422
    
    # Missing skills for Path B
    response = client.post("/project", json={"goal_title": "Python Developer"})
    assert response.status_code == 422
    
    # Having both roadmap_id and goal_title
    response = client.post("/project", json={
        "roadmap_id": "some-id",
        "goal_title": "Python Developer",
        "skills": ["Python"]
    })
    assert response.status_code == 422

def test_project_path_a_success(client, mock_generate_structured, sample_roadmap_response, sample_project_response):
    # Setup state
    roadmap_id = "test-id"
    app.state.app_state.roadmap_store[roadmap_id] = sample_roadmap_response
    mock_generate_structured.return_value = sample_project_response
    
    response = client.post("/project", json={"roadmap_id": roadmap_id})
    assert response.status_code == 200
    assert response.json()["project_title"] == "CLI App"

def test_project_path_a_not_found(client):
    response = client.post("/project", json={"roadmap_id": "non-existent"})
    assert response.status_code == 404

def test_project_path_b_success(client, mock_generate_structured, sample_project_response):
    mock_generate_structured.return_value = sample_project_response
    
    response = client.post("/project", json={
        "goal_title": "Learn AI",
        "skills": ["Python", "FastAPI"]
    })
    assert response.status_code == 200
    assert response.json()["project_title"] == "CLI App"

def test_chat_success(client, mock_generate_structured, mock_retrieve, sample_roadmap_response, sample_chat_response):
    roadmap_id = "test-id"
    app.state.app_state.roadmap_store[roadmap_id] = sample_roadmap_response
    mock_retrieve.return_value = "Retrieved context"
    mock_generate_structured.return_value = sample_chat_response
    
    response = client.post("/chat", json={
        "roadmap_id": roadmap_id,
        "question": "What is next?"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "Here is the answer based on the roadmap."
    assert "session_id" in data
