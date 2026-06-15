"""
Settings/validation endpoints.

These do NOT store any keys server-side. They simply do a lightweight
"does this key work?" check so the frontend can show a green/red status
in the Settings panel immediately after the user types a key.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from anthropic import Anthropic
from app.config import GROQ_API_KEY, INSIGHTSENTRY_API_KEY

router = APIRouter(prefix="/api/settings", tags=["settings"])


class KeyCheckRequest(BaseModel):
    key: str


@router.post("/check-claude-key")
def check_claude_key(req: KeyCheckRequest):
    key = req.key.strip()
    if not key:
        return {"valid": False, "reason": "empty"}
    try:
        client = Anthropic(api_key=key)
        # Minimal call to verify the key works
        client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1,
            messages=[{"role": "user", "content": "hi"}],
        )
        return {"valid": True}
    except Exception as e:
        return {"valid": False, "reason": str(e)}


@router.post("/check-insightsentry-key")
def check_insightsentry_key(req: KeyCheckRequest):
    key = req.key.strip()
    if not key:
        return {"valid": False, "reason": "empty"}
    # InsightSentry validation will be implemented once endpoint details
    # are wired in. For now, accept any non-empty key as "provided" so
    # the UI can reflect the user's intent; actual calls fall back to
    # yfinance until the integration is complete.
    return {"valid": True, "note": "InsightSentry integration pending - using yfinance fallback for now"}


@router.get("/status")
def settings_status():
    """Tells the frontend what server-side fallbacks are available."""
    return {
        "groq_fallback_available": bool(GROQ_API_KEY),
        "insightsentry_server_fallback_available": bool(INSIGHTSENTRY_API_KEY),
    }
