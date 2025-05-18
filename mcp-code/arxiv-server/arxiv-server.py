from mcp.server.fastmcp import FastMCP 
import arxiv 
import warnings
from bs4 import GuessedAtParserWarning

warnings.filterwarnings("ignore", category=GuessedAtParserWarning)

client = arxiv.Client()
mcp = FastMCP("arxiv") 

@mcp.tool() 
async def search_arxiv(query: str) -> str: 
    """ Search arxiv and return a summary. Args: query: The search term. """   
    results_final = {}

    try:
        search = arxiv.Search(
            query = query,
            max_results = 4,
            sort_by = arxiv.SortCriterion.SubmittedDate
        )
        results = client.results(search)
        for r in client.results(search):
            entry = {
                "title": r.title,
                "summary": r.summary
            }
            results_final[r.title] = entry
    except Exception as e:
        results_final["error"] = f"Arxiv query failed: {e}"

    return str(results_final)
        

if __name__ == "__main__": 
    mcp.run(transport='stdio')
