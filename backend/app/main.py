import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.api.knowledge import router as knowledge_router
from app.api.sync import router as sync_router
from app.core.config import settings
from app.core.logging import logger
from app.scripts.reset_equinox_knowledge import reset_knowledge


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown hooks."""
    logger.info(f"Starting {settings.APP_NAME} in {settings.APP_ENV} mode...")
    # Initialize authoritative Equinox 2.0 knowledge on boot
    try:
        await reset_knowledge(bot_id="ems")
        logger.info("Authoritative Equinox 2.0 master knowledge catalog initialized.")
    except Exception as e:
        logger.warning(f"Startup Equinox knowledge sync warning: {e}")

    yield
    logger.info(f"Shutting down {settings.APP_NAME}...")


app = FastAPI(
    title=settings.APP_NAME,
    description="The Equinox 2.0 AI Event Assistant for MLRIT CIE",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS configuration for embed widget
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_WIDGET_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Ensure internal errors do not leak stack traces in production."""
    logger.error(f"Unhandled Exception on {request.url}: {exc}", exc_info=settings.DEBUG)
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "An internal server error occurred. Please try again later."},
    )


# Mount API routers
app.include_router(health_router)
app.include_router(chat_router, prefix=settings.API_PREFIX)
app.include_router(knowledge_router, prefix=settings.API_PREFIX)
app.include_router(sync_router, prefix=settings.API_PREFIX)

# If widget dist exists, mount it statically
widget_dist_path = os.path.join(os.path.dirname(__file__), "..", "..", "widget", "dist")
if os.path.exists(widget_dist_path):
    app.mount("/widget", StaticFiles(directory=widget_dist_path), name="widget")

# If demo folder exists, mount demo statically for easy testing
demo_path = os.path.join(os.path.dirname(__file__), "..", "..", "demo")
if os.path.exists(demo_path):
    app.mount("/demo", StaticFiles(directory=demo_path, html=True), name="demo")


@app.get("/")
async def root():
    return {
        "service": "The Equinox 2.0 Assistant Backend",
        "status": "online",
        "event": "The Equinox 2.0",
        "dates": "30–31 October",
        "location": "MLR Institute of Technology, Hyderabad",
        "docs": "/docs",
        "health": "/health",
        "widget_url": "/widget/widget.js",
        "demo": "/demo/index.html",
    }
