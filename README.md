# PULSAR Agents

Python-based content aggregation agents for PULSAR Intelligence platform.
Runs automatically on GitHub Actions (free) — no VPS or server needed.

## What It Does

Fetches personalized content from the internet based on each user's interests,
generates AI summaries using Groq, and saves everything to Firebase Firestore.
The PULSAR frontend then displays this content to users in real time.

## Agents

| Agent | File | Schedule | Firestore Collection |
|---|---|---|---|
| Papers | `agents/papers_agent.py` | Every 6h | `feed_papers` |
| Articles | `agents/articles_agent.py` | Every 6h | `feed_news` |
| Jobs | `agents/jobs_agent.py` | Every 6h | `feed_jobs` |
| Scholarships | `agents/scholarships_agent.py` | Every 6h | `feed_scholarships` |
| Challenges | `agents/challenges_agent.py` | Every 6h | `feed_problems` |
| Datasets | `agents/datasets_agent.py` | Every 12h | `feed_datasets` |

## Project Structure
```
pulsar-agents/
├── .github/
│   └── workflows/
│       ├── papers.yml
│       ├── articles.yml
│       ├── jobs.yml
│       ├── scholarships.yml
│       ├── challenges.yml
│       └── datasets.yml
├── agents/
│   ├── papers_agent.py
│   ├── articles_agent.py
│   ├── jobs_agent.py
│   ├── scholarships_agent.py
│   ├── challenges_agent.py
│   └── datasets_agent.py
├── core/
│   ├── firestore_client.py
│   ├── groq_client.py
│   └── utils.py
├── requirements.txt
└── README.md
```

## Setup

### Step 1 — Add GitHub Secrets
Go to: Repository → Settings → Secrets and variables → Actions → New repository secret

| Secret Name | Value |
|---|---|
| `FIREBASE_SERVICE_ACCOUNT` | Full Firebase service account JSON content |
| `GROQ_API_KEY` | Your Groq API key from console.groq.com |

### Step 2 — Get Firebase Service Account JSON
1. Go to Firebase Console
2. Project Settings → Service Accounts
3. Click "Generate new private key"
4. Copy the entire content of the downloaded JSON file
5. Paste it as the value of `FIREBASE_SERVICE_ACCOUNT` secret

### Step 3 — Run Manually (First Time)
1. Go to Actions tab in your repository
2. Select any workflow (e.g. "PULSAR — Papers Agent")
3. Click "Run workflow"
4. Check logs to confirm it worked

### Step 4 — Automatic Scheduling
Once secrets are added, GitHub Actions will run each agent automatically
on its schedule — no manual action needed.

## Local Testing
```bash
pip install -r requirements.txt

export FIREBASE_SERVICE_ACCOUNT='{ paste full json here }'
export GROQ_API_KEY='your_groq_key_here'

python agents/papers_agent.py
```

## Tech Stack

- **Python 3.11**
- **feedparser** — RSS feed parsing
- **Groq** — AI summaries (llama-3.3-70b-versatile)
- **Google Cloud Firestore** — database
- **GitHub Actions** — free scheduler
- **PRAW** — Reddit API (for Challenges agent)
