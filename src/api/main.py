"""
FastAPI application for the AI Strategic Co-pilot.

This module creates the FastAPI application that wraps the LangGraph StateGraph
and provides REST and WebSocket endpoints for real-time strategy coaching.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from ..core.config import settings
from ..core.graph import create_strategy_coach_graph
from .endpoints import router as api_router

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)

# Global graph instance
strategy_graph = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifespan - startup and shutdown."""
    global strategy_graph
    
    # Startup
    logger.info("🚀 Starting AI Strategic Co-pilot...")
    
    try:
        # Initialize LangGraph StateGraph
        strategy_graph = create_strategy_coach_graph()
        logger.info("✅ LangGraph StateGraph initialized successfully")
        
        # Validate configuration
        config_errors = settings.validate_configuration()
        if config_errors:
            for error in config_errors:
                logger.warning(f"⚠️ Configuration issue: {error}")
        else:
            logger.info("✅ Configuration validated successfully")
        
        # Setup LangSmith tracing
        settings.setup_langsmith_tracing()
        logger.info("✅ LangSmith tracing configured")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down AI Strategic Co-pilot...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="AI-powered strategic co-pilot using LangGraph and specialist agents",
        lifespan=lifespan,
        debug=settings.debug
    )
    
    # Configure CORS
    if settings.enable_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"] if settings.debug else ["http://localhost:3000"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    # Health check endpoint (before static files)
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "version": settings.app_version,
            "graph_initialized": strategy_graph is not None
        }
    
    # Include API routes
    app.include_router(api_router, prefix="/api/v1")
    
    # Serve static files (frontend) - mount last
    if settings.enable_static_files:
        try:
            app.mount("/", StaticFiles(directory="frontend", html=True), name="static")
        except RuntimeError:
            logger.warning("⚠️ Frontend directory not found - static files not mounted")
    
    return app


# Create the app instance
app = create_app()


def main():
    """Main entry point for running the application."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    main()