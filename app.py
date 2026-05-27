import streamlit as st
import time
import sys
import io
from contextlib import redirect_stdout

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResearchMind · AI Pipeline",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:ital,wght@0,300;0,400;1,300&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #080b12 !important;
    color: #e8eaf0;
    font-family: 'Syne', sans-serif;
}

[data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse 80% 50% at 50% -10%, #0d2340 0%, #080b12 60%) !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
.block-container { padding: 2rem 3rem 4rem !important; max-width: 1100px; margin: 0 auto; }

/* ── Hero Header ── */
.hero {
    text-align: center;
    padding: 3.5rem 0 2.5rem;
    position: relative;
}
.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.25em;
    color: #4a9eff;
    text-transform: uppercase;
    margin-bottom: 1rem;
}
.hero-title {
    font-size: clamp(2.6rem, 5vw, 4rem);
    font-weight: 800;
    line-height: 1.05;
    background: linear-gradient(135deg, #ffffff 30%, #4a9eff 70%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 1rem;
}
.hero-subtitle {
    font-size: 1rem;
    color: #8892a4;
    font-weight: 400;
    max-width: 520px;
    margin: 0 auto;
    line-height: 1.6;
}

/* ── Input card ── */
.input-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(74,158,255,0.15);
    border-radius: 16px;
    padding: 2rem 2.2rem;
    margin: 2rem 0;
    backdrop-filter: blur(10px);
}

