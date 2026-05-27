# Autonomous Multi-Agent Research & Critique System

An advanced, production-ready **Multi-Agent Research Pipeline** built with LangChain that automates deep information gathering, dynamic web scraping, structured report synthesis, and academic validation.

This project implements architectural strategies like **Model Splitting** and **Defensive Token Preprocessing** to completely eliminate API Rate Limiting (429 Throttling) and token-overflow bottlenecks common in multi-turn LLM agentic loops.

---

## 📊 System Architecture & Data Flow

### 🖼️ Architecture Diagram

<img width="1408" height="768" alt="Data_flow_diagram" src="https://github.com/user-attachments/assets/e500f699-8db8-400e-b524-0a8ef6647744" />

### Core Optimization Features

1. **Model Splitting Matrix:** Heavy tool-calling loops (Search & Scrape agents) run efficiently on `mistral-small-latest`. High-reasoning tasks (Report Generation & Academic Critique) are routed to `mistral-large-latest`.
2. **Token Payload Shielding:** Web scraper outputs undergo strict character-slicing filters (`[:1000]` / `[:1200]`) to drop excessive metadata before passing to the writing layout.
3. **Orchestration Cooldown Windows:** Strategic `time.sleep()` offsets are added between agent state handoffs to reset trailing Request-Per-Minute (RPM) bucket limits on the Mistral API gateway.
4. **Fault Tolerance:** Configured with native exponential backoff handlers (`max_retries=5`) to absorb upstream network fluctuations seamlessly.

---

## 🛠️ Project Structure

```text
├── agent.py         # Model initialization, agent configurations, and chain builds
├── pipeline.py      # Main pipeline orchestration state and token flow control
├── tools.py         # Customized tools for Tavily Search and BeautifulSoup4 Scraping
├── main.py          # Execution entry point
├── server.py        # FastAPI backend — streams pipeline events via SSE
├── index.html       # ResearchMind web UI (HTML/CSS/JS)
├── .env.example     # Template for necessary environment variables
└── .gitignore       # Protection layout preventing secure files from pushing to Git
```

---

## 🖥️ Web UI (ResearchMind)

The pipeline now ships with **ResearchMind** — a production-grade browser interface that gives you a real-time view of every pipeline stage without touching the terminal.

### UI Preview

> Enter any topic → watch 4 stages animate live → get a formatted report with one-click Markdown download.

### UI Features

- **Animated star-field background** with a cyan/violet gradient accent system
- **Live stage tracker** — 4 cards animate through `pending → running → done` in real time as each agent completes
- **Progress bar** with shimmer sweep tied to actual pipeline state
- **Cooldown bar** — gold animated fill during `time.sleep()` pauses so the UI never appears frozen
- **Result panels** fade in as each stage finishes: search & scrape in collapsible cards, report in a violet panel, critique in a teal panel
- **One-click Markdown download** of the complete report + critique
- **SSE streaming** — the backend pushes events; the frontend never polls

### Architecture

```
Browser (index.html)
       │
       │  POST /research  { "topic": "..." }
       │  ← text/event-stream (SSE)
       ▼
FastAPI (server.py)
       │
       ├── stage 1 → build_agent()      → search
       ├── stage 2 → build_agent2()     → scrape
       ├── stage 3 → writer_chain       → report
       └── stage 4 → critic_chain       → critique
```

---

## 🚀 Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
cd YOUR_REPOSITORY_NAME
```

### 2. Set Up Virtual Environment

```bash
# Create a virtual environment
python -m venv .venv

# Activate it (Windows)
.venv\Scripts\activate

# Activate it (Mac/Linux)
source .venv/bin/activate
```

### 3. Install Required Dependencies

```bash
pip install langchain langchain-core langchain-mistralai tavily-python \
            requests beautifulsoup4 rich python-dotenv fastapi uvicorn
```

### 4. Setup Environment Variables

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Open `.env` and add your API keys:

```env
MISTRAL_API_KEY=your_actual_mistral_api_key
TAVILY_API_KEY=your_actual_tavily_api_key
```

---

## 💻 Usage

### Option A — Terminal (original)

```bash
python main.py
```

### Option B — Web UI (ResearchMind)

**Important:** Run both commands from inside your project folder.

```bash
cd path/to/multy_agent_system

# Start the FastAPI backend
uvicorn server:app --reload --port 8000
```

Then open `index.html` in your browser (double-click the file, or serve it with any static server).

Enter a topic in the search box and click **Launch Pipeline** — the UI streams every stage live.

---

## 🔄 Execution Pipeline Lifecycle

| Step | Agent | Model | Task |
|------|-------|-------|------|
| 1 | Search Agent | `mistral-small-latest` | Queries Tavily API to map recent, reliable context onto the target topic |
| 2 | Scrape Agent | `mistral-small-latest` | Isolates the best URL and extracts raw semantic content via BeautifulSoup4 |
| 3 | Writer Chain | `mistral-large-latest` | Formats cleaned payload summaries into a structured Markdown report |
| 4 | Critic Chain | `mistral-large-latest` | Evaluates output against 8 academic indexes and provides improvement suggestions |

---

## 🔑 Environment Variables Reference

| Variable | Description |
|----------|-------------|
| `MISTRAL_API_KEY` | Your Mistral AI API key |
| `TAVILY_API_KEY` | Your Tavily search API key |

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `langchain` / `langchain-core` | Agent orchestration framework |
| `langchain-mistralai` | Mistral model integration |
| `tavily-python` | Web search tool |
| `beautifulsoup4` | Web scraping |
| `rich` | Terminal output formatting |
| `python-dotenv` | Environment variable management |
| `fastapi` | Backend API server (UI mode) |
| `uvicorn` | ASGI server for FastAPI (UI mode) |

---

## 🛡️ Rate Limit Strategy

```
Search Agent  ──┐
                ├── 12s cooldown ──► Scrape Agent
                                          │
                                     12s cooldown
                                          │
                                     Writer Chain
                                          │
                                     10s cooldown
                                          │
                                     Critic Chain
```

Strategic sleep windows between stages reset the Mistral API's RPM bucket, preventing 429 errors without requiring manual retries.

---

## 📄 License

This project is open-source. See `LICENSE` for details.
