from .youtube import load_channels, get_new_videos, get_video_metadata
from .transcript import get_transcript
from .extractor import extract_opportunities
from .telegram import format_message, send_telegram
from .state import load_state, save_state


def run():
    channels = load_channels()
    state = load_state()

    for channel in channels:
        channel_id = channel["channel_id"]
        channel_name = channel["name"]
        last_video_id = state.get(channel_id, "")

        print(f"Checking channel: {channel_name} ({channel_id})")

        new_videos = get_new_videos(channel_id, last_video_id)
        if not new_videos:
            print(f"  No new videos for {channel_name}")
            continue

        print(f"  Found {len(new_videos)} new video(s)")

        for video in new_videos:
            video_id = video["video_id"]
            print(f"  Processing: {video['title']}")

            metadata = get_video_metadata(video_id)
            if not metadata:
                print(f"    Skipping - metadata fetch failed")
                continue

            transcript = get_transcript(video_id)

            opportunities = extract_opportunities(
                title=metadata["title"],
                description=metadata["description"],
                transcript=transcript,
            )

            if not opportunities:
                print(f"    No opportunities found in video")
                continue

            print(f"    Found {len(opportunities)} opportunity(ies)")

            message = format_message(opportunities, channel_name, video["url"])
            if send_telegram(message):
                state[channel_id] = video_id
                save_state(state)
                print(f"    State updated to {video_id}")
            else:
                print(f"    Failed to send Telegram notification, skipping state update")

    print("Run complete")


if __name__ == "__main__":
    run()
