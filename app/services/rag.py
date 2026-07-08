import uuid
import asyncio
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from app.models.roadmap import RoadmapResponse
from app.services.llm import embed_text

COLLECTION_NAME = "roadmaps"
EMBEDDING_SIZE = 3072  # Size for gemini-embedding-2

def _ensure_collection_sync(qdrant: QdrantClient):
    if not qdrant.collection_exists(COLLECTION_NAME):
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=EMBEDDING_SIZE, distance=Distance.COSINE),
        )

def _upsert_sync(qdrant: QdrantClient, points: list):
    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

async def index_roadmap(qdrant: QdrantClient, roadmap_id: str, roadmap: RoadmapResponse):
    await asyncio.to_thread(_ensure_collection_sync, qdrant)
    
    points = []
    for task in roadmap.tasks:
        sub_titles = [s.title for s in task.subtasks]
        chunk_text = f"Task: {task.title}. Subtasks: {', '.join(sub_titles)}."
        
        vector = await embed_text(chunk_text)
        
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "roadmap_id": roadmap_id,
                    "text": chunk_text
                }
            )
        )
    
    await asyncio.to_thread(_upsert_sync, qdrant, points)

def _search_sync(qdrant: QdrantClient, query_vector: list, roadmap_id: str, threshold: float):
    if not qdrant.collection_exists(COLLECTION_NAME):
        return []
        
    response = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="roadmap_id",
                    match=MatchValue(value=roadmap_id)
                )
            ]
        ),
        limit=3,
        score_threshold=threshold
    )
    return response.points

async def retrieve(qdrant: QdrantClient, roadmap_id: str, query: str, threshold: float = 0.4) -> str:
    query_vector = await embed_text(query)
    
    results = await asyncio.to_thread(_search_sync, qdrant, query_vector, roadmap_id, threshold)
    
    if not results:
        return ""
        
    return "\n".join([hit.payload["text"] for hit in results])
