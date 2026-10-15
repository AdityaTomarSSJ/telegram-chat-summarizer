"""
Gemini-powered summarizer module.

Uses the Google Generative AI free tier to summarize chat messages.
Includes timeout protection and retry logic for rate limits.
"""

import asyncio
import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
_model = genai.GenerativeModel(GEMINI_MODEL)

# Maximum time (seconds) to wait for Gemini before giving up
TIMEOUT_SECONDS = 600


async def summarize(messages_text: str, word_limit: int = 100) -> str:
    """
    Summarize a block of chat messages using Gemini.

    Args:
        messages_text: Formatted chat messages (one per line).
        word_limit:    Target summary length in words.

    Returns:
        A brief paragraph summarizing the conversation.
    """
    prompt = (
        f"You are a helpful assistant that summarizes group chat conversations.\n\n"
        f"Summarize the following group chat messages in approximately {word_limit} words.\n"
        f"Write a clear, coherent paragraph covering the main topics and key points.\n"
        f"Do NOT start with 'Here is a summary' or similar preamble — "
        f"jump straight into the summary.\n"
        f"If people are discussing multiple topics, mention all of them briefly.\n\n"
        f"--- MESSAGES ---\n"
        f"{messages_text}\n"
        f"--- END ---"
    )

    # Attempt generation with 1 retry in case of transient rate-limits
    max_attempts = 2
    for attempt in range(max_attempts):
        try:
            # Wrap the API call in a timeout so it never hangs forever
            response = await asyncio.wait_for(
                _model.generate_content_async(prompt),
                timeout=TIMEOUT_SECONDS,
            )
            return response.text.strip()

        except asyncio.TimeoutError:
            if attempt < max_attempts - 1:
                await asyncio.sleep(3)
                continue
            return (
                "⚠️ **Gemini took too long to respond (timed out after "
                f"{TIMEOUT_SECONDS}s).**\n\n"
                "This usually means Google's servers are busy or your "
                "free-tier quota is being throttled.\n"
                "• Wait **1–2 minutes** and try again.\n"
                "• Try summarizing fewer messages (e.g., 30 instead of 100)."
            )

        except Exception as e:
            err_str = str(e)
            # If it's a 429 / quota error, wait and try once more
            if ("429" in err_str or "quota" in err_str.lower() or "exhausted" in err_str.lower()) and attempt < max_attempts - 1:
                await asyncio.sleep(4)
                continue

            if "429" in err_str or "quota" in err_str.lower() or "exhausted" in err_str.lower():
                return (
                    "⚠️ **Google Gemini API Rate Limit / Quota Hit**\n\n"
                    "Google's free tier has a per-minute limit on requests.\n"
                    "• Please wait **30 to 60 seconds** and try the command again.\n"
                    "• If you tested many commands in a row, the free daily limit might need a short cooldown."
                )
            return f"⚠️ Summarization failed: {e}"
