# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OneTrip is an AI-powered travel planning automation web service that analyzes scattered travel information and automatically generates optimized travel plans with route optimization and scheduling.

**Core Concept**: "Bringing scattered travel information together" - Users input unstructured travel data (text, PDFs, images) and receive AI-generated optimized travel itineraries.

**Target Architecture**: Full-stack web application with AI agent integration for natural language processing and travel planning.

## Tech Stack (Planned)

### Frontend
- **Framework**: Next.js 15 (App Router) + TypeScript 5.6+
- **Styling**: Tailwind CSS 4.0 + Shadcn/ui components
- **State Management**: Zustand + TanStack Query v5 (React Query)
- **Maps**: Mapbox GL JS + @vis.gl/react-google-maps
- **Development**: Vite, ESLint + Prettier, Playwright (E2E), Storybook 8
- **Deployment**: Vercel with Vercel Analytics and Sentry monitoring

### Backend
- **Framework**: FastAPI 0.110+ + Python 3.12
- **Database**: PostgreSQL 16 + Redis 7 for caching
- **BaaS**: Supabase for backend services
- **Authentication**: JWT + OAuth2
- **File Processing**: PyPDF2 (PDF parsing), Tesseract OCR (image text extraction), Pillow (image processing)
- **Deployment**: Railway/Fly.io with Docker containerization

### AI Agent System
- **Framework**: LangGraph + LangChain for AI workflow orchestration
- **Models**: GPT-4o (main reasoning), GPT-4o-mini (lightweight tasks)
- **NLP**: spaCy + NLTK + python-dateutil for text processing
- **Memory**: LangGraph Local + Persistent Memory for user context
- **Custom Tools**: Maps, Weather, Search, Calendar, PDF Generator, Context Recommendation

### External APIs
- **AI**: OpenAI API for GPT models
- **Maps**: Google Maps API for location services
- **Search**: Google API + Naver API for real-time travel data
- **Weather**: Weather API for travel condition analysis

## Key Features

### Core Functionality
1. **AI Data Analysis Engine**: Natural language processing of unstructured travel data (text, PDF, images)
2. **Smart Trip Planning**: Route optimization, real-time information integration, personalized recommendations
3. **5 Travel Styles**: Economic, Luxury, Family, Adventure, Cultural with style-specific optimizations
4. **Ambiguity Resolution**: Automatic detection and resolution of incomplete/contradictory information
5. **Real-time Customization**: One-click modification of itineraries with instant route recalculation

### UI/UX Design Principles
- **Minimal Design**: Focus on core functionality, avoid complex menus
- **One-Click UX**: Minimize user interactions to achieve goals
- **3-Panel Layout**: Timeline (left), Map (center), Recommendations (right)
- **Real-time Feedback**: Instant response to user actions

## Development Commands

### Frontend Development
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Run tests
npm run test

# Run E2E tests with Playwright
npm run test:e2e

# Run Storybook
npm run storybook
```

### Backend Development
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start FastAPI development server
uvicorn app.main:app --reload

# Run tests
pytest

# Run with Docker
docker-compose up -dev
```

### AI Agent Development
```bash
# Test LangGraph workflows
python -m app.agents.test_workflow

# Debug with LangSmith
export LANGSMITH_API_KEY=your_key
python -m app.agents.debug_agent
```

## Project Structure

```
OneTrip2/
├── frontend/                 # Next.js frontend application
│   ├── app/                 # Next.js App Router pages
│   ├── components/          # Reusable React components
│   ├── hooks/              # Custom React hooks
│   ├── lib/                # Utility functions
│   ├── stores/             # Zustand stores
│   └── types/              # TypeScript type definitions
├── backend/                 # FastAPI backend application
│   ├── app/
│   │   ├── routers/        # FastAPI route handlers
│   │   ├── services/       # Business logic layer
│   │   ├── models/         # Pydantic models
│   │   ├── utils/          # Utility functions
│   │   └── agents/         # LangGraph AI agents
│   ├── tests/              # Backend tests
│   └── requirements.txt    # Python dependencies
├── docs/                   # Documentation and wireframes
│   ├── index.html         # UX wireframe collection
│   ├── wireframe-main.html
│   ├── wireframe-result.html
│   └── wireframe-ambiguity.html
├── cursor_mdc/             # Project documentation
│   ├── PRD.mdc            # Product Requirements Document
│   ├── 기술 스택.mdc       # Technical stack specifications
│   ├── 시스템 아키텍쳐.mdc  # System architecture
│   └── UX_와이어프레임.md  # UX wireframe documentation
└── images/                 # Project assets
    ├── OneTrip_Logo.png
    └── OneTrip_Logo_tr.png
```

