"""
DVMCP Dashboard Backend - FastAPI application
"""
import sys
import os

# Ensure the backend directory is on the import path so we can use
# absolute imports like `from database.models import ...` when running
# this file directly with `python main.py`.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from database.models import init_db
from api.routes.auth import router as auth_router, user_router
from api.routes.challenges import router as challenges_router
from api.routes.submissions import router as submissions_router
from api.routes.leaderboard import router as leaderboard_router
from api.routes.analytics import router as analytics_router
from api.routes.playground import router as playground_router
from api.services.websocket import manager

app = FastAPI(
    title="DVMCP Dashboard API",
    description="Backend API for the Damn Vulnerable MCP Server dashboard",
    version="2.0.0",
)

_cors_origins = os.getenv("DVMCP_CORS_ORIGINS", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if _cors_origins == "*" else [o.strip() for o in _cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(challenges_router)
app.include_router(submissions_router)
app.include_router(leaderboard_router)
app.include_router(analytics_router)
app.include_router(playground_router)


@app.on_event("startup")
async def on_startup():
    init_db()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "dvmcp-dashboard"}


# Serve built frontend with SPA fallback for deep links (e.g. /challenge/11).
frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.isdir(frontend_dist):
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/")
    async def serve_frontend_root():
        return FileResponse(os.path.join(frontend_dist, "index.html"))

    _resolved_dist = os.path.realpath(frontend_dist)

    @app.get("/{full_path:path}")
    async def serve_frontend_spa(full_path: str):
        if full_path.startswith("api/") or full_path in {"api", "ws", "health"}:
            raise HTTPException(status_code=404, detail="Not Found")

        requested_path = os.path.realpath(os.path.join(frontend_dist, full_path))
        if not requested_path.startswith(_resolved_dist + os.sep) and requested_path != _resolved_dist:
            raise HTTPException(status_code=400, detail="Invalid path")

        if os.path.isfile(requested_path):
            return FileResponse(requested_path)

        return FileResponse(os.path.join(frontend_dist, "index.html"))


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8081,
        reload=True,
    )
