import type { MetadataRoute } from "next";

import { SITE_URL, reporters, resolveAllArticles, sectionLabel } from "@/lib/content";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const articles = await resolveAllArticles();
  const articleUrls: MetadataRoute.Sitemap = articles.map((article) => ({
    url: `${SITE_URL}/articles/${article.slug}`,
    lastModified: article.updatedAt
  }));

  const sectionUrls: MetadataRoute.Sitemap = Object.keys(sectionLabel).map((key) => ({
    url: `${SITE_URL}/section/${key}`,
    lastModified: new Date().toISOString()
  }));

  const reporterUrls: MetadataRoute.Sitemap = reporters.map((reporter) => ({
    url: `${SITE_URL}/reporters/${reporter.id}`,
    lastModified: new Date().toISOString()
  }));

  return [
    {
      url: SITE_URL,
      lastModified: new Date().toISOString()
    },
    {
      url: `${SITE_URL}/corrections`,
      lastModified: new Date().toISOString()
    },
    ...sectionUrls,
    ...reporterUrls,
    ...articleUrls
  ];
}
