# FIFA Data Pull Workflow

A simple configurable Python workflow for collecting public data related to Qatar FIFA 2022 and Saudi FIFA 2034 research.

## What it does
- Uses one YAML config file to control keywords, time windows, enabled data sources, and output location.
- Collects from GDELT and manually provided public webpages by default.
- Optionally collects from YouTube comments and Reddit when credentials are available.
- Includes an X/Twitter placeholder collector for future implementation.

## Install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configure sources
Edit `configs/run_config.yaml`:
- Enable/disable sources in `sources.*.enabled`
- Update keywords and time windows
- Set output path

## Run
```bash
python src/main.py --config configs/run_config.yaml
```

## Environment variables
Copy and edit:
```bash
cp .env.example .env
```

### YouTube
Set:
- `YOUTUBE_API_KEY`

If YouTube is enabled but key is missing, collection is skipped safely.

### Reddit
Set:
- `REDDIT_CLIENT_ID`
- `REDDIT_CLIENT_SECRET`
- `REDDIT_USER_AGENT`

If Reddit is enabled but credentials are missing, collection is skipped safely.

## Why X/Twitter is a placeholder
Historical X/Twitter collection may require paid API full-archive access. This version includes only a stub collector with a clear message.

## Output columns
- `source_type`: High-level category (news, web, social)
- `source_name`: Specific source/collector name
- `title`: Title/headline/post title
- `url`: Source URL
- `published_date`: Original published/created date if available
- `date_collected`: UTC timestamp when collected
- `keyword`: Keyword used for query/search
- `matched_terms`: Terms matched in text
- `time_window`: Configured time window label
- `language`: Language if available
- `text`: Main text/body/comment
- `raw_metadata`: JSON blob with source-specific metadata

## Scrape activity tracking
- Each run also writes `output/scrape_activity.csv` to show where collection ran and whether each target succeeded.
- For web scraping, it logs each URL attempted and matched keyword count.
- For GDELT, it logs each keyword + time-window query and how many articles were returned.
- Resume behavior: by default (`output.resume_from_activity_log: true`), a new run will skip previously successful GDELT keyword-window queries and previously successful scraped URLs.

## Out of scope (intentional for v1)
Facebook, Instagram, cloud hosting, scheduling, dashboards, databases, and LLM filtering/scoring.
