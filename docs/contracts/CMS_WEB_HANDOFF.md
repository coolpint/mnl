# CMS ↔ Web Handoff Contract (Thread-B / Thread-D)

Last updated: `2026-03-02`

## 목적
- Thread-B(CMS)와 Thread-D(Public Web)가 동일한 데이터 계약을 기준으로 병렬 개발한다.
- UI 목업 데이터와 실제 CMS 데이터를 교체할 때 코드 충돌을 줄인다.

## Source of Truth
- 편집 원본: `apps/cms-wagtail` (Wagtail Page 모델)
- 공개 웹 노출: `apps/web` (CMS API 우선, 실패 시 로컬 폴백)

참고: 장기 소스 오브 트루스 정책은 master inbox `REQ-20260302-05` 결정에 따름.

## API Base
- `CMS_API_BASE_URL` 환경변수 예시: `http://localhost:8000/api/v1/newsroom`

## Endpoints
1. `GET /articles/?limit=<n>`
- 반환: `{ items: ArticlePayload[], count: number, source: "wagtail" }`
- 기본 정렬: `publishedAt` 내림차순
- 노출 상태: `published`, `published_updated`

2. `GET /articles/<slug>/`
- 반환: `{ item: ArticlePayload, source: "wagtail" }`
- 미존재 시 404

## ArticlePayload
- `id: string` (예: `ART-20260302-001`)
- `slug: string` (발행 후 불변)
- `headline: string`
- `subheadline?: string`
- `summary?: string`
- `section: "economy" | "society" | "policy"`
- `tags?: string[]`
- `reporterId?: string`
- `reporterName?: string`
- `publishedAt?: ISO8601`
- `updatedAt?: ISO8601`
- `editLevel?: "L1" | "L2" | "L3"`
- `correctionNote?: string`
- `imageUrl?: string`
- `imageCaption?: string`
- `body?: string[]`

## 책임 분리
- Thread-B:
  - API 응답 스키마 유지
  - 상태 필터(노출 가능 상태) 보장
  - `slug`/`id` 불변 규칙 보장
- Thread-D:
  - CMS API 우선 fetch + 폴백 전략 유지
  - 필수 필드 누락 시 안전 렌더링
  - SEO 산출물(robots/sitemap/news-sitemap/rss) 반영

## 변경 절차
- 호환성 없는 필드 변경/삭제는 반드시 master inbox에 `OPEN` 등록 후 반영
- 계약 변경 시 이 문서와 `apps/web/lib/content.ts`의 매핑 로직을 동시에 업데이트
