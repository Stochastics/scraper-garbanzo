import logging
import requests
from bs4 import BeautifulSoup


def collect_web_pages(
    keywords: list[str],
    source_config: dict,
    completed_items: set[str] | None = None,
) -> tuple[list[dict], list[dict]]:
    urls = source_config.get("urls", [])
    results = []
    scrape_log = []

    for url in urls:
        if completed_items and url in completed_items:
            scrape_log.append({"source": "web_scraper", "item": url, "status": "skipped", "notes": "already_completed"})
            continue
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
        except Exception as exc:
            logging.warning("Web scrape failed for %s: %s", url, exc)
            scrape_log.append(
                {
                    "source": "web_scraper",
                    "item": url,
                    "status": "failed",
                    "notes": str(exc),
                }
            )
            continue

        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        title = soup.title.get_text(strip=True) if soup.title else ""
        text = soup.get_text(" ", strip=True)
        lower_text = text.lower()
        matched_terms = [k for k in keywords if k.lower() in lower_text]

        results.append(
            {
                "source_type": "web",
                "source_name": "manual_url",
                "title": title,
                "url": url,
                "published_date": "",
                "date_collected": "",
                "keyword": "",
                "matched_terms": matched_terms,
                "time_window": "",
                "language": "",
                "text": text,
                "raw_metadata": {"status_code": resp.status_code},
            }
        )
        scrape_log.append(
            {
                "source": "web_scraper",
                "item": url,
                "status": "success",
                "notes": f"matched_terms={len(matched_terms)}",
            }
        )
    return results, scrape_log
