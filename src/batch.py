import json
import logging

from .config import validate_config, BATCH_STATE_FILE
from .logger import setup_logging
from .youtube import load_channels, get_recent_videos
from .youtube_api import get_video_description
from .transcript import get_transcript
from .extractor import extract_opportunities
from .telegram import filter_opportunities, send_telegram

logger = logging.getLogger(__name__)

VIDEOS_PER_CHANNEL = 10


def _load_batch_state() -> dict:
    try:
        with open(BATCH_STATE_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_batch_state(state: dict) -> None:
    try:
        with open(BATCH_STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
    except OSError as e:
        logger.error("Failed to save batch state: %s", e)


def run() -> None:
    setup_logging()
    validate_config()

    channels = load_channels()
    state = _load_batch_state()

    for channel in channels:
        channel_id = channel["channel_id"]
        channel_name = channel["name"]
        processed_ids = set(state.get(channel_id, []))

        logger.info("Checking channel: %s (%s)", channel_name, channel_id)

        videos = get_recent_videos(channel_id, VIDEOS_PER_CHANNEL)
        if not videos:
            logger.info("No videos found for %s", channel_name)
            continue

        new_videos = [v for v in videos if v["video_id"] not in processed_ids]
        if not new_videos:
            logger.info("All videos already processed for %s", channel_name)
            continue

        logger.info("Found %d unprocessed video(s) for %s", len(new_videos), channel_name)

        for video in new_videos:
            video_id = video["video_id"]
            logger.info("Processing: %s", video["title"])

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
                processed_ids.add(video_id)
                continue

            filtered = filter_opportunities(opportunities)
            if not filtered:
                logger.info("No valid opportunities after filtering for %s", video_id)
                processed_ids.add(video_id)
                continue

            logger.info("Found %d valid opportunity(ies)", len(filtered))

            channel_title = description_data.get("channel_name", channel_name)

            if send_telegram(filtered, channel_title, video["title"], video_id):
                processed_ids.add(video_id)
                logger.info("Telegram notification sent for %s", video_id)
            else:
                logger.warning("Failed to send Telegram notification for %s", video_id)

        state[channel_id] = list(processed_ids)
        _save_batch_state(state)

    logger.info("Batch run complete")


if __name__ == "__main__":
    run()
