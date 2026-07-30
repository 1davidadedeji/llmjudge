#!/usr/bin/env python3
"""
main.py --- FastAPI application exposing eval results

Contains:
    create_app(): builds the FastAPI app with all routers
    app: module-level ASGI application
"""

from fastapi import FastAPI

from api.routes import compare, results


def create_app() -> FastAPI:
    """Builds the FastAPI app with all routers.

    Returns:
        app: Configured FastAPI application.
    """
    app = FastAPI(title="llmjudge", version="0.3.0")
    app.include_router(results.router)
    app.include_router(compare.router)
    return app


app = create_app()
