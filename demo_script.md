# Screen Recording Demo Script

This document outlines how to record the 3-minute Loom video for your submission to perfectly highlight the engineering choices you made.

## Setup
1. Have Postman (or ThunderClient/cURL) ready with tabs for `/roadmap`, `/project`, and `/chat`.
2. Have your IDE open showing `app/services/llm.py` (retry logic) and `app/api/endpoints.py` (validation).
3. Start the server using `uvicorn app.main:app`.

## The Run-Through

### 1. Show the Validation & Generation (`/roadmap`)
* **Action:** Send a `POST /roadmap` with `goal_title: "Full Stack Developer"`, `weekly_hours: 15`.
* **Speak:** "First, I'm generating a roadmap. The API takes the user's constraints and returns a structured roadmap using Gemini's structured output. Notice it returns exactly the nested schema we defined."
* **Action:** Copy the returned `roadmap_id`.

### 2. Show the Dual-Input Validator (`/project`)
* **Action:** Send a `POST /project` using **just** the `roadmap_id` you copied.
* **Speak:** "For the project endpoint, I built a Pydantic `model_validator`. You can pass either the `roadmap_id` alone, OR a custom `goal_title` and `skills`. If you try to pass both, or neither, the API explicitly rejects it with a 422. Here, I'm passing the roadmap ID to generate a personalized capstone."

### 3. The RAG Retrieval Demonstration (`/chat`)
This is the most critical part of your demo.
* **Action:** In your generated roadmap, find a specific task (e.g., "Learn Docker").
* **Speak:** "Now for the RAG chat. When the roadmap was generated, it was asynchronously chunked and embedded into a local Qdrant memory instance. I'm going to ask a question specifically about one of the tasks: 'How do I start learning Docker?'"
* **Action:** Send `POST /chat` with the question.
* **Speak:** "The system embeds my query, does a cosine similarity search against Qdrant, filters by this specific `roadmap_id`, and feeds only the relevant chunks to the LLM to answer. If I ask a completely unrelated question (e.g. 'How do I cook pasta?'), the retrieval threshold drops it and it safely returns an empty context handler."

### 4. Highlight the Engineering Depth
* **Action:** Switch to your IDE showing `app/services/llm.py`.
* **Speak:** "Finally, one detail I want to highlight is the LLM retry logic. If Gemini fails to output the strict JSON schema, my service catches the `ValidationError` and retries the prompt *while feeding the error string back to the model* so it can correct its own missing fields."

**Wrap Up:** "That's the Learning Assistant backend — fully typed, resilient, and ready for deployment."
