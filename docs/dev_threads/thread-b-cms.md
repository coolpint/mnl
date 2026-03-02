# Thread-B (CMS)

## Scope
- 기자/데스크/편집책임자/운영/포털관리자 RBAC
- 기사 작성/검토/승인/예약/수정레벨 선택 UI
- 감사로그/리비전 조회

## Not In Scope
- 공개 사이트 렌더링
- 포털 XML 생성

## Current Backlog
- [x] Wagtail CMS 백엔드 스캐폴딩 (`apps/cms-wagtail`)
- [x] RBAC 스캐폴딩 (`reporter`, `desk`, `editor_in_chief`, `ops_admin`, `portal_admin`) + 부트스트랩 커맨드
- [x] `desk_review`/승인/예약/회수 상태 전이 액션(Desk Queue 1차 UI)
- [x] 발행 후 수정 시 L1/L2/L3 선택 강제 (`ArticlePage.clean`)
- [x] 발행 이후 `slug` 잠금(UI/API 검증)
- [x] 기존 Next CMS(`apps/cms`) 의존 제거 (워크스페이스/스크립트/문서)
- [x] Public Web 연동용 읽기 API (`/api/v1/newsroom/articles*`) 추가
- [x] AI 초안 수신 API (`POST /api/v1/newsroom/intake/ai-draft/`) + 멱등키(`external_id`) 적용
- [ ] 리비전 diff/감사로그 고급 필터(작성자/상태/기간)

## Decision Log
### Decisions
- `2026-03-02`: 발행 기사 `slug` 변경 시도는 UI/API 모두 차단한다.
- `2026-03-02`: 승인/예약/회수 액션은 UI 표시 제어와 API 권한 검증을 동시에 적용한다.
- `2026-03-02`: `published`, `published_updated` 상태 기사 저장 시 `L1/L2/L3` 선택을 필수로 한다.
- `2026-03-02`: `L3`는 원기사 본문 직접 수정을 금지하고 신규 기사 발행 + 원기사 연결로만 처리한다.
- `2026-03-02`: RBAC 세부 권한 매트릭스는 `REQ-20260302-04` master 결정 전까지 보수안으로 운용한다.
- `2026-03-02`: Thread-B CMS 구현은 Wagtail(`apps/cms-wagtail`) 기준으로 착수한다.
- `2026-03-02`: Thread-B CMS는 Wagtail 단일 트랙으로 운영하고 `apps/cms`(Next 스켈레톤) 의존을 중단한다.
- `2026-03-02`: AI draft intake 포맷은 `external_id/headline/body` 필수 + `intent(writing|desk_review)`로 고정한다.
- `2026-03-02`: Render 배포 시작 단계에서 `bootstrap_cms_reporter_user`를 실행해 기자 계정을 `reporter` 권한으로 강제한다.
- `2026-03-02`: `scourt` Teams 최종 리포트는 AI 재작성 프롬프트를 적용한 뒤 CMS intake로 `writing` 초안 적재를 기본 경로로 한다.

### Assumptions
- `2026-03-02`: Thread-A 상태머신(`writing -> desk_review -> approved/scheduled -> published`)을 변경 없이 참조한다.
- `2026-03-02`: 역할 집합은 로드맵 기준 5개 역할로 고정하고, 역할 추가/삭제 제안은 master 승인 이후 반영한다.
- `2026-03-02`: 예약 발행 시각은 저장은 UTC, 입력/표시는 `Asia/Seoul` 기준으로 제공한다.
- `2026-03-02`: 편집 상태 전이 권한은 `desk`, `editor_in_chief` 중심으로 우선 구현하고 운영 역할 확장은 master 승인 이후 검토한다.
- `2026-03-02`: Wagtail 도입 시 소스 오브 트루스/API 경계는 `REQ-20260302-05` master 결정 전까지 Thread-B 내부 경계로 운용한다.
- `2026-03-02`: Thread-D 연동 계약은 `docs/contracts/CMS_WEB_HANDOFF.md`를 기준으로 동기화한다.
- `2026-03-02`: Thread-C는 AI 생성 결과를 CMS intake API 계약(`REQ-20260302-07`)에 맞춰 송신한다.
- `2026-03-02`: 배포 환경(Render)에서 `CMS_REPORTER_*` 환경변수로 기자 계정 자격증명을 관리하고 주기적으로 비밀번호를 교체한다.
- `2026-03-02`: `scourt` 원문/요약 품질 편차를 고려해 1차 업로드는 `writing` 상태로만 적재하고 사람 검토 후 `desk_review`로 올린다.

### Risks
- `2026-03-02`: UI 권한 가드만으로는 우회 호출을 막을 수 없어 승인 게이트가 무력화될 수 있다.
  - 대응: API 단 권한/상태 전이 검증을 필수화하고 `403/409/422` 케이스를 명시 테스트한다.
- `2026-03-02`: 예약 발행 시 타임존 해석 오류가 발생하면 오발행/지연 발행 위험이 있다.
  - 대응: 시각 입력 컴포넌트에 타임존 라벨을 고정 표기하고 서버에서 과거 시각을 차단한다.
- `2026-03-02`: L3 플로우가 복잡하면 사용자가 L2로 우회 입력할 가능성이 있다.
  - 대응: L2 저장 시 영향 필드(제목/핵심 수치/핵심 주장) 변경 감지 경고를 추가한다.
- `2026-03-02`: AI 송신 포맷이 스레드별로 분기되면 데스킹 큐 유입이 불안정해질 수 있다.
  - 대응: intake JSON 스키마를 단일 계약으로 문서화하고 변경은 master 승인 절차로 관리한다.
- `2026-03-02`: `CMS_REPORTER_PASSWORD` 미설정 상태로 운영되면 기본 비밀번호가 적용되어 계정 탈취 위험이 커질 수 있다.
  - 대응: Render 대시보드에서 `CMS_REPORTER_PASSWORD`를 즉시 설정/회전하고 배포 후 로그인 검증을 수행한다.
- `2026-03-02`: AI 재작성 단계에서 보도자료 범위를 벗어난 해석/추정이 과도하게 들어갈 위험이 있다.
  - 대응: 프롬프트에 직접 인용/사실 왜곡 금지 규칙을 고정하고, 초기 운영은 `writing` 단계 수동 데스킹을 필수화한다.

## Master Escalation Rule
- 아래 변경은 반드시 `master/MASTER_INBOX.md`에 `OPEN`으로 등록:
  - 권한 역할 추가/삭제
  - 승인 게이트 우회 예외 도입
  - 수정 정책 UX 완화(특히 L3)
