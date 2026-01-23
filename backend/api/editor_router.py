"""
Academic Editor API Router
Provides endpoints for grammar checking, formatting, and LaTeX support
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict
from pydantic import BaseModel
from services.editor_service import editor_service, Suggestion, FormattingRule

router = APIRouter()


class TextCheckRequest(BaseModel):
    """Request model for text checking"""
    text: str
    template: str = "Generic"


class ParagraphRequest(BaseModel):
    """Request model for paragraph improvement"""
    paragraph: str


class ConversionRequest(BaseModel):
    """Request model for format conversion"""
    text: str
    from_format: str = "plain"
    to_format: str = "latex"


@router.post("/check/grammar", response_model=List[Suggestion])
async def check_grammar(request: TextCheckRequest):
    """
    Check text for grammar errors
    
    Returns a list of suggestions with corrections
    """
    suggestions = await editor_service.check_grammar(request.text)
    return suggestions


@router.post("/check/formatting", response_model=List[Suggestion])
async def check_formatting(request: TextCheckRequest):
    """
    Check text formatting against academic template
    
    - **text**: Text to check
    - **template**: Academic template (IEEE, Elsevier, etc.)
    """
    suggestions = await editor_service.check_formatting(request.text, request.template)
    return suggestions


@router.post("/convert/latex", response_model=Dict[str, str])
async def convert_to_latex(request: ConversionRequest):
    """
    Convert plain text to LaTeX format
    
    Returns the LaTeX formatted version of the text
    """
    latex = await editor_service.convert_to_latex(request.text)
    return {"latex": latex}


@router.post("/improve", response_model=List[str])
async def suggest_improvements(request: ParagraphRequest):
    """
    Suggest academic language improvements
    
    Provides suggestions for more formal phrasing and better academic style
    """
    suggestions = await editor_service.suggest_improvements(request.paragraph)
    return suggestions


@router.get("/templates/{template}/rules", response_model=List[FormattingRule])
async def get_formatting_rules(template: str):
    """
    Get formatting rules for a specific academic template
    
    - **template**: Template name (IEEE, Elsevier, ACM, etc.)
    """
    rules = await editor_service.get_formatting_rules(template)
    if not rules:
        raise HTTPException(
            status_code=404, 
            detail=f"No formatting rules found for template: {template}"
        )
    return rules


@router.post("/validate/citations", response_model=Dict[str, any])
async def validate_citations(request: TextCheckRequest):
    """
    Validate citation formatting
    
    Checks for proper citation format and consistency
    """
    validation = await editor_service.validate_citations(request.text)
    return validation
