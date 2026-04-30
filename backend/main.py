"""
BeyondAcademic - Main Application Entry Point
A modular academic writing system with AI-powered assistance
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import article_router, editor_router, recommendation_router, auth_router

app = FastAPI(
    title="BeyondAcademic",
    description="AI-Powered Academic Writing System",
    version="1.0.0"
)

# CORS origins: comma-separated env var, defaults to localhost for dev
_raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost,http://localhost:3000,http://localhost:80")
origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(article_router.router, prefix="/api/articles", tags=["articles"])
app.include_router(editor_router.router, prefix="/api/editor", tags=["editor"])
app.include_router(recommendation_router.router, prefix="/api/recommendations", tags=["recommendations"])
app.include_router(auth_router.router, prefix="/api/auth", tags=["auth"])


@app.get("/")
async def root():
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
    return {"status": "healthy", "service": "BeyondAcademic"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
