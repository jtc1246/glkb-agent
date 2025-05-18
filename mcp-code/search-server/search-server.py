from mcp.server.fastmcp import FastMCP
from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup
import warnings
from bs4 import GuessedAtParserWarning

warnings.filterwarnings("ignore", category=GuessedAtParserWarning)

mcp = FastMCP("websearch")

@mcp.tool()
async def search_web(query: str) -> str:
    """
    Search the web and return the content of the top 4 pages.
    Args:
        query: The search term.
    Returns:
        A stringified dictionary with URLs and content.
    """
    results = {}
    with DDGS() as ddgs:
        search_results = ddgs.text(query, max_results=4)
        for i, result in enumerate(search_results):
            url = result.get("href") or result.get("url")
            if not url:
                continue
            try:
                response = requests.get(url, timeout=5)
                soup = BeautifulSoup(response.text, "html.parser")
                text = soup.get_text(separator="\n", strip=True)
                results[f"{i+1}: {url}"] = text[:2000]
            except Exception as e:
                results[f"{i+1}: {url}"] = f"Error: {e}"

    return str(results)

if __name__ == "__main__":
    mcp.run(transport='stdio')
