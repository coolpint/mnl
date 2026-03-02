import { resolveAllArticles, SITE_URL } from "@/lib/content";

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
  const items = (await resolveAllArticles()).slice(0, 20);
  const now = new Date().toUTCString();

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>머니앤로우 뉴스룸</title>
    <link>${SITE_URL}</link>
    <description>데스크 승인 기반 금융·법률 보도</description>
    <language>ko-KR</language>
    <lastBuildDate>${now}</lastBuildDate>
    ${items
      .map(
        (article) => `
    <item>
      <guid isPermaLink="true">${SITE_URL}/articles/${article.slug}</guid>
      <title>${escapeXml(article.headline)}</title>
      <link>${SITE_URL}/articles/${article.slug}</link>
      <description>${escapeXml(article.summary)}</description>
      <pubDate>${new Date(article.publishedAt).toUTCString()}</pubDate>
    </item>`
      )
      .join("")}
  </channel>
</rss>`;

  return new Response(xml, {
    headers: {
      "Content-Type": "application/xml; charset=utf-8",
      "Cache-Control": "s-maxage=600, stale-while-revalidate=1200"
    }
  });
}
