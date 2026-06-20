import requests
from .config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def format_message(opportunities: list[dict], channel_name: str, video_url: str) -> str:
    lines = ["🚨 New Opportunities Found", f"📺 Channel: {channel_name}", "─" * 20]

    for i, opp in enumerate(opportunities, 1):
        lines.append(f"\n{i}️⃣ {opp.get('job_title', 'Unknown')}")
        lines.append(f"🏢 Company: {opp.get('company', 'Unknown')}")
        lines.append(f"🎓 Eligible Batch: {', '.join(opp.get('eligible_batches', []))}")

        if opp.get("location") and opp["location"] != "Not specified":
            lines.append(f"📍 Location: {opp['location']}")

        if opp.get("stipend") and opp["stipend"] != "Not specified":
            lines.append(f"💰 Stipend: {opp['stipend']}")

        if opp.get("deadline") and opp["deadline"] != "Not specified":
            lines.append(f"⏰ Deadline: {opp['deadline']}")

        link = opp.get("application_link", "")
        if link and link != "Not mentioned":
            lines.append(f"🔗 Apply: {link}")

        lines.append("─" * 20)

    lines.append(f"\n🎬 Video: {video_url}")
    return "\n".join(lines)


def send_telegram(message: str) -> bool:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            print("Telegram notification sent successfully")
            return True
        else:
            print(f"Telegram error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Telegram send error: {e}")
        return False
