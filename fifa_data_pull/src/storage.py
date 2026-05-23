from pathlib import Path
import pandas as pd


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def save_csv(records: list[dict], output_path: Path) -> None:
    ensure_dir(output_path.parent)
    pd.DataFrame(records).to_csv(output_path, index=False)


def save_activity(activity_rows: list[dict], output_dir: Path) -> None:
    ensure_dir(output_dir)
    path = output_dir / 'scrape_activity.csv'
    df_new = pd.DataFrame(activity_rows)
    if path.exists():
        df_old = pd.read_csv(path)
        df = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df = df_new
    df.to_csv(path, index=False)


def load_completed(output_dir: Path) -> set[str]:
    path = output_dir / 'scrape_activity.csv'
    if not path.exists():
        return set()
    df = pd.read_csv(path)
    if 'status' not in df.columns or 'item_id' not in df.columns:
        return set()
    ok = df[df['status'] == 'success']
    return set(ok['item_id'].astype(str).tolist())
