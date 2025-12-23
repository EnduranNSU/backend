from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from retriever.core.rags import SimpleRag, HydeRag, CoolRag, TagFirstRag

router = APIRouter(prefix="/exercise", tags=["exercise"])




available_rags = {
    "exercises": SimpleRag("exercises"),
    "ex_hyde": HydeRag("exercises"),
    "ex_cool": CoolRag("exercises"),
    "tag_first": TagFirstRag("exercises")
}

class SearchRequest(BaseModel):
    rag_name: str
    query: str
    limit: int = 5
    tags: Optional[list[str]] = []
@router.post("/")
def search(req: SearchRequest):
    if req.rag_name not in available_rags:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"RAG '{req.rag_name}' not found. Available RAGs: {list(available_rags.keys())}"
        )

    rag = available_rags[req.rag_name]
    search_result = rag.request(req.query, tags=req.tags)
    
    return {"results": search_result}



