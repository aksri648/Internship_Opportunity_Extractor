import json
import logging

import feedparser

from .config import CHANNELS_FILE

logger = logging.getLogger(__name__)


def load_channels() -> list[dict]:
    with open(CHANNELS_FILE, "r") as f:
        return json.load(f)


def get_latest_video(channel_id: str) -> dict | None:
    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    feed = feedparser.parse(feed_url)

    if feed.bozo and not feed.entries:
        logger.error("RSS feed error for channel %s: %s", channel_id, feed.bozo_exception)
        return None

    if not feed.entries:
        return None

    entry = feed.entries[0]
    video_id = entry.yt_videoid
    return {
        "video_id": video_id,
        "title": entry.title,
        "published": entry.published,
        "url": f"https://youtube.com/watch?v={video_id}",
    }
