# PULSAR Agents

Python-based content aggregation agents for PULSAR Intelligence.
Runs on GitHub Actions (free) — no VPS needed.

## Setup

### 1. GitHub Secrets add karo
Repository → Settings → Secrets → Actions → New secret

| Secret Name | Value |
|---|---|
| `FIREBASE_SERVICE_ACCOUNT` | Firebase service account JSON (poora) |
| `GROQ_API_KEY` | Groq API key |

### 2. Firebase Service Account kaise milega
1. Firebase Console → Project Settings → Service Accounts
2. "Generate new private key" click karo
3. Downloaded JSON file ka poora content copy karo
4. GitHub Secret mein paste karo

### 3. Agents

| Agent | File | Schedule | Firestore Collection |
|---|---|---|---|
| Papers | `agents/papers_agent.py` | Every 6h | `feed_papers` |
| Articles | `agents/articles_agent.py` | Every 6h | `feed_news` |
| Jobs | `agents/jobs_agent.py` | Every 6h | `feed_jobs` |
| Scholarships | `agents/scholarships_agent.py` | Every 6h | `feed_scholarships` |
| Challenges | `agents/challenges_agent.py` | Every 6h | `feed_problems` |
| Datasets | `agents/datasets_agent.py` | Every 12h | `feed_datasets` |

### 4. Local test karo
```bash
pip install -r requirements.txt
export FIREBASE_SERVICE_ACCOUNT='{ paste json here }'
export GROQ_API_KEY='your_groq_key'
python agents/papers_agent.py
```

### 5. Manual trigger
GitHub → Actions tab → Select workflow → "Run workflow"
