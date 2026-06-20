import logging

import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from .models import Opportunity

logger = logging.getLogger(__name__)

CONFIDENCE_FILTER = {"high", "medium"}
MAX_MESSAGE_LENGTH = 4000


def format_message(
    opportunities: list[Opportunity], channel_name: str, video_title: str, video_id: str
) -> str:
    lines = [
        "🚨 New Opportunities Found",
        "",
        f"Channel: {channel_name}",
        f"Video: {video_title}",
        "",
        "─" * 10,
    ]

    for i, opp in enumerate(opportunities, 1):
        batches = ", ".join(opp.eligible_batches)

        lines.append("")
        lines.append(f"{i}️⃣ {opp.job_title}")
        lines.append(f"")
        lines.append(f"Company: {opp.company}")
        lines.append(f"")
        lines.append(f"Eligible Batch: {batches if batches else 'Not specified'}")
        lines.append(f"")
        lines.append(f"Apply: {opp.application_link if opp.application_link else 'Not available'}")
        lines.append("")
        lines.append("─" * 10)

    lines.append("")
    lines.append(f"Video URL: https://youtube.com/watch?v={video_id}")
    return "\n".join(lines)


def filter_opportunities(opportunities: list[Opportunity]) -> list[Opportunity]:
    return [
        opp
        for opp in opportunities
        if opp.confidence.lower() in CONFIDENCE_FILTER
        and opp.application_link
        and opp.job_title
    ]


def _get_chat_id() -> int:
    chat_id = TELEGRAM_CHAT_ID.strip()
    return int(chat_id) if chat_id.lstrip("-").isdigit() else chat_id


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(requests.RequestException),
    reraise=True,
)
def _send_request(message: str) -> bool:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": _get_chat_id(),
        "text": message[:MAX_MESSAGE_LENGTH],
        "disable_web_page_preview": True,
    }
    response = requests.post(url, json=payload, timeout=30)
    if response.status_code != 200:
        logger.error("Telegram error %s: %s", response.status_code, response.text)
    response.raise_for_status()
    return True


def send_telegram(message: str) -> bool:
    try:
        _send_request(message)
        logger.info("Telegram notification sent successfully")
        return True
    except Exception as e:
        logger.error("Telegram send error: %s", e)
        return False
