import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
from langchain.tools import tool

load_dotenv()

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query: str) -> str:
    """Search the web for recent and reliable information on a topic. 
    Returns the title, URL, and textual snippet content of the top matches.
    """
    search_result = tavily_client.search(query=query, max_results=5)
    results_list = search_result.get("results", [])
    
    if not results_list:
        return "No relevant search results found."
        
    formatted_results = []
    for item in results_list:
        title = item.get("title", "No Title")
        url = item.get("url", "No URL")
        content = item.get("content", "No Content Snippet Available")
        
        formatted_results.append(f"Title: {title}\nURL: {url}\nContent: {content}\n---")
        
    return "\n".join(formatted_results)

@tool
def web_scrape(url: str) -> str:
    """Scrape the content of a webpage given its URL. 
    Returns the main textual content of the page.
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, timeout=8, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for tag in soup(['script', 'style', 'nav', 'footer']):
            tag.decompose()
        
        return soup.get_text(separator=' ', strip=True)[:3000]
      
    except requests.RequestException as e:
        return f"Error fetching the webpage: {e}"