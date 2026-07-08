import os
import asyncio
import google.generativeai as genai
from pydantic import BaseModel
from typing import List
import json
import logging

logging.basicConfig(level=logging.INFO)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

genai.configure(api_key=api_key)

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

model = genai.GenerativeModel(
    "gemini-3.5-flash",
    generation_config=genai.GenerationConfig(
        response_mime_type="application/json",
        response_schema=RoadmapResponse,
    )
)

PROMPTS = [
    "Generate a Backend Developer roadmap for a beginner.",
    "Create a learning roadmap for someone who wants to become a Data Scientist with 1 year experience.",
    "Build a roadmap for learning DevOps from scratch, weekly hours: 10.",
]

async def main():
    for i, p in enumerate(PROMPTS):
        for run in range(2):
            print(f"\n--- Prompt {i} | Run {run} ---")
            try:
                r = await model.generate_content_async(p)
                try:
                    result = RoadmapResponse.model_validate_json(r.text)
                    print(f"OK — Parsed {len(result.tasks)} tasks.")
                except Exception as e:
                    print(f"FAIL (Validation Error) — {e}")
                    print(f"Raw output snippet: {r.text[:500]}")
            except Exception as e:
                print(f"FAIL (Generation Error) — {e}")

if __name__ == "__main__":
    asyncio.run(main())
