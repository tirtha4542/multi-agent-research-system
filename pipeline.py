import time
from agent import build_agent, build_agent2, writer_chain, critic_chain
from rich import print

def run_search_pipeline(topic: str) -> dict:
    state = {}
    
    # Step 1: Build the first agent with web search tool
    print("\n" + " =" * 50)
    print("Step 1: Building the first agent with web search tool")
    print("\n" + " =" * 50)

    search_agent = build_agent()
    search_result = search_agent.invoke({
        "messages": [('user', f"Conduct a web search to gather recent and reliable information on the topic: {topic}. Provide the title, URL, and a brief snippet of content for each relevant result you find.")]
    })
    print("\n" + " =" * 50)
    state['search_result'] = search_result["messages"][-1].content
    print("\n Search Result: \n", state['search_result'])

    print("\n[System Info] Cooling down for 12 seconds to clear request windows...")
    time.sleep(12)

    # Step 2: Build the second agent with web scrape tool
    print("\n" + " =" * 50)
    print("Step 2: Building the second agent with web scrape tool")
    print("\n" + " =" * 50)
    
    scrape_agent = build_agent2()
    scrape_result = scrape_agent.invoke({
        "messages": [('user', f"Based on the search results about {topic}, identify the most relevant URL and scrape the main textual content from that webpage. Here are the search results: {state['search_result'][:800]}")]
    })
    print("\n" + " =" * 50)
    state['scrape_result'] = scrape_result["messages"][-1].content
    print("\n Scrape Result: \n", state['scrape_result'])
    
    print("\n[System Info] Cooling down for 12 seconds to clear token volume tracking...")
    time.sleep(12)

    # Step 3: Generate a structured report using the writer chain
    print("\n" + " =" * 50)
    print("Step 3: Generating a structured report using the writer chain")
    print("\n" + " =" * 50)
    
    # Protect token limit ceilings by parsing slices of your text properties safely
    safe_search = str(state['search_result'])[:1200]
    safe_scrape = str(state['scrape_result'])[:1500]

    research_combined = (
        f"Search Results Summary:\n{safe_search}\n\n"
        f"Scraped Web Content Summary:\n{safe_scrape}"
    )
    
    state['report'] = writer_chain.invoke({
        "topic": topic,
        "research": research_combined
    })
    print("\n" + " =" * 50)
    print("Generated Report: \n", state['report'])
    
    print("\n[System Info] Cooling down for 10 seconds before academic analysis...")
    time.sleep(10)

    # Step 4: Critically evaluate the generated report using the critic chain
    print("\n" + " =" * 50)
    print("Step 4: Critically evaluating the generated report using the critic chain")
    print("\n" + " =" * 50)
    
    state['critique'] = critic_chain.invoke({
        "report": state['report'],
        "topic": topic
    })
    print("\n" + " =" * 50)
    print("Critique of the Report: \n", state['critique'])
    
    return state