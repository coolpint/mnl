# moneynlaw.co.kr AI 자동화 뉴스룸 마스터 플랜

## 1) 목표
- 엔디소프트 의존도를 단계적으로 제거하고 독립형 뉴스 제작/발행 체계를 구축한다.
- AI가 초안을 생산하고, 인간 데스크가 승인하는 편집 정책을 시스템적으로 강제한다.
- 읽기 전용 독자 서비스(회원/댓글/구독 없음)를 고성능/저비용 구조로 운영한다.

## 2) 스레드 구성 (병렬 개발 단위)
- Thread A: 도메인 모델/워크플로우 계약
- Thread B: CMS(데스크/기자)
- Thread C: AI 인제스트/초안 생성 워커
- Thread D: 발행 엔진 + 독자용 웹
- Thread E: 포털 송고(XML/RSS) 모듈
- Thread F: 운영/보안/관측성

각 스레드 상세는 `docs/roadmap/threads/` 하위 문서를 기준으로 진행한다.

## 3) 스레드 간 선행관계
- A → (B, C, D, E): 상태머신/데이터 계약이 기반
- B ↔ D: 승인/예약 발행 이벤트와 프론트 반영 연동
- C → B: AI 송고 데이터가 CMS 검토 큐로 유입
- D ↔ E: 발행 상태와 XML/RSS 노출 정합성 유지
- F ↔ 전체: 로깅/모니터링/권한/백업은 모든 스레드에 횡단 적용

## 4) 공통 설계 원칙
- 채널 분리 원칙: `CMS(원본/승인)` / `Public Web(노출)` / `Portal Adapter(송고)`를 독립 서비스로 분리
- 단일 원본 원칙: 웹 HTML, RSS, sitemap, 포털 XML은 모두 동일한 기사 원본 레코드에서 파생
- 식별자 고정 원칙: `article_id`와 `slug(canonical URL)`는 발행 이후 불변
- 승인 게이트 강제: `desk_review` 상태 기사는 자동 발행 금지
- 멱등성 보장: 수집/송고/발행 API는 `idempotency_key` 기반 재시도 가능
- 근거 추적성: AI 초안마다 source URL, 수집 시각, 요약 근거 저장
- 감사 가능성: 상태 변경/수정/삭제는 모두 이벤트 로그 기록
- 장애 격리: 수집, 생성, 발행, 송고를 큐/잡 단위로 분리

## 5) 표준 상태머신 (초안)
- `draft`: 초안 생성
- `writing`: 작성중
- `desk_review`: 데스크 검토
- `desk_rework`: 수정요청
- `approved`: 승인완료
- `scheduled`: 예약대기
- `published`: 발행
- `published_updated`: 수정발행
- `retracted`: 비노출/회수
- `archived`: 보관

허용 전이:
- `draft -> writing`
- `writing -> desk_review`
- `desk_review -> desk_rework | approved | scheduled`
- `desk_rework -> writing | desk_review`
- `approved -> published`
- `scheduled -> published | desk_review`
- `published -> published_updated | retracted | archived`
- `published_updated -> retracted | archived`
- `retracted -> archived`

## 6) 수정 정책 (고정)
- Level 1 (경미): 오탈자/캡션/링크 수정. URL 유지, 버전 증가, 포털 재송고 기본 비활성
- Level 2 (중요): 사실관계/수치/제목 수정. URL 유지, 수정 고지 필수, 포털 업데이트 송고
- Level 3 (중대): 논지/사실관계 대폭 변경. 기존 URL 본문 전면교체 금지, 정정/추후/반론 기사를 신규 발행하고 원기사와 연결

## 7) 일정 제안 (8~10주)
- Sprint 0 (1주): 환경/리포지토리/CI/기본 스키마 준비
- Sprint 1~2 (2~3주): A + 최소 B (수동 발행 가능 상태)
- Sprint 3 (2~3주): D 안정화 (웹 반영, SEO 기본)
- Sprint 4~5 (3~4주): C (AI 자동 초안, 재시도/로그)
- Sprint 6 (2주): E (포털 피드/핑/재송신)
- 지속: F (운영 안정화/비용 최적화)

## 8) 동시 개발/검토 운영 규칙
- 코드 리뷰 SLA: PR 생성 후 24시간 내 1차 리뷰
- 스레드별 주 2회 인터페이스 검토 회의(30분):
  - 계약 변경 여부
  - 장애/리스크 공유
  - 다음 스프린트 의존성 점검
- 스키마/API 변경은 반드시 ADR 또는 RFC 1건 첨부

## 9) 공통 Definition of Ready (DoR)
- 문제 정의/범위/비범위가 문서화됨
- 입력/출력 계약(API, 이벤트, DB 컬럼)이 확정됨
- 테스트 기준(성공/실패/예외)이 정의됨
- 배포/롤백 전략이 명시됨

## 10) 공통 Definition of Done (DoD)
- 기능 구현 + 테스트 + 문서 + 모니터링 항목 반영
- 운영 알람 기준(오류율/지연/누락) 등록
- 감사 로그 및 권한 검토 완료
- QA 시나리오 통과 및 릴리즈 노트 작성
