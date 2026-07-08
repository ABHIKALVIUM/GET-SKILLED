import uuid
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from qdrant_client import QdrantClient
import logging

from app.models.roadmap import RoadmapRequest, RoadmapResponse
from app.models.project import ProjectRequest, ProjectResponse
from app.models.chat import ChatRequest, ChatResponse
from app.services.llm import generate_structured, LLMParsingError
from app.services.rag import index_roadmap, retrieve
from app.dependencies import get_roadmap_store, get_session_store, get_qdrant

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/roadmap", response_model=Dict[str, Any])
async def create_roadmap(
    request: RoadmapRequest,
    roadmap_store: Dict[str, Any] = Depends(get_roadmap_store),
    qdrant: QdrantClient = Depends(get_qdrant)
):
    prompt = (
        f"Generate a highly detailed, professional learning roadmap for the goal: '{request.goal_title}'.\n"
        f"The user has {request.weekly_hours} hours available per week.\n"
        f"The user already knows these skills: {', '.join(request.known_skills) if request.known_skills else 'None (Beginner)'}.\n"
        "Return the roadmap structured exactly according to the required schema."
    )
    
    try:
        roadmap_response = await generate_structured(prompt, RoadmapResponse)
    except LLMParsingError as e:
        logger.error(f"LLM Parsing failed for roadmap: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, 
            detail="Upstream AI provider failed to return a valid structured response."
        )
    except Exception as e:
        logger.error(f"Unexpected error during roadmap generation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
        
    roadmap_id = str(uuid.uuid4())
    roadmap_store[roadmap_id] = roadmap_response
    
    try:
        await index_roadmap(qdrant, roadmap_id, roadmap_response)
    except Exception as e:
        logger.error(f"Failed to index roadmap: {e}")
        raise HTTPException(status_code=500, detail="Failed to index roadmap for semantic search.")
        
    return {
        "roadmap_id": roadmap_id,
        "roadmap": roadmap_response.model_dump()
    }

@router.post("/project", response_model=ProjectResponse)
async def generate_project(
    request: ProjectRequest,
    roadmap_store: Dict[str, Any] = Depends(get_roadmap_store)
):
    # Depending on input paths
    if request.roadmap_id:
        if request.roadmap_id not in roadmap_store:
            raise HTTPException(status_code=404, detail="Roadmap ID not found.")
        roadmap_data = roadmap_store[request.roadmap_id]
        
        prompt = (
            f"Given the following learning roadmap:\n{roadmap_data.model_dump_json()}\n"
            "Generate a capstone project idea that applies these skills."
        )
    else:
        # Path B: goal_title and skills
        prompt = (
            f"Given the learning goal: '{request.goal_title}' and the skills: {request.skills},\n"
            "Generate a capstone project idea that applies these skills."
        )
        
    try:
        project_response = await generate_structured(prompt, ProjectResponse)
        return project_response
    except LLMParsingError as e:
        logger.error(f"LLM Parsing failed for project: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, 
            detail="Upstream AI provider failed to return a valid structured response."
        )
    except Exception as e:
        logger.error(f"Unexpected error during project generation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    roadmap_store: Dict[str, Any] = Depends(get_roadmap_store),
    session_store: Dict[str, Any] = Depends(get_session_store),
    qdrant: QdrantClient = Depends(get_qdrant)
):
    if request.roadmap_id not in roadmap_store:
        raise HTTPException(status_code=404, detail="Roadmap ID not found.")
        
    # Handle session history
    session_id = request.session_id
    if not session_id or session_id not in session_store:
        # Note on unknown session_id: A client with a typo in session_id will silently 
        # start a fresh conversation. This trades detectability for resilience.
        session_id = str(uuid.uuid4())
        session_store[session_id] = []
        
    history = session_store[session_id]
    
    # RAG Retrieval
    try:
        retrieved_context = await retrieve(qdrant, request.roadmap_id, request.question)
    except Exception as e:
        logger.error(f"Qdrant retrieval error: {e}")
        retrieved_context = ""
        
    if not retrieved_context:
        # Assignment specifies: if no relevant sections, respond accordingly
        return ChatResponse(
            response="No relevant section of your roadmap matched that question.",
            follow_up_questions=[],
            session_id=session_id
        )
        
    # Format the prompt
    history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history[-5:]]) # keep last 5 turns
    prompt = (
        f"You are an AI learning assistant. Use the following roadmap sections to answer the user's question.\n"
        f"Roadmap context:\n{retrieved_context}\n\n"
        f"Conversation History:\n{history_str}\n\n"
        f"User Question: {request.question}\n"
    )
    
    try:
        chat_response = await generate_structured(prompt, ChatResponse)
        chat_response.session_id = session_id
        
        # Append to history
        history.append({"role": "user", "content": request.question})
        history.append({"role": "assistant", "content": chat_response.response})
        
        return chat_response
    except LLMParsingError as e:
        logger.error(f"LLM Parsing failed for chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, 
            detail="Upstream AI provider failed to return a valid structured response."
        )
    except Exception as e:
        logger.error(f"Unexpected error during chat generation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
