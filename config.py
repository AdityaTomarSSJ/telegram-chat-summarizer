"""
Configuration loader for Telegram Chat Summarizer.
Loads credentials from .env file and validates them.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def _clean_int(val: str, default: int = 0) -> int:
    """Extract integer from string even if it has quotes, spaces, or 'Id:' prefix."""
    if not val:
        return default
    # Remove quotes, spaces, and common prefixes like 'Id:' or 'id:'
    cleaned = val.strip().strip("'\"").strip()
    if cleaned.lower().startswith("id:"):
        cleaned = cleaned[3:].strip()
    elif cleaned.lower().startswith("id"):
        cleaned = cleaned[2:].strip().lstrip(":").strip()
    try:
        return int(cleaned)
    except ValueError:
        return default


# ── Telegram API credentials (from https://my.telegram.org) ──────────────
API_ID = _clean_int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "").strip().strip("'\"")

# ── Companion bot token (from @BotFather) ─────────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip().strip("'\"")

# ── Google Gemini API key (from https://aistudio.google.com/apikey) ───────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip().strip("'\"")

# ── Allowed Telegram user IDs (who can use the bot) ─────────────────────
_raw_allowed = os.getenv("ALLOWED_USERS", os.getenv("OWNER_ID", "0"))
ALLOWED_USERS: set[int] = set()
for uid in _raw_allowed.split(","):
    cleaned = _clean_int(uid.strip())
    if cleaned:
        ALLOWED_USERS.add(cleaned)
# Backward-compatibility alias
OWNER_ID = next(iter(ALLOWED_USERS)) if ALLOWED_USERS else 0

# ── Gemini model (change if you want a different free model) ──────────────
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip().strip("'\"")


def validate() -> None:
    """Validate that all required configuration values are present."""
    errors = []
    if not API_ID:
        errors.append("API_ID is missing — get it from https://my.telegram.org")
    if not API_HASH:
        errors.append("API_HASH is missing — get it from https://my.telegram.org")
    if not BOT_TOKEN:
        errors.append("BOT_TOKEN is missing — create a bot via @BotFather on Telegram")
    if not GEMINI_API_KEY:
        errors.append(
            "GEMINI_API_KEY is missing — get it from https://aistudio.google.com/apikey"
        )
    if not OWNER_ID:
        errors.append(
            "OWNER_ID is missing — send /start to @userinfobot on Telegram to get your user ID"
        )

    if errors:
        print("\n❌ Configuration errors found:\n")
        for err in errors:
            print(f"   • {err}")
        print(
            "\n📝 Copy .env.example to .env and fill in your credentials:\n"
            "   copy .env.example .env\n"
        )
        sys.exit(1)
