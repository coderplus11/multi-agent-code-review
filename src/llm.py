"""Shared LLM factory."""

import os
import time
from google.genai.errors import ClientError, ServerError

from google.genai.errors import ServerError
from langchain_google_genai import ChatGoogleGenerativeAI

from src.config import MODEL
from src.logger import get_logger

_log = get_logger("llm")


def get_llm(temperature: float = 0) -> ChatGoogleGenerativeAI:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY / GOOGLE_API_KEY is missing from environment variables."
        )
    return ChatGoogleGenerativeAI(
        model=MODEL,
        temperature=temperature,
        google_api_key=api_key,
        max_retries=2,
    )


def invoke_with_retry(llm: ChatGoogleGenerativeAI, messages, retries: int = 4, base_delay: float = 10.0):
    """Call llm.invoke() with exponential backoff on transient 503/UNAVAILABLE errors."""
    for attempt in range(1, retries + 1):
        try:
            return llm.invoke(messages)
        except ServerError as e:
            if attempt == retries:
                raise
            delay = base_delay * (2 ** (attempt - 1))
            _log.warning(
                "Gemini returned a transient server error (attempt %d/%d): %s. Retrying in %.0fs...",
                attempt, retries, e, delay,
            )
            time.sleep(delay)
        except ClientError as e:
            if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
                raise RuntimeError(
                    "Gemini API quota exceeded (free tier daily limit hit). "
                    "Enable billing on your Google AI Studio project or wait for the daily reset."
                ) from e
            raise