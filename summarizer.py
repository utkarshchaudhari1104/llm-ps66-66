# summarizer.py - LLM summary + sentiment tag for each news item
import json, re
import config

POSITIVE_WORDS = ("profit", "jumps", "rally", "rises", "gain", "surge", "growth", "record", "raises", "upgrade", "beats", "strong", "wins")
NEGATIVE_WORDS = ("loss", "falls", "tumbles", "plunge", "penalty", "fraud", "downgrade", "decline", "slump", "curbs", "sell", "wider", "crash", "fine")

def parse_llm_json(text: str) -> dict | None:
    """Parse the model reply into {'summary','sentiment','company'}; return None if unusable."""
    if not text:
        return None
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    sentiment = str(data.get("sentiment", "")).strip().lower()
    if sentiment not in config.SENTIMENTS:
        return None
    summary = str(data.get("summary", "")).strip()[: config.MAX_SUMMARY_CHARS]
    if not summary:
        return None
    return {"summary": summary, "sentiment": sentiment,
            "company": str(data.get("company", "General")).strip() or "General"}

def rule_based(item: dict) -> dict:
    """Fallback used when the LLM is offline or returns bad JSON."""
    text = (item["title"] + " " + item.get("description", "")).lower()
    pos = sum(w in text for w in POSITIVE_WORDS)
    neg = sum(w in text for w in NEGATIVE_WORDS)
    sentiment = "positive" if pos > neg else "negative" if neg > pos else "neutral"
    return {"summary": item["title"][: config.MAX_SUMMARY_CHARS], "sentiment": sentiment, "company": "General"}

def analyse_item(item: dict, model: str = config.MODEL_NAME, chat=None) -> dict:
    """One LLM call per headline. `chat` can be injected for testing."""
    if chat is None:
        import ollama
        chat = ollama.chat
    user_msg = f"Headline: {item['title']}\nDescription: {item.get('description', '')}"
    try:
        reply = chat(model=model,
                     messages=[{"role": "system", "content": config.PROMPT_V2},
                               {"role": "user", "content": user_msg}],
                     format="json", options={"temperature": 0})
        parsed = parse_llm_json(reply["message"]["content"])
        if parsed:
            parsed["source"] = "LLM"
            return parsed
    except Exception:
        pass
    fb = rule_based(item)
    fb["source"] = "Fallback"
    return fb

def analyse_all(items: list[dict], model: str = config.MODEL_NAME, chat=None) -> list[dict]:
    results = []
    for it in items:
        res = analyse_item(it, model, chat)
        res.update({"title": it["title"], "link": it.get("link", ""), "published": it.get("published", "")})
        results.append(res)
    return results

def list_models() -> list[str]:
    try:
        import ollama
        names = [m.model for m in ollama.list().models]
        return names or [config.MODEL_NAME]
    except Exception:
        return [config.MODEL_NAME]
