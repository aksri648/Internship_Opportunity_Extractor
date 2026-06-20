# YouTube Job Monitor

Automatically monitors YouTube channels for new job/internship opportunity videos, extracts opportunities using AI, and sends Telegram notifications.

## Architecture

```
GitHub Actions (every 15 min)
    ↓
YouTube RSS Feed
    ↓
New Video Found?
    ↓ YES
Get Video Metadata (yt-dlp)
    ↓
Extract Description
    ↓
Get Transcript
    ↓
AI Opportunity Extraction (Groq)
    ↓
Telegram Notification
    ↓
Update state.json
```

## Setup

### 1. Create Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Run `/newbot` and save the `BOT_TOKEN`
3. Send a message to your bot
4. Open `https://api.telegram.org/bot<BOT_TOKEN>/getUpdates`
5. Find `"chat": {"id": 123456789}` and save the `CHAT_ID`

### 2. Create GitHub Repository

Create a repository named `youtube-job-monitor`.

### 3. Get Groq API Key

1. Go to [Groq Console](https://console.groq.com)
2. Create an API key

### 4. Add GitHub Secrets

Go to Repository → Settings → Secrets and create:

- `GROQ_API_KEY`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

### 5. Add Channels

Edit `channels.json`:

```json
[
  {
    "name": "Shivam Lucknowi",
    "channel_id": "UCHkU6txu-9dMsa0yeG4jlWA"
  }
]
```

### 6. Initialize State

Edit `state.json`:

```json
{
  "UCHkU6txu-9dMsa0yeG4jlWA": ""
}
```

### 7. Deploy

Push to GitHub → Go to Actions → Run Workflow

## Testing Locally

```bash
pip install -r requirements.txt
cp .env.example .env
# Fill in your API keys in .env
python -m src.main
```

## Notification Format

```
🚨 New Opportunities Found
📺 Channel: Shivam Lucknowi
──────────────────

1️⃣ Software Engineer Intern
🏢 Company: Microsoft
🎓 Eligible Batch: 2027
🔗 Apply: https://...
──────────────────

🎬 Video: https://youtube.com/watch?v=...
```
