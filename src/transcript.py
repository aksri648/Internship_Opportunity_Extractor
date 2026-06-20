import logging

from swiftshadow import QuickProxy
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    CouldNotRetrieveTranscript,
    NoTranscriptFound,
    TranscriptsDisabled,
)
from youtube_transcript_api.proxies import GenericProxyConfig

logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = ["en", "hi", "en-IN"]


def _get_proxy_config():
    try:
        proxy = QuickProxy(protocol="https")
        if proxy.ip and proxy.port:
            http_url = f"http://{proxy.ip}:{proxy.port}"
            https_url = f"http://{proxy.ip}:{proxy.port}"
            logger.info("Using proxy %s:%s", proxy.ip, proxy.port)
            return GenericProxyConfig(
                http_url=http_url,
                https_url=https_url,
            )
    except Exception as e:
        logger.warning("Failed to get proxy, using direct connection: %s", e)
    return None


def _create_api():
    proxy_config = _get_proxy_config()
    if proxy_config:
        return YouTubeTranscriptApi(proxy_config=proxy_config)
    return YouTubeTranscriptApi()


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def _fetch_transcript(video_id: str) -> list:
    api = _create_api()
    fetched = api.fetch(video_id, languages=SUPPORTED_LANGUAGES)
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
