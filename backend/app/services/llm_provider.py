"""
LLM provider abstraction.

Resolution order per request:
  1. If the frontend sends an `X-Claude-Key` header with a non-empty value,
     use that key with Anthropic's Claude API.
  2. Otherwise, fall back to Groq (using the server's GROQ_API_KEY from .env)
     with a comparable open model.

This lets users demo the app with their own Claude key for best quality,
or rely on the built-in Groq fallback with no setup at all.
"""
from anthropic import Anthropic
from groq import Groq
from app.config import GROQ_API_KEY, CLAUDE_MODEL, GROQ_MODEL


class LLMResult:
    def __init__(self, text: str, source: str):
        self.text = text
        self.source = source  # 'claude' | 'groq'


def get_llm_completion(prompt: str, user_claude_key: str | None, max_tokens: int = 1200) -> LLMResult:
    """
    Sends `prompt` as a single user message and returns the text response,
    along with which provider actually served the request.
    """
    user_claude_key = (user_claude_key or "").strip()

    if user_claude_key:
        try:
            client = Anthropic(api_key=user_claude_key)
            resp = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            text = "".join(block.text for block in resp.content if hasattr(block, "text"))
            return LLMResult(text=text, source="claude")
        except Exception as e:
            # Fall through to Groq if the user's Claude key fails
            print(f"[llm] Claude call failed ({e}); falling back to Groq")

    # Groq fallback
    if not GROQ_API_KEY:
        raise RuntimeError(
            "No Claude key provided and no GROQ_API_KEY configured on the server. "
            "Add a Claude key in Settings, or set GROQ_API_KEY in backend/.env."
        )

    client = Groq(api_key=GROQ_API_KEY)
    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    text = resp.choices[0].message.content
    return LLMResult(text=text, source="groq")
