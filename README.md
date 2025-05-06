# NLP Alpha Engine – News & Social‑Media Sentiment Signals for Equities

A college‑level project that transforms live news articles and Reddit finance chatter
into daily **ticker‑level sentiment factors** you can back‑test against stock returns.

### Why it matters
* **Speed** – ingest >10 000 headlines & posts / day in near‑real‑time  
* **Finance‑tuned NLP** – uses [FinBERT] for domain‑specific sentiment rather than generic models  
* **Plug‑and‑play** – zero‑MQ or REST endpoints let you drop the factor into any quant pipeline  
* **Open source** – no black boxes; every step is reproducible in a single Docker file  

### Core Features
| Module | What it does |
| ------ | ------------ |
| `scrapers/` | Pulls articles from *NewsAPI.org* and Reddit posts via PRAW |
| `models/`   | Wraps FinBERT for fast batch inference on GPUs/CPUs |
| `pipeline.py` | Cleans text, tags tickers (simple regex), scores sentiment |
| `backtest.py` | Merges factors with **yfinance** prices and evaluates IC, Sharpe |
| `app/`       | Streamlit dashboard – leaderboards, time‑series plots, EDA |
| `docker/`    | Docker + docker‑compose for one‑command deployment |

### Quick Start

```bash
# 1. clone repo & install
git clone https://github.com/MalcolmJAPark/nlp-alpha-engine.git
cd nlp-alpha-engine
pip install -r requirements.txt

# 2. add your API keys
cp .env.example .env   # fill NEWS_API_KEY, REDDIT_ID, REDDIT_SECRET …

# 3. run the daily ETL + scoring job
python pipeline.py --date today

# 4. view the dashboard
streamlit run app/dashboard.py
