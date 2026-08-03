import os
from langchain_google_genai import ChatGoogleGenerativeAI
from src.config import MODEL

def get_llm():
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY / GOOGLE_API_KEY environment variable is missing.")
    return ChatGoogleGenerativeAI(model=MODEL, temperature=0, google_api_key=api_key)

def detect_bugs(state):
    llm = get_llm()
    # rest of your detect_bugs logic...