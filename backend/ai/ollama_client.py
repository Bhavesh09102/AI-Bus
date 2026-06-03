import requests


def ask_ollama(message: str, context: str, model: str = "llama3"):
    system = "You are a helpful assistant."
    if context:
        system += f"\n\nContext about the user:\n{context}\n\nOnly use when relevant."
    try:
        resp = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": model,
                "stream": False,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": message},
                ],
            },
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        content = data.get("message", {}).get("content", "")
        return content, None
    except requests.exceptions.ConnectionError:
        return None, "Ollama not running. Run: ollama serve"
    except Exception as e:
        return None, f"Ollama error: {e}"
