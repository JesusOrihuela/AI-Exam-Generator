# logic/llm_client.py
from openai import OpenAI

def make_client(api_key: str) -> OpenAI:
    """Factory mínima para crear el cliente de OpenAI."""
    return OpenAI(api_key=api_key)
