# Thread-D (Public Web)

## Scope
- 독자용 기사/목록/기자 페이지
- `robots.txt`, `sitemap.xml`, `news-sitemap.xml`, `rss.xml`
- NewsArticle/NewsMediaOrganization 구조화 데이터

## Not In Scope
- 관리자 편집 기능
- 포털 전송 제어

## Current Backlog
- [ ] 기사 상세 템플릿 + canonical/OG
- [ ] 뉴스 사이트맵(최근 기사만 반영) 구현
- [ ] 정정/회수/반론 노출 정책 구현

## Decision Log
- `2026-03-02`: 발행/수정/회수 이벤트 기반 ISR 갱신 채택
- `2026-03-02` Decision: canonical 정책 변경은 `master` 승인 전까지 보류하고 기존 정책을 유지한다.
- `2026-03-02` Decision: 회수 기사 표시 정책 변경은 `master` 승인 전까지 보류하고 기존 정책을 유지한다.
- `2026-03-02` Assumption: Thread-D는 기사 노출/SEO/robots/sitemap/news-sitemap/rss/structured data 구현을 우선하며 정책 변경 이슈는 `master/MASTER_INBOX.md` 에스컬레이션으로 처리한다.
- `2026-03-02` Risk: canonical/회수 정책 확정 지연 시 일부 배포 항목(정책 의존 라우팅/메타)이 순차 완료로 밀릴 수 있다.
- `2026-03-02` Assumption: 현재 저장소는 문서 중심(웹 앱 소스 부재)이므로, 코드 구현 전 단계에서 Thread-D는 웹 퍼블리싱 명세/산출물 계약 정의를 선행한다.
- `2026-03-02` Risk: 웹 앱 베이스라인(Next.js 등) 미생성 상태가 지속되면 Thread-D 산출물은 문서화까지만 진행되고 실제 배포 검증은 지연된다.

## Master Escalation Rule
- 아래 변경은 반드시 `master/MASTER_INBOX.md`에 `OPEN`으로 등록:
  - canonical URL 정책 변경
  - 회수 기사 처리 정책(404 vs 안내페이지) 변경
  - 뉴스 사이트맵 범위 규칙 변경
