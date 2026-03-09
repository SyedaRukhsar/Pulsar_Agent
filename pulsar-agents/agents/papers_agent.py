"""
PULSAR — Papers Agent
=====================
Fetches research papers from arXiv based on user interests,
generates AI summaries via Groq, saves to Firestore feed_papers.

Run:  python agents/papers_agent.py
Schedule: GitHub Actions every 6 hours
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import feedparser
from datetime import datetime, timezone
from core.firestore_client import get_db, get_all_users, upsert_document
from core.groq_client import get_groq_client, summarize
from core.utils import make_doc_id, is_recent, now_iso, extract_user_topics


# ── arXiv category mapping ────────────────────────────────────────
TOPIC_TO_ARXIV = {
    "machine learning":        "cs.LG",
    "deep learning":           "cs.LG",
    "neural networks":         "cs.NE",
    "nlp":                     "cs.CL",
    "natural language processing": "cs.CL",
    "computer vision":         "cs.CV",
    "ai":                      "cs.AI",
    "artificial intelligence": "cs.AI",
    "reinforcement learning":  "cs.LG",
    "data science":            "stat.ML",
    "robotics":                "cs.RO",
    "cybersecurity":           "cs.CR",
    "cloud computing":         "cs.DC",
    "software engineering":    "cs.SE",
    "web development":         "cs.SE",
    "bioinformatics":          "q-bio.QM",
    "quantum computing":       "quant-ph",
    "research":                "cs.AI",
}

DEFAULT_CATEGORIES = ["cs.AI", "cs.LG", "cs.CL", "cs.CV"]

ARXIV_RSS = "https://rss.arxiv.org/rss/{category}"


# ── Groq prompt ───────────────────────────────────────────────────
def build_prompt(paper: dict) -> str:
    return f"""You are an expert research advisor. Analyze this research paper and explain it clearly.

Format EXACTLY using HTML below. No markdown. No extra text outside HTML.

<div class="ai-summary-box">
    <h3>📄 {paper['title']}</h3>

    <h4>🔍 What This Paper Is About</h4>
    <p>[2-3 sentence plain English summary of the research]</p>

    <h4>🧠 Key Contributions</h4>
    <ul>
        <li>[Main contribution 1]</li>
        <li>[Main contribution 2]</li>
        <li>[Main contribution 3]</li>
    </ul>

    <h4>💡 Why It Matters</h4>
    <p>[Real-world impact and applications of this research]</p>

    <h4>🛠️ Methods Used</h4>
    <p>[Techniques, models, datasets used in the paper]</p>

    <h4>🎯 Who Should Read This</h4>
    <p>[Which students or researchers would benefit most]</p>

    <p><strong>🔗 Read Paper:</strong> <a href="{paper['link']}" target="_blank">View on arXiv</a></p>
</div>

---
Title: {paper['title']}
Abstract: {paper.get('summary', '')[:800]}
Authors: {paper.get('authors', '')}
"""


# ── Fetch from arXiv ──────────────────────────────────────────────
def fetch_arxiv(category: str, max_items: int = 10) -> list:
    url = ARXIV_RSS.format(category=category)
    print(f"  Fetching arXiv [{category}]: {url}")
    try:
        feed = feedparser.parse(url)
        papers = []
        for entry in feed.entries[:max_items]:
            papers.append({
                "title":     entry.get("title", "").replace("\n", " ").strip(),
                "link":      entry.get("link", ""),
                "summary":   entry.get("summary", ""),
                "authors":   entry.get("author", ""),
                "pubDate":   entry.get("published", ""),
                "arxivId":   entry.get("id", "").split("/abs/")[-1],
                "category":  category,
            })
        print(f"    → {len(papers)} papers fetched")
        return papers
    except Exception as e:
        print(f"    ✗ Error: {e}")
        return []


# ── Main agent ────────────────────────────────────────────────────
def run():
    print("=" * 60)
    print("PULSAR Papers Agent — Starting")
    print("=" * 60)

    db     = get_db()
    groq   = get_groq_client()
    users  = get_all_users(db)
    print(f"✓ {len(users)} users loaded")

    user_topics = extract_user_topics(users)

    # Build: category → list of user IDs interested in it
    category_to_users  = {}
    category_to_topics = {}

    for uid, topics in user_topics.items():
        seen_cats = set()
        for topic in topics:
            cats = [TOPIC_TO_ARXIV.get(topic)] if TOPIC_TO_ARXIV.get(topic) else DEFAULT_CATEGORIES
            for cat in cats:
                if cat not in seen_cats:
                    seen_cats.add(cat)
                if cat not in category_to_users:
                    category_to_users[cat]  = []
                    category_to_topics[cat] = []
                if uid not in category_to_users[cat]:
                    category_to_users[cat].append(uid)
                for t in topics:
                    if t not in category_to_topics[cat]:
                        category_to_topics[cat].append(t)

    # Fallback — always include defaults
    for cat in DEFAULT_CATEGORIES:
        if cat not in category_to_users:
            category_to_users[cat]  = []
            category_to_topics[cat] = ["AI", "Machine Learning"]

    print(f"✓ {len(category_to_users)} arXiv categories to fetch\n")

    saved = 0
    skipped = 0

    for category, user_ids in category_to_users.items():
        papers = fetch_arxiv(category, max_items=5)

        for paper in papers:
            if not paper["title"]:
                continue

            # Skip if older than 7 days (papers are very time-sensitive)
            if not is_recent(paper["pubDate"], days=7):
                skipped += 1
                continue

            print(f"  Processing: {paper['title'][:60]}...")

            # Generate AI summary
            try:
                prompt     = build_prompt(paper)
                ai_summary = summarize(groq, prompt)
            except Exception as e:
                print(f"    ✗ Groq error: {e}")
                continue

            # Build Firestore document
            doc_id = make_doc_id(paper["link"] or paper["title"])
            doc = {
                "title":         paper["title"],
                "creator":       paper["authors"],
                "link":          paper["link"],
                "Publish_Date":  paper["pubDate"],
                "isoDate":       paper["pubDate"],
                "AI_Summary":    ai_summary,
                "arxivCategory": category,
                "topicTags":     ",".join(category_to_topics.get(category, [])),
                "targetUserIds": ",".join(user_ids),
                "fetchedAt":     now_iso(),
                "sourceName":    "arXiv",
                "categories":    category,
            }

            upsert_document(db, "feed_papers", doc_id, doc)
            print(f"    ✓ Saved to Firestore")
            saved += 1

    print(f"\n{'='*60}")
    print(f"Papers Agent Done — Saved: {saved} | Skipped: {skipped}")
    print(f"{'='*60}")


if __name__ == "__main__":
    run()
