from typing import List
from langchain_tavily import TavilySearch

from backend.src.core.settings import settings


def _tavily_search(query: str, max_results: int = 5) -> List[dict]:
    
    tool = TavilySearch(
        max_results=max_results,
        tavily_api_key=settings.TAVILY_API_KEY
    )
    results = tool.invoke({"query": query})

    normalized: List[dict] = []
    for r in results.get("results") or []:
            normalized.append(
                {
                    "title": r.get("title") or "",
                    "url": r.get("url") or "",
                    "snippet": r.get("content") or r.get("snippet") or ""
                }
            )
    return normalized