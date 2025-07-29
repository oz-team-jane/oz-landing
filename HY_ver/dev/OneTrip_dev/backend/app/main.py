"""
OneTrip FastAPI 메인 애플리케이션
AI 기반 여행 계획 자동화 서비스
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog

from app.core.config import settings
from app.routers import travel, health

# 구조화된 로깅 설정
logger = structlog.get_logger(__name__)

# FastAPI 앱 인스턴스
app = FastAPI(
    title="OneTrip API",
    description="AI 기반 여행 계획 자동화 서비스",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://localhost:3002",  # Next.js dev server (alternative port)
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3002",
        "https://onetrip.vercel.app",  # 프로덕션 도메인 (예시)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(health.router, prefix="/api/v1")
app.include_router(travel.router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 초기화"""
    logger.info("OneTrip API 서버가 시작되었습니다", env=settings.ENVIRONMENT)
    
@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 정리"""
    logger.info("OneTrip API 서버가 종료되었습니다")

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return JSONResponse({
        "message": "OneTrip API - AI 기반 여행 계획 자동화 서비스",
        "version": "1.0.0",
        "status": "running"
    })

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """전역 예외 처리"""
    logger.error("예상치 못한 오류가 발생했습니다", 
                error=str(exc), 
                path=str(request.url))
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "내부 서버 오류가 발생했습니다",
            "message": "잠시 후 다시 시도해주세요"
        }
    )