from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.core.management.base import BaseCommand, CommandError


REWRITE_PROMPT = """
당신은 업계 전문가들과 직접 심도있는 논의를 할 수 있는 법조계 관련 전문 지식을 갖춘 베테랑 저널리스트야. 건조하지만 명확한 문장을 쓰는 기자로 유명하고, 번득이는 인사이트를 주는 기사로 명성이 높아.

기사를 작성할 때 반드시 아래의 금지 사항을 배제하고 지향 사항을 준수해야 한다. 전형적인 AI 투를 버리고, '실제 인간 작가'의 감각적인 글쓰기를 구현하라.

1. 절대 금지 사항 (AI Clichéd Patterns)
아래와 같은 유형의 문장과 표현은 절대 사용하지 말 것.
* 인위적인 명언/철학적 마무리: "침묵이 재는 것이다", "삶이란 ~여정이 아닐까", "결국 중요한 것은 ~이다" 식의 작위적인 교훈 금지.
* 추상적 감성/은유 남발: "상처 위에 꽃이 핀다", "계절이 마음을 채운다", "침묵 속에 모든 것이 담겼다", "기억이 발효된다" 등 구체성이 결여된 감성 문장 금지.
* 기계적인 대칭/병렬 구조: "A했기에 B를 알았고, B했기에 A가 되었다", "웃음이 있었고, 눈물이 있었으며..." 식의 반복 패턴 금지.
* 메타 발언/접속사 남발: "이 글에서는", "살펴본 바와 같이", "마지막으로", "결론적으로", "주목할 점은" 등 글의 구조를 노출하는 표현 삭제.
* 불필요한 한자어/격식어: (예: 시사한다, 도출된다, 반면, 제반, 내재되어 있다 등) -> 일상적인 한국어 표현으로 대체할 것.

2. 어휘 교정 가이드 (Vocabulary Guidelines)
AI가 습관적으로 쓰는 단어를 인간의 언어로 바꿀 것.
* 관념어 배제: "의미 있는", "소중한", "따뜻한 온기", "치유", "성장" 등 감정을 직접 명명하는 단어 대신 상황을 묘사할 것.
* 번역투/학술 용어 순화:
  * 이 시점에서 -> 지금
  * 이에 따라 -> 그래서
  * 제공하다/부여하다 -> 주다
  * 활용하다 -> 쓰다
  * 야기되다 -> 생기다
  * 파악하다 -> 알다

핵심 요약: 아름답게 꾸미려 하지 말고, 구체적인 장면(Scene)을 보여주며 투박하더라도 솔직한 문장을 구사할 것.

지금 올린 내용을 기반으로 전문적인 신문기사를 작성해. 분량은 공백 포함 글자 수 3000자를 넘지 않도록 하고, 문체는 평어체로. 외래어 표기는 국립국어원 규칙. 또 숫자를 써야하는 경우는 만 단위로 써. 예를 들어 2억3192만5433원과 같은 표기가 좋아. 숫자에 천단위로 콤마(,)를 찍는 방법은 사용하지 마. 또 '방증하는'이란 표현은 아예 쓰지마. 최대한 구어체로 쉽게 쓰고, 문어체의 어려운 단어는 최소화해줘. 하지만 기사투로 정확하게 끝나는 문장이어야 해. 친구들과 대화하는 것 같은 완전한 구어체는 안 돼.

"법률적으로 볼 때"처럼 법조 전문기자라는 티를 내선 안 돼. 주관이 담긴 내용이 없이 객관적인 문체를 사용해. "인사이트" 식으로 끝에 생각을 붙이는 단락에 제목을 넣는 것도 어색한 형식이야. 인사이트는 별도 표시 없이 자연스럽게 본문에 반영해. 또 돈의 단위와 숫자는 띄어써야해. "100만 달러", "35억7002만 원" 식으로. 하지만 "430원"이나, "9910달러"처럼 숫자 바로 뒤에 돈 단위가 올 땐 붙여서 써.

특히 원래 자료에서 인용을 할 때엔 " " 안에 있는 내용을 그대로 정리해. 영어나 외국어 코멘트일 경우 한국어 번역을 하는 건 좋으나 원문의 뜻을 왜곡하거나 자의적으로 해석하지 않도록 주의해.

또 자료의 내용을 그냥 옮기지 말고 독자에게 인사이트를 줘야 한다는 것을 명심해. 자료의 내용을 보니 앞으로 어떤 변화가 예상된다, 혹은 이런 산업이나 집단이 어떤 영향을 받을 것으로 전망된다, 기존 사례와 비교해 봤을 때 이런 식의 분석이 가능하다, 이런 식의 인사이트를 포함하되, 본문에 자연스럽게 녹여줘.

특히 법률적인 배경지식이나 인사이트를 더해줄 수 있으면 좋아. 이 기사작성은 법률과 경제 전문 매체인 머니앤로(Money and Law)를 위한 것이야. 본 판례와 관련된 최신 뉴스도 찾아보고 해당 기사에서 참조할 수 있는 부분을 반영해. 다만 보도자료에 없고 다른 기사에만 있는 직접 인용 코멘트는 반영하지 마.

반드시 JSON 하나만 출력해:
{
  "headline": "기사 제목",
  "body": "기사 본문(공백 포함 3000자 이하)",
  "summary": "150자 내외 요약"
}
다른 문장이나 코드블록은 추가하지 마.
""".strip()


