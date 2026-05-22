"""文献管理 API 路由 — 导入、查询、删除参考文献。"""

import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from references import parse_file
from storage.db import delete_all_refs, delete_ref, list_refs, save_ref

router = APIRouter()


@router.get("/")
async def get_references():
    refs = await list_refs()
    return {"references": refs}


@router.post("/import")
async def import_references(file: UploadFile = File(...)):
    ext = Path(file.filename or "unknown.ris").suffix.lower()
    if ext not in (".ris", ".bib"):
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式: {ext}（仅支持 .ris 和 .bib）",
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
        raise HTTPException(status_code=500, detail=f"解析失败: {e}")
    finally:
        Path(tmp.name).unlink(missing_ok=True)

    if not refs:
        raise HTTPException(status_code=400, detail="未解析到任何文献记录")

    saved = []
    for ref in refs:
        ref["raw_data"] = content.decode("utf-8", errors="replace")
        saved_ref = await save_ref(ref)
        saved.append(saved_ref)

    return {"imported": len(saved), "references": saved}


@router.delete("/{ref_id}")
async def delete_reference(ref_id: str):
    ok = await delete_ref(ref_id)
    if not ok:
        raise HTTPException(status_code=404, detail="文献不存在")
    return {"deleted": True}


@router.delete("/")
async def clear_references():
    count = await delete_all_refs()
    return {"deleted": count}
