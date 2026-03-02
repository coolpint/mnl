import Link from "next/link";

import { resolveCorrectionArticles } from "@/lib/content";

export default async function CorrectionsPage() {
  const items = await resolveCorrectionArticles();

  return (
    <section className="section-block">
      <h1 className="section-title">정정 및 후속 공지</h1>
      <p className="muted">
        투명성을 위해 수정 레벨 L2/L3 기사를 우선 노출합니다. 논지 변경이 큰 경우
        원문 전면 교체 대신 후속 기사 링크를 권장합니다.
      </p>
      {items.length === 0 ? (
        <p className="empty">현재 등록된 정정 공지가 없습니다.</p>
      ) : (
        <div className="grid">
          {items.map((article) => (
            <article key={article.id} className="grid-main article-card">
              <h3>
                <Link href={`/articles/${article.slug}`}>{article.headline}</Link>
              </h3>
              <p className="card-meta">
                {new Date(article.updatedAt).toLocaleString("ko-KR")} · 수정레벨{" "}
                {article.editLevel}
              </p>
              <p className="card-summary">
                {article.correctionNote ??
                  "수정 내역은 기사 본문의 리비전 이력에 반영되어 있습니다."}
              </p>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
