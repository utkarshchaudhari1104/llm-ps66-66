# Financial News Summarizer (PS66)

**Author:** Utkarsh Chaudhari | Roll No: 66 | Class: LY-AIA-7
**Problem Statement:** PS66 - Summarise daily financial news and tag each item as positive or negative for the company.
**GitHub:** https://github.com/utkarshchaudhari1104/llm-ps66-66

## Features
- Fetches headlines from RSS feeds (Economic Times, Livemint, Moneycontrol, BBC Business)
- Local LLM (Qwen2.5 via Ollama) gives a 1-line summary, sentiment tag and company
- Colour-coded list, sentiment counts, chart and CSV download
- Rule-based fallback if the LLM fails; offline sample headlines for demos

## How to run
    ollama pull qwen2.5:1.5b-instruct
    pip install -r requirements.txt
    streamlit run app.py

Run tests with: python -m pytest -q

## Screenshots
See the screenshots folder.
