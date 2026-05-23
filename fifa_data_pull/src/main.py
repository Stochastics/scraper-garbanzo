import os
import argparse
import logging
from dotenv import load_dotenv
import pandas as pd

from config import load_config, flatten_keywords
from normalize import normalize_record, now_utc_iso
from storage import save_records, ensure_output_dir
from collectors.gdelt import collect_gdelt
from collectors.web_scraper import collect_web_pages
from collectors.youtube import collect_youtube
from collectors.reddit import collect_reddit
from collectors.twitter import collect_twitter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="FIFA data pull workflow")
    parser.add_argument("--config", required=True, help="Path to YAML config")
    return parser.parse_args()


def stamp_dates(records: list[dict]) -> list[dict]:
    collected = now_utc_iso()
    for r in records:
        if not r.get("date_collected"):
            r["date_collected"] = collected
    return records


def stamp_scrape_log(log_items: list[dict]) -> list[dict]:
    collected = now_utc_iso()
    stamped = []
    for item in log_items:
        row = dict(item)
        row["date_collected"] = collected
        stamped.append(row)
    return stamped


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    load_dotenv()
    args = parse_args()
    cfg = load_config(args.config)

    keywords = flatten_keywords(cfg.get("keywords", {}))
    time_windows = cfg.get("time_windows", {})
    source_cfg = cfg.get("sources", {})

    combined = []
    per_source = {
        "gdelt": [],
        "web": [],
        "youtube": [],
        "reddit": [],
        "twitter": [],
    }
    scrape_activity = []
    output_path = cfg.get("output", {}).get("path", "output/results.csv")
    output_dir = os.path.dirname(output_path) or "output"
    activity_path = os.path.join(output_dir, "scrape_activity.csv")
    resume_enabled = cfg.get("output", {}).get("resume_from_activity_log", True)

    completed = {"gdelt": set(), "web_scraper": set()}
    if resume_enabled and os.path.exists(activity_path):
        try:
            existing = pd.read_csv(activity_path)
            for source in ["gdelt", "web_scraper"]:
                done = existing[(existing["source"] == source) & (existing["status"] == "success")]
                completed[source] = set(done["item"].dropna().astype(str).tolist())
            logging.info("Resume enabled: loaded prior completed items from %s", activity_path)
        except Exception as exc:
            logging.warning("Could not read %s for resume. Continuing fresh: %s", activity_path, exc)

    if source_cfg.get("gdelt", {}).get("enabled", False):
        try:
            gdelt_rows, gdelt_log = collect_gdelt(
                keywords, time_windows, source_cfg.get("gdelt", {}), completed_items=completed["gdelt"]
            )
            per_source["gdelt"] = gdelt_rows
            scrape_activity.extend(gdelt_log)
        except Exception as exc:
            logging.exception("GDELT collector failed: %s", exc)

    if source_cfg.get("web_scraper", {}).get("enabled", False):
        try:
            web_rows, web_log = collect_web_pages(
                keywords, source_cfg.get("web_scraper", {}), completed_items=completed["web_scraper"]
            )
            per_source["web"] = web_rows
            scrape_activity.extend(web_log)
        except Exception as exc:
            logging.exception("Web scraper failed: %s", exc)

    if source_cfg.get("youtube", {}).get("enabled", False):
        try:
            per_source["youtube"] = collect_youtube(keywords, source_cfg.get("youtube", {}))
        except Exception as exc:
            logging.exception("YouTube collector failed: %s", exc)

    if source_cfg.get("reddit", {}).get("enabled", False):
        try:
            per_source["reddit"] = collect_reddit(keywords, source_cfg.get("reddit", {}))
        except Exception as exc:
            logging.exception("Reddit collector failed: %s", exc)

    if source_cfg.get("twitter", {}).get("enabled", False):
        try:
            per_source["twitter"] = collect_twitter(keywords, source_cfg.get("twitter", {}))
        except Exception as exc:
            logging.exception("Twitter collector failed: %s", exc)

    save_source_files = cfg.get("output", {}).get("save_source_files", True)
    for source_name, items in per_source.items():
        stamped = stamp_dates(items)
        normalized = [normalize_record(x) for x in stamped]
        combined.extend(normalized)
        if save_source_files:
            save_records(os.path.join(output_dir, f"{source_name}_results.csv"), normalized)

    save_records(output_path, combined)
    if scrape_activity:
        ensure_output_dir(activity_path)
        new_rows = pd.DataFrame(stamp_scrape_log(scrape_activity))
        if os.path.exists(activity_path):
            old_rows = pd.read_csv(activity_path)
            all_rows = pd.concat([old_rows, new_rows], ignore_index=True)
        else:
            all_rows = new_rows
        all_rows.to_csv(activity_path, index=False)
        logging.info("Saved scrape activity log to %s", activity_path)
    logging.info("Saved %s combined records to %s", len(combined), output_path)


if __name__ == "__main__":
    main()
