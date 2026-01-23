"""
Recommendation Service
AI-powered literature and knowledge recommendation system
"""
from typing import List, Dict, Optional
from pydantic import BaseModel
from enum import Enum
from datetime import datetime


class RecommendationType(str, Enum):
    """Types of recommendations"""
    HIGH_IMPACT = "high_impact"
    HIGH_CITATION = "high_citation"
    RELEVANT = "relevant"
    RECENT = "recent"
    SEMINAL = "seminal"


class Paper(BaseModel):
    """Academic paper model"""
    paper_id: str
    title: str
    authors: List[str]
    abstract: str
    year: int
    venue: str
    citations: int
    url: Optional[str] = None
    doi: Optional[str] = None
    relevance_score: float = 0.0


class LanguageOptimization(BaseModel):
    """Language optimization suggestion"""
    original_sentence: str
    optimized_sentence: str
    improvements: List[str]
    formality_score: float
    clarity_score: float


class RecommendationService:
    """Service for AI-powered recommendations"""
    
    def __init__(self):
        # Mock database of papers (in production, connect to real databases)
        self.papers_db = self._initialize_paper_database()
    
    def _initialize_paper_database(self) -> List[Paper]:
        """Initialize mock paper database"""
        return [
            Paper(
                paper_id="p1",
                title="Attention Is All You Need",
                authors=["Vaswani, A.", "Shazeer, N.", "Parmar, N."],
                abstract="The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...",
                year=2017,
                venue="NeurIPS",
                citations=50000,
                doi="10.5555/3295222.3295349",
                relevance_score=0.95
            ),
            Paper(
                paper_id="p2",
                title="BERT: Pre-training of Deep Bidirectional Transformers",
                authors=["Devlin, J.", "Chang, M.", "Lee, K."],
                abstract="We introduce a new language representation model called BERT...",
                year=2019,
                venue="NAACL",
                citations=45000,
                doi="10.18653/v1/N19-1423",
                relevance_score=0.92
            ),
            Paper(
                paper_id="p3",
                title="Deep Residual Learning for Image Recognition",
                authors=["He, K.", "Zhang, X.", "Ren, S."],
                abstract="Deeper neural networks are more difficult to train...",
                year=2016,
                venue="CVPR",
                citations=100000,
                doi="10.1109/CVPR.2016.90",
                relevance_score=0.88
            ),
        ]
    
    async def search_papers(
        self, 
        query: str, 
        limit: int = 10,
        recommendation_type: Optional[RecommendationType] = None
    ) -> List[Paper]:
        """
        Search for relevant papers based on query
        
        Uses semantic search to find relevant academic papers
        
        Args:
            query: Search query or research topic
            limit: Maximum number of papers to return
            recommendation_type: Type of recommendation to prioritize
        """
        # Simple keyword matching (in production, use semantic search)
        query_lower = query.lower()
        results = []
        
        for paper in self.papers_db:
            # Calculate relevance based on keyword matching
            title_match = any(word in paper.title.lower() for word in query_lower.split())
            abstract_match = any(word in paper.abstract.lower() for word in query_lower.split())
            
            if title_match or abstract_match:
                results.append(paper)
        
        # Sort based on recommendation type
        if recommendation_type == RecommendationType.HIGH_CITATION:
            results.sort(key=lambda p: p.citations, reverse=True)
        elif recommendation_type == RecommendationType.RECENT:
            results.sort(key=lambda p: p.year, reverse=True)
        elif recommendation_type == RecommendationType.HIGH_IMPACT:
            results.sort(key=lambda p: p.citations / max(2024 - p.year, 1), reverse=True)
        else:
            results.sort(key=lambda p: p.relevance_score, reverse=True)
        
        return results[:limit]
    
    async def recommend_papers(
        self, 
        context: str,
        limit: int = 5
    ) -> List[Paper]:
        """
        Recommend papers based on writing context
        
        Analyzes the user's current writing and recommends relevant literature
        
        Args:
            context: Current article content or paragraph
            limit: Maximum number of recommendations
        """
        # Extract keywords from context (simplified)
        keywords = context.lower().split()
        
        # Find relevant papers
        scored_papers = []
        for paper in self.papers_db:
            score = 0.0
            for keyword in keywords[:10]:  # Use top keywords
                if keyword in paper.title.lower():
                    score += 2.0
                if keyword in paper.abstract.lower():
                    score += 1.0
            
            if score > 0:
                paper.relevance_score = min(score / 10.0, 1.0)
                scored_papers.append(paper)
        
        # Sort by relevance
        scored_papers.sort(key=lambda p: p.relevance_score, reverse=True)
        
        return scored_papers[:limit]
    
    async def optimize_sentence(self, sentence: str) -> LanguageOptimization:
        """
        Optimize a sentence for academic writing
        
        Provides more formal phrasing and improved clarity
        
        Args:
            sentence: Original sentence to optimize
        """
        # Example optimizations (in production, use AI model)
        optimized = sentence
        improvements = []
        
        # Replace informal words
        replacements = {
            "a lot of": "numerous",
            "very": "significantly",
            "get": "obtain",
            "show": "demonstrate",
            "find": "determine",
            "use": "utilize",
            "good": "effective",
            "bad": "ineffective",
            "big": "substantial",
            "small": "minimal",
        }
        
        for informal, formal in replacements.items():
            if informal in sentence.lower():
                optimized = optimized.replace(informal, formal)
                improvements.append(f"Replaced '{informal}' with '{formal}' for formal tone")
        
        # Add passive voice suggestion for methods
        if "we" in sentence.lower() and "method" in sentence.lower():
            improvements.append("Consider using passive voice in methodology sections")
        
        # Calculate scores
        formality_score = 0.7 + (len(improvements) * 0.1)
        clarity_score = 0.8
        
        return LanguageOptimization(
            original_sentence=sentence,
            optimized_sentence=optimized,
            improvements=improvements,
            formality_score=min(formality_score, 1.0),
            clarity_score=clarity_score
        )
    
    async def optimize_paragraph(self, paragraph: str) -> Dict[str, any]:
        """
        Optimize an entire paragraph
        
        Returns comprehensive suggestions for improvement
        """
        sentences = paragraph.split('.')
        optimizations = []
        
        for sentence in sentences:
            if sentence.strip():
                opt = await self.optimize_sentence(sentence.strip())
                optimizations.append(opt)
        
        # Combine optimized sentences
        optimized_paragraph = '. '.join([opt.optimized_sentence for opt in optimizations])
        if optimized_paragraph and not optimized_paragraph.endswith('.'):
            optimized_paragraph += '.'
        
        return {
            "original": paragraph,
            "optimized": optimized_paragraph,
            "sentence_optimizations": optimizations,
            "overall_formality": sum(opt.formality_score for opt in optimizations) / len(optimizations) if optimizations else 0,
            "overall_clarity": sum(opt.clarity_score for opt in optimizations) / len(optimizations) if optimizations else 0,
        }
    
    async def get_citation_suggestions(self, topic: str) -> List[str]:
        """
        Suggest citations for a given topic
        
        Returns formatted citation strings
        """
        papers = await self.search_papers(topic, limit=5, recommendation_type=RecommendationType.HIGH_CITATION)
        
        citations = []
        for i, paper in enumerate(papers, 1):
            authors_str = ", ".join(paper.authors[:3])
            if len(paper.authors) > 3:
                authors_str += " et al."
            
            citation = f"[{i}] {authors_str}, \"{paper.title}\", {paper.venue}, {paper.year}."
            citations.append(citation)
        
        return citations


# Global service instance
recommendation_service = RecommendationService()
