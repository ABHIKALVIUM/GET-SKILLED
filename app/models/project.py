from pydantic import BaseModel, Field, model_validator
from typing import List, Optional

class ProjectRequest(BaseModel):
    roadmap_id: Optional[str] = None
    goal_title: Optional[str] = Field(default=None, min_length=1)
    skills: Optional[List[str]] = None

    @model_validator(mode="after")
    def check_inputs(self):
        has_id = bool(self.roadmap_id)
        has_goal = bool(self.goal_title)
        has_skills = self.skills is not None
        
        # Valid path A: Only roadmap_id
        if has_id and not has_goal and not has_skills:
            return self
            
        # Valid path B: Only goal_title + skills
        if not has_id and has_goal and has_skills:
            return self
            
        raise ValueError("Must provide EXACTLY EITHER roadmap_id OR (goal_title AND skills)")

class ProjectResponse(BaseModel):
    project_title: str
    description: str
    required_skills: List[str]
    complexity: str
