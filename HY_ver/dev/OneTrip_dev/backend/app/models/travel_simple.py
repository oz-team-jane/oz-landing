"""
간단한 여행 계획 관련 Pydantic 모델 - MVP용
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime, date


class TravelStyle(str, Enum):
    """여행 스타일 열거형"""
    ECONOMIC = "economic"
    LUXURY = "luxury" 
    FAMILY = "family"
    ADVENTURE = "adventure"
    CULTURAL = "cultural"


class TravelPlanRequest(BaseModel):
    """여행 계획 요청"""
    travel_style: TravelStyle = Field(..., description="여행 스타일")
    travel_info: str = Field(..., description="여행 정보 텍스트", max_length=10000)


class SimpleLocation(BaseModel):
    """간단한 위치 정보"""
    name: str = Field(..., description="장소명")
    address: Optional[str] = Field(None, description="주소")


class SimpleActivity(BaseModel):
    """간단한 활동 정보"""
    id: str = Field(..., description="활동 ID")
    title: str = Field(..., description="활동 제목")
    description: Optional[str] = Field(None, description="활동 설명")
    location: SimpleLocation = Field(..., description="위치 정보")
    start_time: Optional[str] = Field(None, description="시작 시간")
    category: str = Field(..., description="활동 카테고리")


class SimpleDayPlan(BaseModel):
    """간단한 일별 계획"""
    date: str = Field(..., description="날짜 (YYYY-MM-DD)")
    day_title: str = Field(..., description="일차 제목")
    activities: List[SimpleActivity] = Field(default=[], description="활동 목록")


class SimpleRecommendation(BaseModel):
    """간단한 추천 정보"""
    id: str = Field(..., description="추천 ID")
    title: str = Field(..., description="추천 제목")
    description: str = Field(..., description="추천 설명")
    category: str = Field(..., description="카테고리")
    location: SimpleLocation = Field(..., description="위치 정보")


class TravelPlanResponse(BaseModel):
    """여행 계획 응답"""
    plan_id: str = Field(..., description="계획 ID")
    title: str = Field(..., description="여행 계획 제목")
    travel_style: TravelStyle = Field(..., description="적용된 여행 스타일")
    summary: str = Field(..., description="여행 계획 요약")
    
    # 여행 기본 정보
    destination: str = Field(..., description="목적지")
    start_date: Optional[str] = Field(None, description="시작 날짜")
    end_date: Optional[str] = Field(None, description="종료 날짜")
    duration: Optional[int] = Field(None, description="여행 기간 (일)")
    
    # 일별 계획
    daily_plans: List[SimpleDayPlan] = Field(default=[], description="일별 계획")
    
    # 추천 리스트
    recommendations: Dict[str, List[SimpleRecommendation]] = Field(
        default={}, 
        description="카테고리별 추천 목록"
    )
    
    # 메타데이터
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="생성 시간")
    processing_time: Optional[float] = Field(None, description="처리 시간 (초)")
    confidence_score: Optional[float] = Field(None, description="신뢰도 점수")