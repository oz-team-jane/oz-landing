"""
애플리케이션 설정 관리
환경변수 기반 설정 클래스
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # 기본 설정
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # 데이터베이스
    DATABASE_URL: Optional[str] = None
    REDIS_URL: str = "redis://localhost:6379"
    
    # Supabase
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    
    # Google APIs
    GOOGLE_MAPS_API_KEY: Optional[str] = None
    GOOGLE_SEARCH_API_KEY: Optional[str] = None
    GOOGLE_SEARCH_ENGINE_ID: Optional[str] = None
    
    # Naver API
    NAVER_CLIENT_ID: Optional[str] = None
    NAVER_CLIENT_SECRET: Optional[str] = None
    
    # Weather API
    WEATHER_API_KEY: Optional[str] = None
    
    # JWT 설정
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24시간
    
    # Sentry
    SENTRY_DSN: Optional[str] = None
    
    # API 제한
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    MAX_TEXT_LENGTH: int = 10000  # 10,000 characters
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 전역 설정 인스턴스
settings = Settings()