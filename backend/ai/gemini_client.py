def ask_gemini(message: str, context: str, api_key: str):
    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        if context:
            full_message = f"Context (use when relevant):\n{context}\n\nQuestion: {message}"
        else:
            full_message = message
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(full_message)
        return response.text, None
    except Exception as e:
        return None, f"Gemini error: {e}"
