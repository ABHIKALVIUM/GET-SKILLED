# AI Learning Assistant (GetSetSkilled Internship Assignment)

## Overview
A FastAPI backend service powered by Gemini 2.5 Flash and Qdrant. It generates personalized learning roadmaps, recommends capstone projects, and provides a conversational RAG interface over the generated roadmap chunks.

## Live Demo

> **Interactive API Docs:** [https://get-skilled.onrender.com/docs](https://get-skilled.onrender.com/docs)
>
> ⚠️ Hosted on Render free tier — the server may take ~30 seconds to wake up on first request (cold start). Once awake, all endpoints respond normally.
>
> ⚠️ Qdrant runs in `:memory:` mode. Call `POST /roadmap` first to generate a roadmap ID, then use that ID for `/project` and `/chat` in the same session.

## Architecture

1. **API Layer (FastAPI):** Handles input validation using Pydantic (including complex `model_validator` edge cases for dual-input paths).
2. **LLM Service (Google GenAI):** Uses `google-genai` SDK for native structured output (avoiding gRPC hangs common in older SDKs). Includes a retry-with-feedback mechanism.
3. **RAG Service (Qdrant `memory` mode):** Embeds task chunks using `gemini-embedding-2` (size 3072) and stores them via Qdrant's local memory client for fast semantic search.

## Setup Instructions

1. Ensure Python 3.10+ is installed.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install fastapi uvicorn google-genai qdrant-client pydantic pydantic-settings python-dotenv pytest
   ```
4. Configure your `.env` file in the root directory:
   ```
   GEMINI_API_KEY=your_gemini_key
   ```
5. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

## Design Decisions & Assumptions

- **Stateless App with In-Memory Stores:** Per assignment requirements to "mock the DB," the system uses dependency-injected singletons (`roadmap_store`, `session_store`) and Qdrant in `:memory:` mode. If the server restarts, data is lost.
- **RAG on Single Documents:** Applying RAG to a single document (the roadmap) can sometimes retrieve disjointed subtasks. We mitigate this by chunking at the `Task` level (incorporating subtask titles) to preserve semantic context.
- **Async I/O:** Qdrant's synchronous python bindings for `:memory:` mode are wrapped in `asyncio.to_thread()` to prevent blocking the FastAPI event loop during upserts and retrieval.
- **Session ID Silent Reset:** An unrecognized `session_id` provided to `/chat` is treated as the start of a new session rather than an error, trading strict detectability for resilience. A client restart shouldn't be blocked by a 404.
- **Goal Title Validation:** Empty or whitespace-only goal strings are rejected at the Pydantic layer (`min_length=1`) to prevent sending nonsensical prompts to the LLM.

## Prompt Design Decisions

1. **System Instructions over Prompt Stuffing:** For generating roadmaps and projects, the complex rules (like avoiding hallucinations and keeping JSON structured) are fed as System Instructions, keeping the user-input prompt clean and focused purely on their parameters (goal, skills, hours).
2. **Context-Grounded Prompts (RAG):** For the Chat endpoint, the prompt explicitly injects the retrieved roadmap chunks as `Context:` and adds strict instructions to *"Only use the context provided. If the answer is not in the context, say 'No relevant section of your roadmap matched that question.'"* This prevents the LLM from hallucinating knowledge outside the generated roadmap.
3. **Structured Output Enforcement:** Instead of using prompt engineering to say "Respond in JSON format like...", we natively bind Pydantic schemas directly into the `google-genai` SDK (`response_schema`), forcing the API to guarantee the output format.

## AI Tools Used
Used an AI assistant to iteratively pressure-test the design against likely reviewer questions across multiple rounds. All architectural decisions — chunking strategy, retry mechanism, async approach, dual-input validation, and threshold calibration — were reasoned through with that process and implemented manually.

## Testing
Unit tests are fully mocked to prevent LLM latency and non-determinism during testing.
Run tests using:
```bash
pytest tests/
```

## Deploying to Render

1. Push this repository to GitHub.
2. Go to [render.com](https://render.com) and create a free account.
3. Click **New → Web Service** and connect your GitHub repository.
4. Configure the service:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port 10000`
5. Under **Environment Variables**, add:
   - `GEMINI_API_KEY` → your Gemini API key
6. Click **Deploy**. Once live, your Swagger UI will be at `https://your-app.onrender.com/docs`.
