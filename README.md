# News Pulse — SE446 Big Data Challenge

A real-time news monitoring pipeline built with PySpark Structured Streaming, Streamlit, and Claude AI.

## Pipeline
1. **Ingester** — pulls live headlines from 4 RSS feeds (BBC, Al Jazeera, NPR, Guardian) every 60 seconds
2. **Spark Streaming** — 3 streaming aggregations: by source, by hour window, top keywords
3. **LLM Summary** — Claude API generates a thematic paragraph from top keywords
4. **Dashboard** — Streamlit live dashboard with bar chart, line chart, keyword table, and LLM summary

## Bonus Features
- Auto-refresh every 10 seconds
- Topic clustering with TF-IDF + KMeans (3 clusters)
- GDELT events join on top keywords

## How to Run

### Terminal 1 — Ingester
```bash
cd newspulse && python3 ingester.py
```

### Terminal 2 — Spark Streaming
```bash
cd newspulse && python3 streaming_job.py
```

### Terminal 3 — Dashboard
```bash
cd newspulse && python3 -m streamlit run app.py
```

## Team
- Dana Ghassan

## Course
SE446 — Big Data Engineering, Spring 2026
Prof. Anis Koubaa
