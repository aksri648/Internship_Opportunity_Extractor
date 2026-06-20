import logging

import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)

TRANSCRIPT_API_URL = "https://youtube-transcript-api-tau-one.vercel.app/transcript"


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    retry=retry_if_exception_type(requests.RequestException),
    reraise=True,
)
def _fetch_transcript(video_id: str) -> str:
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    response = requests.post(
        TRANSCRIPT_API_URL,
        json={"url": video_url},
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()
    return data.get("transcript", "")


def get_transcript(video_id: str) -> str:
    try:
        transcript = _fetch_transcript(video_id)
        if transcript:
            return transcript
        logger.warning("Empty transcript for video %s", video_id)
        return ""

    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            logger.warning("No transcript available for video %s", video_id)
        else:
            logger.error("Transcript API error for %s: %s", video_id, e)
        return ""

    except Exception as e:
        logger.error("Unexpected transcript error for %s: %s", video_id, e)
        return ""
