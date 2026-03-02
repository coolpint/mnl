# Thread-F (Ops/Security/Observability)

## Scope
- 인증/권한 보안(2FA 포함), 비밀키 관리
- 로그/메트릭/알림/백업/복구
- 비용 관측과 경보

## Not In Scope
- 기사 작성/발행 기능 자체 개발
- 포털 XML 포맷 상세

## Current Backlog
- [ ] 공통 로그 필드(request_id/article_id/job_id) 표준화
- [ ] 발행 실패/송고 실패/큐 적체 알림 룰
- [ ] 백업/복구 리허설 문서화

## Decision Log
- `2026-03-02`: 운영 정책 변경은 기능 머지 전 검토 게이트 통과 필요
- `2026-03-02` (Decision): 보안 완화, 감사로그 정책 변경, 운영 우회 정책 변경은 `master` 승인 없이는 진행하지 않음
- `2026-03-02` (Assumption): `master/MASTER_INBOX.md`의 `OPEN` 항목으로 승인 요청과 상태 추적이 가능함
- `2026-03-02` (Risk): `master` 승인 대기 시 긴급 장애 대응 리드타임이 증가할 수 있어 우회 없는 복구 런북 최신 상태 유지가 필요함

## Master Escalation Rule
- 아래 변경은 반드시 `master/MASTER_INBOX.md`에 `OPEN`으로 등록:
  - 보안 정책 완화
  - 감사로그 보존기간 변경
  - 장애시 우회 발행 정책 변경
