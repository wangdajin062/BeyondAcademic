"""
BeyondAcademic - Main Application Entry Point
A modular academic writing system with AI-powered assistance
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from storage.db import init_db

# BeyondAcademic original routers
from api import article_router, editor_router, recommendation_router, auth_router

# PaperFlow workflow engine routers
from api.workflows import router as workflows_router
from api.execution import router as execution_router
from api.models import router as models_router
from api.references_api import router as references_router

# Paper Writing Platform router
from api.paper_writing import router as paper_writing_router

# Literature Management router
from api.literature_router import router as literature_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="BeyondAcademic",
    description="AI-Powered Academic Writing System with Workflow Engine",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# BeyondAcademic original routes
app.include_router(article_router.router, prefix="/api/articles", tags=["articles"])
app.include_router(editor_router.router, prefix="/api/editor", tags=["editor"])
app.include_router(recommendation_router.router, prefix="/api/recommendations", tags=["recommendations"])
app.include_router(auth_router.router, prefix="/api/auth", tags=["auth"])

# PaperFlow workflow engine routes
app.include_router(workflows_router, prefix="/api/workflows", tags=["workflows"])
app.include_router(execution_router, prefix="/api/execution", tags=["execution"])
app.include_router(models_router, prefix="/api/models", tags=["models"])
app.include_router(references_router, prefix="/api/references", tags=["references"])

# Paper Writing Platform routes
app.include_router(paper_writing_router, prefix="/api/paper-writing", tags=["paper-writing"])

# Literature Management routes
app.include_router(literature_router, prefix="/api/literature", tags=["literature"])


@app.get("/")
async def root():
    return {
        "name": "BeyondAcademic",
        "description": "AI-Powered Academic Writing System with Workflow Engine",
        "version": "2.0.0",
        "modules": [
            "Article Management",
            "Academic Editor",
            "AI-Assisted Knowledge Recommendation",
            "Workflow Engine",
            "Reference Manager",
                "Paper Writing Platform",
            ],
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "BeyondAcademic"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
