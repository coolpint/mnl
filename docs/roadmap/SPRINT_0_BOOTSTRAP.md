# Sprint 0 부트스트랩 (2주)

## 목표
- 수동 송고/승인/발행이 가능한 최소 운영 체계를 만든다.
- AI 파이프라인 연결 전, 데이터/상태/배포 기반을 안정화한다.

## 역할 제안
- Platform Lead: 아키텍처/배포/관측성
- Backend Lead: API/DB/상태머신
- CMS Lead: 편집 UI/RBAC
- Frontend Lead: 독자 웹/SEO
- AI Lead: 수집기/생성기 기초

## 주차 계획
### Week 1
- Day 1~2: 리포지토리 구조, 환경변수 표준, DB 마이그레이션 체계
- Day 3~4: Article 상태머신 API + CMS 기본 폼
- Day 5: 승인/발행 이벤트 -> 웹 반영 기초

### Week 2
- Day 6~7: 리비전/감사 로그 + 운영 로그 수집
- Day 8~9: AI 수집기 최소 1개 소스 + 초안 송고 샘플
- Day 10: 통합 점검/버그 수정/릴리즈 체크리스트 확정

## 오늘 바로 시작할 10개 티켓
1. `[A][TASK] PostgreSQL 핵심 테이블 마이그레이션 초안 작성`
2. `[A][TASK] 기사 상태머신 유효성 검사 모듈 구현`
3. `[A][TASK] OpenAPI 1차 문서 생성 (articles/status endpoints)`
4. `[B][TASK] CMS RBAC 스캐폴딩 (reporter/desk/admin)`
5. `[B][TASK] 기사 편집 + desk_review 전환 UI 최소 기능`
6. `[D][TASK] Next.js 기사 상세 페이지 스켈레톤 + SEO 메타 기본`
7. `[D][TASK] published 이벤트 수신 후 ISR 재생성 훅 초안`
8. `[F][TASK] 공통 로그 필드(request_id/article_id/job_id) 미들웨어`
9. `[F][TASK] 알림 기준 초안 (발행 실패/송고 실패/큐 적체)`
10. `[C][TASK] RSS 1개 소스 수집 -> source_items 저장 PoC`

## 동시 검토 루틴
- 매일 15분 스탠드업: blocker/의존성 확인
- 화/금 30분 인터페이스 리뷰:
  - A ↔ B/C/D/E 계약 변경 확인
  - D ↔ E 발행/송고 데이터 정합성 확인
  - F 관측 포인트 누락 확인
- PR 규칙:
  - 계약 변경 PR은 최소 2인 승인
  - 기능 PR은 테스트/문서 없으면 머지 금지

## Sprint 0 완료 기준
- 기자 작성 -> 데스크 승인 -> 발행 -> 독자 웹 노출까지 E2E 동작
- 상태 전이/권한/감사 로그가 일관되게 기록
- 최소 1개 실패 시나리오(발행 실패)에서 알림 동작 확인
