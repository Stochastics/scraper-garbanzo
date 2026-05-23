from pathlib import Path
import yaml


def load_config(config_path: str) -> dict:
    path = Path(config_path)
    with path.open('r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def flatten_keywords(keywords_cfg: dict) -> list[str]:
    words = []
    for group in keywords_cfg.values():
        words.extend(group or [])
    return list(dict.fromkeys(words))
