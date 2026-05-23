from datetime import datetime, timezone
import logging
import requests
from bs4 import BeautifulSoup

LOGGER = logging.getLogger(__name__)


def collect(config: dict, keywords: list[str], completed_items: set[str] | None = None):
    results, activity = [], []
    urls = config.get('urls', [])
    completed_items = completed_items or set()

    for url in urls:
        item_id = f'web::{url}'
        if item_id in completed_items:
            activity.append(_activity(item_id, 'web_scraper', 'skipped', 0, None, None))
            continue
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            for tag in soup(['script', 'style', 'noscript']):
                tag.decompose()
            title = soup.title.get_text(strip=True) if soup.title else url
            text = ' '.join(soup.stripped_strings)
            matched = [k for k in keywords if k.lower() in text.lower()]
            results.append({
                'source_type': 'web', 'source_name': 'web_scraper', 'title': title, 'url': url,
                'published_date': None, 'keyword': None, 'matched_terms': matched,
                'time_window': None, 'language': None, 'text': text, 'raw_metadata': {'status_code': resp.status_code}
            })
            activity.append(_activity(item_id, 'web_scraper', 'success', 1, None, None))
        except Exception as exc:
            LOGGER.warning('Web scrape failed for %s: %s', url, exc)
            activity.append(_activity(item_id, 'web_scraper', 'failed', 0, None, None, str(exc)))
    return results, activity


def _activity(item_id, source, status, records, keyword, time_window, error=None):
    return {
        'item_id': item_id,
        'source_name': source,
        'status': status,
        'records_count': records,
        'keyword': keyword,
        'time_window': time_window,
        'error': error,
        'date_collected': datetime.now(timezone.utc).isoformat(),
    }
