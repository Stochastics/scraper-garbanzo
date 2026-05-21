import yaml


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def flatten_keywords(keyword_groups: dict) -> list[str]:
    keywords: list[str] = []
    for _, group_terms in (keyword_groups or {}).items():
        if isinstance(group_terms, list):
            keywords.extend([str(term).strip() for term in group_terms if str(term).strip()])
    return list(dict.fromkeys(keywords))
