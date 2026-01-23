"""
BeyondAcademic - Main Application Entry Point
A modular academic writing system with AI-powered assistance
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import article_router, editor_router, recommendation_router

app = FastAPI(
    title="BeyondAcademic",
    description="AI-Powered Academic Writing System",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(article_router.router, prefix="/api/articles", tags=["articles"])
app.include_router(editor_router.router, prefix="/api/editor", tags=["editor"])
app.include_router(recommendation_router.router, prefix="/api/recommendations", tags=["recommendations"])

@app.get("/")
async def root():
    """Root endpoint providing system information"""
    return {
        "name": "BeyondAcademic",
        "description": "AI-Powered Academic Writing System",
        "version": "1.0.0",
        "modules": [
            "Article Management",
            "Academic Editor",
            "AI-Assisted Knowledge Recommendation"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "BeyondAcademic"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
