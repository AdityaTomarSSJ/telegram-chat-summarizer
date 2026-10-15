"""
Utility helpers for message formatting and text processing.
"""


def format_messages_for_llm(messages: list[dict]) -> str:
    """
    Format fetched messages into a readable string for the LLM.

    Each message becomes:  [SenderName]: message text
    Messages are in chronological order (oldest first).
    """
    lines = []
    for msg in messages:
        lines.append(f"[{msg['sender']}]: {msg['text']}")
    return "\n".join(lines)


def format_group_list(groups: list[dict]) -> str:
    """Format the group list with unread counts for display in Telegram."""
    if not groups:
        return "📭 You're not in any groups, or no groups were found."

    lines = ["📋 **Your Groups:**\n"]
    for i, group in enumerate(groups, 1):
        unread = group["unread_count"]
        emoji = "🔴" if unread > 0 else "⚪"
        lines.append(f"`{i}.` {emoji} **{escape_md(group['name'])}** — {unread} unread")

    lines.append(
        "\n💡 Use: `/summarize <group name or #> <N> [words]`\n"
        "Example: `/summarize 3 100` or `/summarize College 100 50`"
    )
    return "\n".join(lines)


def truncate_text(text: str, max_chars: int = 30_000) -> str:
    """
    Truncate text to stay within Gemini's comfortable input range.
    The free-tier limit is generous, but we cap at 30k chars to keep
    responses fast and focused.
    """
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n... [truncated — too many messages]"


def escape_md(text: str) -> str:
    """Escape special Markdown characters for Telegram's Markdown mode."""
    return text.replace("_", "\\_").replace("*", "\\*").replace("`", "\\`")
