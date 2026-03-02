import type { Metadata } from "next";
import { notFound } from "next/navigation";

import {
  SITE_URL,
  absoluteArticleUrl,
  getReporterById,
  resolveArticleBySlug,
  sectionLabel
} from "@/lib/content";
import { SectionChip } from "@/components/section-chip";

type ArticlePageProps = {
  params: {
    slug: string;
  };
};

function absoluteAssetUrl(path: string): string {
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }

  return `${SITE_URL}${path.startsWith("/") ? path : `/${path}`}`;
}

export async function generateMetadata({ params }: ArticlePageProps): Promise<Metadata> {
  const article = await resolveArticleBySlug(params.slug);
  if (!article) {
    return {
      title: "기사를 찾을 수 없습니다"
    };
  }

  const imageUrl = absoluteAssetUrl(article.imageUrl);

  return {
    title: article.headline,
    description: article.summary,
    alternates: {
      canonical: absoluteArticleUrl(article.slug)
    },
    openGraph: {
      type: "article",
      url: absoluteArticleUrl(article.slug),
      title: article.headline,
      description: article.summary,
      images: [
        {
          url: imageUrl,
          alt: article.imageCaption
        }
      ],
      publishedTime: article.publishedAt,
      modifiedTime: article.updatedAt
    }
  };
}

export default async function ArticlePage({ params }: ArticlePageProps) {
  const article = await resolveArticleBySlug(params.slug);
  if (!article) {
    notFound();
  }

  const reporter = getReporterById(article.reporterId);
  const imageUrl = absoluteAssetUrl(article.imageUrl);

  const newsArticleJsonLd = {
    "@context": "https://schema.org",
    "@type": "NewsArticle",
    headline: article.headline,
    image: [imageUrl],
    datePublished: article.publishedAt,
    dateModified: article.updatedAt,
    author: [
      {
        "@type": "Person",
        name: reporter?.name ?? "moneynlaw 데스크"
      }
    ],
    publisher: {
      "@type": "NewsMediaOrganization",
      name: "moneynlaw",
      url: SITE_URL
    },
    mainEntityOfPage: absoluteArticleUrl(article.slug)
  };

  return (
    <article className="article-shell">
      <SectionChip label={sectionLabel[article.section]} />
      <h1>{article.headline}</h1>
      <p className="article-subheadline">{article.subheadline}</p>
      <p className="card-meta">
        {reporter?.name} · {new Date(article.publishedAt).toLocaleString("ko-KR")}
      </p>
      <p className="card-meta">
        수정 {new Date(article.updatedAt).toLocaleString("ko-KR")} · 수정레벨{" "}
        {article.editLevel}
      </p>
      <p className="card-meta muted">{article.imageCaption}</p>
      {article.correctionNote ? <p className="notice">{article.correctionNote}</p> : null}
      <section className="article-body">
        {article.body.map((paragraph, index) => (
          <p key={`${article.id}-${index}`}>{paragraph}</p>
        ))}
      </section>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(newsArticleJsonLd) }}
      />
    </article>
  );
}
