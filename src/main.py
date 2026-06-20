import logging

from .config import validate_config
from .logger import setup_logging
from .youtube import load_channels, get_new_videos
from .youtube_api import get_video_description
from .transcript import get_transcript
from .extractor import extract_opportunities
from .telegram import format_message, filter_opportunities, send_telegram
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
        last_video_id = state.get(channel_id, "")

        logger.info("Checking channel: %s (%s)", channel_name, channel_id)

        new_videos = get_new_videos(channel_id, last_video_id)
        if not new_videos:
            logger.info("No new videos for %s", channel_name)
            continue

        logger.info("Found %d new video(s)", len(new_videos))

        for video in new_videos:
            video_id = video["video_id"]
            logger.info("Processing: %s", video["title"])

            description_data = get_video_description(video_id)
            if not description_data:
                logger.warning("Skipping %s - description fetch failed", video_id)
                continue

            logger.info("Description retrieved for %s", video_id)

            transcript = get_transcript(video_id)
            if transcript:
                logger.info("Transcript retrieved for %s", video_id)
            else:
                logger.warning("No transcript available for %s", video_id)

            opportunities = extract_opportunities(
                title=description_data["title"],
                description=description_data["description"],
                transcript=transcript,
            )

            if not opportunities:
                logger.info("No opportunities found in video %s", video_id)
                continue

            logger.info("Extracted %d opportunity(ies) from %s", len(opportunities), video_id)

            filtered = filter_opportunities(opportunities)
            if not filtered:
                logger.info("No valid opportunities after filtering for %s", video_id)
                continue

            logger.info("Found %d valid opportunity(ies)", len(filtered))

            channel_title = description_data.get("channel_name", channel_name)
            message = format_message(
                filtered, channel_title, video["title"], video_id
            )

            if send_telegram(message):
                state[channel_id] = video_id
                save_state(state)
                logger.info("State updated to %s", video_id)
            else:
                logger.warning(
                    "Failed to send Telegram notification, skipping state update"
                )

    logger.info("Run complete")


if __name__ == "__main__":
    run()
