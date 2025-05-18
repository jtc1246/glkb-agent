from pymed import PubMed
from mcp.server.fastmcp import FastMCP
import warnings

warnings.filterwarnings("ignore")

pubmed = PubMed(tool="MyTool", email="kvchang@umich.edu")
mcp = FastMCP("pubmed")

@mcp.tool()
async def search_pubmed(query: str) -> str:
    """Search PubMed and return metadata and abstracts for relevant publications."""
    results = {}

    try:
        articles = pubmed.query(query, max_results=4)
        for article in articles:
            article_data = {
                "title": article.title,
                "abstract": article.abstract,
            }
            results[article.pubmed_id] = article_data

    except Exception as e:
        results["error"] = f"PubMed query failed: {e}"

    return str(results)

if __name__ == "__main__":
    mcp.run(transport='stdio')
