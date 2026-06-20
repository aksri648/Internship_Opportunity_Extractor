from youtube_transcript_api import YouTubeTranscriptApi


def get_transcript(video_id: str) -> str:
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=["en", "hi", "en-IN"])
        return " ".join(entry["text"] for entry in transcript_list)
    except Exception as e:
        print(f"Transcript error for {video_id}: {e}")
        return ""
