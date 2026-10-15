"""
Companion Bot — the Telegram bot you DM to send commands.

Handles /start, /help, /list, and /summarize commands.
Uses the Userbot to fetch messages and the Summarizer to generate summaries.
"""

import asyncio
import re
import time
from telethon import TelegramClient, events
from config import API_ID, API_HASH, BOT_TOKEN, ALLOWED_USERS
from userbot import UserBot
from summarizer import summarize
from utils import format_messages_for_llm, format_group_list, truncate_text


class CompanionBot:
    """Telegram bot that receives commands and responds with summaries."""

    def __init__(self, userbot: UserBot):
        self.bot = TelegramClient("bot_session", API_ID, API_HASH)
        self.userbot = userbot
        self._last_groups: list[dict] = []  # Cache from last /list call
        self._register_handlers()

    def _is_allowed(self, event) -> bool:
        """Security check — only whitelisted user IDs can use this bot."""
        return event.sender_id in ALLOWED_USERS

    def _register_handlers(self) -> None:
        """Register all command handlers on the bot client."""

        @self.bot.on(events.NewMessage(pattern="/start"))
        async def start_handler(event):
            if not self._is_allowed(event):
                await event.reply("⛔ Sorry, this bot is private.")
                return
            await event.reply(
                "👋 **Welcome to Telegram Chat Summarizer!**\n\n"
                "I can summarize unread messages from your group chats "
                "using AI — all for free.\n\n"
                "📌 **Commands:**\n"
                "• `/list` — Show your groups with unread counts\n"
                "• `/summarize <group> <N> [words]` — Summarize last N messages\n"
                "• `/help` — Show detailed usage\n\n"
                "Try `/list` to get started!",
                parse_mode="md",
            )

        @self.bot.on(events.NewMessage(pattern="/help"))
        async def help_handler(event):
            if not self._is_allowed(event):
                return
            await event.reply(
                "📖 **How to Use**\n\n"
                "**Step 1 — List your groups:**\n"
                "`/list`\n"
                "Shows all your groups/supergroups with unread message counts.\n\n"
                "**Step 2 — Summarize messages:**\n"
                "`/summarize <group> <N> [words]`\n\n"
                "• `group` — Group name (partial match works) or # from `/list`\n"
                "• `N` — Number of recent messages to summarize\n"
                "• `words` — _(Optional)_ Target summary length (default: 100)\n\n"
                "**Examples:**\n"
                '• `/summarize College 100` — Last 100 msgs from "College..." group\n'
                '• `/summarize "Work Team" 50 30` — 50 msgs in ~30 words\n'
                "• `/summarize 3 100` — 100 msgs from group #3 in `/list`\n"
                "• `/summarize 2 200 50` — 200 msgs from group #2, ~50 words\n\n"
                "💡 **Tips:**\n"
                "• Run `/list` first to see group numbers\n"
                "• Partial names work: `college` matches `College Friends`\n"
                "• Wrap multi-word names in quotes if needed",
                parse_mode="md",
            )

        @self.bot.on(events.NewMessage(pattern="/list"))
        async def list_handler(event):
            if not self._is_allowed(event):
                return

            await event.reply("🔍 Fetching your groups...")

            try:
                self._last_groups = await self.userbot.get_groups_with_unread()
                text = format_group_list(self._last_groups)
                await event.reply(text, parse_mode="md")
            except Exception as e:
                await event.reply(f"❌ Error fetching groups:\n`{e}`", parse_mode="md")

        @self.bot.on(events.NewMessage(pattern=r"/summarize\s+(.+)"))
        async def summarize_handler(event):
            if not self._is_allowed(event):
                return

            raw_args = event.pattern_match.group(1).strip()

            # ── Parse arguments ──────────────────────────────────────
            parsed = self._parse_summarize_args(raw_args)
            if parsed is None:
                await event.reply(
                    "❌ **Invalid format!**\n\n"
                    "Usage: `/summarize <group> <N> [words]`\n\n"
                    "Examples:\n"
                    "• `/summarize College 100`\n"
                    "• `/summarize 3 100 50`\n"
                    '• `/summarize "Work Team" 50 30`',
                    parse_mode="md",
                )
                return

            group_query, msg_count, word_limit = parsed

            # Cap message count to a reasonable limit
            if msg_count > 1000:
                await event.reply(
                    "⚠️ Max 1000 messages at a time. Using 1000.",
                    parse_mode="md",
                )
                msg_count = 1000

            # ── Resolve group ────────────────────────────────────────
            display_name = group_query
            entity = None

            # Check if it's a number reference from /list
            try:
                idx = int(group_query)
                if self._last_groups and 1 <= idx <= len(self._last_groups):
                    group_info = self._last_groups[idx - 1]
                    entity = await self.userbot.find_group(str(group_info["id"]))
                    display_name = group_info["name"]
            except (ValueError, IndexError):
                pass

            if entity is None:
                entity = await self.userbot.find_group(group_query)
                # Update display name if we found a match
                if entity:
                    display_name = getattr(entity, "title", group_query)

            if entity is None:
                await event.reply(
                    f"❌ Group **{group_query}** not found.\n"
                    "Run `/list` to see available groups.",
                    parse_mode="md",
                )
                return

            # ── Fetch messages with live timer ───────────────────────
            start_time = time.time()
            status_msg = await event.reply(
                f"⏳ `[0.0s]` Fetching last {msg_count} messages from **{display_name}**...",
                parse_mode="md",
            )

            try:
                messages = await self.userbot.get_messages(entity, limit=msg_count)

                if not messages:
                    await status_msg.edit(
                        "📭 No text messages found in this group "
                        "(images/stickers are skipped)."
                    )
                    return

                actual_count = len(messages)
                fetch_time = round(time.time() - start_time, 1)

                await status_msg.edit(
                    f"🤖 `[{fetch_time}s]` Collected {actual_count} text messages. "
                    f"Gemini AI is generating your summary...",
                    parse_mode="md",
                )

                # ── Summarize with live heartbeat timer ──────────────
                messages_text = format_messages_for_llm(messages)
                messages_text = truncate_text(messages_text)

                # Background task: update the status message every 5s
                heartbeat_active = True

                async def _heartbeat():
                    tick = 0
                    spinner = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
                    while heartbeat_active:
                        await asyncio.sleep(5)
                        if not heartbeat_active:
                            break
                        tick += 1
                        elapsed = round(time.time() - start_time, 1)
                        icon = spinner[tick % len(spinner)]
                        try:
                            await status_msg.edit(
                                f"{icon} `[{elapsed}s]` Gemini AI is still working on your summary...",
                                parse_mode="md",
                            )
                        except Exception:
                            pass

                heartbeat_task = asyncio.create_task(_heartbeat())

                try:
                    async with self.bot.action(event.chat_id, "typing"):
                        summary = await summarize(messages_text, word_limit)
                finally:
                    heartbeat_active = False
                    heartbeat_task.cancel()

                total_time = round(time.time() - start_time, 1)

                # ── Edit into final result with timing badge ──────────
                response = (
                    f"📝 **Summary of {display_name}**\n"
                    f"_({actual_count} messages → ~{word_limit} words • ⏱️ took {total_time}s)_\n\n"
                    f"{summary}"
                )
                try:
                    await status_msg.edit(response, parse_mode="md")
                except Exception:
                    # If edit fails (e.g. Markdown parsing), send as new message
                    await event.reply(response)

            except Exception as e:
                elapsed = round(time.time() - start_time, 1)
                await status_msg.edit(f"❌ `[{elapsed}s]` Error: `{e}`")

    @staticmethod
    def _parse_summarize_args(raw: str):
        """
        Parse the /summarize arguments.

        Supported formats:
            "Group Name" 100 50    → ("Group Name", 100, 50)
            "Group Name" 100       → ("Group Name", 100, 100)
            College 100 50         → ("College", 100, 50)
            College 100            → ("College", 100, 100)
            3 100 50               → ("3", 100, 50)   ← index from /list
            3 100                  → ("3", 100, 100)

        Returns:
            (group_query, msg_count, word_limit) or None on parse failure.
        """
        # ── Try quoted group name: "Group Name" N [words] ──
        match = re.match(r'"([^"]+)"\s+(\d+)(?:\s+(\d+))?$', raw)
        if match:
            return (
                match.group(1),
                int(match.group(2)),
                int(match.group(3)) if match.group(3) else 100,
            )

        # ── Try single-quoted: 'Group Name' N [words] ──
        match = re.match(r"'([^']+)'\s+(\d+)(?:\s+(\d+))?$", raw)
        if match:
            return (
                match.group(1),
                int(match.group(2)),
                int(match.group(3)) if match.group(3) else 100,
            )

        # ── Unquoted: split from the right ──
        parts = raw.rsplit(maxsplit=2)

        if len(parts) >= 2:
            # Try: group_name N words  (last two are numbers)
            try:
                words = int(parts[-1])
                count = int(parts[-2])
                group = " ".join(parts[:-2]) if len(parts) > 2 else None
                if group:
                    return (group, count, words)
            except ValueError:
                pass

            # Try: group_name N  (only last is a number)
            try:
                count = int(parts[-1])
                group = " ".join(parts[:-1])
                if group:
                    return (group, count, 100)
            except ValueError:
                pass

        return None

    async def start(self) -> None:
        """Start the companion bot with the bot token."""
        await self.bot.start(bot_token=BOT_TOKEN)
        me = await self.bot.get_me()
        print(f"✅ Companion bot started: @{me.username}")
        print(f"   Open https://t.me/{me.username} and send /start")

    async def stop(self) -> None:
        """Disconnect the companion bot."""
        await self.bot.disconnect()
