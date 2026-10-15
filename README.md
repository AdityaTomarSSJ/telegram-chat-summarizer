# 📱 Telegram Chat Summarizer

Summarize unread group chat messages using AI — **completely free**.

Send a command to your dedicated Telegram bot, and it reads your group messages and returns a concise summary powered by Google Gemini.

## ✨ Features

- 📋 **`/list`** — See all your groups with unread message counts
- 📝 **`/summarize`** — Get AI-powered summaries of group messages
- 🔒 **Private** — Only you can use the bot (secured by your user ID)
- 💸 **100% Free** — No paid APIs, no server costs

## 🏗️ Architecture

```
You (Telegram) → Companion Bot → Core Engine → Userbot (reads chats)
                                             → Gemini API (summarizes)
                                ← Summary ←
```

## 🚀 Setup (One-Time, ~5 Minutes)

### Prerequisites

- **Python 3.10+** installed ([download](https://www.python.org/downloads/))
- A **Telegram account**

### Step 1: Get Your Credentials

You need 4 things (all free and instant):

| Credential | Where to Get It |
|---|---|
| `API_ID` + `API_HASH` | [my.telegram.org](https://my.telegram.org) → "API development tools" |
| `BOT_TOKEN` | Open [@BotFather](https://t.me/BotFather) on Telegram → `/newbot` |
| `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com/apikey) → "Create API Key" |
| `OWNER_ID` | Open [@userinfobot](https://t.me/userinfobot) on Telegram → `/start` |

### Step 2: Install

```bash
# Navigate to the project folder
cd telegram-chat-summarizer

# Create a virtual environment (recommended)
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure

```bash
# Copy the example config
copy .env.example .env

# Edit .env and fill in your credentials
notepad .env
```

Your `.env` should look like:
```ini
API_ID=12345678
API_HASH=abcdef1234567890abcdef1234567890
BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
GEMINI_API_KEY=AIzaSy...your-key...
OWNER_ID=987654321
```

### Step 4: Log in & Run

**Option A (Recommended — QR Code Login):**
```bash
python login_qr.py
```
A browser window opens with a QR code. On your phone: **Settings → Devices → Link Desktop Device** and scan it. Your session is saved.

**Option B (Phone number & OTP):**
```bash
python main.py
```
Telethon will prompt for phone number (+countrycode) and code.

Then start the bot:
```bash
python main.py
```

### Step 5: Use

1. Open your companion bot on Telegram (the one you created with BotFather)
2. Send `/start`
3. Send `/list` to see your groups
4. Send `/summarize "Group Name" 100` to summarize!

## 📖 Commands

| Command | Description | Example |
|---|---|---|
| `/start` | Welcome message | `/start` |
| `/help` | Detailed usage guide | `/help` |
| `/list` | Show groups with unread counts | `/list` |
| `/summarize <group> <N> [words]` | Summarize N messages (~words length) | `/summarize College 100 50` |

### `/summarize` Examples

```
/summarize College 100           → Last 100 msgs, ~100 words
/summarize "Work Team" 50 30    → 50 msgs from "Work Team", ~30 words
/summarize 3 100                → Group #3 from /list, 100 msgs
/summarize 2 200 50             → Group #2, 200 msgs, ~50 words
```

## 🔒 Security Notes

- **Session file** (`user_session.session`) contains your Telegram login — never share it
- **`.env`** contains all your API keys — never commit to git
- The bot only responds to your `OWNER_ID` — others are blocked
- The userbot runs under your personal account — don't use it for spam

## 💰 Cost

| Component | Free Tier Limits |
|---|---|
| Telegram API | Unlimited (personal use) |
| Gemini API | 15 requests/min, 1M tokens/day |
| Everything else | Open source |

For personal use, you'll never hit these limits.

## 🛠️ Troubleshooting

**"SessionPasswordNeededError"** — You have 2FA enabled. Enter your 2FA password when prompted.

**"FloodWaitError"** — Telegram rate limit. Wait the specified time and try again.

**"API_ID_INVALID"** — Double-check your `API_ID` and `API_HASH` in `.env`.

**Bot doesn't respond** — Make sure `OWNER_ID` matches your Telegram user ID. Check with @userinfobot.

## 📄 License

MIT — Use freely, modify as you wish.
