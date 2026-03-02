import { resolveNewsSitemapTargets, SITE_URL } from "@/lib/content";

export const revalidate = 600;

function escapeXml(value: string): string {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&apos;");
}

export async function GET() {
  const items = await resolveNewsSitemapTargets();

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset
  xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
  xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">
  ${items
    .map(
      (article) => `
  <url>
    <loc>${escapeXml(`${SITE_URL}/articles/${article.slug}`)}</loc>
    <news:news>
      <news:publication>
        <news:name>머니앤로우</news:name>
        <news:language>ko</news:language>
      </news:publication>
      <news:publication_date>${article.publishedAt}</news:publication_date>
      <news:title>${escapeXml(article.headline)}</news:title>
    </news:news>
  </url>`
    )
    .join("")}
</urlset>`;

  return new Response(xml, {
    headers: {
      "Content-Type": "application/xml; charset=utf-8",
      "Cache-Control": "s-maxage=600, stale-while-revalidate=1200"
    }
  });
}
