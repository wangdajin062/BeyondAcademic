import json
import uuid
from pathlib import Path
from datetime import datetime

import aiosqlite

DB_PATH = Path(__file__).parent.parent / "beyond_academic.db"


async def get_db() -> aiosqlite.Connection:
    db = await aiosqlite.connect(str(DB_PATH))
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    return db


async def init_db():
    db = await get_db()
    try:
        # Migration: add columns to refs for existing databases
        try:
            await db.executescript("""
                ALTER TABLE refs ADD COLUMN notes TEXT DEFAULT '';
                ALTER TABLE refs ADD COLUMN updated_at TEXT NOT NULL DEFAULT (datetime('now'));
            """)
        except Exception:
            pass  # Columns already exist

        await db.executescript("""
            CREATE TABLE IF NOT EXISTS workflows (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                nodes TEXT NOT NULL DEFAULT '[]',
                edges TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS model_configs (
                id TEXT PRIMARY KEY,
                provider TEXT NOT NULL,
                api_key TEXT NOT NULL DEFAULT '',
                model_name TEXT NOT NULL DEFAULT '',
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS chat_history (
                id TEXT PRIMARY KEY,
                workflow_id TEXT NOT NULL,
                node_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS execution_logs (
                id TEXT PRIMARY KEY,
                workflow_id TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                started_at TEXT,
                finished_at TEXT,
                output TEXT DEFAULT '{}',
                FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS refs (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL DEFAULT '',
                authors TEXT NOT NULL DEFAULT '[]',
                year TEXT DEFAULT '',
                journal TEXT DEFAULT '',
                volume TEXT DEFAULT '',
                number TEXT DEFAULT '',
                pages TEXT DEFAULT '',
                doi TEXT DEFAULT '',
                abstract TEXT DEFAULT '',
                keywords TEXT NOT NULL DEFAULT '[]',
                url TEXT DEFAULT '',
                ref_type TEXT DEFAULT 'article',
                notes TEXT DEFAULT '',
                raw_data TEXT DEFAULT '',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS article_sections (
                id TEXT PRIMARY KEY,
                article_id TEXT NOT NULL,
                node_id TEXT NOT NULL,
                content TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'pending',
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                UNIQUE(article_id, node_id)
            );

            CREATE TABLE IF NOT EXISTS articles (
                article_id TEXT PRIMARY KEY,
                title TEXT NOT NULL DEFAULT '',
                abstract TEXT DEFAULT '',
                content TEXT DEFAULT '',
                status TEXT DEFAULT 'DRAFT',
                template TEXT DEFAULT 'GENERIC',
                authors TEXT NOT NULL DEFAULT '[]',
                keywords TEXT NOT NULL DEFAULT '[]',
                references_list TEXT NOT NULL DEFAULT '[]',
                current_version INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                submitted_at TEXT,
                published_at TEXT
            );

            CREATE TABLE IF NOT EXISTS article_versions (
                version_id TEXT PRIMARY KEY,
                article_id TEXT NOT NULL,
                version_number INTEGER NOT NULL,
                content TEXT DEFAULT '',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                changes_summary TEXT DEFAULT '',
                author TEXT DEFAULT '',
                FOREIGN KEY (article_id) REFERENCES articles(article_id) ON DELETE CASCADE
            );
        """)
        await db.commit()
    finally:
        await db.close()


# --- Article Section CRUD ---

async def get_article_section(article_id: str, node_id: str) -> dict | None:
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM article_sections WHERE article_id = ? AND node_id = ?",
            (article_id, node_id),
        )
        row = await cursor.fetchone()
        return dict(row) if row else None
    finally:
        await db.close()


async def upsert_article_section(article_id: str, node_id: str, content: str, status: str) -> dict:
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT id FROM article_sections WHERE article_id = ? AND node_id = ?",
            (article_id, node_id),
        )
        existing = await cursor.fetchone()
        section_id = existing["id"] if existing else str(uuid.uuid4())

        await db.execute(
            """INSERT INTO article_sections (id, article_id, node_id, content, status, updated_at)
               VALUES (?, ?, ?, ?, ?, datetime('now'))
               ON CONFLICT(id) DO UPDATE SET
                 content=excluded.content, status=excluded.status,
                 updated_at=datetime('now')""",
            (section_id, article_id, node_id, content, status),
        )
        await db.commit()
        cursor = await db.execute("SELECT * FROM article_sections WHERE id = ?", (section_id,))
        row = await cursor.fetchone()
        return dict(row) if row else {}
    finally:
        await db.close()


