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


st.subheader("Topic clusters")
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
titles = df["title"].dropna().tolist()
if len(titles) >= 3:
    try:
        vec = TfidfVectorizer(max_features=50, stop_words="english")
        X = vec.fit_transform(titles)
        k = KMeans(n_clusters=3, random_state=0, n_init=10).fit(X)
        df2 = pd.DataFrame({"title": titles, "cluster": k.labels_})
        for i in range(3):
            st.markdown(f"**Cluster {i+1}**")
            st.write(df2[df2.cluster==i]["title"].head(3).tolist())
    except Exception as e:
        st.info(f"Clustering unavailable: {e}")


st.subheader("GDELT join")
try:
    import pandas as pd
    gdelt = pd.read_csv("20260511091500.export.CSV", sep="\t", header=None, usecols=[1,5,6], names=["date","country","url"], on_bad_lines="skip")
    keywords = word_df["word"].tolist()[:5]
    pattern = "|".join(keywords)
    matched = gdelt[gdelt["url"].str.contains(pattern, case=False, na=False)]
    st.write(f"GDELT events matching top keywords: {len(matched)}")
    st.dataframe(matched.head(10), use_container_width=True)
except Exception as e:
    st.info(f"GDELT unavailable: {e}")

time.sleep(10); st.rerun()
