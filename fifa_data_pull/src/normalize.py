import json
from datetime import datetime, timezone

FINAL_COLUMNS = [
    "source_type",
    "source_name",
    "title",
    "url",
    "published_date",
    "date_collected",
    "keyword",
    "matched_terms",
    "time_window",
    "language",
    "text",
    "raw_metadata",
]


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_record(record: dict) -> dict:
    out = {k: record.get(k, "") for k in FINAL_COLUMNS}
    if isinstance(out.get("matched_terms"), list):
        out["matched_terms"] = ", ".join(out["matched_terms"])
    if isinstance(out.get("raw_metadata"), (dict, list)):
        out["raw_metadata"] = json.dumps(out["raw_metadata"], ensure_ascii=False)
    return out