async def list_article_sections(article_id: str) -> list[dict]:
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM article_sections WHERE article_id = ? ORDER BY updated_at ASC",
            (article_id,),
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        await db.close()


# --- Workflow CRUD ---

def _row_to_workflow(row: aiosqlite.Row) -> dict:
    d = dict(row)
    if isinstance(d.get("nodes"), str):
        d["nodes"] = json.loads(d["nodes"])
    if isinstance(d.get("edges"), str):
        d["edges"] = json.loads(d["edges"])
    return d


async def list_workflows() -> list[dict]:
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM workflows ORDER BY updated_at DESC")
        rows = await cursor.fetchall()
        return [_row_to_workflow(r) for r in rows]
    finally:
        await db.close()


async def get_workflow(workflow_id: str) -> dict | None:
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM workflows WHERE id = ?", (workflow_id,))
        row = await cursor.fetchone()
        return _row_to_workflow(row) if row else None
    finally:
        await db.close()


async def save_workflow(workflow: dict) -> dict:
    db = await get_db()
    try:
        await db.execute(
            """INSERT INTO workflows (id, name, description, nodes, edges, updated_at)
               VALUES (?, ?, ?, ?, ?, datetime('now'))
               ON CONFLICT(id) DO UPDATE SET
                 name=excluded.name, description=excluded.description,
                 nodes=excluded.nodes, edges=excluded.edges,
                 updated_at=datetime('now')""",
            (
                workflow["id"],
                workflow["name"],
                workflow.get("description", ""),
                json.dumps(workflow.get("nodes", [])),
                json.dumps(workflow.get("edges", [])),
            ),
        )
        await db.commit()
        cursor = await db.execute("SELECT * FROM workflows WHERE id = ?", (workflow["id"],))
        row = await cursor.fetchone()
        return _row_to_workflow(row) if row else {}
    finally:
        await db.close()


async def delete_workflow(workflow_id: str) -> bool:
    db = await get_db()
    try:
        cursor = await db.execute("DELETE FROM workflows WHERE id = ?", (workflow_id,))
        await db.commit()
        return cursor.rowcount > 0
    finally:
        await db.close()


# --- Reference CRUD ---

def _row_to_ref(row: aiosqlite.Row) -> dict:
    d = dict(row)
    for field in ("authors", "keywords"):
        if isinstance(d.get(field), str):
            d[field] = json.loads(d[field])
    return d


async def list_refs() -> list[dict]:
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM refs ORDER BY created_at DESC")
        rows = await cursor.fetchall()
        return [_row_to_ref(r) for r in rows]
    finally:
        await db.close()


async def save_ref(ref: dict) -> dict:
    ref_id = ref.get("id") or str(uuid.uuid4())
    db = await get_db()
    try:
        await db.execute(
            """INSERT INTO refs (id, title, authors, year, journal, volume, number,
                                 pages, doi, abstract, keywords, url, ref_type, raw_data)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(id) DO UPDATE SET
                 title=excluded.title, authors=excluded.authors,
                 year=excluded.year, journal=excluded.journal,
                 volume=excluded.volume, number=excluded.number,
                 pages=excluded.pages, doi=excluded.doi,
                 abstract=excluded.abstract, keywords=excluded.keywords,
                 url=excluded.url, ref_type=excluded.ref_type""",
            (
                ref_id,
                ref.get("title", ""),
                json.dumps(ref.get("authors", []), ensure_ascii=False),
                ref.get("year", ""),
                ref.get("journal", ""),
                ref.get("volume", ""),
                ref.get("number", ""),
                ref.get("pages", ""),
                ref.get("doi", ""),
                ref.get("abstract", ""),
                json.dumps(ref.get("keywords", []), ensure_ascii=False),
                ref.get("url", ""),
                ref.get("ref_type", "article"),
                ref.get("raw_data", ""),
            ),
        )
        await db.commit()
        cursor = await db.execute("SELECT * FROM refs WHERE id = ?", (ref_id,))
        row = await cursor.fetchone()
        return _row_to_ref(row) if row else {}
    finally:
        await db.close()


async def delete_ref(ref_id: str) -> bool:
    db = await get_db()
    try:
        cursor = await db.execute("DELETE FROM refs WHERE id = ?", (ref_id,))
        await db.commit()
        return cursor.rowcount > 0
    finally:
        await db.close()


