from .ollama_client import ask_ollama
from .claude_client import ask_claude
from .gpt_client import ask_gpt
from .gemini_client import ask_gemini
from .groq_client import ask_groq
from .cohere_client import ask_cohere


def get_ai_response(message: str, context: str, ai_choice: str, api_key: str = None, model: str = None):
    ai_choice = (ai_choice or "ollama").lower()

    if ai_choice == "ollama":
        return ask_ollama(message, context, model or "llama3")

    if not api_key:
        return None, "API key required"

    if ai_choice == "claude":
        return ask_claude(message, context, api_key)
    if ai_choice in ("gpt4", "gpt-4", "gpt"):
        return ask_gpt(message, context, api_key)
    if ai_choice == "gemini":
        return ask_gemini(message, context, api_key)
    if ai_choice == "groq":
        return ask_groq(message, context, api_key)
    if ai_choice == "cohere":
        return ask_cohere(message, context, api_key)

    return None, f"Unknown AI: {ai_choice}"
