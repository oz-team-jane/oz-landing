"""
여행 계획 관련 API 라우터
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional, List
import structlog

from app.models.travel_simple import TravelPlanRequest, TravelPlanResponse, TravelStyle
from app.services.travel_service import TravelPlanService

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/travel", tags=["travel"])

# 여행 계획 서비스 인스턴스
travel_service = TravelPlanService()

@router.post("/analyze", response_model=TravelPlanResponse)
async def analyze_travel_plan(
    travel_style: TravelStyle,
    travel_info: str = Form(..., description="여행 정보 텍스트"),
    files: Optional[List[UploadFile]] = File(None, description="PDF/이미지 파일들")
):
    """
    여행 정보를 분석하여 최적화된 여행 계획 생성
    
    - **travel_style**: 여행 스타일 (economic, luxury, family, adventure, cultural)
    - **travel_info**: 자유 형식 여행 정보 텍스트
    - **files**: 선택적 PDF/이미지 파일 업로드
    """
    try:
        logger.info("여행 계획 분석 요청", 
                   travel_style=travel_style.value,
                   text_length=len(travel_info),
                   file_count=len(files) if files else 0)
        
        # 업로드된 파일들 처리
        extracted_text = ""
        if files:
            extracted_text = await travel_service.process_uploaded_files(files)
            logger.info("파일 처리 완료", extracted_length=len(extracted_text))
        
        # UTF-8 디코딩 처리
        import urllib.parse
        try:
            decoded_travel_info = urllib.parse.unquote(travel_info, encoding='utf-8')
            if decoded_travel_info != travel_info:
                travel_info = decoded_travel_info
                logger.info("텍스트 디코딩 완료")
        except Exception as e:
            logger.warning("텍스트 디코딩 실패", error=str(e))
        
        # 원본 텍스트와 파일에서 추출한 텍스트 결합
        combined_info = travel_info
        if extracted_text:
            combined_info = f"{travel_info}\n\n[파일에서 추출된 정보]\n{extracted_text}"
        
        # 요청 데이터 구성
        request_data = TravelPlanRequest(
            travel_style=travel_style,
            travel_info=combined_info
        )
        
        # 여행 계획 생성
        travel_plan = await travel_service.create_travel_plan(request_data)
        
        logger.info("여행 계획 생성 완료", plan_id=travel_plan.plan_id)
        
        return travel_plan
        
    except Exception as e:
        logger.error("여행 계획 생성 실패", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="여행 계획 생성 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
        )

@router.get("/styles")
async def get_travel_styles():
    """지원하는 여행 스타일 목록 조회"""
    styles = [
        {
            "id": "economic",
            "name": "경제적",
            "description": "저예산 최적화",
            "icon": "💰"
        },
        {
            "id": "luxury", 
            "name": "럭셔리",
            "description": "프리미엄 서비스 중심",
            "icon": "✨"
        },
        {
            "id": "family",
            "name": "가족",
            "description": "안전성 및 편의성 중심", 
            "icon": "👨‍👩‍👧‍👦"
        },
        {
            "id": "adventure",
            "name": "모험",
            "description": "액티비티 및 체험 중심",
            "icon": "🏔️"
        },
        {
            "id": "cultural",
            "name": "문화",
            "description": "역사 및 문화 유적 중심",
            "icon": "🏛️"
        }
    ]
    
    return JSONResponse({"styles": styles})

@router.get("/plan/{plan_id}")
async def get_travel_plan(plan_id: str):
    """여행 계획 조회"""
    # TODO: 구현 예정
    return JSONResponse({
        "plan_id": plan_id,
        "status": "not_implemented"
    })

@router.post("/analyze/ambiguities")
async def detect_ambiguities(
    travel_style: TravelStyle,
    travel_info: str = Form(..., description="여행 정보 텍스트"),
    files: Optional[List[UploadFile]] = File(None, description="PDF/이미지 파일들")
):
    """
    여행 정보에서 모호한 부분을 감지하고 추가 질문을 생성
    
    - **travel_style**: 여행 스타일
    - **travel_info**: 여행 정보 텍스트
    - **files**: 선택적 파일 업로드
    """
    try:
        logger.info("모호함 감지 요청", 
                   travel_style=travel_style.value,
                   text_length=len(travel_info),
                   file_count=len(files) if files else 0)
        
        # 파일 처리 (파일 업로드 기능 재사용)
        extracted_text = ""
        if files:
            extracted_text = await travel_service.process_uploaded_files(files)
        
        # 텍스트 결합
        combined_info = travel_info
        if extracted_text:
            combined_info = f"{travel_info}\n\n[파일에서 추출된 정보]\n{extracted_text}"
        
        # 여행 정보 파싱
        parsed_info = await travel_service.openai_service.parse_travel_info(
            combined_info, 
            travel_style.value
        )
        
        # 모호함 감지
        ambiguities = await travel_service.openai_service.detect_ambiguities(
            combined_info, 
            parsed_info
        )
        
        response_data = {
            "ambiguities": ambiguities,
            "parsed_info": parsed_info,
            "has_ambiguities": len(ambiguities) > 0,
            "confidence_score": parsed_info.get('confidence_score', 0.7)
        }
        
        logger.info("모호함 감지 완료", 
                   ambiguity_count=len(ambiguities),
                   confidence=parsed_info.get('confidence_score'))
        
        return JSONResponse(response_data)
        
    except Exception as e:
        logger.error("모호함 감지 실패", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="모호함 감지 중 오류가 발생했습니다."
        )

@router.post("/clarify")
async def clarify_travel_info(
    travel_style: str = Form(..., description="여행 스타일"),
    original_info: str = Form(..., description="원본 여행 정보"),
    clarifications: str = Form(..., description="사용자 답변 (JSON 형태)")
):
    """
    사용자의 답변을 받아 여행 정보를 보완하고 최종 계획 생성
    
    - **travel_style**: 여행 스타일
    - **original_info**: 원본 여행 정보
    - **clarifications**: 사용자 답변들
    """
    try:
        import json
        
        # TravelStyle enum으로 변환
        try:
            travel_style_enum = TravelStyle(travel_style)
        except ValueError:
            raise HTTPException(status_code=400, detail="잘못된 여행 스타일입니다.")
        
        logger.info("정보 보완 요청", 
                   travel_style=travel_style_enum.value)
        
        # 사용자 답변 파싱
        try:
            clarification_data = json.loads(clarifications)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="잘못된 답변 형식입니다.")
        
        # 원본 정보와 답변을 결합
        enhanced_info = original_info + "\n\n[추가 정보]\n"
        for qa in clarification_data.get('answers', []):
            enhanced_info += f"Q: {qa.get('question', '')}\nA: {qa.get('answer', '')}\n\n"
        
        # 요청 데이터 구성
        request_data = TravelPlanRequest(
            travel_style=travel_style_enum,
            travel_info=enhanced_info
        )
        
        # 최종 여행 계획 생성
        travel_plan = await travel_service.create_travel_plan(request_data)
        
        logger.info("정보 보완 후 계획 생성 완료", plan_id=travel_plan.plan_id)
        
        return travel_plan
        
    except Exception as e:
        logger.error("정보 보완 실패", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="정보 보완 중 오류가 발생했습니다."
        )

@router.put("/plan/{plan_id}")
async def update_travel_plan(plan_id: str):
    """여행 계획 수정"""
    # TODO: 구현 예정
    return JSONResponse({
        "plan_id": plan_id,
        "status": "not_implemented"
    })