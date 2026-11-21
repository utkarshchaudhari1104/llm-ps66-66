import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import summarizer, news_fetcher

def fake_chat(content):
    return lambda **kw: {"message": {"content": content}}

ITEM = {"title": "Infosys raises revenue guidance", "description": "Strong deal wins", "link": "", "published": ""}

def test_parse_valid_json():
    r = summarizer.parse_llm_json('{"summary":"Infosys raised guidance.","sentiment":"Positive","company":"Infosys"}')
    assert r["sentiment"] == "positive" and r["company"] == "Infosys"

def test_parse_json_with_extra_text():
    assert summarizer.parse_llm_json('Sure! {"summary":"x","sentiment":"negative","company":"A"} done')["sentiment"] == "negative"

def test_parse_bad_sentiment_rejected():
    assert summarizer.parse_llm_json('{"summary":"x","sentiment":"bullish","company":"A"}') is None

def test_parse_garbage_rejected():
    assert summarizer.parse_llm_json("not json") is None
    assert summarizer.parse_llm_json("") is None

def test_summary_is_truncated():
    r = summarizer.parse_llm_json('{"summary":"%s","sentiment":"neutral","company":"A"}' % ("a" * 500))
    assert len(r["summary"]) <= 200

def test_llm_path_used():
    r = summarizer.analyse_item(ITEM, chat=fake_chat('{"summary":"ok","sentiment":"positive","company":"Infosys"}'))
    assert r["source"] == "LLM" and r["sentiment"] == "positive"

def test_fallback_on_bad_json():
    r = summarizer.analyse_item(ITEM, chat=fake_chat("oops"))
    assert r["source"] == "Fallback" and r["sentiment"] == "positive"

def test_fallback_when_llm_down():
    def boom(**kw): raise ConnectionError("ollama down")
    assert summarizer.analyse_item(ITEM, chat=boom)["source"] == "Fallback"

def test_rule_based_negative_and_neutral():
    assert summarizer.rule_based({"title": "Paytm loss widens, penalty imposed", "description": ""})["sentiment"] == "negative"
    assert summarizer.rule_based({"title": "Gold steady ahead of data", "description": ""})["sentiment"] == "neutral"

def test_analyse_all_keeps_title():
    out = summarizer.analyse_all([ITEM, ITEM], chat=fake_chat('{"summary":"s","sentiment":"neutral","company":"G"}'))
    assert len(out) == 2 and out[0]["title"] == ITEM["title"]

def test_clean_html():
    assert news_fetcher.clean_html("<p>Hello &amp; <b>world</b></p>") == "Hello & world"

def test_sample_loads():
    assert len(news_fetcher.load_sample(5)) == 5