async def delete_all_refs() -> int:
    db = await get_db()
    try:
        cursor = await db.execute("DELETE FROM refs")
        await db.commit()
        return cursor.rowcount
    finally:
        await db.close()


async def get_ref(ref_id: str) -> dict | None:
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM refs WHERE id = ?", (ref_id,))
        row = await cursor.fetchone()
        return _row_to_ref(row) if row else None
    finally:
        await db.close()


async def update_ref(ref_id: str, updates: dict) -> dict | None:
    existing = await get_ref(ref_id)
    if not existing:
        return None

    fields = {
        "title": updates.get("title", existing["title"]),
        "authors": json.dumps(updates.get("authors", existing["authors"]), ensure_ascii=False),
        "year": updates.get("year", existing["year"]),
        "journal": updates.get("journal", existing["journal"]),
        "volume": updates.get("volume", existing["volume"]),
        "number": updates.get("number", existing["number"]),
        "pages": updates.get("pages", existing["pages"]),
        "doi": updates.get("doi", existing["doi"]),
        "abstract": updates.get("abstract", existing["abstract"]),
        "keywords": json.dumps(updates.get("keywords", existing["keywords"]), ensure_ascii=False),
        "url": updates.get("url", existing["url"]),
        "ref_type": updates.get("ref_type", existing["ref_type"]),
        "notes": updates.get("notes", existing.get("notes", "")),
        "updated_at": datetime.utcnow().isoformat(),
    }

    sets = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [ref_id]

    db = await get_db()
    try:
        await db.execute(f"UPDATE refs SET {sets} WHERE id = ?", values)
        await db.commit()
        return await get_ref(ref_id)
    finally:
        await db.close()


async def search_refs(
    query: str = "",
    field: str = "all",
    limit: int = 20,
    offset: int = 0,
    sort: str = "updated_at",
    order: str = "DESC",
    ref_type: str | None = None,
) -> list[dict]:
    db = await get_db()
    try:
        conditions = []
        params = []

        if query:
            if field == "title":
                conditions.append("title LIKE ?")
                params.append(f"%{query}%")
            elif field == "author":
                conditions.append("authors LIKE ?")
                params.append(f"%{query}%")
            elif field == "doi":
                conditions.append("doi LIKE ?")
                params.append(f"%{query}%")
            else:
                conditions.append("(title LIKE ? OR authors LIKE ? OR abstract LIKE ? OR keywords LIKE ?)")
                params.extend([f"%{query}%"] * 4)

        if ref_type:
            conditions.append("ref_type = ?")
            params.append(ref_type)

        where = " AND ".join(conditions) if conditions else "1=1"
        valid_orders = {"ASC", "DESC"}
        order_dir = order.upper() if order.upper() in valid_orders else "DESC"
        valid_sorts = {"title", "year", "created_at", "updated_at"}
        order_col = sort if sort in valid_sorts else "updated_at"

        sql = f"SELECT * FROM refs WHERE {where} ORDER BY {order_col} {order_dir} LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor = await db.execute(sql, params)
        rows = await cursor.fetchall()
        return [_row_to_ref(r) for r in rows]
    finally:
        await db.close()


async def count_refs(query: str = "", ref_type: str | None = None) -> int:
    db = await get_db()
    try:
        conditions = []
        params = []

        if query:
            conditions.append("(title LIKE ? OR authors LIKE ? OR abstract LIKE ? OR keywords LIKE ?)")
            params.extend([f"%{query}%"] * 4)

        if ref_type:
            conditions.append("ref_type = ?")
            params.append(ref_type)

        where = " AND ".join(conditions) if conditions else "1=1"
        cursor = await db.execute(f"SELECT COUNT(*) as cnt FROM refs WHERE {where}", params)
        row = await cursor.fetchone()
        return row["cnt"] if row else 0
    finally:
        await db.close()


# --- Article CRUD ---

def _row_to_article(row: aiosqlite.Row) -> dict:
    d = dict(row)
    for field in ("authors", "keywords", "references_list"):
        if isinstance(d.get(field), str):
            d[field] = json.loads(d[field])
    return d


