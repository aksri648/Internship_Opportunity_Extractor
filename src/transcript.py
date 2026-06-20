import logging

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    CouldNotRetrieveTranscript,
    NoTranscriptFound,
    TranscriptsDisabled,
)

logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = ["en", "hi", "en-IN"]

ytt_api = YouTubeTranscriptApi()


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def _fetch_transcript(video_id: str) -> list:
    fetched = ytt_api.fetch(video_id, languages=SUPPORTED_LANGUAGES)
    return fetched.to_raw_data()


def get_transcript(video_id: str) -> str:
    try:
        transcript_list = _fetch_transcript(video_id)
        return " ".join(entry["text"] for entry in transcript_list)

    except TranscriptsDisabled:
        logger.warning("Transcripts disabled for video %s", video_id)
        return ""

    except NoTranscriptFound:
        logger.warning("No transcript found for video %s", video_id)
        return ""

    except CouldNotRetrieveTranscript:
        logger.warning("Could not retrieve transcript for video %s", video_id)
        return ""

    except Exception as e:
        logger.error("Unexpected transcript error for %s: %s", video_id, e)
        return ""
