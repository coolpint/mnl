import { notFound } from "next/navigation";

import { ArticleCard } from "@/components/article-card";
import { resolveArticlesBySection, sectionLabel, type SectionKey } from "@/lib/content";

type SectionPageProps = {
  params: {
    section: string;
  };
};

function isSectionKey(section: string): section is SectionKey {
  return section in sectionLabel;
}

export default async function SectionPage({ params }: SectionPageProps) {
  if (!isSectionKey(params.section)) {
    notFound();
  }

  const list = await resolveArticlesBySection(params.section);

  return (
    <section className="section-block">
      <h1 className="section-title">{sectionLabel[params.section]}</h1>
      {list.length === 0 ? (
        <p className="empty">이 섹션에 노출된 기사가 아직 없습니다.</p>
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
