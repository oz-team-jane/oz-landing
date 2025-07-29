"""
OpenAI API를 활용한 여행 정보 분석 서비스
"""

import structlog
import json
from typing import Dict, Any, Optional, List
from openai import OpenAI
from app.core.config import settings
from app.models.travel_simple import SimpleDayPlan, SimpleActivity, SimpleLocation

logger = structlog.get_logger(__name__)


class OpenAIService:
    """OpenAI API 서비스"""
    
    def __init__(self):
        self.client = None
        if settings.OPENAI_API_KEY:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info("OpenAI 클라이언트 초기화 완료")
        else:
            logger.warning("OpenAI API 키가 설정되지 않았습니다")
    
    async def parse_travel_info(self, travel_info: str, travel_style: str) -> Dict[str, Any]:
        """
        여행 정보 텍스트를 파싱하여 구조화된 데이터로 변환
        
        Args:
            travel_info: 사용자가 입력한 여행 정보 텍스트
            travel_style: 선택된 여행 스타일
            
        Returns:
            Dict: 파싱된 여행 정보
        """
        if not self.client:
            logger.warning("OpenAI API 키가 없어 기본 파싱 사용")
            return self._fallback_parsing(travel_info)
        
        try:
            system_prompt = self._get_system_prompt(travel_style)
            user_prompt = self._get_user_prompt(travel_info)
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # 비용 효율적인 모델 사용
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # 일관된 결과를 위해 낮은 temperature
                max_tokens=1000
            )
            
            result_text = response.choices[0].message.content
            logger.info("OpenAI API 파싱 완료", tokens_used=response.usage.total_tokens)
            
            # JSON 파싱 시도
            try:
                parsed_result = json.loads(result_text)
                return self._validate_and_clean_result(parsed_result)
            except json.JSONDecodeError as e:
                logger.error("JSON 파싱 실패", error=str(e), response_text=result_text)
                return self._fallback_parsing(travel_info)
                
        except Exception as e:
            logger.error("OpenAI API 호출 실패", error=str(e))
            return self._fallback_parsing(travel_info)
    
    def _get_system_prompt(self, travel_style: str) -> str:
        """여행 스타일에 따른 시스템 프롬프트 생성"""
        
        style_descriptions = {
            "economic": "저예산 최적화에 초점을 맞춘 경제적인 여행",
            "luxury": "프리미엄 서비스와 고급 경험 중심의 럭셔리 여행", 
            "family": "안전성과 편의성을 중시하는 가족 여행",
            "adventure": "액티비티와 체험 활동 중심의 모험적인 여행",
            "cultural": "역사, 문화, 유적지 탐방 중심의 문화 여행"
        }
        
        style_desc = style_descriptions.get(travel_style, "일반적인 여행")
        
        return f"""당신은 전문적인 여행 계획 AI 어시스턴트입니다. 
사용자가 제공한 여행 정보를 분석하여 구조화된 JSON 형태로 변환해주세요.

선택된 여행 스타일: {style_desc}

다음 JSON 형식으로 정확히 응답해주세요:
{{
    "destination": "목적지 (예: 일본 도쿄)",
    "start_date": "시작 날짜 (YYYY-MM-DD 형식, 없으면 null)",
    "end_date": "종료 날짜 (YYYY-MM-DD 형식, 없으면 null)", 
    "duration": "여행 기간 일수 (숫자, 계산 가능하면 계산, 없으면 null)",
    "budget": "예산 정보 (문자열, 없으면 null)",
    "interests": ["관심사 목록", "배열 형태"],
    "transportation": "교통편 정보 (문자열, 없으면 null)",
    "accommodation": "숙소 정보 (문자열, 없으면 null)",
    "special_requirements": "특별 요구사항 (문자열, 없으면 null)",
    "confidence_score": 0.8
}}

주의사항:
- 정확한 JSON 형식만 반환
- 없는 정보는 null로 설정
- 날짜는 반드시 YYYY-MM-DD 형식 사용
- 상대적 날짜 표현은 절대 날짜로 변환 시도"""

    def _get_user_prompt(self, travel_info: str) -> str:
        """사용자 프롬프트 생성"""
        return f"""다음 여행 정보를 분석해서 JSON으로 변환해주세요:

{travel_info}

위 정보를 분석하여 구조화된 JSON 형태로 반환해주세요."""

    def _validate_and_clean_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """파싱 결과 검증 및 정리"""
        
        # 필수 필드 확인
        required_fields = ['destination', 'start_date', 'end_date', 'duration', 'interests']
        for field in required_fields:
            if field not in result:
                result[field] = None
        
        # interests가 리스트가 아니면 빈 리스트로 설정
        if not isinstance(result.get('interests'), list):
            result['interests'] = []
        
        # confidence_score 기본값 설정
        if 'confidence_score' not in result:
            result['confidence_score'] = 0.7
            
        logger.info("파싱 결과 검증 완료", 
                   destination=result.get('destination'),
                   confidence=result.get('confidence_score'))
        
        return result
    
    def _fallback_parsing(self, travel_info: str) -> Dict[str, Any]:
        """OpenAI API 사용 불가 시 기본 파싱"""
        logger.info("기본 파싱 모드 사용")
        
        # URL 디코딩 처리
        import urllib.parse
        try:
            # URL 디코딩 시도
            decoded_text = urllib.parse.unquote(travel_info)
            if decoded_text != travel_info:
                travel_info = decoded_text
                logger.info("URL 디코딩 완료")
        except:
            pass
        
        # 간단한 키워드 기반 파싱
        text_lower = travel_info.lower()
        
        # 목적지 추측 (한국어와 한자/영어 포함)
        destinations = {
            '도쿄': '일본 도쿄', '동경': '일본 도쿄', 'tokyo': '일본 도쿄', '하네다': '일본 도쿄',
            '오사카': '일본 오사카', 'osaka': '일본 오사카',
            '교토': '일본 교토', 'kyoto': '일본 교토',
            '서울': '한국 서울', 'seoul': '한국 서울',
            '부산': '한국 부산', 'busan': '한국 부산',
            '제주': '한국 제주', 'jeju': '한국 제주',
            '파리': '프랑스 파리', 'paris': '프랑스 파리',
            '런던': '영국 런던', 'london': '영국 런던',
            '뉴욕': '미국 뉴욕', 'new york': '미국 뉴욕',
            '방콕': '태국 방콕', 'bangkok': '태국 방콕',
            '싱가포르': '싱가포르', '싱가폴': '싱가포르', 'singapore': '싱가포르',
            '홍콩': '중국 홍콩', 'hong kong': '중국 홍콩',
            '일본': '일본', '한국': '한국', '프랑스': '프랑스', '영국': '영국', '미국': '미국', '태국': '태국'
        }
        
        # 임시로 일본 도쿄를 기본값으로 설정 (UTF-8 인코딩 문제 해결 전까지)
        destination = "일본 도쿄"
        logger.info("목적지 파싱 시도", text_sample=travel_info[:100])
        
        # 원본 텍스트와 소문자 버전 모두에서 검색
        search_texts = [travel_info.lower(), travel_info]
        
        for text in search_texts:
            for key, value in destinations.items():
                if key in text:
                    destination = value
                    logger.info("목적지 발견", keyword=key, destination=value, in_text=text[:50])
                    break
            if destination != "알 수 없는 목적지":
                break
        
        # 관심사 추측
        interests = []
        interest_keywords = {
            '맛집': ['맛집', '음식', '식당', '레스토랑'],
            '쇼핑': ['쇼핑', '구매', '쇼핑몰', '시장'],
            '문화체험': ['문화', '박물관', '미술관', '유적'],
            '자연': ['자연', '산', '바다', '공원'],
            '액티비티': ['액티비티', '체험', '스포츠']
        }
        
        for interest, keywords in interest_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                interests.append(interest)
        
        return {
            'destination': destination,
            'start_date': None,
            'end_date': None,
            'duration': None,
            'budget': None,
            'interests': interests if interests else ['일반 관광'],
            'transportation': None,
            'accommodation': None,
            'special_requirements': None,
            'confidence_score': 0.3  # 기본 파싱의 낮은 신뢰도
        }
    
    async def generate_travel_plan(
        self, 
        parsed_info: Dict[str, Any], 
        travel_style: str
    ) -> List[SimpleDayPlan]:
        """
        파싱된 여행 정보를 바탕으로 상세한 여행 계획 생성
        
        Args:
            parsed_info: 파싱된 여행 정보
            travel_style: 여행 스타일
            
        Returns:
            List[SimpleDayPlan]: 생성된 일별 여행 계획
        """
        if not self.client:
            logger.warning("OpenAI API 키가 없어 기본 계획 생성 사용")
            return self._fallback_plan_generation(parsed_info)
        
        try:
            system_prompt = self._get_plan_system_prompt(travel_style)
            user_prompt = self._get_plan_user_prompt(parsed_info)
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,  # 창의적인 계획을 위해 높은 temperature
                max_tokens=2000
            )
            
            result_text = response.choices[0].message.content
            logger.info("OpenAI API 계획 생성 완료", tokens_used=response.usage.total_tokens)
            
            # JSON 파싱 시도
            try:
                plan_data = json.loads(result_text)
                return self._convert_to_simple_day_plans(plan_data)
            except json.JSONDecodeError as e:
                logger.error("계획 JSON 파싱 실패", error=str(e))
                return self._fallback_plan_generation(parsed_info)
                
        except Exception as e:
            logger.error("OpenAI API 계획 생성 실패", error=str(e))
            return self._fallback_plan_generation(parsed_info)
    
    def _get_plan_system_prompt(self, travel_style: str) -> str:
        """여행 계획 생성을 위한 시스템 프롬프트"""
        
        style_guidelines = {
            "economic": "저예산으로 최대한 많은 경험을 할 수 있는 계획. 무료 관광지, 저렴한 맛집, 대중교통 활용을 중심으로 구성",
            "luxury": "프리미엄 경험과 편안함을 중시하는 계획. 고급 레스토랑, 럭셔리 쇼핑, 프리미엄 서비스 중심",
            "family": "가족 모두가 안전하고 편리하게 즐길 수 있는 계획. 어린이 친화적 장소, 안전한 이동수단 중심",
            "adventure": "스릴 넘치는 체험과 액티비티 중심의 계획. 야외 활동, 익스트림 스포츠, 모험적 경험",
            "cultural": "현지 문화와 역사를 깊이 체험할 수 있는 계획. 박물관, 유적지, 전통 문화 체험 중심"
        }
        
        guideline = style_guidelines.get(travel_style, "일반적인 관광 중심의 계획")
        
        return f"""당신은 전문 여행 가이드입니다. 주어진 여행 정보를 바탕으로 상세한 일별 여행 계획을 작성해주세요.

여행 스타일: {travel_style} - {guideline}

다음 JSON 형식으로 정확히 응답해주세요:
{{
    "daily_plans": [
        {{
            "date": "YYYY-MM-DD",
            "day_title": "1일차 제목",
            "activities": [
                {{
                    "id": "activity_1",
                    "title": "활동 제목",
                    "description": "활동 상세 설명",
                    "location": {{
                        "name": "장소명",
                        "address": "주소"
                    }},
                    "start_time": "HH:MM",
                    "category": "카테고리 (교통, 관광, 맛집, 쇼핑, 숙박 등)"
                }}
            ]
        }}
    ]
}}

주의사항:
- 실제 존재하는 장소와 현실적인 시간 배정
- 이동 시간과 거리를 고려한 효율적인 동선
- 각 활동은 1-3시간 소요 시간 고려
- 식사 시간과 휴식 시간 포함
- 여행 스타일에 맞는 장소와 활동 선택"""

    def _get_plan_user_prompt(self, parsed_info: Dict[str, Any]) -> str:
        """여행 계획 생성을 위한 사용자 프롬프트"""
        
        info_str = f"""
목적지: {parsed_info.get('destination', '미지정')}
시작 날짜: {parsed_info.get('start_date', '미지정')}
종료 날짜: {parsed_info.get('end_date', '미지정')}
여행 기간: {parsed_info.get('duration', '미지정')}일
관심사: {', '.join(parsed_info.get('interests', []))}
예산: {parsed_info.get('budget', '미지정')}
교통편: {parsed_info.get('transportation', '미지정')}
숙소: {parsed_info.get('accommodation', '미지정')}
특별 요구사항: {parsed_info.get('special_requirements', '없음')}
"""
        
        return f"""위 여행 정보를 바탕으로 상세한 일별 여행 계획을 작성해주세요:

{info_str}

현실적이고 실행 가능한 계획으로 작성하되, 각 날짜별로 효율적인 동선과 적절한 시간 배분을 고려해주세요."""

    def _convert_to_simple_day_plans(self, plan_data: Dict[str, Any]) -> List[SimpleDayPlan]:
        """JSON 데이터를 SimpleDayPlan 객체로 변환"""
        
        daily_plans = []
        
        for day_data in plan_data.get('daily_plans', []):
            activities = []
            
            for act_data in day_data.get('activities', []):
                location_data = act_data.get('location', {})
                
                activity = SimpleActivity(
                    id=act_data.get('id', f"activity_{len(activities) + 1}"),
                    title=act_data.get('title', '활동'),
                    description=act_data.get('description'),
                    location=SimpleLocation(
                        name=location_data.get('name', '장소'),
                        address=location_data.get('address')
                    ),
                    start_time=act_data.get('start_time'),
                    category=act_data.get('category', '일반')
                )
                activities.append(activity)
            
            day_plan = SimpleDayPlan(
                date=day_data.get('date', '2024-01-01'),
                day_title=day_data.get('day_title', '여행 일정'),
                activities=activities
            )
            daily_plans.append(day_plan)
        
        return daily_plans
    
    def _fallback_plan_generation(self, parsed_info: Dict[str, Any]) -> List[SimpleDayPlan]:
        """OpenAI API 사용 불가 시 기본 계획 생성"""
        logger.info("기본 계획 생성 모드 사용")
        
        destination = parsed_info.get('destination', '여행지')
        interests = parsed_info.get('interests', ['일반 관광'])
        
        # 목적지별 실제 장소 정보 생성
        specific_locations = self._get_destination_specific_locations(destination, interests)
        
        # 기본 1일차 계획
        activities = []
        
        for i, location_info in enumerate(specific_locations[:3]):  # 최대 3개 활동
            activities.append(SimpleActivity(
                id=f"activity_{i+1}",
                title=location_info['title'],
                description=location_info['description'],
                location=SimpleLocation(
                    name=location_info['name'],
                    address=location_info['address']
                ),
                start_time=location_info['time'],
                category=location_info['category']
            ))
        
        # 관심사에 따른 추가 활동
        if '쇼핑' in interests:
            activities.append(SimpleActivity(
                id="activity_4",
                title="쇼핑 투어",
                description="현지 쇼핑 명소 방문",
                location=SimpleLocation(
                    name="쇼핑 센터",
                    address=f"{destination} 쇼핑가"
                ),
                start_time="16:00",
                category="쇼핑"
            ))
        
        # 날짜가 없는 경우 기본값 설정
        start_date = parsed_info.get('start_date')
        if not start_date:
            # 현재 날짜를 기본값으로 사용
            from datetime import datetime
            start_date = datetime.now().strftime('%Y-%m-%d')
        
        day_plan = SimpleDayPlan(
            date=start_date,
            day_title=f"{destination} 첫째 날",
            activities=activities
        )
        
        return [day_plan]
    
    def _get_destination_specific_locations(self, destination: str, interests: list) -> list:
        """목적지별 실제 장소 정보 생성"""
        
        # 목적지별 실제 장소 매핑
        location_data = {
            '일본 도쿄': [
                {
                    'title': '도쿄역 도착',
                    'description': '도쿄역에 도착하여 여행 시작',
                    'name': '도쿄역',
                    'address': '일본 도쿄도 치요다구 마루노우치 1초메',
                    'time': '10:00',
                    'category': '교통'
                },
                {
                    'title': '센소지 절 방문',
                    'description': '도쿄에서 가장 오래된 절, 아사쿠사의 대표 관광지',
                    'name': '센소지 절',
                    'address': '일본 도쿄도 다이토구 아사쿠사 2-3-1',
                    'time': '14:00',
                    'category': '관광'
                },
                {
                    'title': '도쿄 스카이트리',
                    'description': '도쿄의 랜드마크, 전망대에서 도쿄 전경 감상',
                    'name': '도쿄 스카이트리',
                    'address': '일본 도쿄도 스미다구 오시아게 1-1-2',
                    'time': '16:30',
                    'category': '관광'
                }
            ],
            '한국 서울': [
                {
                    'title': '인천공항 도착',
                    'description': '인천국제공항 도착 후 서울로 이동',
                    'name': '인천국제공항',
                    'address': '인천광역시 중구 공항로 272',
                    'time': '09:00',
                    'category': '교통'
                },
                {
                    'title': '경복궁 관람',
                    'description': '조선왕조의 정궁, 한국의 대표 궁궐',
                    'name': '경복궁',
                    'address': '서울특별시 종로구 사직로 161',
                    'time': '14:00',
                    'category': '문화'
                },
                {
                    'title': '명동 쇼핑',
                    'description': '서울의 대표 쇼핑 거리, 맛집과 쇼핑몰',
                    'name': '명동',
                    'address': '서울특별시 중구 명동길',
                    'time': '17:00',
                    'category': '쇼핑'
                }
            ],
            '프랑스 파리': [
                {
                    'title': '샤를 드골 공항 도착',
                    'description': '파리 샤를 드골 공항 도착',
                    'name': '샤를 드골 공항',
                    'address': 'Roissy-en-France, France',
                    'time': '10:00',
                    'category': '교통'
                },
                {
                    'title': '에펠탑 방문',
                    'description': '파리의 상징, 에펠탑 전망대',
                    'name': '에펠탑',
                    'address': 'Champ de Mars, 5 Avenue Anatole France, 75007 Paris, France',
                    'time': '15:00',
                    'category': '관광'
                },
                {
                    'title': '루브르 박물관',
                    'description': '세계 최대의 박물관, 모나리자 관람',
                    'name': '루브르 박물관',
                    'address': 'Rue de Rivoli, 75001 Paris, France',
                    'time': '17:30',
                    'category': '문화'
                }
            ]
        }
        
        # 기본 장소들
        default_locations = [
            {
                'title': f'{destination} 도착',
                'description': f'{destination}에 도착하여 여행 시작',
                'name': f'{destination} 중심가',
                'address': f'{destination}',
                'time': '10:00',
                'category': '도착'
            },
            {
                'title': '주요 관광지 방문',
                'description': f'{destination}의 대표적인 관광지',
                'name': '관광 명소',
                'address': f'{destination} 관광지',
                'time': '14:00',
                'category': '관광'
            },
            {
                'title': '현지 맛집 체험',
                'description': '현지 유명 맛집에서 식사',
                'name': '현지 맛집',
                'address': f'{destination} 맛집 거리',
                'time': '18:00',
                'category': '맛집'
            }
        ]
        
        # 목적지에 맞는 장소가 있으면 사용, 없으면 기본값 사용
        return location_data.get(destination, default_locations)
    
    async def detect_ambiguities(self, travel_info: str, parsed_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        여행 정보에서 모호하거나 불완전한 부분을 감지하고 질문을 생성합니다.
        
        Args:
            travel_info: 원본 여행 정보 텍스트
            parsed_info: 파싱된 여행 정보
            
        Returns:
            List[Dict]: 감지된 모호함과 관련 질문들
        """
        if not self.client:
            logger.warning("OpenAI API 키가 없어 기본 모호함 감지 사용")
            return self._fallback_ambiguity_detection(parsed_info)
        
        try:
            system_prompt = self._get_ambiguity_detection_prompt()
            user_prompt = self._get_ambiguity_user_prompt(travel_info, parsed_info)
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=1500
            )
            
            result_text = response.choices[0].message.content
            logger.info("모호함 감지 완료", tokens_used=response.usage.total_tokens)
            
            try:
                ambiguities = json.loads(result_text)
                return self._validate_ambiguities(ambiguities)
            except json.JSONDecodeError as e:
                logger.error("모호함 감지 JSON 파싱 실패", error=str(e))
                return self._fallback_ambiguity_detection(parsed_info)
                
        except Exception as e:
            logger.error("모호함 감지 실패", error=str(e))
            return self._fallback_ambiguity_detection(parsed_info)
    
    def _get_ambiguity_detection_prompt(self) -> str:
        """모호함 감지를 위한 시스템 프롬프트"""
        return """당신은 여행 계획 전문가입니다. 사용자가 제공한 여행 정보를 분석하여 모호하거나 불완전한 부분을 찾아 질문을 생성해주세요.

다음과 같은 경우에 모호함으로 판단하세요:
1. 목적지가 너무 광범위하거나 구체적이지 않은 경우
2. 여행 날짜가 명확하지 않은 경우
3. 예산 정보가 없거나 모호한 경우
4. 동행인 정보가 불분명한 경우
5. 교통편이나 숙소 정보가 부족한 경우
6. 관심사나 선호도가 명확하지 않은 경우

다음 JSON 형식으로 응답해주세요:
{
    "ambiguities": [
        {
            "category": "날짜",
            "issue": "구체적인 여행 날짜가 명시되지 않았습니다",
            "question": "구체적인 여행 출발일과 귀국일을 알려주세요.",
            "importance": "high",
            "suggestions": ["3월 15일-18일", "4월 첫째 주", "연휴 기간"]
        }
    ],
    "confidence_impact": "모호함 해결 시 계획 정확도가 20% 향상될 것으로 예상됩니다"
}

중요도는 high, medium, low로 분류하고, 최대 5개까지만 질문하세요."""

    def _get_ambiguity_user_prompt(self, travel_info: str, parsed_info: Dict[str, Any]) -> str:
        """모호함 감지를 위한 사용자 프롬프트"""
        return f"""다음 여행 정보를 분석해서 모호하거나 불완전한 부분을 찾아주세요:

원본 정보:
{travel_info}

파싱된 정보:
- 목적지: {parsed_info.get('destination', '없음')}
- 시작 날짜: {parsed_info.get('start_date', '없음')}
- 종료 날짜: {parsed_info.get('end_date', '없음')}
- 여행 기간: {parsed_info.get('duration', '없음')}일
- 예산: {parsed_info.get('budget', '없음')}
- 관심사: {', '.join(parsed_info.get('interests', []))}
- 교통편: {parsed_info.get('transportation', '없음')}
- 숙소: {parsed_info.get('accommodation', '없음')}
- 특별 요구사항: {parsed_info.get('special_requirements', '없음')}

더 정확한 여행 계획을 위해 어떤 정보가 더 필요한지 분석해주세요."""

    def _validate_ambiguities(self, ambiguities: Dict[str, Any]) -> List[Dict[str, Any]]:
        """모호함 감지 결과 검증"""
        if not isinstance(ambiguities, dict) or 'ambiguities' not in ambiguities:
            return []
        
        validated = []
        for item in ambiguities.get('ambiguities', []):
            if all(key in item for key in ['category', 'issue', 'question', 'importance']):
                validated.append(item)
        
        # 중요도 순으로 정렬 (high -> medium -> low)
        importance_order = {'high': 0, 'medium': 1, 'low': 2}
        validated.sort(key=lambda x: importance_order.get(x.get('importance', 'low'), 2))
        
        return validated[:5]  # 최대 5개까지만
    
    def _fallback_ambiguity_detection(self, parsed_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """OpenAI API 사용 불가 시 기본 모호함 감지"""
        ambiguities = []
        
        # 기본적인 모호함 체크
        if not parsed_info.get('start_date') or not parsed_info.get('end_date'):
            ambiguities.append({
                "category": "날짜",
                "issue": "여행 날짜가 명확하지 않습니다",
                "question": "구체적인 여행 출발일과 귀국일을 알려주세요.",
                "importance": "high",
                "suggestions": ["YYYY-MM-DD 형식으로 입력", "예: 2024-03-15 ~ 2024-03-18"]
            })
        
        if not parsed_info.get('budget'):
            ambiguities.append({
                "category": "예산",
                "issue": "여행 예산 정보가 없습니다",
                "question": "1인당 예상 여행 예산을 알려주세요.",
                "importance": "medium",
                "suggestions": ["50만원 이하", "100만원 정도", "200만원 이상"]
            })
        
        if not parsed_info.get('transportation'):
            ambiguities.append({
                "category": "교통편",
                "issue": "교통편 정보가 부족합니다",
                "question": "주요 교통편(항공편, 기차 등)을 알려주세요.",
                "importance": "medium",
                "suggestions": ["항공편", "KTX/기차", "버스", "자차"]
            })
        
        return ambiguities[:3]  # 기본 감지에서는 최대 3개까지