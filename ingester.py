import os, json, time, feedparser
INCOMING = "data/incoming"
os.makedirs(INCOMING, exist_ok=True)
FEEDS = {
    "BBC":       "http://feeds.bbci.co.uk/news/rss.xml",
    "AlJazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "NPR":       "https://feeds.npr.org/1001/rss.xml",
    "Guardian":  "https://www.theguardian.com/world/rss",
}
def pull_once(tick):
    rows = []
    for source, url in FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:20]:
                rows.append({"source":source,"title":entry.get("title",""),"url":entry.get("link",""),"ts":entry.get("published",time.strftime("%Y-%m-%dT%H:%M:%SZ"))})
        except Exception as e:
            print(f"[WARN] {source} failed: {e}")
    path = os.path.join(INCOMING, f"batch_{tick}.json")
    with open(path,"w") as f:
        for r in rows:
            f.write(json.dumps(r)+"\n")
    print(f"Wrote {len(rows)} rows -> {path}")
if __name__ == "__main__":
    tick = 0
    while True:
        pull_once(tick); tick += 1; time.sleep(60)
