#!/usr/bin/env python3
"""
main.py --- FastAPI application exposing eval results

Contains:
    create_app(): builds the FastAPI app with all routers
    app: module-level ASGI application
"""

from fastapi import FastAPI

from api.routes import results


def create_app() -> FastAPI:
    """Builds the FastAPI app with all routers.

    Returns:
        app: Configured FastAPI application.
    """
    app = FastAPI(title="llmjudge", version="0.1.0")
    app.include_router(results.router)
    return app


app = create_app()
