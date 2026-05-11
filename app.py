import streamlit as st, time, requests, os, json, glob
import pandas as pd

def get_llm_summary(keywords):
    kw_str = ", ".join(keywords[:15])
    try:
        resp = requests.post("https://api.anthropic.com/v1/messages",
            headers={"x-api-key":os.environ.get("ANTHROPIC_API_KEY",""),"anthropic-version":"2023-06-01","content-type":"application/json"},
            json={"model":"claude-sonnet-4-20250514","max_tokens":150,"messages":[{"role":"user","content":f"Based on these trending news keywords: {kw_str}\n\nWrite exactly one paragraph (max 80 words) summarising the main themes in todays global news. Mention at least three specific named storylines. Be factual and concise."}]},
            timeout=10)
        return resp.json()["content"][0]["text"]
    except Exception as e:
        return f"Top keywords: {kw_str}. (LLM unavailable: {e})"

st.set_page_config(page_title="News Pulse",layout="wide")
st.title("News Pulse — Live")

files = glob.glob("data/incoming/*.json")
if not files:
    st.warning("No data yet — is ingester.py running?")
    time.sleep(5); st.rerun()

rows = []
for f in files:
    with open(f) as fh:
        for line in fh:
            line = line.strip()
            if line:
                try: rows.append(json.loads(line))
                except: pass

df = pd.DataFrame(rows)

if df.empty:
    st.warning("No data yet — waiting...")
    time.sleep(5); st.rerun()

df["ts"] = pd.to_datetime(df["ts"], errors="coerce", utc=True)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Headlines by source")
    src_counts = df.groupby("source").size().reset_index(name="count")
    st.bar_chart(src_counts.set_index("source")["count"])

with col2:
    st.subheader("Volume by hour")
    df_time = df.dropna(subset=["ts"])
    if not df_time.empty:
        df_time = df_time.copy()
        df_time["hour"] = df_time["ts"].dt.floor("h")
        win_counts = df_time.groupby("hour").size().reset_index(name="count")
        st.line_chart(win_counts.set_index("hour")["count"])
    else:
        st.info("Waiting for timestamp data...")

STOPWORDS = {"the","a","an","and","or","in","is","to","of","for","on","at","by","with","this","that","was","are","be","as","it","have","has","will","from","not","but","its","been","more","says","after","over","amid","into","than","then","their","what","when","who","your","about","just","also"}
words = []
for title in df["title"].dropna():
    for w in title.lower().split():
        w = "".join(c for c in w if c.isalpha())
        if len(w) > 3 and w not in STOPWORDS:
            words.append(w)
word_df = pd.Series(words).value_counts().reset_index()
word_df.columns = ["word","count"]
word_df = word_df.head(10)

st.subheader("Top keywords")
st.dataframe(word_df, use_container_width=True)

st.subheader("LLM thematic summary")
st.info(get_llm_summary(word_df["word"].tolist()))

time.sleep(10); st.rerun()
