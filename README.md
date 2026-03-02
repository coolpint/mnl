# moneynlaw

AI-assisted newsroom platform bootstrap.

## Workspace
- `apps/web`: public reader-facing web
- `apps/cms-wagtail`: Wagtail-based CMS backend (RBAC/workflow policy enforcement)
- `docs/`: roadmap, policy, and dev-thread operation docs

## Quick Start
1. Install dependencies:
```bash
npm install
```
2. Run public web:
```bash
npm run dev:web
```
Public Web가 CMS 데이터를 우선 참조하도록 하려면:
```bash
CMS_API_BASE_URL=http://localhost:8000/api/v1/newsroom npm run dev:web
```
설정하지 않으면 `apps/web/lib/content.ts`의 로컬 샘플 데이터로 동작한다.

3. Run Wagtail CMS backend:
```bash
cd apps/cms-wagtail
python3 -m venv .venv
. .venv/bin/activate
pip install .
python manage.py makemigrations newsroom
python manage.py migrate
python manage.py bootstrap_cms_rbac
python manage.py bootstrap_cms_site
python manage.py bootstrap_cms_reporter_user --username reporter --password 'ChangeMe123!'
python manage.py bootstrap_cms_demo_users --password 'ChangeMe123!'
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

Alternative (after `.venv` setup):
```bash
npm run cms:setup
npm run cms:migrate
npm run cms:bootstrap-rbac
npm run cms:bootstrap-site
npm run cms:demo-users
npm run cms:run
```

4. Access CMS:
- Admin: `http://localhost:8000/admin/`
- Desk queue custom view: `http://localhost:8000/admin/newsroom/desk-queue/`
- Demo role accounts: `demo_reporter`, `demo_desk`, `demo_editor_in_chief`, `demo_ops_admin`, `demo_portal_admin` (password is what you pass to `bootstrap_cms_demo_users`)

## AI Draft Intake API (v1)
1. Set intake token:
```bash
export CMS_AI_INTAKE_TOKEN='replace-with-strong-token'
```
2. POST AI draft payload:
```bash
curl -X POST 'http://localhost:8000/api/v1/newsroom/intake/ai-draft/' \
  -H 'Content-Type: application/json' \
  -H "X-CMS-Token: ${CMS_AI_INTAKE_TOKEN}" \
  -d '{
    "external_id": "ai-20260302-0001",
    "headline": "AI 초안 제목",
    "summary": "요약 문장",
    "section": "policy",
    "intent": "writing",
    "slug": "optional-custom-slug",
    "reporter_username": "demo_reporter",
    "desk_editor_username": "demo_desk",
    "body": [
      "첫 번째 문단",
      "두 번째 문단"
    ],
    "source_urls": ["https://example.com/source-1"],
    "citations": [{"url": "https://example.com/source-1", "title": "source"}],
    "model": {"provider": "openai", "name": "gpt-5", "prompt_version": "v1"}
  }'
```
3. Response:
- `201`: 신규 초안 생성 (`writing` 또는 `desk_review`)
- `200`: `external_id` 중복으로 기존 초안 반환(멱등)
- `403`: 토큰 오류
- `409`: CMS 홈 미초기화 (`bootstrap_cms_site` 필요)
- `422`: 필수 필드 누락

필수 필드:
- `external_id` (멱등 키)
- `headline`
- `body` (문자열 또는 문자열 배열)

`intent`:
- `writing`: 데스킹 요청 전 상태
- `desk_review`: 데스킹 큐로 바로 투입

## Current Phase
- Phase 1 in progress: web + Wagtail CMS backend
- Backend workflow/API and portal adapters integration in progress

## Deploy (Render Free for CMS)
Repository includes [`render.yaml`](./render.yaml) for `apps/cms-wagtail`.

1. Push this repo to GitHub.
2. In Render, create Blueprint from the repo (auto-detects `render.yaml`).
3. Set required env vars in Render service:
   - `DATABASE_URL` (recommended: Neon free Postgres connection string)
   - `WAGTAILADMIN_BASE_URL` (e.g. `https://<your-service>.onrender.com`)
4. Reporter bootstrap env vars (blueprint defaults):
   - `CMS_REPORTER_USERNAME=reporter`
   - `CMS_REPORTER_EMAIL=reporter@moneynlaw.local`
   - `CMS_REPORTER_PASSWORD` (auto generated secret)
5. After first deploy, open Render Shell and run:
```bash
python manage.py bootstrap_cms_site
python manage.py createsuperuser
```
6. Connect Web to CMS API:
   - Netlify env: `CMS_API_BASE_URL=https://<your-service>.onrender.com/api/v1/newsroom`
