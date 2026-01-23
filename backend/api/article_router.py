"""
Article Management API Router
Provides REST endpoints for article CRUD operations and version control
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from models.article import (
    Article, ArticleCreate, ArticleUpdate, 
    ArticleStatus, ArticleVersion, ArticleResponse
)
from services.article_service import article_service

router = APIRouter()


@router.post("/", response_model=Article, status_code=201)
async def create_article(article_data: ArticleCreate, author: str = "default_user"):
    """
    Create a new article
    
    - **title**: Article title (required)
    - **abstract**: Article abstract (optional)
    - **content**: Initial content (optional)
    - **template**: Academic template to use (IEEE, Elsevier, etc.)
    """
    article = await article_service.create_article(article_data, author)
    return article


@router.get("/", response_model=List[ArticleResponse])
async def list_articles(
    status: Optional[ArticleStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """
    List all articles with optional filtering
    
    - **status**: Filter by article status (draft, in_review, etc.)
    - **skip**: Number of articles to skip (pagination)
    - **limit**: Maximum number of articles to return
    """
    articles = await article_service.list_articles(status, skip, limit)
    return [
        ArticleResponse(
            article_id=a.article_id,
            title=a.title,
            status=a.status,
            current_version=a.current_version,
            created_at=a.created_at,
            updated_at=a.updated_at
        )
        for a in articles
    ]


@router.get("/{article_id}", response_model=Article)
async def get_article(article_id: str):
    """
    Get a specific article by ID
    
    Returns the complete article including all versions
    """
    article = await article_service.get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.put("/{article_id}", response_model=Article)
async def update_article(
    article_id: str, 
    update_data: ArticleUpdate,
    author: str = "default_user"
):
    """
    Update an article
    
    If content is updated, a new version is automatically created
    """
    article = await article_service.update_article(article_id, update_data, author)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.delete("/{article_id}", status_code=204)
async def delete_article(article_id: str):
    """Delete an article"""
    success = await article_service.delete_article(article_id)
    if not success:
        raise HTTPException(status_code=404, detail="Article not found")


@router.get("/{article_id}/versions", response_model=List[ArticleVersion])
async def get_version_history(article_id: str):
    """
    Get complete version history of an article
    
    Returns all versions with their content and metadata
    """
    versions = await article_service.get_version_history(article_id)
    if versions is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return versions


@router.get("/{article_id}/versions/{version_number}", response_model=ArticleVersion)
async def get_article_version(article_id: str, version_number: int):
    """Get a specific version of an article"""
    version = await article_service.get_article_version(article_id, version_number)
    if not version:
        raise HTTPException(
            status_code=404, 
            detail="Article or version not found"
        )
    return version


@router.post("/{article_id}/revert/{version_number}", response_model=Article)
async def revert_to_version(
    article_id: str, 
    version_number: int,
    author: str = "default_user"
):
    """
    Revert article to a previous version
    
    Creates a new version with the content from the specified version
    """
    article = await article_service.revert_to_version(article_id, version_number, author)
    if not article:
        raise HTTPException(
            status_code=404, 
            detail="Article or version not found"
        )
    return article
