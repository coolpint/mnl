# 검색/포털 정책 베이스라인 (확인일: 2026-03-02)

이 문서는 설계 고정용 정책 기준이다. 세부 제휴 XML 규격은 계약/파트너 문서가 별도로 필요할 수 있다.

## 1) Naver Search Advisor 기준 (공개 문서)
- robots 파일 제공 권장: 크롤러 제어 및 sitemap 위치 안내
- XML Sitemap 제출/관리 권장
- RSS 피드 지원 및 수집 경로 관리 가능
- 구조화 데이터 형식은 JSON-LD, Microdata, RDFa 지원 안내

참고:
- [네이버 서치어드바이저 - robots.txt](https://searchadvisor.naver.com/guide/seo-basic-robots)
- [네이버 서치어드바이저 - 사이트맵](https://searchadvisor.naver.com/guide/request-feed)
- [네이버 서치어드바이저 - RSS 피드](https://searchadvisor.naver.com/guide/request-rss)
- [네이버 서치어드바이저 - 구조화 데이터 소개](https://searchadvisor.naver.com/guide/structured-data-intro)
- [네이버 서치어드바이저 - 구조화 데이터 문법](https://searchadvisor.naver.com/guide/structured-data-syntax)

## 2) Google Search Central 기준 (공개 문서)
- 뉴스 사이트맵은 최근 기사 중심으로 유지 권장
- News sitemap에서는 일반적으로 최근 2일 이내 URL만 유지 권장
- News sitemap의 `news:news` 엔트리는 1,000개 제한 권장
- 기사 페이지에 `NewsArticle` 구조화 데이터(`headline`, `image`, `datePublished`, `dateModified`, `author`) 권장
- Top stories 노출에 구조화 데이터가 절대 필수는 아니나 권장

참고:
- [Google - Build a sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
- [Google - News Sitemap](https://developers.google.com/search/docs/advanced/sitemaps/news-sitemap)
- [Google - Article structured data](https://developers.google.com/search/docs/appearance/structured-data/article)

## 3) Daum 뉴스검색 제휴 기준 (공개 페이지)
- 제휴 페이지에 `제휴기술가이드`, `송고 XML 테스트` 메뉴 존재
- 위반 사례로 다음 항목 명시:
  - 동일 URL에서 제목/본문 전면 변경
  - 수정/삭제 미반영
  - 변경 없는 반복 송고
  - 실패 상태 반복 송고
- 도메인 변경 시 과거 기사 DB 보존 원칙 명시

참고:
- [Daum 뉴스검색 제휴](https://cp.news.search.daum.net/)

## 4) 설계에 반영된 고정 규칙
- `article_id`/`slug` 발행 후 불변
- 수정 정책 `L1/L2/L3` 강제
- 포털 송고는 어댑터 분리 + checksum 기반 재송고 제어
- 실패 무한 재송고 방지(재시도 한도/쿨다운/수동 개입)
- `retracted/updated` 이벤트 우선 반영

## 5) 확인 필요(비공개/제휴 영역)
- 네이버/다음 제휴 전용 XML 상세 스키마(필수 필드, 코드값, 응답코드)
- 포털별 ping/재수집 트리거 세부 프로토콜
- 정정/삭제 이벤트별 필수 파라미터
