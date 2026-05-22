"""Literature Management API Router — enhanced CRUD, search, import/export."""

import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, Query

from references import parse_file
from services.literature_service import literature_service

router = APIRouter()


@router.get("/")
async def list_literature(
    query: str = Query("", description="Search query"),
    field: str = Query("all", description="Search field: all, title, author, doi"),
    sort: str = Query("updated_at", description="Sort field"),
    order: str = Query("DESC", description="Sort order: ASC or DESC"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    ref_type: str | None = Query(None, description="Filter by reference type"),
):
    """List references with search, filtering, and pagination."""
    return await literature_service.list_literature(
        query=query,
        field=field,
        sort=sort,
        order=order,
        page=page,
        page_size=page_size,
        ref_type=ref_type,
    )


@router.post("/")
async def create_literature(data: dict):
    """Create a new reference manually."""
    if not data.get("title"):
        raise HTTPException(status_code=400, detail="Title is required")
    ref = await literature_service.create_literature(data)
    return ref


@router.get("/{ref_id}")
async def get_literature(ref_id: str):
    """Get a single reference by ID."""
    ref = await literature_service.get_literature(ref_id)
    if not ref:
        raise HTTPException(status_code=404, detail="Reference not found")
    return ref


@router.put("/{ref_id}")
async def update_literature(ref_id: str, data: dict):
    """Update an existing reference."""
    ref = await literature_service.update_literature(ref_id, data)
    if not ref:
        raise HTTPException(status_code=404, detail="Reference not found")
    return ref


@router.delete("/{ref_id}")
async def delete_literature(ref_id: str):
    """Delete a reference."""
    ok = await literature_service.delete_literature(ref_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Reference not found")
    return {"deleted": True}


@router.post("/batch-delete")
async def batch_delete_literature(body: dict):
    """Delete multiple references."""
    ref_ids = body.get("ref_ids", [])
    if not ref_ids:
        raise HTTPException(status_code=400, detail="No reference IDs provided")
    deleted = await literature_service.batch_delete_literature(ref_ids)
    return {"deleted": deleted}


@router.post("/export")
async def export_literature(body: dict):
    """Export references in specified format (bibtex, ris, text)."""
    ref_ids = body.get("ref_ids")
    fmt = body.get("format", "bibtex")
    content = await literature_service.export_literature(ref_ids=ref_ids, format=fmt)
    media_type_map = {
        "bibtex": "application/x-bibtex",
        "ris": "application/x-research-info-systems",
        "text": "text/plain",
    }
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(
        content=content,
        media_type=media_type_map.get(fmt, "text/plain"),
        headers={"Content-Disposition": f'attachment; filename="references.{fmt}"'},
    )


@router.post("/import")
async def import_literature(file: UploadFile = File(...)):
    """Import references from RIS or BibTeX file."""
    ext = Path(file.filename or "unknown.ris").suffix.lower()
    if ext not in (".ris", ".bib"):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {ext} (only .ris and .bib)",
        )

    tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
    try:
        content = await file.read()
        tmp.write(content)
        tmp.close()
        refs = parse_file(tmp.name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parse failed: {e}")
    finally:
        Path(tmp.name).unlink(missing_ok=True)

    if not refs:
        raise HTTPException(status_code=400, detail="No references found in file")

    saved = []
    for ref in refs:
        ref["raw_data"] = content.decode("utf-8", errors="replace")
        saved_ref = await literature_service.create_literature(ref)
        saved.append(saved_ref)

    return {"imported": len(saved), "references": saved}
