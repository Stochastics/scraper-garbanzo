import logging
import os
from datetime import datetime, timezone
import praw


def collect_reddit(keywords: list[str], source_config: dict) -> list[dict]:
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT")

    if not all([client_id, client_secret, user_agent]):
        logging.info("Reddit enabled but credentials missing. Skipping Reddit.")
        return []

    reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)
    subreddits = source_config.get("subreddits", [])
    max_posts = int(source_config.get("max_posts_per_keyword", 50))
    max_comments = int(source_config.get("max_comments_per_post", 25))
    results = []

    for keyword in keywords:
        for sub in subreddits:
            try:
                subreddit = reddit.subreddit(sub)
                for post in subreddit.search(keyword, limit=max_posts, sort="new"):
                    results.append({
                        "source_type": "social",
                        "source_name": "reddit_post",
                        "title": post.title,
                        "url": f"https://www.reddit.com{post.permalink}",
                        "published_date": datetime.fromtimestamp(post.created_utc, tz=timezone.utc).isoformat(),
                        "date_collected": "",
                        "keyword": keyword,
                        "matched_terms": [keyword],
                        "time_window": "",
                        "language": "",
                        "text": post.selftext or "",
                        "raw_metadata": {"score": post.score, "subreddit": sub},
                    })
                    post.comments.replace_more(limit=0)
                    for comment in post.comments[:max_comments]:
                        results.append({
                            "source_type": "social",
                            "source_name": "reddit_comment",
                            "title": f"Comment on: {post.title}",
                            "url": f"https://www.reddit.com{post.permalink}",
                            "published_date": datetime.fromtimestamp(comment.created_utc, tz=timezone.utc).isoformat() if hasattr(comment, 'created_utc') else "",
                            "date_collected": "",
                            "keyword": keyword,
                            "matched_terms": [keyword],
                            "time_window": "",
                            "language": "",
                            "text": getattr(comment, "body", ""),
                            "raw_metadata": {"score": getattr(comment, "score", None), "subreddit": sub},
                        })
            except Exception as exc:
                logging.warning("Reddit fetch failed for r/%s keyword '%s': %s", sub, keyword, exc)
                continue

    return results
