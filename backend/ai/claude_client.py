def ask_claude(message: str, context: str, api_key: str):
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)
        system = "You are a helpful assistant."
        if context:
            system += f"\n\nContext about the user:\n{context}\n\nOnly use when relevant."
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=system,
            messages=[{"role": "user", "content": message}],
        )
        text = response.content[0].text
        return text, None
    except Exception as e:
        return None, f"Claude error: {e}"
