"""Shared LLM factory.

IMPORTANT: Never instantiate ChatGoogleGenerativeAI at module import time.
GitHub Actions injects secrets as environment variables only for the running
job step — if the client is built at import time (before that env var is
guaranteed to be set/visible), or if the secret is simply missing on the repo
running the workflow, this raises a pydantic ValidationError. Building it
lazily inside get_llm(), called from within each agent function, avoids that.
"""

import os

from langchain_google_genai import ChatGoogleGenerativeAI

from src.config import MODEL


def get_llm(temperature: float = 0) -> ChatGoogleGenerativeAI:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY / GOOGLE_API_KEY is missing from environment variables. "
            "Set it as a secret in this repo's Settings > Secrets and variables > "
            "Actions (Secrets tab, not Variables), then re-run the workflow."
        )
    return ChatGoogleGenerativeAI(model=MODEL, temperature=temperature, google_api_key=api_key)
