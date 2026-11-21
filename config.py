# config.py - central settings for the Financial News Summarizer (PS66)

MODEL_NAME = "qwen2.5:1.5b-instruct"   # local model served by Ollama (no API key needed)
MAX_HEADLINES = 10                      # how many headlines to summarise per run
MAX_SUMMARY_CHARS = 200                 # safety cap for the 1-line summary

# Free public RSS feeds (no login needed)
FEEDS = {
    "Economic Times - Markets": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "Livemint - Markets": "https://www.livemint.com/rss/markets",
    "Moneycontrol - Business": "https://www.moneycontrol.com/rss/business.xml",
    "BBC - Business": "http://feeds.bbci.co.uk/news/business/rss.xml",
}

SENTIMENTS = ("positive", "negative", "neutral")

# Prompt V1 (first attempt, kept for the report comparison)
PROMPT_V1 = "Summarise this financial news in one line and say if it is positive or negative."

# Prompt V2 (final) - strict JSON, company tag, "impact on the company" wording
PROMPT_V2 = (
    "You are a financial news analyst. Read the headline and description.\n"
    "Return ONLY valid JSON with these keys:\n"
    '{"summary": "<one sentence, max 25 words, facts only>", '
    '"sentiment": "positive|negative|neutral", '
    '"company": "<main company/index/sector or General>"}\n'
    "Rules:\n"
    "1. sentiment = likely impact on the main company/market: positive (profit, growth, "
    "rally, upgrade), negative (loss, fall, fraud, downgrade, penalty), else neutral.\n"
    "2. Use only facts present in the text. Never invent numbers or names.\n"
    "3. If unsure, use neutral."
)
