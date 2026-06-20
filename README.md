# YouTube Job & Internship Opportunity Alert Bot

Automatically monitors YouTube channels for job, internship, and hiring opportunity videos. Extracts every opportunity using AI and sends structured Telegram notifications.

## Features

- Monitors multiple YouTube channels via RSS feeds
- Fetches video descriptions using YouTube Data API v3
- Retrieves transcripts using youtube-transcript-api
- Extracts opportunities using Groq LLM (configurable model)
- Sends structured Telegram notifications
- Filters by confidence (high/medium only)
- Automatic state management with deduplication
- Runs every 15 minutes via GitHub Actions
- Structured logging throughout
- Retry logic with exponential backoff

## Architecture

```
GitHub Actions (every 15 min)
    ↓
YouTube RSS Feed
    ↓
New Video Detected
    ↓
YouTube Data API v3 → Title, Description, Channel Name
    ↓
youtube-transcript-api → Transcript
    ↓
LLM Opportunity Extractor (Groq)
    ↓
Structured JSON Output
    ↓
Filter by Confidence + Link
    ↓
Telegram Notification
    ↓
Update state.json
```

## Installation

### Prerequisites

- Python 3.11+
- A Telegram bot
- A YouTube Data API key
- A Groq API key

### Local Setup

```bash
git clone https://github.com/yourusername/youtube-job-monitor.git
cd youtube-job-monitor
pip install -r requirements.txt
cp .env.example .env
# Fill in your API keys in .env
python -m src.main
```

## Telegram Setup

### 1. Create Bot with BotFather

1. Open Telegram and search for `@BotFather`
2. Send `/newbot`
3. Choose a name for your bot
4. Choose a username for your bot
5. Save the `BOT_TOKEN` from the response

### 2. Get Your Chat ID

1. Send any message to your bot
2. Open `https://api.telegram.org/bot<BOT_TOKEN>/getUpdates` in your browser
3. Find the `"chat"` object
4. Copy the `"id"` value — this is your `CHAT_ID`

For group chats:
1. Add the bot to your group
2. Send a message in the group
3. Use the same URL to get updates
4. The chat ID will be negative (e.g., `-1001234567890`)

## YouTube Data API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Navigate to **APIs & Services** → **Library**
4. Search for **YouTube Data API v3** and enable it
5. Go to **APIs & Services** → **Credentials**
6. Click **Create Credentials** → **API Key**
7. Copy the API key

**Note:** The free tier allows 10,000 units/day. Each video metadata request costs ~1 unit.

## Groq Setup

1. Go to [Groq Console](https://console.groq.com)
2. Create an account or sign in
3. Go to **API Keys**
4. Create a new API key
5. Copy the key

Default model: `llama-3.3-70b-versatile`. Override via `GROQ_MODEL` env var.

## GitHub Secrets Setup

Go to your repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these secrets:

| Secret | Description |
|--------|-------------|
| `GROQ_API_KEY` | Your Groq API key |
| `GROQ_MODEL` | (Optional) Model name, defaults to `llama-3.3-70b-versatile` |
| `YOUTUBE_API_KEY` | Your YouTube Data API key |
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID |

## Deployment

1. Push the repository to GitHub
2. Go to **Actions** tab
3. Click **YouTube Job Monitor**
4. Click **Run workflow** to test manually
5. The workflow runs automatically every 15 minutes

## Adding Channels

Edit `channels.json`:

```json
[
  {
    "name": "Channel Name",
    "channel_id": "UC_CHANNEL_ID"
  },
  {
    "name": "Another Channel",
    "channel_id": "UC_ANOTHER_ID"
  }
]
```

To find a channel ID:
1. Go to the YouTube channel
2. Click **About** tab
3. Click **Share** → **Copy channel ID**
4. Or view page source and search for `channelId`

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | Yes | - | Groq API key |
| `GROQ_MODEL` | No | `llama-3.3-70b-versatile` | LLM model name |
| `YOUTUBE_API_KEY` | Yes | - | YouTube Data API key |
| `TELEGRAM_BOT_TOKEN` | Yes | - | Telegram bot token |
| `TELEGRAM_CHAT_ID` | Yes | - | Telegram chat ID |

## Notification Format

```
🚨 New Opportunities Found

Channel: Shivam Lucknowi
Video: Today's Job Update

──────────

1️⃣ Software Engineer Intern

Company: Microsoft

Eligible Batch: 2027

Apply: https://careers.microsoft.com/...

──────────

2️⃣ Data Analyst Intern

Company: Google

Eligible Batch: 2026, 2027

Apply: https://careers.google.com/...

──────────

Video URL: https://youtube.com/watch?v=...
```

## How It Works

1. **RSS Detection** — Parses YouTube RSS feed to detect new uploads
2. **Description Fetch** — Uses YouTube Data API v3 to get video description (application links)
3. **Transcript Fetch** — Uses youtube-transcript-api to get spoken content (eligibility info)
4. **AI Extraction** — Sends combined data to Groq LLM to extract structured opportunities
5. **Filtering** — Removes low-confidence entries and those missing application links
6. **Notification** — Sends formatted message to Telegram
7. **State Update** — Records processed video ID to avoid duplicates

## Troubleshooting

### Bot not sending messages

1. Verify bot token is correct
2. Ensure you've sent at least one message to the bot
3. Check chat ID is correct (use getUpdates URL)
4. For groups, bot must be added as admin

### No transcript available

Some videos don't have captions. The bot will log a warning and continue processing using only the description.

### YouTube API quota exceeded

The free tier allows 10,000 units/day. Each video costs ~1 unit. Monitor usage in Google Cloud Console.

### State file issues

Delete `state.json` to reset. The bot will reprocess all videos in the feed.

### Groq errors

Check your API key and quota at [console.groq.com](https://console.groq.com).

## Common Issues

| Issue | Solution |
|-------|----------|
| `Missing required environment variables` | Set all required env vars in `.env` or GitHub Secrets |
| `RSS feed error` | Channel ID may be invalid. Verify in channel settings |
| `Transcript disabled` | Creator disabled captions. Bot skips transcript gracefully |
| `Telegram error 403` | Bot blocked or not added to chat. Send `/start` to bot |
| `Telegram error 400` | Chat ID incorrect. Verify with getUpdates |

## Project Structure

```
youtube-job-monitor/
├── .github/workflows/monitor.yml   # GitHub Actions schedule
├── src/
│   ├── __init__.py
│   ├── config.py                   # Environment variables & validation
│   ├── logger.py                   # Structured logging setup
│   ├── models.py                   # Pydantic data models
│   ├── youtube.py                  # RSS feed parsing
│   ├── youtube_api.py              # YouTube Data API v3 client
│   ├── transcript.py               # Transcript retrieval
│   ├── extractor.py                # LLM opportunity extraction
│   ├── telegram.py                 # Telegram formatting & sending
│   ├── state.py                    # State management
│   └── main.py                     # Main pipeline orchestrator
├── channels.json                   # Monitored channels config
├── state.json                      # Last processed video IDs
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## License

MIT
