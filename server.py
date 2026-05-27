"""
ResearchMind · FastAPI Backend
Run with: uvicorn server:app --reload --port 8000
"""

import asyncio
import json
import time
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# ── Import your pipeline components ──────────────────────────────────────────
from agent import build_agent, build_agent2, writer_chain, critic_chain

app = FastAPI(title="ResearchMind API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten in production
    allow_methods=["*"],
    allow_headers=["*"],
)


class ResearchRequest(BaseModel):
    topic: str


def sse(event: str, data: dict) -> str:
    """Format a Server-Sent Event frame."""
    payload = json.dumps(data)
    return f"event: {event}\ndata: {payload}\n\n"


async def run_pipeline(topic: str) -> AsyncGenerator[str, None]:
    """
    Streams SSE events to the client as each pipeline stage completes.

    Event types:
        status   – { stage: int, message: str }
        result   – { stage: int, key: str, content: str }
        cooldown – { seconds: int, message: str }
        done     – { }
        error    – { message: str }
    """
    state: dict = {}
    loop = asyncio.get_event_loop()

    try:
        # ── Stage 1: Web Search ───────────────────────────────────────────────
        yield sse("status", {"stage": 1, "message": "Agent 1 is querying the web…"})

        def do_search():
            agent = build_agent()
            return agent.invoke({
                "messages": [("user",
                    f"Conduct a web search to gather recent and reliable information on the topic: {topic}. "
                    "Provide the title, URL, and a brief snippet of content for each relevant result."
                )]
            })

        search_result = await loop.run_in_executor(None, do_search)
        state["search_result"] = search_result["messages"][-1].content
        yield sse("result", {"stage": 1, "key": "search", "content": state["search_result"]})

        # cooldown
        yield sse("cooldown", {"seconds": 12, "message": "Clearing request windows…"})
        await asyncio.sleep(12)

        # ── Stage 2: Web Scrape ───────────────────────────────────────────────
        yield sse("status", {"stage": 2, "message": "Agent 2 is scraping the top result…"})

        def do_scrape():
            agent = build_agent2()
            return agent.invoke({
                "messages": [("user",
                    f"Based on the search results about {topic}, identify the most relevant URL and "
                    f"scrape the main textual content. Search results: {state['search_result'][:800]}"
                )]
            })

        scrape_result = await loop.run_in_executor(None, do_scrape)
        state["scrape_result"] = scrape_result["messages"][-1].content
        yield sse("result", {"stage": 2, "key": "scrape", "content": state["scrape_result"]})

        # cooldown
        yield sse("cooldown", {"seconds": 12, "message": "Resetting token volume tracking…"})
        await asyncio.sleep(12)

        # ── Stage 3: Report Generation ────────────────────────────────────────
        yield sse("status", {"stage": 3, "message": "Writer chain is composing the report…"})

        research_combined = (
            f"Search Results Summary:\n{str(state['search_result'])[:1200]}\n\n"
            f"Scraped Web Content Summary:\n{str(state['scrape_result'])[:1500]}"
        )

        def do_write():
            return writer_chain.invoke({"topic": topic, "research": research_combined})

        state["report"] = await loop.run_in_executor(None, do_write)
        yield sse("result", {"stage": 3, "key": "report", "content": state["report"]})

        # cooldown
        yield sse("cooldown", {"seconds": 10, "message": "Brief pause before critique…"})
        await asyncio.sleep(10)

        # ── Stage 4: Critical Review ──────────────────────────────────────────
        yield sse("status", {"stage": 4, "message": "Critic chain is reviewing the report…"})

        def do_critique():
            return critic_chain.invoke({"report": state["report"], "topic": topic})

        state["critique"] = await loop.run_in_executor(None, do_critique)
        yield sse("result", {"stage": 4, "key": "critique", "content": state["critique"]})

        yield sse("done", {})

    except Exception as exc:
        yield sse("error", {"message": str(exc)})


@app.post("/research")
async def research_endpoint(req: ResearchRequest):
    """
    POST /research  { "topic": "..." }
    Returns a text/event-stream of SSE events.
    """
    return StreamingResponse(
        run_pipeline(req.topic),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # disable Nginx buffering
        },
    )


@app.get("/health")
async def health():
    return {"status": "ok"}