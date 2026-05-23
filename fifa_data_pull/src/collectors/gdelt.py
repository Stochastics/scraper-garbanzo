from datetime import datetime, timezone
import logging
import requests


LOGGER = logging.getLogger(__name__)
GDELT_DOC_API = 'https://api.gdeltproject.org/api/v2/doc/doc'


def collect(config: dict, keywords: list[str], time_windows: dict, completed_items: set[str] | None = None):
    results, activity = [], []
    max_records = config.get('max_records_per_keyword', 25)
    completed_items = completed_items or set()

    for window_name, dates in time_windows.items():
        for keyword in keywords:
            item_id = f'gdelt::{window_name}::{keyword}'
            if item_id in completed_items:
                activity.append(_activity(item_id, 'gdelt', 'skipped', 0, keyword, window_name))
                continue
            try:
                params = {
                    'query': keyword,
                    'mode': 'ArtList',
                    'maxrecords': max_records,
                    'format': 'json',
                    'startdatetime': dates['start_date'].replace('-', '') + '000000',
                    'enddatetime': dates['end_date'].replace('-', '') + '235959',
                }
                resp = requests.get(GDELT_DOC_API, params=params, timeout=30)
                resp.raise_for_status()
                articles = resp.json().get('articles', [])
                for a in articles:
                    results.append({
                        'source_type': 'news', 'source_name': a.get('source', 'GDELT'),
                        'title': a.get('title'), 'url': a.get('url'),
                        'published_date': a.get('seendate'), 'keyword': keyword,
                        'matched_terms': [keyword], 'time_window': window_name,
                        'language': None, 'text': a.get('snippet', ''), 'raw_metadata': a,
                    })
                activity.append(_activity(item_id, 'gdelt', 'success', len(articles), keyword, window_name))
            except Exception as exc:
                LOGGER.warning('GDELT failed for %s %s: %s', window_name, keyword, exc)
                activity.append(_activity(item_id, 'gdelt', 'failed', 0, keyword, window_name, str(exc)))
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
