# Thread-C (AI Ingestion/Generation)

## Scope
- 소스 수집, 중복제거, LLM 초안 생성
- CMS `desk_review` 송고
- 근거(citations) 및 프롬프트/모델 버전 추적

## Not In Scope
- 자동 발행
- 포털 직접 송고

## Current Backlog
- [ ] RSS 어댑터 1종 구현
- [ ] 멱등성 키 + 중복 필터
- [ ] 초안 검증기(길이/금칙어/근거 누락) 구현

## Decision Log
- `2026-03-02`: AI 산출물은 무조건 미검증 상태로 저장
- `2026-03-02` [Decision]: Thread-C 송고 범위는 `desk_review`까지로 제한하며 자동발행 제안은 수행하지 않음
- `2026-03-02` [Decision]: citation 필수 규칙 완화는 Thread-C 단독 결정 금지, `master/MASTER_INBOX.md` 정책 승인 필요
- `2026-03-02` [Assumption]: 소스 수집/중복제거/초안 생성/`desk_review` 송고는 Thread-C 단독 실행 책임 범위로 간주
- `2026-03-02` [Risk]: 승인 없는 정책 완화 또는 발행 자동화 제안 시 거버넌스 위반 및 운영 리스크 발생 가능

## Master Escalation Rule
- 아래 변경은 반드시 `master/MASTER_INBOX.md`에 `OPEN`으로 등록:
  - 데스크 승인 없는 자동발행 제안
  - 근거(citation) 필수 규칙 완화
  - 수집 소스 법적/정책 리스크 이슈
