from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import os
import sys

from app.db.session import get_db
from app.core.config import settings

router = APIRouter(tags=["Health"])

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "ERP API",
        "version": "1.0.0"
    }

@router.get("/health/ready", status_code=status.HTTP_200_OK)
async def readiness_check(db: Session = Depends(get_db)):
    """
    Readiness check - verifies all dependencies are ready
    Returns 200 if ready, 503 if not ready
    """
    checks = {
        "database": False,
        "migrations": False,
        "required_tables": False
    }
    errors = []
    
    # Check database connection
    try:
        result = db.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception as e:
        errors.append(f"Database connection failed: {str(e)}")
    
    # Check if migrations have been run (check for essential tables)
    try:
        essential_tables = ['users', 'roles', 'permissions', 'organizations', 'leads']
        result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
        """))
        existing_tables = [row[0] for row in result]
        
        missing_tables = [table for table in essential_tables if table not in existing_tables]
        if missing_tables:
            errors.append(f"Missing tables: {', '.join(missing_tables)}")
        else:
            checks["migrations"] = True
            checks["required_tables"] = True
    except Exception as e:
        errors.append(f"Failed to check tables: {str(e)}")
    
    # Overall status
    is_ready = all(checks.values())
    
    response = {
        "status": "ready" if is_ready else "not_ready",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks
    }
    
    if errors:
        response["errors"] = errors
    
    if not is_ready:
        return response, status.HTTP_503_SERVICE_UNAVAILABLE
    
    return response

@router.get("/health/live", status_code=status.HTTP_200_OK)
async def liveness_check():
    """
    Liveness check - verifies the service is running
    Used by orchestrators to determine if the service needs to be restarted
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": get_uptime(),
        "memory_usage": get_memory_usage(),
        "python_version": sys.version
    }

@router.get("/health/db", status_code=status.HTTP_200_OK)
async def database_health(db: Session = Depends(get_db)):
    """Detailed database health check"""
    try:
        # Test basic connectivity
        result = db.execute(text("SELECT version()"))
        db_version = result.fetchone()[0]
        
        # Count records in main tables
        stats = {}
        tables = ['users', 'roles', 'permissions', 'organizations', 'leads']
        
        for table in tables:
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.fetchone()[0]
                stats[table] = count
            except:
                stats[table] = "table_not_found"
        
        # Check connection pool (if using one)
        return {
            "status": "connected",
            "database_version": db_version,
            "table_statistics": stats,
            "connection_string": settings.DATABASE_URL.split('@')[-1] if hasattr(settings, 'DATABASE_URL') else "configured"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }, status.HTTP_503_SERVICE_UNAVAILABLE

def get_uptime():
    """Calculate service uptime"""
    if not hasattr(get_uptime, 'start_time'):
        get_uptime.start_time = datetime.utcnow()
    
    uptime_delta = datetime.utcnow() - get_uptime.start_time
    return {
        "seconds": int(uptime_delta.total_seconds()),
        "human_readable": str(uptime_delta)
    }

def get_memory_usage():
    """Get memory usage statistics"""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    return {
        "rss_mb": round(memory_info.rss / 1024 / 1024, 2),
        "vms_mb": round(memory_info.vms / 1024 / 1024, 2),
        "percent": round(process.memory_percent(), 2)
    }