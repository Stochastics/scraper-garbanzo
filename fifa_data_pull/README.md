# FIFA Data Pull (Qatar 2022 + Saudi 2034)

Simple, config-driven Python workflow for collecting public text data from:
- GDELT/news
- manual public URLs (web scraping)
- YouTube (optional)
- Reddit (optional)
- X/Twitter placeholder

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python src/main.py --config configs/run_config.yaml
```

## Source configuration

Enable/disable sources in `configs/run_config.yaml`.

- GDELT and web scraper are enabled by default.
- YouTube runs only if enabled **and** `YOUTUBE_API_KEY` exists.
- Reddit runs only if enabled **and** all required Reddit env vars exist.
- Twitter is a placeholder only.

## Env vars

Create `.env` from example:

```bash
cp .env.example .env
```

Set:

- `YOUTUBE_API_KEY`
- `REDDIT_CLIENT_ID`
- `REDDIT_CLIENT_SECRET`
- `REDDIT_USER_AGENT`

## Output

Main output CSV columns:

- source_type
- source_name
- title
- url
- published_date
- date_collected
- keyword
- matched_terms
- time_window
- language
- text
- raw_metadata

Outputs are written under the folder from `output.path`, including:
- `results.csv`
- source-specific CSVs if `save_source_files: true`
- `scrape_activity.csv` for resume/coverage tracking

## Resume behavior

If `resume_from_activity_log: true`, successful GDELT keyword-window queries and successful scraped URLs are skipped on rerun.

## Scope note (intentionally out of scope v1)

No Facebook, Instagram, cloud hosting, scheduling, Docker, dashboards, or LLM filtering in this first version.
