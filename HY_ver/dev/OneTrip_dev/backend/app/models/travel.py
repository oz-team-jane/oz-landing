"""
여행 계획 관련 Pydantic 모델
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from enum import Enum
from datetime import datetime, date

if TYPE_CHECKING:
    from fastapi import UploadFile


class TravelStyle(str, Enum):
    """여행 스타일 열거형"""
    ECONOMIC = "economic"
    LUXURY = "luxury" 
    FAMILY = "family"
    ADVENTURE = "adventure"
    CULTURAL = "cultural"


class Location(BaseModel):
    """위치 정보"""
    name: str = Field(..., description="장소명")
    address: Optional[str] = Field(None, description="주소")
    latitude: Optional[float] = Field(None, description="위도")
    longitude: Optional[float] = Field(None, description="경도")
    category: Optional[str] = Field(None, description="카테고리 (관광지, 맛집, 숙소 등)")


class TimeSlot(BaseModel):
    """시간대 정보"""
    start_time: Optional[str] = Field(None, description="시작 시간 (HH:MM)")
    end_time: Optional[str] = Field(None, description="종료 시간 (HH:MM)")
    duration: Optional[int] = Field(None, description="소요 시간 (분)")


class Activity(BaseModel):
    """활동 정보"""
    id: str = Field(..., description="활동 ID")
    title: str = Field(..., description="활동 제목")
    description: Optional[str] = Field(None, description="활동 설명")
    location: Location = Field(..., description="위치 정보")
    time_slot: TimeSlot = Field(..., description="시간대 정보")
    category: str = Field(..., description="활동 카테고리")
    estimated_cost: Optional[float] = Field(None, description="예상 비용")
    rating: Optional[float] = Field(None, description="평점")
    tips: Optional[List[str]] = Field(None, description="팁 및 주의사항")


class DayPlan(BaseModel):
    """일별 계획"""
    date: date = Field(..., description="날짜")
    day_title: str = Field(..., description="일차 제목")
    activities: List[Activity] = Field(..., description="활동 목록")
    total_distance: Optional[float] = Field(None, description="총 이동 거리 (km)")
    total_duration: Optional[int] = Field(None, description="총 소요 시간 (분)")
    estimated_cost: Optional[float] = Field(None, description="예상 비용")


class Route(BaseModel):
    """경로 정보"""
    from_location: Location = Field(..., description="출발지")
    to_location: Location = Field(..., description="도착지")
    transport_mode: str = Field(..., description="교통수단")
    duration: int = Field(..., description="소요 시간 (분)")
    distance: float = Field(..., description="거리 (km)")
    cost: Optional[float] = Field(None, description="교통비")


class Recommendation(BaseModel):
    """추천 정보"""
    id: str = Field(..., description="추천 ID")
    title: str = Field(..., description="추천 제목")
    description: str = Field(..., description="추천 설명")
    location: Location = Field(..., description="위치 정보")
    category: str = Field(..., description="카테고리")
    rating: Optional[float] = Field(None, description="평점")
    price_range: Optional[str] = Field(None, description="가격대")
    opening_hours: Optional[str] = Field(None, description="운영시간")
    contact: Optional[str] = Field(None, description="연락처")
    website: Optional[str] = Field(None, description="웹사이트")


class TravelPlanRequest(BaseModel):
    """여행 계획 요청"""
    travel_style: TravelStyle = Field(..., description="여행 스타일")
    travel_info: str = Field(..., description="여행 정보 텍스트", max_length=10000)
    # files: Optional[List[UploadFile]] = Field(None, description="첨부 파일들") # TODO: 나중에 구현


class AmbiguityResolution(BaseModel):
    """모호함 해결 정보"""
    question: str = Field(..., description="질문")
    options: List[str] = Field(..., description="선택 옵션들")
    question_type: str = Field(..., description="질문 유형")
    priority: int = Field(..., description="우선순위")


class TravelPlanResponse(BaseModel):
    """여행 계획 응답"""
    plan_id: str = Field(..., description="계획 ID")
    title: str = Field(..., description="여행 계획 제목")
    travel_style: TravelStyle = Field(..., description="적용된 여행 스타일")
    summary: str = Field(..., description="여행 계획 요약")
    
    # 여행 기본 정보
    destination: str = Field(..., description="목적지")
    start_date: Optional[date] = Field(None, description="시작 날짜")
    end_date: Optional[date] = Field(None, description="종료 날짜")
    duration: Optional[int] = Field(None, description="여행 기간 (일)")
    
    # 일별 계획
    daily_plans: List[DayPlan] = Field(..., description="일별 계획")
    
    # 경로 정보
    routes: List[Route] = Field(default=[], description="경로 정보")
    
    # 추천 리스트
    recommendations: Dict[str, List[Recommendation]] = Field(
        default={}, 
        description="카테고리별 추천 목록"
    )
    
    # 예산 정보
    estimated_total_cost: Optional[float] = Field(None, description="총 예상 비용")
    cost_breakdown: Optional[Dict[str, float]] = Field(None, description="비용 구성")
    
    # 추가 정보
    weather_info: Optional[Dict[str, Any]] = Field(None, description="날씨 정보")
    travel_tips: Optional[List[str]] = Field(None, description="여행 팁")
    
    # 모호함 해결
    ambiguities: Optional[List[AmbiguityResolution]] = Field(
        None, 
        description="해결이 필요한 모호한 정보들"
    )
    
    # 메타데이터
    created_at: datetime = Field(default_factory=datetime.utcnow, description="생성 시간")
    processing_time: Optional[float] = Field(None, description="처리 시간 (초)")
    confidence_score: Optional[float] = Field(None, description="신뢰도 점수")