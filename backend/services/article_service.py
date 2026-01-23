"""
Article Management Service
Handles article CRUD operations, version control, and document organization
"""
from typing import List, Optional, Dict
from datetime import datetime
import uuid
from models.article import (
    Article, ArticleCreate, ArticleUpdate, 
    ArticleVersion, ArticleStatus, ArticleResponse
)


class ArticleService:
    """Service for managing articles with version control"""
    
    def __init__(self):
        # In-memory storage (replace with database in production)
        self.articles: Dict[str, Article] = {}
    
    async def create_article(self, article_data: ArticleCreate, author: str) -> Article:
        """
        Create a new article with initial version
        
        Args:
            article_data: Article creation data
            author: Author creating the article
            
        Returns:
            Created article with version history initialized
        """
        article_id = str(uuid.uuid4())
        
        # Create initial version
        initial_version = ArticleVersion(
            version_id=str(uuid.uuid4()),
            version_number=1,
            content=article_data.content,
            author=author,
            changes_summary="Initial version"
        )
        
        article = Article(
            article_id=article_id,
            title=article_data.title,
            abstract=article_data.abstract,
            content=article_data.content,
            template=article_data.template,
            authors=article_data.authors if article_data.authors else [author],
            keywords=article_data.keywords,
            current_version=1,
            versions=[initial_version]
        )
        
        self.articles[article_id] = article
        return article
    
    async def get_article(self, article_id: str) -> Optional[Article]:
        """Retrieve an article by ID"""
        return self.articles.get(article_id)
    
    async def list_articles(
        self, 
        status: Optional[ArticleStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Article]:
        """
        List articles with optional filtering
        
        Args:
            status: Filter by article status
            skip: Number of articles to skip (pagination)
            limit: Maximum number of articles to return
            
        Returns:
            List of articles matching criteria
        """
        articles = list(self.articles.values())
        
        if status:
            articles = [a for a in articles if a.status == status]
        
        # Sort by updated_at descending
        articles.sort(key=lambda x: x.updated_at, reverse=True)
        
        return articles[skip:skip + limit]
    
    async def update_article(
        self, 
        article_id: str, 
        update_data: ArticleUpdate,
        author: str
    ) -> Optional[Article]:
        """
        Update an article and create a new version if content changed
        
        Args:
            article_id: ID of article to update
            update_data: Update data
            author: Author making the update
            
        Returns:
            Updated article or None if not found
        """
        article = self.articles.get(article_id)
        if not article:
            return None
        
        # Track if content changed for version control
        content_changed = False
        
        # Update fields
        if update_data.title is not None:
            article.title = update_data.title
        if update_data.abstract is not None:
            article.abstract = update_data.abstract
        if update_data.content is not None and update_data.content != article.content:
            content_changed = True
            old_content = article.content
            article.content = update_data.content
        if update_data.status is not None:
            article.status = update_data.status
        if update_data.template is not None:
            article.template = update_data.template
        if update_data.authors is not None:
            article.authors = update_data.authors
        if update_data.keywords is not None:
            article.keywords = update_data.keywords
        if update_data.references is not None:
            article.references = update_data.references
        
        # Create new version if content changed
        if content_changed:
            new_version_number = article.current_version + 1
            new_version = ArticleVersion(
                version_id=str(uuid.uuid4()),
                version_number=new_version_number,
                content=article.content,
                author=author,
                changes_summary=update_data.changes_summary or f"Version {new_version_number} update"
            )
            article.versions.append(new_version)
            article.current_version = new_version_number
        
        article.updated_at = datetime.utcnow()
        
        # Update status-specific timestamps
        if update_data.status == ArticleStatus.SUBMITTED and not article.submitted_at:
            article.submitted_at = datetime.utcnow()
        elif update_data.status == ArticleStatus.PUBLISHED and not article.published_at:
            article.published_at = datetime.utcnow()
        
        return article
    
    async def delete_article(self, article_id: str) -> bool:
        """Delete an article"""
        if article_id in self.articles:
            del self.articles[article_id]
            return True
        return False
    
    async def get_article_version(
        self, 
        article_id: str, 
        version_number: int
    ) -> Optional[ArticleVersion]:
        """Retrieve a specific version of an article"""
        article = self.articles.get(article_id)
        if not article:
            return None
        
        for version in article.versions:
            if version.version_number == version_number:
                return version
        return None
    
    async def get_version_history(self, article_id: str) -> Optional[List[ArticleVersion]]:
        """Get complete version history of an article"""
        article = self.articles.get(article_id)
        if not article:
            return None
        return article.versions
    
    async def revert_to_version(
        self, 
        article_id: str, 
        version_number: int,
        author: str
    ) -> Optional[Article]:
        """
        Revert article to a previous version
        
        Creates a new version with the content from the specified version
        """
        article = self.articles.get(article_id)
        if not article:
            return None
        
        # Find the target version
        target_version = None
        for version in article.versions:
            if version.version_number == version_number:
                target_version = version
                break
        
        if not target_version:
            return None
        
        # Create new version with reverted content
        new_version_number = article.current_version + 1
        new_version = ArticleVersion(
            version_id=str(uuid.uuid4()),
            version_number=new_version_number,
            content=target_version.content,
            author=author,
            changes_summary=f"Reverted to version {version_number}"
        )
        
        article.content = target_version.content
        article.versions.append(new_version)
        article.current_version = new_version_number
        article.updated_at = datetime.utcnow()
        
        return article


# Global service instance
article_service = ArticleService()
