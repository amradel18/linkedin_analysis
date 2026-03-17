# LinkedIn Deep Analytics Dashboard

A Streamlit-based analytics application that transforms exported LinkedIn content and audience files into deep performance insights, interactive visualizations, and an AI-ready Markdown report.

## Overview

This project analyzes two LinkedIn export sources:

1. `posts_linkedin.txt` (raw post export text)
2. `Content.xlsx` (LinkedIn analytics export with multiple sheets)

The app cleans and enriches both sources, computes advanced KPIs, and produces:

- Interactive dashboard (Plotly + Streamlit)
- Hook-level and language-level performance analytics
- Weekly change metrics (WoW) from daily performance data
- A downloadable static `.md` report designed for LLM advisory workflows

## Project Structure

```text
linked_in/
├─ app.py               # Streamlit app (UI, analytics, report generation)
├─ clean.py             # Data extraction and cleaning functions
├─ posts_linkedin.txt   # LinkedIn post export input
├─ Content.xlsx         # LinkedIn analytics Excel input
├─ data_ex.md           # Data sample/reference
└─ README.md
```

## Core Features

### 1) Data Ingestion and Cleaning

- Extracts posts using `extract_posts(...)` in `clean.py`
- Loads and cleans Excel analytics using `read_and_clean_excel(...)`
- Supports file upload directly from the dashboard sidebar
- Supports optional fallback to local files in project directory

### 2) Deep KPI Layer

The app computes a broad KPI set across post and daily performance data, including:

- Post-level metrics: impressions, likes, comments, reposts, engagement actions
- Rate metrics: engagement rate, comment rate, repost rate, like rate
- Text metrics: Arabic/English word counts, emoji usage
- Hook metrics: hook length, hook word count, presence of questions/numbers/emojis/alert words
- Daily funnel metrics: impressions, engagements, new followers
- Weekly WoW metrics: change percentages for impressions, engagements, followers, engagement rate

### 3) Advanced Analytics Views

- Daily timeline trends (impressions, engagements, followers)
- Top-performing posts (with engagement efficiency coloring)
- Content-type performance comparison
- Correlation heatmap across major variables
- Hook feature impact analysis
- Hook length band analysis
- Language mix analytics (Arabic-led / Mixed / English-led)
- Emoji density impact analysis

### 4) AI-Oriented Reporting

The app generates a downloadable Markdown report containing:

- Profile context (Headline, About, publishing goal)
- KPI dictionary with values and explanations
- Deep insights summary
- Hook performance matrix
- Top posts table
- Last 15 raw published content rows
- Full demographics table
- Weekly change analytics table
- A high-quality LLM advisor prompt for keyword strategy, profile optimization, content planning, and experimentation

## Data Inputs

### A) `posts_linkedin.txt`

Used by `extract_posts` to parse:

- post date
- content
- hook
- likes/comments/impressions/reposts
- post type flags (`is_text`, `is_image`, `is_link`, `is_pdf`)
- word/emoji counts

### B) `Content.xlsx`

Used by `read_and_clean_excel` to parse and merge:

- daily impressions and engagements
- daily new followers
- demographics (`category`, `value`, `percentage`)

## Installation

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the App

```bash
streamlit run app.py
```

Then open the local Streamlit URL in your browser.

## How to Use

1. Upload `Content.xlsx` and `posts_linkedin.txt` from the sidebar.
2. Fill optional profile context fields:
   - LinkedIn Headline
   - LinkedIn About
   - Publishing Goal
3. Adjust date range for scoped analysis.
4. Review KPIs and charts.
5. Download the generated Markdown report.

## Technical Notes

- `clean.py` handles extraction/cleaning logic.
- `app.py` handles enrichment, analytics, visualization, and reporting.
- Weekly metrics are aggregated from daily `merged_df` and include week-over-week change rates.
- Markdown tables are generated in-code to keep report generation self-contained.

## Troubleshooting

- If Excel loading fails, ensure sheet names in your export match expected names:
  - `DISCOVERY`
  - `ENGAGEMENT`
  - `FOLLOWERS`
  - `DEMOGRAPHICS`
- If uploaded files are missing, the app stops and requests valid inputs.
- If date-range filter returns empty subsets, the app falls back to full available data.

## Future Enhancements

- Export report as PDF in addition to Markdown
- Add benchmark scoring per KPI
- Add automated content calendar generation from top-performing patterns

