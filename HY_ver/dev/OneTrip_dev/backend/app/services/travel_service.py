"""
여행 계획 생성 서비스
AI 기반 여행 정보 분석 및 계획 생성
"""

import structlog
from typing import List, Optional
from datetime import datetime, date
import uuid
from fastapi import UploadFile

from app.models.travel_simple import (
    TravelPlanRequest, TravelPlanResponse, TravelStyle,
    SimpleDayPlan, SimpleActivity, SimpleLocation, SimpleRecommendation
)
from app.services.openai_service import OpenAIService
from app.services.file_service import FileProcessingService

logger = structlog.get_logger(__name__)


class TravelPlanService:
    """여행 계획 생성 서비스"""
    
    def __init__(self):
        self.logger = logger.bind(service="TravelPlanService")
        self.openai_service = OpenAIService()
        self.file_service = FileProcessingService()
    
    async def create_travel_plan(
        self, 
        request: TravelPlanRequest
    ) -> TravelPlanResponse:
        """
        여행 계획을 생성합니다.
        
        Args:
            request: 여행 계획 요청 데이터
            
        Returns:
            TravelPlanResponse: 생성된 여행 계획
        """
        start_time = datetime.utcnow()
        plan_id = str(uuid.uuid4())
        
        self.logger.info("여행 계획 생성 시작", 
                        plan_id=plan_id,
                        travel_style=request.travel_style.value)
        
        try:
            # 1. 여행 정보 파싱 및 분석 (OpenAI 활용)
            parsed_info = await self.openai_service.parse_travel_info(
                request.travel_info, 
                request.travel_style.value
            )
            
            # 2. 파일 처리 (PDF/이미지) - TODO: 추후 구현
            # if request.files:
            #     file_info = await self._process_files(request.files)
            #     parsed_info.update(file_info)
            
            # 3. 여행 스타일에 따른 계획 생성
            travel_plan = await self._generate_travel_plan(
                parsed_info, 
                request.travel_style
            )
            
            # 4. 추천 정보 생성
            recommendations = await self._generate_recommendations(
                parsed_info,
                request.travel_style
            )
            
            # 5. 응답 데이터 구성
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            response = TravelPlanResponse(
                plan_id=plan_id,
                title=f"{parsed_info.get('destination', '여행')} 계획",
                travel_style=request.travel_style,
                summary=f"{request.travel_style.value} 스타일의 AI 맞춤형 여행 계획입니다.",
                destination=parsed_info.get('destination', '알 수 없는 목적지'),
                start_date=parsed_info.get('start_date'),
                end_date=parsed_info.get('end_date'),
                duration=parsed_info.get('duration'),
                daily_plans=travel_plan,
                recommendations=recommendations,
                processing_time=processing_time,
                confidence_score=parsed_info.get('confidence_score', 0.7)
            )
            
            self.logger.info("여행 계획 생성 완료", 
                           plan_id=plan_id,
                           processing_time=processing_time)
            
            return response
            
        except Exception as e:
            self.logger.error("여행 계획 생성 실패", 
                            plan_id=plan_id, 
                            error=str(e))
            raise
    
    # _parse_travel_info 메소드는 OpenAIService로 이동됨
    
    async def process_uploaded_files(self, files: List[UploadFile]) -> str:
        """업로드된 파일들에서 텍스트를 추출합니다."""
        try:
            extracted_text = await self.file_service.process_files(files)
            
            # 파일 타입별 카운트
            pdf_count = sum(1 for f in files if f.content_type == 'application/pdf')
            image_count = sum(1 for f in files if f.content_type and f.content_type.startswith('image/'))
            
            self.logger.info("파일 처리 완료", 
                           file_count=len(files),
                           pdf_count=pdf_count,
                           image_count=image_count,
                           extracted_length=len(extracted_text))
            
            return extracted_text
            
        except Exception as e:
            self.logger.error("파일 처리 실패", error=str(e))
            return ""
    
    async def _generate_travel_plan(
        self, 
        parsed_info: dict, 
        travel_style: TravelStyle
    ) -> List[SimpleDayPlan]:
        """여행 계획을 생성합니다."""
        
        # OpenAI 서비스를 사용하여 실제 여행 계획 생성
        daily_plans = await self.openai_service.generate_travel_plan(
            parsed_info, 
            travel_style.value
        )
        
        self.logger.info("여행 계획 생성 완료", 
                        days=len(daily_plans),
                        travel_style=travel_style.value)
        
        return daily_plans
    
    async def _generate_recommendations(
        self, 
        parsed_info: dict,
        travel_style: TravelStyle
    ) -> dict:
        """추천 정보를 생성합니다."""
        
        # 임시 추천 데이터
        recommendations = {
            "맛집": [
                SimpleRecommendation(
                    id="restaurant_1",
                    title="스키야바시 지로",
                    description="미슐랭 3스타 스시 레스토랑",
                    category="일식",
                    location=SimpleLocation(
                        name="스키야바시 지로",
                        address="도쿄도 주오구 긴자"
                    )
                )
            ],
            "관광지": [
                SimpleRecommendation(
                    id="attraction_1",
                    title="센소지 절",
                    description="도쿄에서 가장 오래된 절",
                    category="문화재",
                    location=SimpleLocation(
                        name="센소지",
                        address="도쿄도 다이토구 아사쿠사"
                    )
                )
            ],
            "쇼핑": [
                SimpleRecommendation(
                    id="shopping_1", 
                    title="시부야 109",
                    description="젊은 패션의 메카",
                    category="쇼핑몰",
                    location=SimpleLocation(
                        name="시부야 109",
                        address="도쿄도 시부야구 시부야"
                    )
                )
            ]
        }
        
        self.logger.info("추천 정보 생성 완료", 
                        categories=list(recommendations.keys()))
        
        return recommendations