## Development Phases

### MVP Phase
- Basic text input → AI analysis → travel plan generation
- 5 travel style selection
- Simple 3-panel result display
- Google/Naver API integration for real-time search

### Version 1.0
- PDF/image parsing capabilities
- Weather data integration
- Advanced ambiguity resolution system
- Enhanced recommendation engine

### Version 2.0
- Advanced personalization
- Collaboration features (real-time sharing)
- Direct booking integration
- Mobile PWA optimization

## API Integration Notes

### External API Dependencies
- **OpenAI API**: Core AI functionality - budget approximately $300-500/month for MVP
- **Google Maps API**: Mapping and route calculation - use free tier initially
- **Google/Naver APIs**: Real-time travel data - monitor usage costs
- **Weather API**: Travel condition analysis

### Performance Requirements
- **AI Analysis**: <5 seconds response time
- **Concurrent Users**: Support 1,000 simultaneous users
- **File Processing**: Up to 10MB PDF/image files
- **Uptime**: 99.9% service availability

## Security & Compliance
- **Data Encryption**: AES-256 for data transmission and storage
- **Authentication**: OAuth 2.0 implementation
- **Privacy**: GDPR and Korean Personal Information Protection Act compliance
- **API Security**: Rate limiting and CORS policies

## Quality Standards

### Code Quality
- TypeScript strict mode enforcement
- ESLint + Prettier code formatting
- Pydantic models for data validation
- Component-driven development with Storybook
- Test coverage: 80%+ unit tests, 70%+ integration tests

### Performance Targets
- **Load Time**: <3s on 3G, <1s on WiFi
- **Bundle Size**: <500KB initial, <2MB total
- **AI Processing**: <5s analysis time
- **Database**: <200ms API response time

## Business Context

This is a startup project targeting Korean MZ generation (25-35 years old) who value time efficiency and digital convenience. The service aims to reduce travel planning time from 2-3 hours to under 5 minutes through AI automation.

**Success Metrics**:
- MAU: 50,000+ users (6 months)
- User satisfaction: NPS 70+
- AI accuracy: 90%+ parsing success rate
- Business: Monthly revenue 100M KRW (1 year target)

## Current Status

**Project Phase**: MVP 개발 완료, 추가 기능 개발 중
**Available Assets**: 완전한 동작하는 MVP, OpenAI API 통합, 3-패널 결과 화면

### ✅ 완료된 기능
- 프로젝트 초기 설정 (Next.js 15, FastAPI)
- 기본 UI 컴포넌트 (여행 스타일 선택, 정보 입력)
- FastAPI 백엔드 구조 (라우터, 모델, 서비스)
- CORS 설정 및 프론트엔드-백엔드 연동
- OpenAI API 통합 (실제 AI 분석 + fallback 모드)
- 3-패널 결과 화면 (타임라인, 지도, 추천 리스트)
- 완전한 end-to-end 여행 계획 생성 플로우

### 🚧 진행 중인 작업
- 결과 페이지 UI/UX 개선
- Google Maps API 연동

### 📋 예정된 작업
- PDF/이미지 파일 업로드 및 파싱 기능
- 모호함 해결을 위한 대화형 다이얼로그
- 실시간 일정 수정 및 경로 재계산 기능
- 여행 계획 저장 및 공유 기능

The project documentation in `cursor_mdc/` contains comprehensive Korean-language specifications that should guide implementation decisions.

## Rules

- 답변은 항상 한국어로 해줘