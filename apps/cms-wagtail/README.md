# mnl-cms-wagtail

Wagtail-based CMS service for the reporter/desk workflow.

## Local setup
1. Create a virtual environment:
```bash
python3 -m venv .venv
. .venv/bin/activate
```
2. Install dependencies:
```bash
pip install .
```
3. Run migrations and bootstrap RBAC groups:
```bash
python manage.py makemigrations newsroom
python manage.py migrate
python manage.py bootstrap_cms_rbac
python manage.py bootstrap_cms_site
python manage.py bootstrap_cms_reporter_user --username reporter --password 'ChangeMe123!'
python manage.py bootstrap_cms_demo_users --password 'ChangeMe123!'
```
4. Create an admin user and run server:
```bash
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

## Access URLs
- Admin: `http://localhost:8000/admin/`
- Desk queue: `http://localhost:8000/admin/newsroom/desk-queue/`
- Public Web handoff API:
  - `http://localhost:8000/api/v1/newsroom/articles/`
  - `http://localhost:8000/api/v1/newsroom/articles/<slug>/`

From repository root you can also run:
```bash
npm run cms:setup
npm run cms:migrate
npm run cms:bootstrap-rbac
npm run cms:bootstrap-site
npm run cms:demo-users
npm run cms:run
```

## AI draft intake format
Endpoint:
- `POST /api/v1/newsroom/intake/ai-draft/`

Headers:
- `Content-Type: application/json`
- `X-CMS-Token: <CMS_AI_INTAKE_TOKEN>`

Required JSON fields:
- `external_id`: idempotency key from AI pipeline
- `headline`
- `body`: string or string array

Optional fields:
- `summary`, `section` (`economy|society|policy`), `slug`
- `intent` (`writing|desk_review`, default `writing`)
- `reporter_username`, `desk_editor_username`
- `source_urls`, `citations`, `model`

Result:
- `201` created
- `200` idempotent replay (same `external_id`)

## Policy guards included
- Published article `slug` immutability.
- `L1/L2/L3` required on published updates.
- `L3` requires creating a new linked article instead of replacing the original body.
- Role-based transition gates for `reporter`, `desk`, `editor_in_chief`, `ops_admin`, `portal_admin`.

## Troubleshooting
### `django.db.utils.OperationalError: no such table: newsroom_newsroomhomepage`
원인: `newsroom` 초기 마이그레이션이 생성/적용되지 않은 상태.

해결:
```bash
. .venv/bin/activate
python manage.py makemigrations newsroom
python manage.py migrate
```

검증:
```bash
sqlite3 db.sqlite3 ".tables" | tr ' ' '\n' | rg '^newsroom_'
```

## Render Free Deploy
`render.yaml` is configured at repo root for this CMS service.

### Required env vars
- `DATABASE_URL`: external Postgres connection string (Neon free 권장)
- `WAGTAILADMIN_BASE_URL`: `https://<service>.onrender.com`

### Default env vars in blueprint
- `DJANGO_DEBUG=0`
- `DJANGO_ALLOWED_HOSTS=.onrender.com`
- `DJANGO_CSRF_TRUSTED_ORIGINS=https://*.onrender.com`
- `DJANGO_SECRET_KEY`: auto generated
- `CMS_REPORTER_USERNAME=reporter`
- `CMS_REPORTER_EMAIL=reporter@moneynlaw.local`
- `CMS_REPORTER_PASSWORD`: auto generated

### Reporter account bootstrap
Render start command runs these automatically on each deploy:
```bash
python manage.py migrate
python manage.py bootstrap_cms_rbac
python manage.py bootstrap_cms_reporter_user ...
```

Default fallback credentials if `CMS_REPORTER_PASSWORD` is unset:
```text
username: reporter
password: ChangeMe123!
```

### Optional first-run bootstrap (Render Shell)
```bash
python manage.py bootstrap_cms_site
python manage.py createsuperuser
```

### Notes
- Render Free web instance는 유휴 시 슬립될 수 있어 CMS 응답 지연이 발생할 수 있다.
- 현재 `MEDIA_ROOT`는 로컬 파일시스템 기반이므로 Render 인스턴스 재배포 시 업로드 이미지가 유실될 수 있다.
