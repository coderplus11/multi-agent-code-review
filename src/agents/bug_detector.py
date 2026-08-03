import os
from langchain_google_genai import ChatGoogleGenerativeAI
from src.config import MODEL
from src.state import AgentState

def get_llm():
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY / GOOGLE_API_KEY is missing from environment variables.")
    return ChatGoogleGenerativeAI(model=MODEL, temperature=0, google_api_key=api_key)

def detect_bugs(state: AgentState):
    llm = get_llm()  # Instantiate inside the function, NOT at top-level import
    # ... rest of your function code using llm ...
