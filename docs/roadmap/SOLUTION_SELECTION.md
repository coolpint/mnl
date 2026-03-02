# 솔루션 선택안 (비용 최소화 우선)

## 결론
- 장기 목표: `Python 중심 자체개발`이 총비용/운영복잡도 측면에서 유리
- 단기 목표: 빠른 시작이 필요하면 일부 OSS를 붙여 MVP 속도를 확보

## 권장 아키텍처 (권장안 A: Python 중심)
- CMS/Workflow API: FastAPI + PostgreSQL
- 백그라운드 잡: Celery(or RQ) + Redis
- 공개 웹: Next.js
- 포털 송고기: FastAPI worker(어댑터 플러그인 구조)
- 파일 저장소: S3 호환(Object Storage)

장점:
- 런타임 2개(Node+Python) 운영 부담 최소화
- 상태머신/송고/감사 로그를 한 코드베이스에서 강제 가능
- AI 파이프라인과 CMS 정책이 분리되지 않아 일관성 유지

단점:
- CMS UI를 직접 구현해야 하므로 초반 개발량 증가

## 대안 (권장안 B: MVP 속도 우선)
- CMS: Strapi
- AI/송고/잡: FastAPI + Redis
- 공개 웹: Next.js

장점:
- 데스크 UI/권한을 빠르게 확보

단점:
- Python + Node 이중 운영
- 상태머신과 수정정책 강제 로직이 분산될 위험

## “직접 개발 vs OSS 재사용” 분리

직접 개발 권장:
- 기사 도메인 모델/상태머신
- 수정정책 L1/L2/L3 강제 로직
- 포털 어댑터/재송고 정책/checksum
- 감사로그/승인 이력/정정-반론 관계 모델

OSS 재사용 권장:
- 에디터: Tiptap or CKEditor
- 관리자 UI 컴포넌트: React 기반 어드민 템플릿
- 이미지 처리: imgproxy/Thumbor 계열
- 모니터링: Prometheus + Grafana + Loki
- 작업 큐: Celery/RQ + Redis

## 비용 절감 우선순위
1. 검색은 초기 Postgres FTS로 시작(외부 검색엔진 도입 지연)
2. AI 모델 라우팅(제목/분류 저비용, 본문만 고성능)
3. 미디어 리사이즈/캐시는 CDN 우선 활용
4. 송고 실패 무한재시도 금지(비용/장애 전파 차단)

## 추천 실행
- Sprint 0~1: 권장안 A 기준으로 코어 모델/상태/API 확정
- Sprint 2: CMS 최소 기능(작성/승인/예약/수정레벨)
- Sprint 3: 공개 웹 + 검색/발견 산출물
- Sprint 4: AI 워커 + 포털 어댑터
