import logging

import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from .models import Opportunity

logger = logging.getLogger(__name__)

CONFIDENCE_FILTER = {"high", "medium"}
MAX_MESSAGE_LENGTH = 4096


def _format_opportunity(i: int, opp: Opportunity) -> str:
    batches = ", ".join(opp.eligible_batches)
    link = opp.application_link if opp.application_link else "Not available"
    return (
        f"\n{i}️⃣ {opp.job_title}\n"
        f"\n"
        f"Company: {opp.company}\n"
        f"\n"
        f"Eligible Batch: {batches if batches else 'Not specified'}\n"
        f"\n"
        f"Apply: {link}\n"
        f"\n"
        f"─" * 10
    )


def _build_messages(
    opportunities: list[Opportunity], channel_name: str, video_title: str, video_id: str
) -> list[str]:
    header = (
        f"🚨 New Opportunities Found\n"
        f"\n"
        f"Channel: {channel_name}\n"
        f"Video: {video_title}\n"
        f"\n"
        f"─" * 10
    )
    footer = f"\n\nVideo URL: https://youtube.com/watch?v={video_id}"

    if not opportunities:
        return [header + footer]

    opp_texts = [_format_opportunity(i, opp) for i, opp in enumerate(opportunities, 1)]

    messages = []
    current = header
    for text in opp_texts:
        if len(current) + len(text) > MAX_MESSAGE_LENGTH - len(footer):
            messages.append(current)
            current = text
        else:
            current += text
    current += footer
    messages.append(current)

    return messages


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
        "text": message,
        "disable_web_page_preview": True,
    }
    response = requests.post(url, json=payload, timeout=30)
    if response.status_code != 200:
        logger.error("Telegram error %s: %s", response.status_code, response.text)
    response.raise_for_status()
    return True


def send_telegram(opportunities: list[Opportunity], channel_name: str, video_title: str, video_id: str) -> bool:
    messages = _build_messages(opportunities, channel_name, video_title, video_id)
    try:
        for msg in messages:
            _send_request(msg)
        logger.info("Telegram notification sent successfully (%d message(s))", len(messages))
        return True
    except Exception as e:
        logger.error("Telegram send error: %s", e)
        return False
