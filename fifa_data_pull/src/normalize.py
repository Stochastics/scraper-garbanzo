import json
from datetime import datetime, timezone

SCHEMA = [
    'source_type', 'source_name', 'title', 'url', 'published_date',
    'date_collected', 'keyword', 'matched_terms', 'time_window',
    'language', 'text', 'raw_metadata'
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_record(record: dict) -> dict:
    out = {key: None for key in SCHEMA}
    out.update(record)
    out['date_collected'] = out.get('date_collected') or now_iso()
    mt = out.get('matched_terms')
    if isinstance(mt, list):
        out['matched_terms'] = '|'.join(mt)
    meta = out.get('raw_metadata')
    if isinstance(meta, (dict, list)):
        out['raw_metadata'] = json.dumps(meta, ensure_ascii=False)
    return out
