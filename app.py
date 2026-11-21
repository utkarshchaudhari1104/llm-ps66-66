# app.py - Streamlit UI for the Financial News Summarizer (PS66)
# Run with:  streamlit run app.py
import pandas as pd
import streamlit as st
import config, news_fetcher, summarizer

st.set_page_config(page_title="Financial News Summarizer", page_icon="📈", layout="wide")
st.title("📈 Financial News Summarizer")
st.caption("RSS headlines → local LLM (Qwen2.5 via Ollama) → 1-line summary + sentiment tag")
st.warning("For information only - not financial advice. Sentiment is an AI estimate and can be wrong.")

COLORS = {"positive": ("#e6f4ea", "#137333", "🟢"), "negative": ("#fce8e6", "#c5221f", "🔴"), "neutral": ("#f1f3f4", "#5f6368", "⚪")}

with st.sidebar:
    st.header("⚙️ Settings")
    source = st.selectbox("News source", list(config.FEEDS) + ["Offline sample headlines"])
    model = st.selectbox("Model", summarizer.list_models())
    n = st.slider("Number of headlines", 3, 15, config.MAX_HEADLINES)
    run = st.button("Fetch & Summarise", type="primary", use_container_width=True)

if run:
    try:
        items = news_fetcher.load_sample(n) if source.startswith("Offline") else news_fetcher.fetch_feed(config.FEEDS[source], n)
    except Exception as exc:
        st.error(f"Could not fetch news: {exc}")
        st.info("Tip: choose 'Offline sample headlines' in the sidebar.")
        st.stop()
    bar = st.progress(0.0, text="Analysing headlines...")
    results = []
    for i, it in enumerate(items):
        r = summarizer.analyse_item(it, model)
        r.update({"title": it["title"], "link": it["link"], "published": it["published"]})
        results.append(r)
        bar.progress((i + 1) / len(items), text=f"Analysed {i + 1}/{len(items)}")
    bar.empty()
    st.session_state["results"] = results

results = st.session_state.get("results")
if not results:
    st.info("Choose a source in the sidebar and click **Fetch & Summarise**.")
    st.stop()

df = pd.DataFrame(results)
counts = df["sentiment"].value_counts().reindex(config.SENTIMENTS, fill_value=0)
c1, c2, c3 = st.columns(3)
c1.metric("🟢 Positive", int(counts["positive"]))
c2.metric("🔴 Negative", int(counts["negative"]))
c3.metric("⚪ Neutral", int(counts["neutral"]))

left, right = st.columns([3, 1])
with left:
    st.subheader("News list")
    for r in results:
        bg, fg, icon = COLORS[r["sentiment"]]
        title = f"<a href='{r['link']}' target='_blank'>{r['title']}</a>" if r["link"] else r["title"]
        st.markdown(
            f"<div style='background:{bg};border-left:6px solid {fg};padding:10px 14px;margin-bottom:8px;border-radius:6px;color:#202124'>"
            f"<b>{icon} {r['sentiment'].upper()}</b> &nbsp;|&nbsp; <i>{r['company']}</i><br>"
            f"{r['summary']}<br><small style='color:#5f6368'>{title}</small></div>",
            unsafe_allow_html=True)
with right:
    st.subheader("Sentiment mix")
    st.bar_chart(counts)

st.download_button("⬇️ Download as CSV", df.to_csv(index=False).encode("utf-8"), "financial_news_summary.csv", "text/csv")
