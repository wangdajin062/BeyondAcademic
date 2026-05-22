"""Paper Writing Platform API Router
Provides endpoints for the integrated paper writing experience.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services import paper_writing_service

router = APIRouter()


class SectionUpdate(BaseModel):
    content: str = ""
    status: str = "pending"


class GenerateRequest(BaseModel):
    upstream_ids: list[str] = []


@router.get("/{article_id}/sections/{node_id}")
async def api_get_section(article_id: str, node_id: str):
    """Get saved content for a specific section/node."""
    section = await paper_writing_service.get_section(article_id, node_id)
    return section


@router.put("/{article_id}/sections/{node_id}")
async def api_update_section(
    article_id: str, node_id: str, payload: SectionUpdate
):
    """Save or update section content."""
    ok = await paper_writing_service.update_section(
        article_id, node_id, payload.content, payload.status
    )
    if not ok:
        raise HTTPException(404, "Article not found")
    return {"ok": True}


@router.post("/{article_id}/generate/{node_id}")
async def api_generate_section(
    article_id: str, node_id: str, payload: GenerateRequest
):
    """Run AI generation for a single workflow step.
    Returns generated text without auto-saving; client must explicitly accept.
    """
    output = await paper_writing_service.generate_section(
        article_id, node_id, payload.upstream_ids
    )
    if output is None:
        raise HTTPException(404, "Article or workflow node not found")
    return {"output": output}


@router.get("/{article_id}/compile")
async def api_compile_paper(article_id: str):
    """Concatenate all completed sections in topological order.
    Also updates articles.content for consistency.
    """
    result = await paper_writing_service.compile_paper(article_id)
    if result is None:
        raise HTTPException(404, "Article not found")
    return result


@router.get("/{article_id}/status")
async def api_get_paper_status(article_id: str):
    """Return completion status for each workflow section."""
    status = await paper_writing_service.get_paper_status(article_id)
    if status is None:
        raise HTTPException(404, "Article not found")
    return {"sections": status}
