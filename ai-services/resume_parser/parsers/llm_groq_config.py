# ai-services/resume_parser/parsers/llm_groq_config.py

import os
from langchain_groq import ChatGroq

def get_llm():
    """Get the Groq LLM instance with API key from environment."""
    # Get API key from environment variable
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        # Fallback to hardcoded key if environment variable is not set
        api_key = "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"
        print("Warning: Using fallback API key. Set GROQ_API_KEY environment variable for production.")
    
    try:
        return ChatGroq(
            model="llama-3.1-8b-instant",
            api_key=api_key
        )
    except Exception as e:
        print(f"Error creating ChatGroq: {e}")
        return None

# Don't initialize here - let it be created dynamically
llm = None
