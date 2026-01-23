"""
Recommendation API Router
Provides endpoints for AI-powered literature recommendations and language optimization
"""
from fastapi import APIRouter, Query
from typing import List, Dict, Optional
from pydantic import BaseModel
from services.recommendation_service import (
    recommendation_service, 
    Paper, 
    LanguageOptimization,
    RecommendationType
)

router = APIRouter()


class SearchRequest(BaseModel):
    """Request model for paper search"""
    query: str
    limit: int = 10
    recommendation_type: Optional[RecommendationType] = None


class RecommendationRequest(BaseModel):
    """Request model for paper recommendations"""
    context: str
    limit: int = 5


class SentenceOptimizationRequest(BaseModel):
    """Request model for sentence optimization"""
    sentence: str


class ParagraphOptimizationRequest(BaseModel):
    """Request model for paragraph optimization"""
    paragraph: str


class CitationRequest(BaseModel):
    """Request model for citation suggestions"""
    topic: str


@router.post("/search", response_model=List[Paper])
async def search_papers(request: SearchRequest):
    """
    Search for academic papers
    
    - **query**: Search query or keywords
    - **limit**: Maximum number of results
    - **recommendation_type**: Type of papers to prioritize (high_impact, high_citation, recent, etc.)
    """
    papers = await recommendation_service.search_papers(
        request.query, 
        request.limit,
        request.recommendation_type
    )
    return papers


@router.post("/recommend", response_model=List[Paper])
async def recommend_papers(request: RecommendationRequest):
    """
    Get paper recommendations based on writing context
    
    Analyzes the content and recommends relevant literature
    
    - **context**: Current article content or paragraph
    - **limit**: Maximum number of recommendations
    """
    papers = await recommendation_service.recommend_papers(
        request.context,
        request.limit
    )
    return papers


@router.post("/optimize/sentence", response_model=LanguageOptimization)
async def optimize_sentence(request: SentenceOptimizationRequest):
    """
    Optimize a sentence for academic writing
    
    Provides more formal phrasing and improved clarity
    """
    optimization = await recommendation_service.optimize_sentence(request.sentence)
    return optimization


@router.post("/optimize/paragraph", response_model=Dict[str, any])
async def optimize_paragraph(request: ParagraphOptimizationRequest):
    """
    Optimize an entire paragraph
    
    Returns comprehensive suggestions for improvement including:
    - Optimized paragraph
    - Sentence-level improvements
    - Formality and clarity scores
    """
    result = await recommendation_service.optimize_paragraph(request.paragraph)
    return result


@router.post("/citations", response_model=List[str])
async def get_citation_suggestions(request: CitationRequest):
    """
    Get citation suggestions for a topic
    
    Returns formatted citation strings for relevant high-impact papers
    """
    citations = await recommendation_service.get_citation_suggestions(request.topic)
    return citations


@router.get("/papers/high-impact", response_model=List[Paper])
async def get_high_impact_papers(
    field: Optional[str] = None,
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get high-impact papers
    
    Returns papers with high citation counts and impact
    """
    query = field if field else "machine learning"
    papers = await recommendation_service.search_papers(
        query,
        limit,
        RecommendationType.HIGH_IMPACT
    )
    return papers


@router.get("/papers/recent", response_model=List[Paper])
async def get_recent_papers(
    field: Optional[str] = None,
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get recent papers
    
    Returns the most recent publications in a field
    """
    query = field if field else "artificial intelligence"
    papers = await recommendation_service.search_papers(
        query,
        limit,
        RecommendationType.RECENT
    )
    return papers
