from pydantic import BaseModel, Field
from typing import List, Optional

class RoadmapRequest(BaseModel):
    goal_title: str = Field(..., min_length=1)
    weekly_hours: int = Field(..., gt=0)
    known_skills: List[str]

class Subtask(BaseModel):
    title: str

class Task(BaseModel):
    title: str
    estimated_hours: int
    subtasks: List[Subtask]

class RoadmapResponse(BaseModel):
    estimated_hours: int
    skills: List[str]
    tasks: List[Task]
