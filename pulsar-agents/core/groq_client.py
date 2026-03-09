import os
from groq import Groq


def get_groq_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY env var not set")
    return Groq(api_key=api_key)


def summarize(client, prompt: str) -> str:
    """Call Groq LLM and return text response."""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()