@dataclass(frozen=True)
class ScourtNotice:
    notice_id: str
    title: str
    posted_date: str
    detail_url: str
    pdf_url: str | None
    content_hash: str
    article_text: str


def _strip_fence(text: str) -> str:
    raw = text.strip()
    if raw.startswith("```"):
        lines = raw.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return raw


def _extract_output_text(payload: dict[str, Any]) -> str:
    output_text = payload.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    chunks: list[str] = []
    for item in payload.get("output", []):
        if not isinstance(item, dict):
            continue
        for content in item.get("content", []):
            if not isinstance(content, dict):
                continue
            if content.get("type") not in {"output_text", "text"}:
                continue
            text_value = content.get("text")
            if isinstance(text_value, dict):
                text_value = text_value.get("value")
            if isinstance(text_value, str) and text_value.strip():
                chunks.append(text_value.strip())
    return "\n".join(chunks).strip()


def _decode_json_or_raise(text: str) -> dict[str, Any]:
    normalized = _strip_fence(text)
    try:
        return json.loads(normalized)
    except json.JSONDecodeError:
        start = normalized.find("{")
        end = normalized.rfind("}")
        if start < 0 or end <= start:
            raise CommandError("OpenAI response is not valid JSON.")
        try:
            return json.loads(normalized[start : end + 1])
        except json.JSONDecodeError as exc:
            raise CommandError(f"OpenAI JSON parse failed: {exc}") from exc


def _http_json(url: str, *, headers: dict[str, str], data: dict[str, Any]) -> dict[str, Any]:
    request = Request(
        url=url,
        method="POST",
        headers=headers,
        data=json.dumps(data).encode("utf-8"),
    )
    try:
        with urlopen(request, timeout=60) as response:
            body = response.read().decode("utf-8")
            return json.loads(body) if body else {}
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise CommandError(f"HTTP {exc.code} from {url}: {detail}") from exc
    except URLError as exc:
        raise CommandError(f"Network error calling {url}: {exc.reason}") from exc


