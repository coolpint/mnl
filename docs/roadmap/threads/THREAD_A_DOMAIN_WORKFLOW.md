# Thread A: 도메인 모델/워크플로우 계약

## 목표
- 전체 시스템이 공유할 기사 생명주기 상태머신, 핵심 엔터티, API/이벤트 계약을 확정한다.

## 범위
- PostgreSQL 스키마 초안 작성
- 상태 전이 규칙 및 권한 규칙 정의
- 서비스 간 API/이벤트 계약 문서화
- 단일 원본/ID-URL 불변/수정 정책 레벨 고정

## 제외 범위
- UI 구현
- AI 프롬프트 고도화
- 포털별 상세 송고 로직 구현

## 원칙 (고정)
- 기사 원본은 1개만 둔다. 공개 HTML/RSS/sitemap/포털 XML은 원본에서 파생한다.
- 발행 후 `article_id`와 `slug`는 변경하지 않는다.
- 발행 기사의 대폭 내용 변경은 Level 3 정책으로 분리 기사 발행 후 관계로 연결한다.

## 핵심 엔터티 (초안)
- `articles`
  - `id`, `slug`, `canonical_url`, `status`, `section`, `title`, `subtitle`, `body_html`, `body_text`
  - `author_type` (`human|ai`), `author_id`, `last_editor_id`, `desk_editor_id`
  - `keywords_json`, `tags_json`, `embargo_at`, `published_at`, `scheduled_at`, `updated_at`, `created_at`
  - `hero_image_url`, `hero_image_caption`, `hero_image_credit`
  - `revision_no`, `is_correction_notice`, `is_followup_notice`, `is_rebuttal_notice`
- `article_revisions`
  - `id`, `article_id`, `version`, `edit_level` (`L1|L2|L3`), `title`, `body_html`, `edited_by`, `edited_at`, `change_note`
- `article_relations`
  - `id`, `parent_article_id`, `child_article_id`, `relation_type` (`correction|followup|rebuttal`)
- `source_items`
  - `id`, `source_type`, `source_url`, `source_hash`, `collected_at`, `raw_payload`
- `ai_drafts`
  - `id`, `article_id`, `model_name`, `prompt_version`, `titles_json`, `category`, `citations_json`
- `publish_jobs`
  - `id`, `article_id`, `job_type`, `status`, `attempt`, `idempotency_key`, `run_at`, `error_message`
- `portal_delivery_logs`
  - `id`, `article_id`, `portal`, `action`, `status`, `request_checksum`, `response_code`, `response_body`, `created_at`
- `article_portal_states`
  - `id`, `article_id`, `portal`, `last_sent_revision`, `last_sent_checksum`, `last_sent_at`, `last_status`
- `audit_events`
  - `id`, `actor_id`, `actor_role`, `entity_type`, `entity_id`, `event_type`, `before_json`, `after_json`, `created_at`

## 상태머신 계약
- 허용 상태: `draft`, `writing`, `desk_review`, `desk_rework`, `approved`, `scheduled`, `published`, `published_updated`, `retracted`, `archived`
- 권한 규칙:
  - 기자(`reporter`): `draft`, `writing`, `desk_review`까지 변경 가능
  - 데스크(`desk`): `desk_rework`, `approved`, `scheduled`, `published_updated`, `retracted` 변경 가능
  - 편집책임자(`editor_in_chief`): 전 상태 변경 가능
  - 포털송고관리자(`portal_admin`): 상태 변경 불가, 송고 재처리만 가능
  - 운영관리자(`ops_admin`): 계정/권한/운영 설정만 가능
  - 시스템 잡: `approved/scheduled -> published`만 가능

## API 계약 (최소)
- `POST /api/articles` 기사 생성
- `PATCH /api/articles/{id}` 기사 수정
- `POST /api/articles/{id}/submit` 데스크 검토 전환
- `POST /api/articles/{id}/approve` 발행 승인
- `POST /api/articles/{id}/schedule` 예약 발행
- `POST /api/articles/{id}/publish` 즉시 발행
- `POST /api/articles/{id}/edit-level` 수정 레벨 지정 (`L1|L2|L3`)
- `POST /api/articles/{id}/retract` 회수
- `POST /api/articles/{id}/archive` 보관
- `GET /api/articles?status=...` 목록 조회

## 이벤트 계약 (예시)
- `article.submitted`
- `article.approved`
- `article.scheduled`
- `article.published`
- `article.updated`
- `article.retracted`
- `article.archived`

payload 필수:
- `event_id`, `occurred_at`, `article_id`, `revision_no`, `status_before`, `status_after`, `idempotency_key`, `content_checksum`

## 수정 정책 계약
- L1: URL 유지, 버전 증가, 포털 송고는 기본 비활성 (정책 옵션으로 허용 가능)
- L2: URL 유지, 수정 고지 필수, 포털 업데이트 송고 의무
- L3: 기존 URL 대폭 내용 교체 금지, 별도 기사 발행 후 `article_relations`로 연결

## 작업 항목
1. ERD 및 컬럼 타입 확정
2. 상태 전이 유효성 검증 로직 설계
3. API OpenAPI 스펙 1차 작성
4. 이벤트 스키마(JSON Schema) 확정
5. 감사 로그 정책 확정

## 완료 기준 (DoD)
- 스키마/상태/권한/API/이벤트 문서가 서로 충돌 없이 정합
- B~F 스레드에서 계약 참조 가능
- 계약 변경 프로세스(ADR/RFC) 문서화 완료

## 검토 체크리스트
- 전이 불가능 상태가 명시적으로 차단되는가
- 회수/정정 시 과거 버전 추적이 가능한가
- `article_id`/`slug` 불변 조건이 강제되는가
- AI/인간 기사 구분 및 책임 추적이 가능한가
- 재시도 시 중복 발행이 방지되는가
- 변경 없는 반복 송고가 checksum으로 차단되는가
