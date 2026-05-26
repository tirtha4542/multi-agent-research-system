# Autonomous Multi-Agent Research & Critique System

An advanced, production-ready **Multi-Agent Research Pipeline** built with LangChain that automates deep information gathering, dynamic web scraping, structured report synthesis, and academic validation. 

This project implements architectural strategies like **Model Splitting** and **Defensive Token Preprocessing** to completely eliminate API Rate Limiting ($429$ Throttling) and token-overflow bottlenecks common in multi-turn LLM agentic loops.

---

## 📊 System Architecture & Data Flow

### 🖼️ Architecture Diagram
 <img width="1408" height="768" alt="Data_flow_diagram" src="https://github.com/user-attachments/assets/e500f699-8db8-400e-b524-0a8ef6647744" />

### Core Optimization Features:
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

├── .env.example     # Template for necessary environment variables
└── .gitignore       # Protection layout preventing secure files from pushing to Git
🚀 Step-by-Step Installation
1. Clone the Repository
Bash
git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git)
cd YOUR_REPOSITORY_NAME
2. Set Up Virtual Environment
Bash
# Create a virtual environment
python -m venv .venv

# Activate it (Windows)
.venv\Scripts\activate

# Activate it (Mac/Linux)
source .venv/bin/activate
3. Install Required Dependencies
Bash
pip install langchain langchain-core langchain-mistralai tavily-python requests beautifulsoup4 rich python-dotenv
4. Setup Environment Variables
Create a .env file in the root directory:

Bash
cp .env.example .env
Open the .env file and input your secure API keys:

Code snippet
MISTRAL_API_KEY=your_actual_mistral_api_key
TAVILY_API_KEY=your_actual_tavily_api_key
💻 Usage
To launch the multi-agent pipeline and observe the structured steps directly in your terminal, run:

Bash
python main.py
🔄 Execution Pipeline Lifecycle
Step 1 (Search Agent): Queries the web via Tavily API using mistral-small-latest to map out recent, reliable context onto the targeted topic.

Step 2 (Scrape Agent): Isolates the best relevant URL and extracts raw semantic content from the viewport via BeautifulSoup4.

Step 3 (Writer Chain): Formats the cleaned, character-limited payload summaries into a professionally structured markdown report using mistral-large-latest.

Step 4 (Critic Chain): Evaluates the resulting output against 8 rigorous academic evaluation indexes to provide objective suggestions for improvements.


---