async def list_articles(status: str | None = None, skip: int = 0, limit: int = 100) -> list[dict]:
    db = await get_db()
    try:
        if status:
            cursor = await db.execute(
                "SELECT * FROM articles WHERE status = ? ORDER BY updated_at DESC LIMIT ? OFFSET ?",
                (status, limit, skip),
            )
        else:
            cursor = await db.execute(
                "SELECT * FROM articles ORDER BY updated_at DESC LIMIT ? OFFSET ?",
                (limit, skip),
            )
        rows = await cursor.fetchall()
        return [_row_to_article(r) for r in rows]
    finally:
        await db.close()


async def get_article(article_id: str) -> dict | None:
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM articles WHERE article_id = ?", (article_id,))
        row = await cursor.fetchone()
        return _row_to_article(row) if row else None
    finally:
        await db.close()


async def create_article(article: dict) -> dict:
    article_id = article.get("article_id") or str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    db = await get_db()
    try:
        await db.execute(
            """INSERT INTO articles (article_id, title, abstract, content, status, template,
                 authors, keywords, references_list, current_version, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                article_id,
                article.get("title", ""),
                article.get("abstract", ""),
                article.get("content", ""),
                article.get("status", "DRAFT"),
                article.get("template", "GENERIC"),
                json.dumps(article.get("authors", []), ensure_ascii=False),
                json.dumps(article.get("keywords", []), ensure_ascii=False),
                json.dumps(article.get("references", []), ensure_ascii=False),
                article.get("current_version", 1),
                now,
                now,
            ),
        )
        await db.commit()
        cursor = await db.execute("SELECT * FROM articles WHERE article_id = ?", (article_id,))
        row = await cursor.fetchone()
        return _row_to_article(row) if row else {}
    finally:
        await db.close()


async def update_article(article_id: str, updates: dict) -> dict | None:
    existing = await get_article(article_id)
    if not existing:
        return None

    fields = {
        "title": updates.get("title", existing["title"]),
        "abstract": updates.get("abstract", existing["abstract"]),
        "content": updates.get("content", existing["content"]),
        "status": updates.get("status", existing["status"]),
        "template": updates.get("template", existing["template"]),
        "authors": json.dumps(updates.get("authors", existing["authors"]), ensure_ascii=False),
        "keywords": json.dumps(updates.get("keywords", existing["keywords"]), ensure_ascii=False),
        "references_list": json.dumps(updates.get("references", existing.get("references_list", [])), ensure_ascii=False),
        "updated_at": datetime.utcnow().isoformat(),
    }

    if updates.get("status") == "SUBMITTED" and not existing.get("submitted_at"):
        fields["submitted_at"] = datetime.utcnow().isoformat()
    if updates.get("status") == "PUBLISHED" and not existing.get("published_at"):
        fields["published_at"] = datetime.utcnow().isoformat()

    sets = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [article_id]

    db = await get_db()
    try:
        await db.execute(f"UPDATE articles SET {sets} WHERE article_id = ?", values)
        await db.commit()
        cursor = await db.execute("SELECT * FROM articles WHERE article_id = ?", (article_id,))
        row = await cursor.fetchone()
        return _row_to_article(row) if row else None
    finally:
        await db.close()


async def delete_article(article_id: str) -> bool:
    db = await get_db()
    try:
        cursor = await db.execute("DELETE FROM articles WHERE article_id = ?", (article_id,))
        await db.commit()
        return cursor.rowcount > 0
    finally:
        await db.close()


# --- Article Version CRUD ---

async def create_article_version(version: dict) -> dict:
    version_id = version.get("version_id") or str(uuid.uuid4())
    db = await get_db()
    try:
        await db.execute(
            """INSERT INTO article_versions (version_id, article_id, version_number, content,
                 changes_summary, author)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                version_id,
                version["article_id"],
                version["version_number"],
                version.get("content", ""),
                version.get("changes_summary", ""),
                version.get("author", ""),
            ),
        )
        await db.commit()
        cursor = await db.execute("SELECT * FROM article_versions WHERE version_id = ?", (version_id,))
        row = await cursor.fetchone()
        return dict(row) if row else {}
    finally:
        await db.close()


async def list_article_versions(article_id: str) -> list[dict]:
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM article_versions WHERE article_id = ? ORDER BY version_number ASC",
            (article_id,),
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        await db.close()


async def get_article_version(article_id: str, version_number: int) -> dict | None:
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM article_versions WHERE article_id = ? AND version_number = ?",
            (article_id, version_number),
        )
        row = await cursor.fetchone()
        return dict(row) if row else None
    finally:
        await db.close()
