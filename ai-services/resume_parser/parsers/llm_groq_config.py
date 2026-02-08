import os
from langchain_groq import ChatGroq

def get_llm():
    """Get the Groq LLM instance using API key from environment variables."""
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Please configure it as an environment variable."
        )

    return ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=api_key
    )

# Don't initialize here - let it be created dynamically
llm = None
