from mcp.server.fastmcp import FastMCP 
import wikipedia 
import warnings
from bs4 import GuessedAtParserWarning

warnings.filterwarnings("ignore", category=GuessedAtParserWarning)

mcp = FastMCP("wikipedia") 

@mcp.tool() 
async def search_wikipedia(query: str) -> str: 
    """ Search Wikipedia and return a summary. Args: query: The search term. """   
    terms = query.split()
    results = {}

    # Attempt full query first
    try:
        search_results = wikipedia.search(query)
        if search_results:
            try:
                page = wikipedia.page(search_results[0])
                results[query] = page.content
            except Exception as e:
                results[query] = f"Error retrieving page: {e}"
        else:
            results[query] = "No search results found."
    except Exception as e:
        results[query] = f"Search error: {e}"

    # Then process each individual word in the query
    for term in terms:
        try:
            search_results = wikipedia.search(term)
            if search_results:
                try:
                    page = wikipedia.page(search_results[0])
                    results[term] = page.content
                except Exception as e:
                    results[term] = f"Error retrieving page: {e}"
            else:
                results[term] = "No search results found."
        except Exception as e:
            results[term] = f"Search error: {e}"

    return(str(results))
        

if __name__ == "__main__": 
    mcp.run(transport='stdio')
