import argparse
import logging
from pathlib import Path

from dotenv import load_dotenv

from config import load_config, flatten_keywords
from normalize import normalize_record
from storage import save_csv, save_activity, load_completed
from collectors import gdelt, web_scraper, youtube, reddit, twitter


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    return parser.parse_args()


def run():
    load_dotenv()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
    args = parse_args()
    cfg = load_config(args.config)

    keywords = flatten_keywords(cfg.get('keywords', {}))
    time_windows = cfg.get('time_windows', {})
    sources = cfg.get('sources', {})
    output_cfg = cfg.get('output', {})
    output_path = Path(output_cfg.get('path', 'output/results.csv'))
    output_dir = output_path.parent

    completed = load_completed(output_dir) if output_cfg.get('resume_from_activity_log', True) else set()

    all_rows, activity_rows = [], []
    source_rows = {}

    if sources.get('gdelt', {}).get('enabled', False):
        rows, activity = gdelt.collect(sources['gdelt'], keywords, time_windows, completed)
        source_rows['gdelt'] = rows
        all_rows.extend(rows)
        activity_rows.extend(activity)

    if sources.get('web_scraper', {}).get('enabled', False):
        rows, activity = web_scraper.collect(sources['web_scraper'], keywords, completed)
        source_rows['web'] = rows
        all_rows.extend(rows)
        activity_rows.extend(activity)

    if sources.get('youtube', {}).get('enabled', False):
        rows, activity = youtube.collect(sources['youtube'], keywords)
        source_rows['youtube'] = rows
        all_rows.extend(rows)
        activity_rows.extend(activity)

    if sources.get('reddit', {}).get('enabled', False):
        rows, activity = reddit.collect(sources['reddit'], keywords)
        source_rows['reddit'] = rows
        all_rows.extend(rows)
        activity_rows.extend(activity)

    if sources.get('twitter', {}).get('enabled', False):
        rows, activity = twitter.collect(sources['twitter'], keywords)
        source_rows['twitter'] = rows
        all_rows.extend(rows)
        activity_rows.extend(activity)

    normalized = [normalize_record(r) for r in all_rows]
    save_csv(normalized, output_path)

    if output_cfg.get('save_source_files', True):
        for source_name, rows in source_rows.items():
            save_csv([normalize_record(r) for r in rows], output_dir / f'{source_name}_results.csv')

    if activity_rows:
        save_activity(activity_rows, output_dir)

    logging.info('Done. Total records: %s', len(normalized))


if __name__ == '__main__':
    run()
