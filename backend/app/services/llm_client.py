from groq import Groq
from app.config import settings

_client = Groq(api_key=settings.GROQ_API_KEY)


def complete(system: str, user: str, max_tokens: int = 1200) -> str:
    resp = _client.chat.completions.create(
        model=settings.LLM_MODEL,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return resp.choices[0].message.content