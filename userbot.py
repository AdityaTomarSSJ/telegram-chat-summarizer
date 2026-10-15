"""
Telethon Userbot — connects with your personal Telegram account
to read chat history and fetch messages from groups/supergroups.
"""

from telethon import TelegramClient
from config import API_ID, API_HASH


class UserBot:
    """Manages the Telethon user-account client for reading chats."""

    def __init__(self):
        self.client = TelegramClient("user_session", API_ID, API_HASH)

    async def start(self) -> None:
        """
        Start the userbot client.
        On first run, Telethon will prompt in the terminal for:
          1. Your phone number
          2. The OTP code sent to your Telegram
          3. (Optional) Your 2FA password if enabled
        After that, a session file is saved and you won't be asked again.
        """
        await self.client.start()
        me = await self.client.get_me()
        print(f"✅ Userbot logged in as: {me.first_name} (@{me.username or 'N/A'})")

    async def get_groups_with_unread(self) -> list[dict]:
        """
        Fetch all group/supergroup dialogs with their unread message counts.

        Returns a list sorted by unread count (highest first):
            [{"name": str, "id": int, "unread_count": int}, ...]
        """
        groups = []
        async for dialog in self.client.iter_dialogs():
            if dialog.is_group:
                groups.append(
                    {
                        "name": dialog.name,
                        "id": dialog.id,
                        "unread_count": dialog.unread_count,
                    }
                )
        # Sort: most unread first
        groups.sort(key=lambda g: g["unread_count"], reverse=True)
        return groups

    async def find_group(self, query: str):
        """
        Find a group entity by name (case-insensitive partial match) or by ID.

        Args:
            query: Group name (partial match) or numeric group ID.

        Returns:
            The Telethon entity for the matched group, or None.
        """
        # Try as numeric ID first
        try:
            group_id = int(query)
            async for dialog in self.client.iter_dialogs():
                if dialog.is_group and dialog.id == group_id:
                    return dialog.entity
            return None
        except ValueError:
            pass

        # Search by name (case-insensitive partial match)
        query_lower = query.lower()
        best_match = None
        best_score = 0

        async for dialog in self.client.iter_dialogs():
            if not dialog.is_group:
                continue
            name_lower = dialog.name.lower()

            # Exact match wins immediately
            if name_lower == query_lower:
                return dialog.entity

            # Partial match — prefer shorter names (more specific)
            if query_lower in name_lower:
                score = len(query_lower) / len(name_lower)  # Higher = better match
                if score > best_score:
                    best_score = score
                    best_match = dialog.entity

        return best_match

    async def get_messages(self, entity, limit: int = 100) -> list[dict]:
        """
        Fetch the last `limit` text messages from a chat entity.

        Skips non-text messages (images, stickers, etc.).
        Returns messages in chronological order (oldest first).

        Returns:
            [{"sender": str, "text": str, "date": datetime}, ...]
        """
        messages = []
        # Inspect up to 4x the limit so non-text items (stickers, photos) are skipped
        max_scan = max(limit * 4, 200)
        async for msg in self.client.iter_messages(entity, limit=max_scan):
            if not msg.text:
                continue

            # Get sender name
            sender_name = "Unknown"
            try:
                sender = await msg.get_sender()
                if sender:
                    first = getattr(sender, "first_name", "") or ""
                    last = getattr(sender, "last_name", "") or ""
                    sender_name = f"{first} {last}".strip() or "Unknown"
            except Exception:
                pass

            messages.append(
                {
                    "sender": sender_name,
                    "text": msg.text,
                    "date": msg.date,
                }
            )

            # Stop once we have reached the requested count of text messages
            if len(messages) >= limit:
                break

        # Reverse so oldest message is first (chronological order)
        messages.reverse()
        return messages

    async def stop(self) -> None:
        """Disconnect the userbot client."""
        await self.client.disconnect()
