import Link from "next/link";

import type { Article } from "@/lib/content";
import { getReporterById, sectionLabel } from "@/lib/content";
import { SectionChip } from "@/components/section-chip";

type ArticleCardProps = {
  article: Article;
};

export function ArticleCard({ article }: ArticleCardProps) {
  const reporter = getReporterById(article.reporterId);
  const thumb = article.imageUrl || "/images/mock/default-news.svg";

  return (
    <article className="article-card">
      <Link href={`/articles/${article.slug}`} className="article-thumb">
        <img src={thumb} alt={article.imageCaption} loading="lazy" />
      </Link>
      <div className="card-headline-wrap">
        <SectionChip label={sectionLabel[article.section]} />
        <p className="card-meta">
          {new Date(article.publishedAt).toLocaleString("ko-KR", {
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit"
          })}
        </p>
      </div>
      <h3>
        <Link href={`/articles/${article.slug}`}>{article.headline}</Link>
      </h3>
      <p className="card-summary">{article.summary}</p>
      <p className="card-meta">
        {reporter?.name ?? "데스크"} · 수정레벨 {article.editLevel}
      </p>
    </article>
  );
}
