"""
Telegram Chat Summarizer — Main Entry Point

Starts both the Telethon userbot (reads your chats) and the companion bot
(receives your commands) in the same async event loop.
"""

import asyncio
import sys

from config import validate
from userbot import UserBot
from bot import CompanionBot


BANNER = r"""
 ╔═══════════════════════════════════════════════╗
 ║     📱 Telegram Chat Summarizer              ║
 ║     Powered by Gemini AI (Free Tier)         ║
 ╚═══════════════════════════════════════════════╝
"""


async def main():
    print(BANNER)

    # ── Validate configuration ───────────────────────────────────
    validate()

    # ── Initialize components ────────────────────────────────────
    userbot = UserBot()
    bot = CompanionBot(userbot)

    print("🚀 Starting up...\n")

    # ── Start userbot (prompts for phone/OTP on first run) ───────
    print("── Userbot ──")
    await userbot.start()

    # ── Start companion bot ──────────────────────────────────────
    print("\n── Companion Bot ──")
    await bot.start()

    print("\n" + "=" * 48)
    print("✅ Everything is running!")
    print("💬 Open the companion bot on Telegram and send /start")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 48 + "\n")

    # ── Keep running until interrupted ───────────────────────────
    try:
        # Both Telethon clients process events while the loop is alive
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        print("\n🛑 Shutting down...")
        await bot.stop()
        await userbot.stop()
        print("👋 Goodbye!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bye!")
