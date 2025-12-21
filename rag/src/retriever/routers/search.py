from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from retriever.core.rags import SimpleRag


router = APIRouter()


class SearchRequest(BaseModel):
    rag_name: str
    query: str
    limit: int = 5

available_rags = {
    "exercises": SimpleRag("exercises")
}


@router.post("/")
def search(req: SearchRequest):
    if req.rag_name not in available_rags:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"RAG '{req.rag_name}' not found. Available RAGs: {list(available_rags.keys())}"
        )
    
    rag = available_rags[req.rag_name]
    search_result = rag.request(req.query)
    
    return {"results": search_result}
