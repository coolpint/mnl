# Thread-A (Domain/Workflow)

## Scope
- 기사 원본 스키마, 상태머신, API/이벤트 계약
- 수정정책 L1/L2/L3 강제 규칙

## Not In Scope
- CMS 화면 구현
- 포털 송고 구현

## Current Backlog
- [ ] `articles`, `article_revisions`, `article_relations` DDL 확정
- [ ] 상태 전이 검증 규칙 코드화
- [ ] OpenAPI + 이벤트 스키마 1차 고정

## Decision Log
### Decisions
- `2026-03-02`: 단일 원본 + `article_id/slug` 불변 원칙 적용
- `2026-03-02`: 공통 계약 변경은 `master/MASTER_INBOX.md`에 먼저 `OPEN`으로 등록 후 진행
- `2026-03-02`: 결정 완료 전 계약 파괴적 변경(상태 enum 삭제/이벤트명 변경/URL 정책 파괴)은 머지 금지

### Assumptions
- `2026-03-02`: Thread-A는 도메인 스키마/상태머신/API·이벤트 계약의 단일 기준 문서를 유지한다
- `2026-03-02`: 스레드 간 계약 충돌 조정은 master inbox 합의 프로세스를 통해 해결한다

### Risks
- `2026-03-02`: 공통 계약 결정 지연 시 DDL/OpenAPI/Event 스키마 고정이 지연될 수 있음
  - 대응: `master/MASTER_INBOX.md`에 이슈를 조기 등록하고 마감일/의사결정자를 함께 명시
- `2026-03-02`: 합의 없이 개별 스레드가 계약을 선반영하면 역호환성 이슈가 발생할 수 있음
  - 대응: 파괴적 변경은 합의 전 브랜치에만 유지하고 mainline 머지를 차단

## Master Escalation Rule
- 아래 변경은 반드시 `master/MASTER_INBOX.md`에 `OPEN`으로 등록:
  - status enum 추가/삭제
  - 이벤트명 변경
  - 발행 후 URL 정책 변경
