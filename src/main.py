import logging

from .config import validate_config
from .logger import setup_logging
from .youtube import load_channels, get_latest_video
from .youtube_api import get_video_description
from .transcript import get_transcript
from .extractor import extract_opportunities
from .telegram import filter_opportunities, send_telegram
from .state import load_state, save_state


def run() -> None:
    setup_logging()
    validate_config()

    logger = logging.getLogger(__name__)

    channels = load_channels()
    state = load_state()

    for channel in channels:
        channel_id = channel["channel_id"]
        channel_name = channel["name"]

        logger.info("Checking channel: %s (%s)", channel_name, channel_id)

        video = get_latest_video(channel_id)
        if not video:
            logger.info("No videos found for %s", channel_name)
            continue

        video_id = video["video_id"]

        if state.get(channel_id) == video_id:
            logger.info("Already processed %s, skipping", video_id)
            continue

        logger.info("Processing latest: %s", video["title"])

        description_data = get_video_description(video_id)
        if not description_data:
            logger.warning("Skipping %s - description fetch failed", video_id)
            continue

        transcript = get_transcript(video_id)

        opportunities = extract_opportunities(
            title=description_data["title"],
            description=description_data["description"],
            transcript=transcript,
        )

        if not opportunities:
            logger.info("No opportunities found in video %s", video_id)
            continue

        filtered = filter_opportunities(opportunities)
        if not filtered:
            logger.info("No valid opportunities after filtering for %s", video_id)
            continue

        logger.info("Found %d valid opportunity(ies)", len(filtered))

        channel_title = description_data.get("channel_name", channel_name)

        if send_telegram(filtered, channel_title, video["title"], video_id):
            state[channel_id] = video_id
            save_state(state)
            logger.info("Telegram notification sent for %s", video_id)
        else:
            logger.warning("Failed to send Telegram notification for %s", video_id)

    logger.info("Run complete")


if __name__ == "__main__":
    run()
