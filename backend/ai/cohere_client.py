def ask_cohere(message: str, context: str, api_key: str):
    try:
        import cohere

        client = cohere.Client(api_key)
        preamble = "You are a helpful assistant."
        if context:
            preamble += f"\n\nContext about the user:\n{context}\n\nOnly use when relevant."
        response = client.chat(
            model="command-r",
            message=message,
            preamble=preamble,
        )
        return response.text, None
    except Exception as e:
        return None, f"Cohere error: {e}"
