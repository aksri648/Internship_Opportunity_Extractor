import os
import sys

from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL") or "openai/gpt-oss-120b"
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHANNELS_FILE = os.path.join(BASE_DIR, "channels.json")
STATE_FILE = os.path.join(BASE_DIR, "state.json")
BATCH_STATE_FILE = os.path.join(BASE_DIR, "batch_state.json")

REQUIRED_VARS = {
    "GROQ_API_KEY": GROQ_API_KEY,
    "YOUTUBE_API_KEY": YOUTUBE_API_KEY,
    "TELEGRAM_BOT_TOKEN": TELEGRAM_BOT_TOKEN,
    "TELEGRAM_CHAT_ID": TELEGRAM_CHAT_ID,
}


def validate_config() -> None:
    missing = [name for name, value in REQUIRED_VARS.items() if not value]
    if missing:
        print(f"ERROR: Missing required environment variables: {', '.join(missing)}")
        print("Set them in .env file or as environment variables.")
        sys.exit(1)
