"""
Gemini-powered summarizer module.

Uses the Google Generative AI free tier to summarize chat messages.
"""

import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
_model = genai.GenerativeModel(GEMINI_MODEL)


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

    try:
        response = await _model.generate_content_async(prompt)
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Summarization failed: {e}"
