"""Literature Management Service — CRUD, search, export for reference library."""

import json
from typing import Any, Optional

from storage.db import (
    count_refs,
    delete_ref,
    get_ref,
    list_refs,
    save_ref,
    search_refs,
    update_ref,
)


class LiteratureService:
    """Business logic for literature/reference management."""

    async def list_literature(
        self,
        query: str = "",
        field: str = "all",
        sort: str = "updated_at",
        order: str = "DESC",
        page: int = 1,
        page_size: int = 20,
        ref_type: Optional[str] = None,
    ) -> dict[str, Any]:
        """List references with search, filter, pagination."""
        offset = (page - 1) * page_size
        items = await search_refs(
            query=query,
            field=field,
            limit=page_size,
            offset=offset,
            sort=sort,
            order=order,
            ref_type=ref_type,
        )
        total = await count_refs(query=query, ref_type=ref_type)
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    async def get_literature(self, ref_id: str) -> Optional[dict]:
        """Get single reference by ID."""
        return await get_ref(ref_id)

    async def create_literature(self, data: dict) -> dict:
        """Create a new reference manually."""
        return await save_ref(data)

    async def update_literature(self, ref_id: str, data: dict) -> Optional[dict]:
        """Update an existing reference."""
        return await update_ref(ref_id, data)

    async def delete_literature(self, ref_id: str) -> bool:
        """Delete a single reference."""
        return await delete_ref(ref_id)

    async def batch_delete_literature(self, ref_ids: list[str]) -> int:
        """Delete multiple references. Returns count of deleted."""
        deleted = 0
        for rid in ref_ids:
            if await delete_ref(rid):
                deleted += 1
        return deleted

    async def export_literature(
        self, ref_ids: Optional[list[str]] = None, format: str = "bibtex"
    ) -> str:
        """Export references in the specified format."""
        if ref_ids:
            items = []
            for rid in ref_ids:
                item = await get_ref(rid)
                if item:
                    items.append(item)
        else:
            items = await list_refs()

        if format == "ris":
            return self._to_ris(items)
        elif format == "bibtex":
            return self._to_bibtex(items)
        else:
            # Plain text formatted list
            lines = []
            for i, ref in enumerate(items, 1):
                authors = ", ".join(ref.get("authors", []))
                lines.append(
                    f"[{i}] {authors} ({ref.get('year', 'n.d.')}). "
                    f"{ref.get('title', 'Untitled')}. "
                    f"{ref.get('journal', '')}. "
                    f"{'doi: ' + ref['doi'] if ref.get('doi') else ''}"
                )
            return "\n\n".join(lines)

    def _to_ris(self, items: list[dict]) -> str:
        """Convert references to RIS format."""
        entries = []
        type_map = {
            "article": "JOUR",
            "book": "BOOK",
            "conference": "CONF",
            "thesis": "THES",
            "report": "RPT",
        }
        for ref in items:
            lines = [f"TY  - {type_map.get(ref.get('ref_type', ''), 'JOUR')}"]
            lines.append(f"TI  - {ref.get('title', '')}")
            for author in ref.get("authors", []):
                lines.append(f"AU  - {author}")
            if ref.get("year"):
                lines.append(f"PY  - {ref['year']}")
            if ref.get("journal"):
                lines.append(f"JO  - {ref['journal']}")
            if ref.get("volume"):
                lines.append(f"VL  - {ref['volume']}")
            if ref.get("number"):
                lines.append(f"IS  - {ref['number']}")
            if ref.get("pages"):
                lines.append(f"SP  - {ref['pages']}")
            if ref.get("doi"):
                lines.append(f"DO  - {ref['doi']}")
            if ref.get("abstract"):
                lines.append(f"AB  - {ref['abstract']}")
            for kw in ref.get("keywords", []):
                lines.append(f"KW  - {kw}")
            if ref.get("url"):
                lines.append(f"UR  - {ref['url']}")
            lines.append("ER  - ")
            entries.append("\n".join(lines))
        return "\n\n".join(entries)

    def _to_bibtex(self, items: list[dict]) -> str:
        """Convert references to BibTeX format."""
        entries = []
        type_map = {
            "article": "article",
            "book": "book",
            "conference": "inproceedings",
            "thesis": "phdthesis",
            "report": "techreport",
        }
        for ref in items:
            bibtype = type_map.get(ref.get("ref_type", ""), "misc")
            key = ref.get("id", "ref")[:16]
            lines = [f"@{bibtype}{{{key},"]
            fields = {
                "title": ref.get("title", ""),
                "year": ref.get("year", ""),
                "journal": ref.get("journal", ""),
                "volume": ref.get("volume", ""),
                "number": ref.get("number", ""),
                "pages": ref.get("pages", ""),
                "doi": ref.get("doi", ""),
                "url": ref.get("url", ""),
                "abstract": ref.get("abstract", ""),
            }
            authors = ref.get("authors", [])
            if authors:
                fields["author"] = " and ".join(authors)

            for k, v in fields.items():
                if v:
                    lines.append(f"  {k} = {{{v}}},")
            lines.append("}")
            entries.append("\n".join(lines))
        return "\n\n".join(entries)


# Global service instance
literature_service = LiteratureService()
