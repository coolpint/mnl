# MASTER INBOX

master 스레드에서 의사결정이 필요한 요청을 모으는 곳.

상태:
- `OPEN`: 결정 대기
- `DECIDED`: master 결정 완료
- `APPLIED`: 스레드 반영 완료

---

## [OPEN][REQ-20260302-01] 계약 레이어 변경 승인 규칙 확정
- from: `Thread-A`
- date: `2026-03-02`
- type: `contract-change`
- affected: `DB schema, API spec, event schema`
- summary: 공통 계약 변경 시 스레드별로 독립 수정할지, master 사전 승인 후 수정할지 확정 필요.
- options:
  1. 스레드 자율 변경 후 사후 동기화
  2. master 사전 승인 후 변경 (권장)
- recommendation: 옵션 2. 초기 단계에서 계약 흔들림을 줄이고 병렬 충돌을 최소화한다.
- decision-needed-by: `2026-03-03`
- links: `docs/roadmap/MASTER_PLAN.md`, `docs/roadmap/threads/THREAD_A_DOMAIN_WORKFLOW.md`

## [OPEN][REQ-20260302-02] 포털 재송고 임계치(재시도 횟수/쿨다운) 수치 확정
- from: `Thread-E`
- date: `2026-03-02`
- type: `policy-change`
- affected: `portal adapter retry policy`
- summary: 무한 재송고 방지 규칙은 확정됐으나, 재시도 횟수/백오프/쿨다운 수치가 미정.
- options:
  1. 보수적: 3회 재시도 + 1시간 쿨다운
  2. 완화: 5회 재시도 + 30분 쿨다운
- recommendation: 옵션 1. 초기 비용/장애 전파 최소화에 유리.
- decision-needed-by: `2026-03-04`
- links: `docs/roadmap/threads/THREAD_E_PORTAL_DELIVERY.md`

## [OPEN][REQ-20260302-03] 포털 필수 필드 매핑 기준(공통/포털별 확장) 확정
- from: `Thread-E`
- date: `2026-03-02`
- type: `contract-change`
- affected: `portal adapters (naver, daum, google-news-feed), XML validator`
- summary: 포털별 필수 필드 매핑이 고정되지 않아 어댑터 검증 기준 확정이 불가함. 공통 필수 필드와 포털별 확장 필드의 분리 기준이 필요함.
- options:
  1. 공통 최소 필드(`title`, `link`, `guid`, `pubDate`, `description`) 1차 고정 + 포털별 확장 필드 분리
  2. 포털별 전체 필드를 초기부터 각각 독립 고정
- recommendation: 옵션 1. 공통 검증/테스트 파이프라인을 재사용하면서 초기 구현 복잡도를 낮출 수 있음.
- decision-needed-by: `2026-03-04`
- links: `docs/dev_threads/thread-e-portal.md`, `docs/roadmap/threads/THREAD_E_PORTAL_DELIVERY.md`

## [OPEN][REQ-20260302-04] CMS RBAC 세부 권한 매트릭스 확정
- from: `Thread-B`
- date: `2026-03-02`
- type: `policy-change`
- affected: `CMS approval/schedule/retract actions, ops_admin/portal_admin action scope`
- summary: 역할 집합은 고정되어 있으나, 액션 단위 권한 매트릭스(특히 `ops_admin`, `portal_admin`의 편집 액션 허용 범위) 확정이 필요함.
- options:
  1. 보수적 분리(권장): 편집 상태 전이는 `desk`, `editor_in_chief`만 수행, `ops_admin`/`portal_admin`은 운영 큐 처리만 허용
  2. 운영 확장: `ops_admin`에 긴급 회수 등 일부 편집 상태 전이 권한 부여
- recommendation: 옵션 1. 승인 게이트 우회 가능성을 줄이고 편집/운영 책임 분리를 유지한다.
- decision-needed-by: `2026-03-04`
- links: `docs/dev_threads/thread-b-cms.md`, `docs/roadmap/threads/THREAD_B_CMS_DESK_REPORTER.md`
