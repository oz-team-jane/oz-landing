# OneTrip - AI 여행 계획 자동화 서비스

흩어진 여행 정보를 AI가 분석하여 최적화된 여행 계획을 자동으로 생성하는 웹 서비스입니다.

## 🚀 주요 기능

- **AI 기반 여행 정보 분석**: 자유 형식 텍스트, PDF, 이미지 파싱
- **5가지 여행 스타일**: 경제적/럭셔리/가족/모험/문화 맞춤 계획
- **실시간 경로 최적화**: 지도 기반 동선 계산 및 시각화
- **모호함 자동 해결**: 불완전한 정보 탐지 및 대화형 해결
- **원클릭 커스터마이징**: 추천 리스트에서 즉시 일정 수정

## 🛠️ 기술 스택

### Frontend
- Next.js 15 (App Router)
- TypeScript 5.6+
- Tailwind CSS 4.0 + Shadcn/ui
- Zustand + TanStack Query v5
- Mapbox GL JS

### Backend
- FastAPI 0.110+
- Python 3.12
- PostgreSQL 16 + Redis 7
- Supabase

### AI Agent
- LangGraph + LangChain
- GPT-4o + GPT-4o-mini
- spaCy + NLTK

## 🏗️ 프로젝트 구조

```
OneTrip2/
├── frontend/          # Next.js 프론트엔드
├── backend/           # FastAPI 백엔드
├── shared/            # 공통 타입 및 유틸리티
├── docs/              # 문서화 및 와이어프레임
└── cursor_mdc/        # 프로젝트 명세서
```

## 🚀 개발 시작하기

### 프론트엔드
```bash
cd frontend
npm install
npm run dev
```

### 백엔드
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 📋 개발 단계

- [x] 프로젝트 구조 설정
- [ ] Frontend 초기화 (Next.js 15)
- [ ] Backend 초기화 (FastAPI)
- [ ] 기본 UI 구현 (메인 화면)
- [ ] AI Agent 시스템 구축
- [ ] API 통합 및 테스트

## 📚 문서

자세한 프로젝트 명세는 다음 문서를 참조하세요:
- [PRD (제품 요구사항)](./cursor_mdc/PRD.mdc)
- [기술 스택](./cursor_mdc/기술%20스택.mdc)
- [시스템 아키텍처](./cursor_mdc/시스템%20아키텍쳐.mdc)
- [UX 와이어프레임](./cursor_mdc/UX_와이어프레임.md)

## 🎯 목표

**비전**: 여행 계획 시간을 2-3시간에서 5분 이내로 단축하는 AI 자동화 서비스