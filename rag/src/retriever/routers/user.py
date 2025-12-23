from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from retriever.core.rags import SimpleRag, HydeRag, CoolRag, CoolRagTagOnly
from retriever.generator.collection_handler import CollectionHandler, CollectionEntry


router = APIRouter(prefix="/user", tags=["user"])


class UserRequest(BaseModel):
    rag_name: str
    query: str
    limit: int = 5
    tags: list[str]

available_rags = {
    "tag_only": CoolRagTagOnly("users")
}


@router.post("/")
def search(req: UserRequest):
    if req.rag_name not in available_rags:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"RAG '{req.rag_name}' not found. Available RAGs: {list(available_rags.keys())}"
        )
    
    rag = available_rags[req.rag_name]

    search_result = rag.request(req.query, tags=req.tags)
    
    return {"results": search_result}

ch = CollectionHandler("users")
class RememberRequest(BaseModel):
    user: str
    info: str
@router.post("/save")
def remember(req: RememberRequest):
    entry = CollectionEntry(
        text=req.info,
        payload={
            "text": req.info,
            "tags": [req.user]
        }
    )
     
    ch.write_data([entry])

    return {"status": "ok"}

