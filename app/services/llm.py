from google import genai
from google.genai import types
from pydantic import BaseModel, ValidationError
from typing import Type, TypeVar, List
import logging
from app.config import settings

logger = logging.getLogger(__name__)

client = genai.Client(api_key=settings.gemini_api_key)

T = TypeVar("T", bound=BaseModel)

class LLMParsingError(Exception):
    pass

async def generate_structured(prompt: str, schema_type: Type[T]) -> T:
    """
    Generates structured output matching the schema_type.
    Includes a 1-attempt retry loop with error feedback if Pydantic validation fails.
    """
    for attempt in range(2):
        if attempt > 0:
            logger.info("Retrying LLM structured generation with error feedback...")
            
        try:
            response = await client.aio.models.generate_content(
                model=settings.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=schema_type,
                )
            )
            return schema_type.model_validate_json(response.text)
        except ValidationError as e:
            if attempt == 0:
                # Provide the error feedback for the second attempt
                prompt += f"\n\nPrevious attempt failed validation with error:\n{e}\nPlease correct the JSON output to match the required schema exactly."
            else:
                logger.error(f"Failed to parse LLM output after 2 attempts: {e}")
                logger.error(f"Raw output: {response.text if 'response' in locals() else 'None'}")
                raise LLMParsingError("LLM output failed validation after 2 attempts.") from e
        except Exception as e:
            logger.error(f"LLM API Error during generation: {e}")
            raise

async def embed_text(text: str) -> List[float]:
    """
    Generates an embedding vector for the given text.
    """
    try:
        response = await client.aio.models.embed_content(
            model='gemini-embedding-2',
            contents=text
        )
        return response.embeddings[0].values
    except Exception as e:
        logger.error(f"LLM API Error during embedding: {e}")
        raise