class Command(BaseCommand):
    help = "Rewrite scourt Teams reports into newsroom-style drafts and upload to CMS intake API."

    def add_arguments(self, parser):
        parser.add_argument(
            "--db-path",
            default=os.getenv("SCOURT_DB_PATH", "/Users/air/codes/scourt/data/scourt_news.db"),
            help="Path to scourt sqlite database.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=3,
            help="Max number of latest notices to process when --notice-id is not set.",
        )
        parser.add_argument(
            "--notice-id",
            action="append",
            default=[],
            help="Specific scourt notice_id to process (repeatable).",
        )
        parser.add_argument(
            "--cms-base-url",
            default=os.getenv("CMS_API_BASE_URL", "http://localhost:8000/api/v1/newsroom"),
            help="CMS API base URL.",
        )
        parser.add_argument(
            "--intent",
            default="writing",
            choices=["writing", "desk_review"],
            help="Target workflow intent for intake API.",
        )
        parser.add_argument(
            "--section",
            default="policy",
            choices=["economy", "society", "policy"],
            help="Target newsroom section.",
        )
        parser.add_argument(
            "--reporter-username",
            default=os.getenv("CMS_REPORTER_USERNAME", "판결소식"),
            help="Reporter username to assign in CMS draft.",
        )
        parser.add_argument(
            "--openai-model",
            default=os.getenv("SCOURT_REWRITE_MODEL", "gpt-5-mini"),
            help="OpenAI model for rewrite.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Run rewrite without sending to CMS.",
        )

    def handle(self, *args, **options):
        db_path = Path(options["db_path"]).expanduser()
        if not db_path.exists():
            raise CommandError(f"scourt db not found: {db_path}")

        notices = self._load_notices(
            db_path=db_path,
            notice_ids=options["notice_id"],
            limit=options["limit"],
        )
        if not notices:
            self.stdout.write(self.style.WARNING("No scourt notice rows found."))
            return

        intake_token = os.getenv("CMS_AI_INTAKE_TOKEN", "").strip()
        openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
        dry_run = bool(options["dry_run"])

        if not dry_run and not intake_token:
            raise CommandError("Missing CMS_AI_INTAKE_TOKEN.")
        if not openai_api_key:
            raise CommandError("Missing OPENAI_API_KEY.")

        cms_base_url = options["cms_base_url"].rstrip("/")
        intake_url = f"{cms_base_url}/intake/ai-draft/"
        intent = options["intent"]
        section = options["section"]
        reporter_username = options["reporter_username"]
        openai_model = options["openai_model"]

        for notice in notices:
            rewritten = self._rewrite_notice(notice=notice, openai_api_key=openai_api_key, model=openai_model)
            headline = str(rewritten.get("headline", "")).strip()
            body = str(rewritten.get("body", "")).strip()
            summary = str(rewritten.get("summary", "")).strip()

            if not headline:
                raise CommandError(f"[{notice.notice_id}] rewritten headline is empty.")
            if not body:
                raise CommandError(f"[{notice.notice_id}] rewritten body is empty.")
            if len(body) > 3000:
                body = body[:3000].rstrip()

            external_id = f"scourt-{notice.notice_id}-{notice.content_hash[:12]}"
            source_urls = [notice.detail_url]
            if notice.pdf_url:
                source_urls.append(notice.pdf_url)

            payload = {
                "external_id": external_id,
                "headline": headline,
                "summary": summary,
                "section": section,
                "intent": intent,
                "reporter_username": reporter_username,
                "body": body,
                "source_urls": source_urls,
                "model": {
                    "provider": "openai",
                    "name": openai_model,
                    "prompt_version": "scourt-newsroom-v1-20260302",
                },
                "citations": [],
            }

            if dry_run:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"[DRY RUN] notice_id={notice.notice_id} headline='{headline}' body_len={len(body)}"
                    )
                )
                continue

            response = _http_json(
                intake_url,
                headers={
                    "Content-Type": "application/json",
                    "X-CMS-Token": intake_token,
                },
                data=payload,
            )
            status = "idempotent" if response.get("idempotent") else "created"
            self.stdout.write(
                self.style.SUCCESS(
                    "[{notice_id}] {status} article_id={article_id} slug={slug}".format(
                        notice_id=notice.notice_id,
                        status=status,
                        article_id=response.get("article_id", ""),
                        slug=response.get("slug", ""),
                    )
                )
            )

    def _load_notices(self, *, db_path: Path, notice_ids: list[str], limit: int) -> list[ScourtNotice]:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        try:
            if notice_ids:
                placeholders = ",".join("?" for _ in notice_ids)
                query = f"""
                    SELECT notice_id, title, posted_date, detail_url, pdf_url, content_hash, article_text
                    FROM notices
                    WHERE notice_id IN ({placeholders})
                    ORDER BY CAST(notice_id AS INTEGER) DESC
                """
                rows = conn.execute(query, notice_ids).fetchall()
            else:
                query = """
                    SELECT notice_id, title, posted_date, detail_url, pdf_url, content_hash, article_text
                    FROM notices
                    ORDER BY CAST(notice_id AS INTEGER) DESC
                    LIMIT ?
                """
                rows = conn.execute(query, (max(limit, 1),)).fetchall()
        finally:
            conn.close()

        notices: list[ScourtNotice] = []
        for row in rows:
            notices.append(
                ScourtNotice(
                    notice_id=str(row["notice_id"]),
                    title=str(row["title"]),
                    posted_date=str(row["posted_date"]),
                    detail_url=str(row["detail_url"]),
                    pdf_url=str(row["pdf_url"]) if row["pdf_url"] else None,
                    content_hash=str(row["content_hash"]),
                    article_text=str(row["article_text"]),
                )
            )
        return notices

    def _rewrite_notice(self, *, notice: ScourtNotice, openai_api_key: str, model: str) -> dict[str, Any]:
        user_context = (
            "아래 자료를 기사로 재작성해.\n"
            f"- notice_id: {notice.notice_id}\n"
            f"- posted_date: {notice.posted_date}\n"
            f"- detail_url: {notice.detail_url}\n"
            f"- pdf_url: {notice.pdf_url or '없음'}\n"
            f"- scourt_title: {notice.title}\n\n"
            "[teams_report]\n"
            f"{notice.article_text}\n"
        )

        response_payload = _http_json(
            "https://api.openai.com/v1/responses",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {openai_api_key}",
            },
            data={
                "model": model,
                "input": [
                    {"role": "system", "content": REWRITE_PROMPT},
                    {"role": "user", "content": user_context},
                ],
            },
        )
        output_text = _extract_output_text(response_payload)
        if not output_text:
            raise CommandError(f"[{notice.notice_id}] OpenAI returned empty output.")
        return _decode_json_or_raise(output_text)
