# Thread D: 발행 엔진 + 독자용 웹

## 목표
- 승인/예약된 기사를 빠르게 정적 반영(SSG/ISR)하여 읽기 전용 독자 웹을 제공한다.

## 범위
- Next.js 기사 페이지/목록/섹션 페이지
- SEO 메타(OG, canonical, Schema.org NewsArticle)
- 발행 이벤트 기반 ISR 재생성 트리거
- 404/회수 기사 처리 정책
- 검색/발견 산출물 자동화: `robots.txt`, `sitemap.xml`, `news-sitemap.xml`, `rss.xml`
- 매체 메타: `NewsMediaOrganization` 구조화 데이터

## 제외 범위
- 회원/댓글/구독 기능
- CMS 편집 기능

## 페이지 구성
- 홈(최신/주요 기사)
- 섹션 목록(경제/사회 등)
- 기사 상세
- 검색 결과(선택: 초기엔 DB 검색 API 연동)
- 기자 페이지
- 정정/추후/반론 안내 페이지
- 에러/점검 페이지

## 발행 계약
- 입력: `article.published`, `article.updated`, `article.retracted`
- 처리:
  - `published`: 상세+목록 페이지 재생성
  - `updated`: 상세 캐시 무효화 + 수정 시각 반영
  - `retracted`: 회수 안내 페이지 또는 404 정책 적용

## 작업 항목
1. 페이지 라우팅/레이아웃 구현
2. 기사 API 페칭 계층 구현
3. ISR 훅/온디맨드 재생성 연동
4. SEO 메타 자동 삽입
5. `robots/sitemap/news-sitemap/rss` 자동 생성
6. 회수/정정/반론 표기 정책 반영
7. 성능 최적화(Core Web Vitals 목표 설정)

## 완료 기준 (DoD)
- 승인 기사가 목표 시간 내 사이트 반영
- SEO 필수 태그 누락률 목표 이하
- 회수/정정 표시 정책이 일관되게 동작
- 뉴스 사이트맵은 최근 기사만 반영하고 stale URL이 자동 제거
- 트래픽 급증 시 읽기 성능 유지

## 검토 체크리스트
- 발행 직후 캐시 불일치가 없는가
- 섹션/목록 정렬 기준이 명확한가
- OG 이미지 누락 시 대체 전략이 있는가
- 접근성(헤딩 구조, alt, 키보드 탐색) 기준을 만족하는가
- `headline`, `author`, `datePublished`, `dateModified`, `image` 등 뉴스 구조화 데이터 필수 속성이 누락되지 않는가
