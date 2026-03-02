import { notFound } from "next/navigation";

import { ArticleCard } from "@/components/article-card";
import { getReporterById, resolveArticlesByReporter } from "@/lib/content";

type ReporterPageProps = {
  params: {
    reporterId: string;
  };
};

export default async function ReporterPage({ params }: ReporterPageProps) {
  const reporter = getReporterById(params.reporterId);
  if (!reporter) {
    notFound();
  }

  const list = await resolveArticlesByReporter(reporter.id);

  return (
    <section className="section-block">
      <h1 className="section-title">{reporter.name}</h1>
      <p className="muted">
        {reporter.title} · {reporter.bio}
      </p>
      {list.length === 0 ? (
        <p className="empty">이 기자의 발행 기사 이력이 아직 없습니다.</p>
      ) : (
        <div className="grid">
          {list.map((article) => (
            <div key={article.id} className="grid-main">
              <ArticleCard article={article} />
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