/* ── Streamlit input overrides ── */
[data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.04) !important;
    border: 1.5px solid rgba(74,158,255,0.25) !important;
    border-radius: 10px !important;
    color: #e8eaf0 !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.75rem 1rem !important;
    transition: border-color 0.2s;
}
[data-testid="stTextInput"] input:focus {
    border-color: #4a9eff !important;
    box-shadow: 0 0 0 3px rgba(74,158,255,0.12) !important;
}
[data-testid="stTextInput"] label {
    color: #8892a4 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}

/* ── Button ── */
.stButton > button {
    background: linear-gradient(135deg, #1a6fff 0%, #7c3aed 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.75rem 2.2rem !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.03em !important;
    cursor: pointer !important;
    transition: transform 0.15s, box-shadow 0.15s !important;
    box-shadow: 0 4px 20px rgba(74,158,255,0.25) !important;
    width: 100% !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(74,158,255,0.4) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── Pipeline steps ── */
.pipeline-header {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    color: #4a9eff;
    text-transform: uppercase;
    margin: 2.5rem 0 1rem;
}

.step-card {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    border-left: 3px solid #1a6fff;
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    position: relative;
    transition: border-color 0.3s;
}
.step-card.active  { border-left-color: #4a9eff; background: rgba(74,158,255,0.06); }
.step-card.done    { border-left-color: #22d3a0; }
.step-card.pending { opacity: 0.45; }

.step-number {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: #4a9eff;
    letter-spacing: 0.1em;
    margin-bottom: 0.3rem;
}
.step-title {
    font-size: 1rem;
    font-weight: 700;
    color: #e8eaf0;
    margin-bottom: 0.2rem;
}
.step-desc {
    font-size: 0.82rem;
    color: #6b7585;
    font-family: 'DM Mono', monospace;
}
.step-badge {
    position: absolute;
    top: 1.2rem; right: 1.4rem;
    font-size: 0.68rem;
    font-family: 'DM Mono', monospace;
    padding: 0.2rem 0.6rem;
    border-radius: 20px;
    letter-spacing: 0.05em;
}
.badge-active  { background: rgba(74,158,255,0.15); color: #4a9eff; }
.badge-done    { background: rgba(34,211,160,0.12); color: #22d3a0; }
.badge-pending { background: rgba(255,255,255,0.05); color: #4a5568; }
.badge-wait    { background: rgba(251,191,36,0.12); color: #fbbf24; }

/* ── Result panels ── */
.result-panel {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1.6rem 1.8rem;
    margin-top: 1.2rem;
}
.result-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #4a9eff;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.result-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(74,158,255,0.2);
}
.result-content {
    font-family: 'DM Mono', monospace;
    font-size: 0.83rem;
    line-height: 1.75;
    color: #b0bac8;
    white-space: pre-wrap;
    word-break: break-word;
}

/* ── Report & Critique panels ── */
.report-panel {
    background: rgba(124,58,237,0.06);
    border: 1px solid rgba(124,58,237,0.2);
    border-radius: 14px;
    padding: 1.8rem 2rem;
    margin-top: 1.2rem;
}
.critique-panel {
    background: rgba(34,211,160,0.04);
    border: 1px solid rgba(34,211,160,0.2);
    border-radius: 14px;
    padding: 1.8rem 2rem;
    margin-top: 1.2rem;
}
.panel-title {
    font-size: 1.05rem;
    font-weight: 700;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.panel-body {
    font-size: 0.88rem;
    line-height: 1.8;
    color: #c4cdd8;
    white-space: pre-wrap;
    word-break: break-word;
}

/* ── Progress bar ── */
[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #1a6fff, #7c3aed) !important;
    border-radius: 4px !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] { color: #4a9eff !important; }

/* ── Divider ── */
hr { border-color: rgba(255,255,255,0.06) !important; margin: 2rem 0 !important; }

/* ── Expandable ── */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 10px !important;
}
[data-testid="stExpander"] summary {
    color: #8892a4 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.82rem !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(74,158,255,0.2); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">Multi-Agent · Research System</div>
    <h1 class="hero-title">ResearchMind</h1>
    <p class="hero-subtitle">
        A 4-stage autonomous pipeline — search, scrape, write, and critique —
        powered by coordinated AI agents.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Pipeline overview ──────────────────────────────────────────────────────────
STEPS = [
    ("01", "Web Search", "Agent 1 queries the web for recent, reliable sources", "🔍"),
    ("02", "Content Scrape", "Agent 2 extracts full content from the best URL", "🕸️"),
    ("03", "Report Generation", "Writer chain synthesises a structured report", "✍️"),
    ("04", "Critical Review", "Critic chain evaluates accuracy, depth & balance", "🧠"),
]

def render_steps(active: int = -1, done_up_to: int = -1, waiting: int = -1):
    st.markdown('<div class="pipeline-header">Pipeline stages</div>', unsafe_allow_html=True)
    for i, (num, title, desc, icon) in enumerate(STEPS):
        if i < done_up_to:
            cls, badge_cls, badge_txt = "done", "badge-done", "✓ done"
        elif i == active:
            cls, badge_cls, badge_txt = "active", "badge-active", "● running"
        elif i == waiting:
            cls, badge_cls, badge_txt = "active", "badge-wait", "⏳ cooling down"
        else:
            cls, badge_cls, badge_txt = "pending", "badge-pending", "pending"

        st.markdown(f"""
        <div class="step-card {cls}">
            <span class="step-badge {badge_cls}">{badge_txt}</span>
            <div class="step-number">STEP {num}</div>
            <div class="step-title">{icon}&nbsp; {title}</div>
            <div class="step-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)


# ── Input ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="input-card">', unsafe_allow_html=True)
topic = st.text_input(
    "Research topic",
    placeholder="e.g. Quantum computing breakthroughs in 2025",
    help="Enter any topic — the pipeline will search, scrape, write, and critique a report.",
)
run_btn = st.button("🚀  Launch Research Pipeline", disabled=not topic.strip())
st.markdown('</div>', unsafe_allow_html=True)

# ── Run pipeline ───────────────────────────────────────────────────────────────
if run_btn and topic.strip():
    try:
        from pipeline import run_search_pipeline
    except ImportError:
        st.error("⚠️  Could not import `pipeline.py`. Make sure it's in the same directory as `app.py`.")
        st.stop()

    st.markdown("---")

    # Placeholders
    steps_ph  = st.empty()
    prog_ph   = st.empty()
    status_ph = st.empty()
    results   = {}

    def update_ui(active=-1, done=-1, waiting=-1, status="", progress=0):
        with steps_ph.container():
            render_steps(active=active, done_up_to=done, waiting=waiting)
        prog_ph.progress(progress)
        if status:
            status_ph.markdown(
                f'<div style="font-family:\'DM Mono\',monospace;font-size:0.78rem;'
                f'color:#6b7585;text-align:center;padding:0.3rem 0;">{status}</div>',
                unsafe_allow_html=True
            )

    # ── Patch pipeline to stream state back ───────────────────────────────────
    # We monkey-patch time.sleep so the UI can show cooldown messages
    original_sleep = time.sleep
    sleep_messages = [
        "Cooling down · clearing request windows…",
        "Cooling down · resetting token volume tracking…",
        "Brief pause before academic critique…",
    ]
    sleep_counter = {"n": 0, "active": -1, "done": -1}

    def patched_sleep(secs):
        msg = sleep_messages[min(sleep_counter["n"], len(sleep_messages)-1)]
        update_ui(
            active=sleep_counter["active"],
            done=sleep_counter["done"],
            waiting=sleep_counter["active"],
            status=f"⏳ {msg} ({int(secs)}s)",
            progress=max(0, sleep_counter["done"] / 4),
        )
        sleep_counter["n"] += 1
        original_sleep(secs)

    time.sleep = patched_sleep

    try:
        # Step 1
        update_ui(active=0, done=-1, status="🔍 Agent 1 is searching the web…", progress=0.05)
        sleep_counter.update({"active": 0, "done": -1})

        # Capture stdout (rich prints) silently
        buf = io.StringIO()
        with redirect_stdout(buf):
            from agent import build_agent
            search_agent = build_agent()
            search_result = search_agent.invoke({
                "messages": [('user',
                    f"Conduct a web search to gather recent and reliable information on the topic: {topic}. "
                    "Provide the title, URL, and a brief snippet of content for each relevant result you find."
                )]
            })
        results['search_result'] = search_result["messages"][-1].content

        # Cooldown 1
        sleep_counter.update({"active": 0, "done": 0})
        update_ui(active=0, done=1, status="⏳ Cooling down…", progress=0.25)
        original_sleep(12)

        # Step 2
        update_ui(active=1, done=1, status="🕸️ Agent 2 is scraping the top result…", progress=0.3)
        sleep_counter.update({"active": 1, "done": 1})

        buf = io.StringIO()
        with redirect_stdout(buf):
            from agent import build_agent2
            scrape_agent = build_agent2()
            scrape_result = scrape_agent.invoke({
                "messages": [('user',
                    f"Based on the search results about {topic}, identify the most relevant URL and "
                    f"scrape the main textual content from that webpage. Here are the search results: "
                    f"{results['search_result'][:800]}"
                )]
            })
        results['scrape_result'] = scrape_result["messages"][-1].content

        # Cooldown 2
        sleep_counter.update({"active": 1, "done": 2})
        update_ui(active=1, done=2, status="⏳ Cooling down…", progress=0.5)
        original_sleep(12)

        # Step 3
        update_ui(active=2, done=2, status="✍️ Writer chain is composing the report…", progress=0.55)
        sleep_counter.update({"active": 2, "done": 2})

        safe_search = str(results['search_result'])[:1200]
        safe_scrape = str(results['scrape_result'])[:1500]
        research_combined = (
            f"Search Results Summary:\n{safe_search}\n\n"
            f"Scraped Web Content Summary:\n{safe_scrape}"
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            from agent import writer_chain
            results['report'] = writer_chain.invoke({"topic": topic, "research": research_combined})

        # Cooldown 3
        sleep_counter.update({"active": 2, "done": 3})
        update_ui(active=2, done=3, status="⏳ Brief pause before critique…", progress=0.75)
        original_sleep(10)

        # Step 4
        update_ui(active=3, done=3, status="🧠 Critic chain is reviewing the report…", progress=0.8)
        sleep_counter.update({"active": 3, "done": 3})

        buf = io.StringIO()
        with redirect_stdout(buf):
            from agent import critic_chain
            results['critique'] = critic_chain.invoke({"report": results['report'], "topic": topic})

        update_ui(active=-1, done=4, status="", progress=1.0)
        status_ph.empty()

    finally:
        time.sleep = original_sleep

    # ── Render results ────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("""
    <div style="font-family:'DM Mono',monospace;font-size:0.68rem;letter-spacing:0.2em;
    text-transform:uppercase;color:#22d3a0;margin-bottom:1.5rem;">
    ✓ Pipeline complete · All 4 stages finished
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        with st.expander("🔍 Search Results", expanded=False):
            st.markdown(f"""
            <div class="result-panel">
                <div class="result-label">Raw agent output</div>
                <div class="result-content">{results.get('search_result','—')}</div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        with st.expander("🕸️ Scraped Content", expanded=False):
            st.markdown(f"""
            <div class="result-panel">
                <div class="result-label">Raw agent output</div>
                <div class="result-content">{results.get('scrape_result','—')}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="report-panel">
        <div class="panel-title" style="color:#a78bfa;">✍️ &nbsp;Generated Report</div>
        <div class="panel-body">{results.get('report','—')}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="critique-panel">
        <div class="panel-title" style="color:#22d3a0;">🧠 &nbsp;Critical Review</div>
        <div class="panel-body">{results.get('critique','—')}</div>
    </div>
    """, unsafe_allow_html=True)

    # Download
    st.markdown("<br>", unsafe_allow_html=True)
    report_md = f"# Research Report: {topic}\n\n## Report\n{results.get('report','')}\n\n## Critique\n{results.get('critique','')}"
    st.download_button(
        label="⬇️  Download Report as Markdown",
        data=report_md,
        file_name=f"research_{topic[:30].replace(' ','_')}.md",
        mime="text/markdown",
    )

else:
    # Idle state — show greyed pipeline
    render_steps()
    st.markdown("""
    <div style="text-align:center;margin-top:2rem;font-family:'DM Mono',monospace;
    font-size:0.78rem;color:#3a4455;letter-spacing:0.08em;">
    Enter a topic above and hit Launch to begin the pipeline.
    </div>
    """, unsafe_allow_html=True)