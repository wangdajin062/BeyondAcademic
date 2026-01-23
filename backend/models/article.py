"""
Article Model - Database schema for articles
Manages the lifecycle of academic articles including version control
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class ArticleStatus(str, Enum):
    """Status of an article in its lifecycle"""
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    REVISED = "revised"
    SUBMITTED = "submitted"
    PUBLISHED = "published"


class TemplateType(str, Enum):
    """Supported academic templates"""
    IEEE = "IEEE"
    ELSEVIER = "Elsevier"
    ACM = "ACM"
    SPRINGER = "Springer"
    NATURE = "Nature"
    SCIENCE = "Science"
    GENERIC = "Generic"


class ArticleVersion(BaseModel):
    """Version control for article revisions"""
    version_id: str = Field(..., description="Unique version identifier")
    version_number: int = Field(..., description="Sequential version number")
    content: str = Field(..., description="Article content at this version")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    changes_summary: Optional[str] = Field(None, description="Summary of changes in this version")
    author: str = Field(..., description="Author of this version")


class Article(BaseModel):
    """Main article model with version control and metadata"""
    article_id: str = Field(..., description="Unique article identifier")
    title: str = Field(..., min_length=1, max_length=500)
    abstract: Optional[str] = Field(None, max_length=5000)
    content: str = Field(..., description="Current article content")
    status: ArticleStatus = Field(default=ArticleStatus.DRAFT)
    template: TemplateType = Field(default=TemplateType.GENERIC)
    
    # Metadata
    authors: List[str] = Field(default_factory=list, description="List of author names")
    keywords: List[str] = Field(default_factory=list, description="Article keywords")
    references: List[str] = Field(default_factory=list, description="List of references")
    
    # Version control
    current_version: int = Field(default=1, description="Current version number")
    versions: List[ArticleVersion] = Field(default_factory=list, description="Version history")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    submitted_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    
    class Config:
        use_enum_values = True


class ArticleCreate(BaseModel):
    """Schema for creating a new article"""
    title: str = Field(..., min_length=1, max_length=500)
    abstract: Optional[str] = Field(None, max_length=5000)
    content: str = Field(default="", description="Initial article content")
    template: TemplateType = Field(default=TemplateType.GENERIC)
    authors: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)


class ArticleUpdate(BaseModel):
    """Schema for updating an article"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    abstract: Optional[str] = Field(None, max_length=5000)
    content: Optional[str] = None
    status: Optional[ArticleStatus] = None
    template: Optional[TemplateType] = None
    authors: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    references: Optional[List[str]] = None
    changes_summary: Optional[str] = Field(None, description="Summary of changes for version control")


class ArticleResponse(BaseModel):
    """Response schema for article operations"""
    article_id: str
    title: str
    status: ArticleStatus
    current_version: int
    created_at: datetime
    updated_at: datetime
