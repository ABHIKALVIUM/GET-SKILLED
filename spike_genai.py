import os
import asyncio
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import List
import json
import logging

logging.basicConfig(level=logging.INFO)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

client = genai.Client(api_key=api_key)

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
                r = await client.aio.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=p,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=RoadmapResponse,
                    )
                )
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
