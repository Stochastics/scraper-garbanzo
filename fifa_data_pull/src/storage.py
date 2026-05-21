import os
import pandas as pd
from normalize import FINAL_COLUMNS


def ensure_output_dir(path: str) -> None:
    output_dir = os.path.dirname(path) or "."
    os.makedirs(output_dir, exist_ok=True)


def save_records(path: str, records: list[dict]) -> None:
    ensure_output_dir(path)
    df = pd.DataFrame(records)
    if df.empty:
        df = pd.DataFrame(columns=FINAL_COLUMNS)
    else:
        for col in FINAL_COLUMNS:
            if col not in df.columns:
                df[col] = ""
        df = df[FINAL_COLUMNS]
    df.to_csv(path, index=False)
