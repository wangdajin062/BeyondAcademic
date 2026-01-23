"""
Editor Service
Provides academic editing capabilities including grammar correction,
formatting guidance, and LaTeX support
"""
from typing import List, Dict, Optional
from pydantic import BaseModel
from enum import Enum


class SuggestionType(str, Enum):
    """Types of editing suggestions"""
    GRAMMAR = "grammar"
    SPELLING = "spelling"
    STYLE = "style"
    FORMATTING = "formatting"
    LATEX = "latex"
    CITATION = "citation"


class Suggestion(BaseModel):
    """Editing suggestion model"""
    type: SuggestionType
    position: int
    length: int
    original: str
    suggestion: str
    explanation: str
    confidence: float


class FormattingRule(BaseModel):
    """Academic formatting rule"""
    rule_id: str
    template: str
    category: str
    description: str
    example: str


class EditorService:
    """Service for academic editing features"""
    
    def __init__(self):
        self.formatting_rules = self._load_formatting_rules()
    
    def _load_formatting_rules(self) -> Dict[str, List[FormattingRule]]:
        """Load formatting rules for different templates"""
        return {
            "IEEE": [
                FormattingRule(
                    rule_id="ieee_title",
                    template="IEEE",
                    category="Title",
                    description="Title should use title case",
                    example="Deep Learning for Image Recognition"
                ),
                FormattingRule(
                    rule_id="ieee_sections",
                    template="IEEE",
                    category="Sections",
                    description="Main sections: Introduction, Related Work, Methodology, Results, Conclusion",
                    example="I. Introduction\\nII. Related Work"
                ),
            ],
            "Elsevier": [
                FormattingRule(
                    rule_id="elsevier_abstract",
                    template="Elsevier",
                    category="Abstract",
                    description="Abstract should be 150-250 words",
                    example="A concise summary of the work..."
                ),
            ],
        }
    
    async def check_grammar(self, text: str) -> List[Suggestion]:
        """
        Check text for grammar errors
        
        In production, this would integrate with advanced NLP models
        """
        suggestions = []
        
        # Simple example checks (replace with real NLP in production)
        common_errors = {
            " i ": " I ",
            "dont": "don't",
            "wont": "won't",
            "cant": "can't",
        }
        
        for error, correction in common_errors.items():
            pos = text.find(error)
            if pos != -1:
                suggestions.append(Suggestion(
                    type=SuggestionType.GRAMMAR,
                    position=pos,
                    length=len(error),
                    original=error,
                    suggestion=correction,
                    explanation=f"Replace '{error}' with '{correction}'",
                    confidence=0.95
                ))
        
        return suggestions
    
    async def check_formatting(self, text: str, template: str) -> List[Suggestion]:
        """
        Check text formatting against academic template
        
        Args:
            text: Text to check
            template: Academic template (IEEE, Elsevier, etc.)
        """
        suggestions = []
        
        # Check for common formatting issues
        lines = text.split('\n')
        
        # Check for proper section numbering (example)
        if template == "IEEE":
            for i, line in enumerate(lines):
                if line.strip().startswith("Introduction") and not line.strip().startswith("I."):
                    suggestions.append(Suggestion(
                        type=SuggestionType.FORMATTING,
                        position=text.find(line),
                        length=len(line),
                        original=line,
                        suggestion=f"I. {line.strip()}",
                        explanation="IEEE format requires Roman numerals for main sections",
                        confidence=0.90
                    ))
        
        return suggestions
    
    async def convert_to_latex(self, text: str) -> str:
        """
        Convert plain text to LaTeX format
        
        Basic conversion - can be enhanced with more sophisticated parsing
        """
        latex = "\\documentclass{article}\n"
        latex += "\\usepackage{amsmath}\n"
        latex += "\\usepackage{graphicx}\n\n"
        latex += "\\begin{document}\n\n"
        
        # Simple conversion
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                latex += "\n"
            elif line.isupper():  # Assume all-caps is a section
                latex += f"\\section{{{line.title()}}}\n"
            else:
                latex += f"{line}\n"
        
        latex += "\n\\end{document}"
        return latex
    
    async def suggest_improvements(self, paragraph: str) -> List[str]:
        """
        Suggest academic language improvements for a paragraph
        
        Uses AI to suggest more formal phrasing
        """
        suggestions = []
        
        # Example improvements (in production, use AI model)
        informal_phrases = {
            "a lot of": "numerous",
            "very important": "significant",
            "shows that": "demonstrates that",
            "find out": "determine",
            "get": "obtain",
        }
        
        for informal, formal in informal_phrases.items():
            if informal.lower() in paragraph.lower():
                suggestions.append(
                    f"Consider replacing '{informal}' with '{formal}' for more academic tone"
                )
        
        return suggestions
    
    async def get_formatting_rules(self, template: str) -> List[FormattingRule]:
        """Get formatting rules for a specific template"""
        return self.formatting_rules.get(template, [])
    
    async def validate_citations(self, text: str) -> Dict[str, any]:
        """
        Validate citation formatting
        
        Check for proper citation format and consistency
        """
        # Count citations
        citation_count = text.count('[')
        
        # Check for consistency
        has_numbered = '[1]' in text or '[2]' in text
        has_author_year = '(' in text and ')' in text
        
        return {
            "citation_count": citation_count,
            "style_detected": "numbered" if has_numbered else "author-year" if has_author_year else "unknown",
            "consistent": True,  # Would do real validation in production
            "suggestions": []
        }


# Global service instance
editor_service = EditorService()
