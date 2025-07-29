"""
헬스체크 및 시스템 상태 라우터
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
import structlog
from datetime import datetime

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check():
    """기본 헬스체크"""
    return JSONResponse({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "OneTrip API"
    })

@router.get("/health/detailed")
async def detailed_health_check():
    """상세 헬스체크"""
    # TODO: 데이터베이스, Redis, 외부 API 연결 상태 확인
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "OneTrip API",
        "version": "1.0.0",
        "components": {
            "database": "not_implemented",
            "redis": "not_implemented", 
            "openai": "not_implemented",
            "google_apis": "not_implemented"
        }
    }
    
    return JSONResponse(health_status)