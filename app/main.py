from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.dependencies import AppState

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the app state (in-memory stores and Qdrant)
    app.state.app_state = AppState()
    # Here we would initialize the Qdrant collection if needed.
    # Qdrant :memory: collections are created on first use if not checking, but explicit is better.
    # We will let the rag service handle collection creation/verification.
    yield
    # Cleanup logic if any
    pass

from app.api.endpoints import router as api_router

app = FastAPI(
    title="AI Learning Assistant",
    description="FastAPI service for generating and querying learning roadmaps",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(api_router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
