import logging
from typing import Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .config import YOUTUBE_API_KEY

logger = logging.getLogger(__name__)


def _get_youtube_client():
    return build("youtube", "v3", developerKey=YOUTUBE_API_KEY)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(HttpError),
    reraise=True,
)
def get_video_description(video_id: str) -> Optional[dict]:
    try:
        youtube = _get_youtube_client()
        response = youtube.videos().list(
            part="snippet",
            id=video_id,
        ).execute()

        items = response.get("items", [])
        if not items:
            logger.warning("No data returned for video %s", video_id)
            return None

        snippet = items[0].get("snippet", {})
        return {
            "title": snippet.get("title", ""),
            "description": snippet.get("description", ""),
            "channel_name": snippet.get("channelTitle", ""),
        }

    except HttpError as e:
        logger.error("YouTube API request failed for %s: %s", video_id, e)
        raise
    except (KeyError, IndexError) as e:
        logger.error("Unexpected API response structure for %s: %s", video_id, e)
        return None
