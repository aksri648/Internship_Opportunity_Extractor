import json
import subprocess
from typing import Optional
from .config import CHANNELS_FILE


def load_channels() -> list[dict]:
    with open(CHANNELS_FILE, "r") as f:
        return json.load(f)


def get_new_videos(channel_id: str, last_video_id: str) -> list[dict]:
    import feedparser

    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    feed = feedparser.parse(feed_url)

    videos = []
    found_last = not last_video_id
    for entry in feed.entries:
        video_id = entry.yt_videoid
        if not found_last:
            if video_id == last_video_id:
                found_last = True
            continue
        videos.append(
            {
                "video_id": video_id,
                "title": entry.title,
                "published": entry.published,
                "url": f"https://youtube.com/watch?v={video_id}",
            }
        )
    return videos


def get_video_metadata(video_id: str) -> Optional[dict]:
    url = f"https://youtube.com/watch?v={video_id}"
    try:
        result = subprocess.run(
            [
                "yt-dlp",
                "--dump-json",
                "--no-download",
                "--no-warnings",
                url,
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            print(f"yt-dlp error for {video_id}: {result.stderr}")
            return None
        data = json.loads(result.stdout)
        return {
            "title": data.get("title", ""),
            "description": data.get("description", ""),
            "uploader": data.get("uploader", ""),
            "upload_date": data.get("upload_date", ""),
            "url": url,
        }
    except Exception as e:
        print(f"Error fetching metadata for {video_id}: {e}")
        return None
