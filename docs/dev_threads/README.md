# Dev Threads 운영 가이드

이 디렉터리는 moneynlaw 프로젝트의 병렬 개발 스레드를 운영하기 위한 실행 문서다.

## 목적
- 스레드별 개발/의사결정을 분리
- 공통 계약(API/DB/이벤트) 충돌 시 master에서 최종 결정
- 결정 이력과 변경 사유를 추적 가능하게 유지

## 스레드 문서
- `thread-a-domain.md`
- `thread-b-cms.md`
- `thread-c-ai.md`
- `thread-d-web.md`
- `thread-e-portal.md`
- `thread-f-ops.md`
- `THREAD_START_PROMPTS.md` (새 대화 스레드 시작용)

## Master 문서
- `master/MASTER_INBOX.md`: 스레드가 올리는 결정 요청/충돌 보고
- `master/MASTER_DECISIONS.md`: 최종 결정 기록
- `master/MESSAGE_TEMPLATE.md`: master 업데이트 메시지 템플릿

## 운영 규칙
1. 스레드 내 결정은 해당 `thread-*.md`의 Decision Log에 기록한다.
2. 아래 조건이면 반드시 `master/MASTER_INBOX.md`에 올린다.
   - 공통 스키마/상태머신/API/이벤트 변경
   - 다른 스레드와 충돌 가능성이 있는 설계 변경
   - 운영정책(수정 레벨, URL 불변, 송고 정책) 변경
3. master에서 결정되면 `MASTER_DECISIONS.md`에 `M-XXX`로 기록하고, 각 스레드 문서에 반영한다.
4. `MASTER_INBOX.md` 항목 상태는 `OPEN -> DECIDED -> APPLIED`로 관리한다.
