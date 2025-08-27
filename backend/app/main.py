# Entry point for FastAPI
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime

from app.api.routes import lead, role, permission, auth, health
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ERP System API",
    description="Commercial Grade ERP System with modular architecture",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS - MUST be before routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Add your frontend URLs
    allow_credentials=True,  # Required for cookies
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]  # Allows frontend to read all headers
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception handler caught: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": str(type(exc).__name__),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Root endpoint
@app.get('/')
def read_root():
    return {
        "message": "ERP API is running",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "timestamp": datetime.utcnow().isoformat()
    }

# Include routers
app.include_router(health.router)  # Health checks first
app.include_router(auth.router, prefix="/api")
app.include_router(lead.router, prefix="/api")
app.include_router(role.router, prefix="/api")
app.include_router(permission.router, prefix="/api")

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 ERP API Starting up...")
    logger.info(f"📝 Docs available at http://localhost:8000/docs")
    logger.info(f"🏥 Health check at http://localhost:8000/health")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("👋 ERP API Shutting down...")