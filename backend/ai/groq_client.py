def ask_groq(message: str, context: str, api_key: str):
    try:
        from groq import Groq

        client = Groq(api_key=api_key)
        system = "You are a helpful assistant."
        if context:
            system += f"\n\nContext about the user:\n{context}\n\nOnly use when relevant."
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            max_tokens=1000,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": message},
            ],
        )
        text = response.choices[0].message.content
        return text, None
    except Exception as e:
        return None, f"Groq error: {e}"
