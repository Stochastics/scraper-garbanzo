import logging
import os
import requests


def collect_youtube(keywords: list[str], source_config: dict) -> list[dict]:
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        logging.info("YouTube enabled but YOUTUBE_API_KEY not found. Skipping YouTube.")
        return []

    max_videos = int(source_config.get("max_videos_per_keyword", 5))
    max_comments = int(source_config.get("max_comments_per_video", 100))
    results = []

    for keyword in keywords:
        try:
            search_resp = requests.get(
                "https://www.googleapis.com/youtube/v3/search",
                params={
                    "key": api_key,
                    "q": keyword,
                    "part": "snippet",
                    "type": "video",
                    "maxResults": max_videos,
                },
                timeout=30,
            )
            search_resp.raise_for_status()
        except Exception as exc:
            logging.warning("YouTube search failed for '%s': %s", keyword, exc)
            continue

        for item in search_resp.json().get("items", []):
            video_id = item.get("id", {}).get("videoId")
            if not video_id:
                continue
            video_title = item.get("snippet", {}).get("title", "")
            video_url = f"https://www.youtube.com/watch?v={video_id}"

            try:
                comment_resp = requests.get(
                    "https://www.googleapis.com/youtube/v3/commentThreads",
                    params={
                        "key": api_key,
                        "videoId": video_id,
                        "part": "snippet",
                        "maxResults": min(max_comments, 100),
                        "textFormat": "plainText",
                    },
                    timeout=30,
                )
                comment_resp.raise_for_status()
            except Exception as exc:
                logging.warning("YouTube comments failed for video '%s': %s", video_id, exc)
                continue

            for c in comment_resp.json().get("items", []):
                text = c.get("snippet", {}).get("topLevelComment", {}).get("snippet", {}).get("textDisplay", "")
                results.append({
                    "source_type": "social",
                    "source_name": "youtube",
                    "title": video_title,
                    "url": video_url,
                    "published_date": "",
                    "date_collected": "",
                    "keyword": keyword,
                    "matched_terms": [keyword],
                    "time_window": "",
                    "language": "",
                    "text": text,
                    "raw_metadata": c,
                })
    return results
