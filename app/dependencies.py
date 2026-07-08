from typing import Dict, Any
from qdrant_client import QdrantClient
from fastapi import Request

class AppState:
    def __init__(self):
        # In-memory stores required by the assignment
        self.roadmap_store: Dict[str, Any] = {}
        self.session_store: Dict[str, Any] = {}
        
        # Qdrant client in memory mode
        self.qdrant = QdrantClient(location=":memory:")

# The global state object, initialized during the FastAPI lifespan
_app_state: AppState | None = None

def get_app_state(request: Request) -> AppState:
    """Dependency to retrieve the initialized app state."""
    return request.app.state.app_state

def get_roadmap_store(request: Request) -> Dict[str, Any]:
    return get_app_state(request).roadmap_store

def get_session_store(request: Request) -> Dict[str, Any]:
    return get_app_state(request).session_store

def get_qdrant(request: Request) -> QdrantClient:
    return get_app_state(request).qdrant
