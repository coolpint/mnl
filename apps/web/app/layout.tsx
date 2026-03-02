import type { Metadata } from "next";
import Link from "next/link";

import { SITE_URL } from "@/lib/content";

import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: "머니앤로우 | 금융·법률 뉴스",
    template: "%s | moneynlaw"
  },
  description:
    "데스크 승인 기반의 금융·법률 뉴스룸. 정정 이력과 수정 내역을 공개합니다.",
  alternates: {
    canonical: "/"
  },
  openGraph: {
    type: "website",
    title: "머니앤로우 | 금융·법률 뉴스",
    description:
      "데스크 승인 기사와 정정/반론 공지 이력을 함께 제공하는 공개 뉴스 웹.",
    url: SITE_URL
  }
};

const newsOrgJsonLd = {
  "@context": "https://schema.org",
  "@type": "NewsMediaOrganization",
  name: "머니앤로우",
  url: SITE_URL,
  correctionsPolicy: `${SITE_URL}/corrections`,
  ethicsPolicy: `${SITE_URL}/about/editorial-policy`,
  masthead: `${SITE_URL}/about`,
  ownershipFundingInfo: `${SITE_URL}/about/ownership`,
  publishingPrinciples: `${SITE_URL}/about/editorial-policy`
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body>
        <div className="shell">
          <header className="top-nav">
            <Link href="/" className="brand">
              moneynlaw newsroom
            </Link>
            <nav className="nav-links" aria-label="Primary">
              <Link href="/section/economy">경제</Link>
              <Link href="/section/society">사회</Link>
              <Link href="/section/policy">정책</Link>
              <Link href="/corrections">정정/반론</Link>
            </nav>
          </header>
          <main>{children}</main>
        </div>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(newsOrgJsonLd) }}
        />
      </body>
    </html>
  );
}
