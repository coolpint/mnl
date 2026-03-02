import Link from "next/link";

import {
  getReporterById,
  resolveAllArticles,
  sectionLabel,
  type Article,
  type SectionKey
} from "@/lib/content";

const sectionOrder: SectionKey[] = ["economy", "policy", "society"];

function formatPublishedAt(value: string): string {
  return new Date(value).toLocaleString("ko-KR", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit"
  });
}

function thumbnailSrc(article: Article): string {
  return article.imageUrl || "/images/mock/default-news.svg";
}

export default async function HomePage() {
  const all = await resolveAllArticles();
  const latest = all[0];
  const topHeadlines = all.slice(1, 8);
  const mainCards = all.slice(0, 6);
  const popular = all.slice(0, 10);

  return (
    <div className="portal-home">
      <section className="front-top">
        {latest ? (
          <article className="lead-story">
            <Link href={`/articles/${latest.slug}`} className="lead-media">
              <img src={thumbnailSrc(latest)} alt={latest.imageCaption} loading="eager" />
            </Link>
            <div className="lead-content">
              <p className="lead-kicker">{sectionLabel[latest.section]}</p>
              <h1 className="lead-title">
                <Link href={`/articles/${latest.slug}`}>{latest.headline}</Link>
              </h1>
              <p className="lead-summary">{latest.summary}</p>
              <p className="lead-meta">
                {getReporterById(latest.reporterId)?.name ?? "데스크"} ·{" "}
                {formatPublishedAt(latest.publishedAt)}
              </p>
            </div>
          </article>
        ) : (
          <p className="empty">현재 노출할 메인 기사가 없습니다.</p>
        )}

        <aside className="headline-aside">
          <h2 className="aside-title">주요 헤드라인</h2>
          {topHeadlines.length === 0 ? (
            <p className="empty">추가 헤드라인이 없습니다.</p>
          ) : (
            <ol className="headline-list">
              {topHeadlines.map((article, index) => (
                <li key={article.id}>
                  <span className="headline-no">{index + 1}</span>
                  <div>
                    <p className="headline-section">{sectionLabel[article.section]}</p>
                    <h3>
                      <Link href={`/articles/${article.slug}`}>{article.headline}</Link>
                    </h3>
                    <p className="card-meta">{formatPublishedAt(article.publishedAt)}</p>
                  </div>
                </li>
              ))}
            </ol>
          )}
        </aside>
      </section>

      <section className="news-grid-wrap">
        <div className="news-grid-main">
          <div className="news-grid-head">
            <h2 className="section-title">주요 기사</h2>
            <Link href="/section/policy" className="more-link">
              전체보기
            </Link>
          </div>
          <div className="story-grid">
            {mainCards.map((article) => (
              <article key={article.id} className="story-card">
                <Link href={`/articles/${article.slug}`} className="story-thumb">
                  <img src={thumbnailSrc(article)} alt={article.imageCaption} loading="lazy" />
                </Link>
                <div className="story-text">
                  <p className="headline-section">{sectionLabel[article.section]}</p>
                  <h3>
                    <Link href={`/articles/${article.slug}`}>{article.headline}</Link>
                  </h3>
                  <p className="card-summary">{article.summary}</p>
                  <p className="card-meta">{formatPublishedAt(article.publishedAt)}</p>
                </div>
              </article>
            ))}
          </div>
        </div>

        <aside className="popular-box">
          <div className="news-grid-head">
            <h2 className="section-title">많이 본 뉴스</h2>
          </div>
          <ol className="popular-list">
            {popular.map((article, index) => (
              <li key={`${article.id}-popular`}>
                <span className="popular-rank">{index + 1}</span>
                <Link href={`/articles/${article.slug}`}>{article.headline}</Link>
              </li>
            ))}
          </ol>
        </aside>
      </section>

      <div className="section-rows">
        {sectionOrder.map((section) => {
          const list = all.filter((article) => article.section === section).slice(0, 4);
          const featured = list[0];
          return (
            <section key={section} className="section-block-compact">
              <div className="news-grid-head">
                <h2 className="section-title">{sectionLabel[section]}</h2>
                <Link href={`/section/${section}`} className="more-link">
                  섹션 전체보기
                </Link>
              </div>
              {list.length === 0 ? (
                <p className="empty">섹션 기사가 없습니다.</p>
              ) : (
                <div className="section-compact-body">
                  {featured ? (
                    <Link href={`/articles/${featured.slug}`} className="section-compact-thumb">
                      <img
                        src={thumbnailSrc(featured)}
                        alt={featured.imageCaption}
                        loading="lazy"
                      />
                    </Link>
                  ) : null}
                  <ul className="section-compact-list">
                    {list.map((article) => (
                      <li key={`${section}-${article.id}`}>
                        <Link href={`/articles/${article.slug}`}>{article.headline}</Link>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </section>
          );
        })}
      </div>
    </div>
  );
}
