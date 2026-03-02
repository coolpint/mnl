# Thread-E (Portal Adapters)

## Scope
- 포털별 XML 어댑터(`naver`, `daum`, `google-news-feed`)
- 송고 큐/재시도/응답로그/checksum 기반 재송고 제어
- 수정/회수 우선 처리

## Not In Scope
- CMS 에디터 기능
- 공개 사이트 UI

## Current Backlog
- [ ] 어댑터 인터페이스(`render/validate/send/parse_response`) 구현
- [ ] checksum 동일 시 송고 생략 로직 + `article_portal_states` 갱신
- [ ] 실패 누적 시 송고 정지(서킷 브레이커) + 수동 복구 플로우 구현
- [ ] 포털 필수 필드 매핑표 1차 고정 (`REQ-20260302-03` 결정 후 반영)
- [ ] 재시도 임계치/백오프/쿨다운 수치 반영 (`REQ-20260302-02` 결정 후 반영)

## Decision Log
### Decisions
- `2026-03-02`: 변경 없는 반복 송고 금지, 실패 무한 재송고 금지
- `2026-03-02`: 필수 필드 매핑/재시도 임계치 수치 변경은 `master` 승인 전 반영하지 않음
- `2026-03-02`: `article.updated`, `article.retracted` 이벤트는 일반 발행보다 우선순위 큐로 처리

### Assumptions
- `2026-03-02`: 입력 이벤트 계약(`article.published`, `article.updated`, `article.retracted`)은 Thread-A 기준을 그대로 사용
- `2026-03-02`: 초기 구현은 테스트 송고/샌드박스 경로를 우선 활성화하고 운영 송고는 검증 완료 후 전환

### Risks
- `2026-03-02`: `master`에서 재시도 수치/필수 필드 매핑 결정이 지연되면 통합 검증(샘플 XML, 재시도 시나리오) 일정이 지연될 수 있음
  - 대응: 결정 대기 중에는 인터페이스/큐/체크섬/응답로그 구현을 선행해 정책 의존 영역을 분리
- `2026-03-02`: 포털별 필드 요구사항 차이로 단일 매핑 강제 시 검증 실패 또는 예외 케이스 누락 위험이 있음
  - 대응: 공통 필수 필드와 포털별 확장 필드를 분리한 매핑 구조로 설계

## Master Escalation Rule
- 아래 변경은 반드시 `master/MASTER_INBOX.md`에 `OPEN`으로 등록:
  - 포털별 필수 필드 매핑 변경
  - 재시도 임계치/쿨다운 정책 변경
  - 수정/삭제 반영 SLA 변경
