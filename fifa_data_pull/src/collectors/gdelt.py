import logging
import requests

GDELT_API = "https://api.gdeltproject.org/api/v2/doc/doc"


def collect_gdelt(
    keywords: list[str],
    time_windows: dict,
    source_config: dict,
    completed_items: set[str] | None = None,
) -> tuple[list[dict], list[dict]]:
    results = []
    query_log = []
    max_records = int(source_config.get("max_records_per_keyword", 25))

    for window_name, window in (time_windows or {}).items():
        start_date = window.get("start_date")
        end_date = window.get("end_date")
        for keyword in keywords:
            item_key = f"{keyword} | {window_name}"
            if completed_items and item_key in completed_items:
                query_log.append({"source": "gdelt", "item": item_key, "status": "skipped", "notes": "already_completed"})
                continue
            params = {
                "query": keyword,
                "mode": "ArtList",
                "maxrecords": max_records,
                "format": "json",
                "startdatetime": start_date.replace("-", "") + "000000" if start_date else "",
                "enddatetime": end_date.replace("-", "") + "235959" if end_date else "",
            }
            try:
                resp = requests.get(GDELT_API, params=params, timeout=30)
                resp.raise_for_status()
                data = resp.json()
            except Exception as exc:
                logging.warning("GDELT request failed for '%s' in '%s': %s", keyword, window_name, exc)
                query_log.append(
                    {
                        "source": "gdelt",
                        "item": item_key,
                        "status": "failed",
                        "notes": str(exc),
                    }
                )
                continue

            articles = data.get("articles", []) or []
            query_log.append(
                {
                    "source": "gdelt",
                    "item": item_key,
                    "status": "success",
                    "notes": f"articles={len(articles)}",
                }
            )

            for item in articles:
                results.append(
                    {
                        "source_type": "news",
                        "source_name": item.get("source", "GDELT"),
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "published_date": item.get("seendate", ""),
                        "date_collected": "",
                        "keyword": keyword,
                        "matched_terms": [keyword],
                        "time_window": window_name,
                        "language": item.get("language", ""),
                        "text": item.get("title", ""),
                        "raw_metadata": item,
                    }
                )
    return results, query_log
