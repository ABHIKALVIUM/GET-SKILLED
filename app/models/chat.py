from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    roadmap_id: str
    session_id: Optional[str] = None
    question: str

class ChatResponse(BaseModel):
    response: str
    follow_up_questions: List[str]
    session_id: str
