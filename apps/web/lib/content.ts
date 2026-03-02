export type SectionKey = "economy" | "society" | "policy";
export type EditLevel = "L1" | "L2" | "L3";

export type Reporter = {
  id: string;
  name: string;
  title: string;
  bio: string;
};

export type Article = {
  id: string;
  slug: string;
  headline: string;
  subheadline: string;
  summary: string;
  section: SectionKey;
  tags: string[];
  reporterId: string;
  publishedAt: string;
  updatedAt: string;
  editLevel: EditLevel;
  correctionNote?: string;
  imageUrl: string;
  imageCaption: string;
  body: string[];
};

const DEFAULT_SITE_URL = "https://moneynlaw.co.kr";

function normalizeSiteUrl(value: string | undefined): string {
  if (!value) {
    return DEFAULT_SITE_URL;
  }

  const trimmed = value.trim();
  if (!trimmed) {
    return DEFAULT_SITE_URL;
  }

  return trimmed.endsWith("/") ? trimmed.slice(0, -1) : trimmed;
}

export const SITE_URL = normalizeSiteUrl(process.env.NEXT_PUBLIC_SITE_URL);

export const sectionLabel: Record<SectionKey, string> = {
  economy: "경제",
  society: "사회",
  policy: "정책"
};

export const reporters: Reporter[] = [
  {
    id: "han-seo-jin",
    name: "한서진",
    title: "정책금융 수석기자",
    bio: "금융감독, 기업공시, 규제 이슈를 중점 취재합니다."
  },
  {
    id: "kim-dae-ho",
    name: "김대호",
    title: "법원·사법제도 기자",
    bio: "주요 판결과 제도 개편 이슈를 추적합니다."
  },
  {
    id: "ai-desk-01",
    name: "AI 데스크 리포터",
    title: "자동화 초안팀",
    bio: "공개 데이터를 기반으로 초안을 만들고 데스크 검수 후 발행합니다."
  }
];

export const articles: Article[] = [
  {
    id: "ART-20260302-001",
    slug: "fsc-inspection-priority-2026-q2",
    headline: "금융당국, 2분기 공시·내부자 신호 집중 점검",
    subheadline:
      "데스크 승인 브리프에서 상장사 대상 점검 범위와 집행 우선순위를 제시했다.",
    summary:
      "공시 시점과 표현 일관성에 대한 모니터링이 강화된다. 정정 공시가 반복된 기업은 심층 점검 대상이 될 수 있다.",
    section: "policy",
    tags: ["금융당국", "공시", "감독"],
    reporterId: "han-seo-jin",
    publishedAt: "2026-03-02T08:10:00+09:00",
    updatedAt: "2026-03-02T09:25:00+09:00",
    editLevel: "L2",
    correctionNote:
      "09:25 KST 기준 점검 기간 표현을 명확히 하기 위해 제목을 수정했습니다.",
    imageUrl: "/images/mock/policy-watch.svg",
    imageCaption: "서울 금융감독기관 청사 전경. 자료사진.",
    body: [
      "금융당국은 2분기 점검 계획에서 오해를 유발할 수 있는 공시 문구와 비정상적 내부자 신호를 핵심 감독 항목으로 제시했다.",
      "데스크 확인 결과, 점검팀은 내부 의사결정 시점과 실제 공시 시점 사이의 간극을 중점적으로 확인할 예정이다.",
      "시장 참여자들은 공시 일정 예측 가능성이 높아지면 장 개시 전후 변동성이 완화될 수 있다고 평가했다."
    ]
  },
  {
    id: "ART-20260301-004",
    slug: "high-court-ruling-related-party-loans",
    headline: "고법, 특수관계인 대출 분쟁에서 이사회 책임 기준 구체화",
    subheadline:
      "긴급 승인 상황에서도 정보 비대칭 주장만으로 면책되기 어렵다는 취지를 명시했다.",
    summary:
      "시간 제약이 있는 거래라도 반대 의견 기록과 독립 가치평가 자료를 남겨야 한다는 판단이 강조됐다.",
    section: "society",
    tags: ["법원", "지배구조", "책임"],
    reporterId: "kim-dae-ho",
    publishedAt: "2026-03-01T17:20:00+09:00",
    updatedAt: "2026-03-01T17:20:00+09:00",
    editLevel: "L1",
    imageUrl: "/images/mock/court-ruling.svg",
    imageCaption: "서울고등법원 외관. 겨울 오후 촬영.",
    body: [
      "서울고법 재판부는 특수관계인 긴급 대출 승인 과정에서 이사 책임을 판단하는 세부 기준을 제시했다.",
      "재판부는 광범위한 긴급성 주장만으로는 부족하며, 위험 검토와 독립 가격 검증이 문서로 남아야 한다고 봤다.",
      "법조계는 이번 판단 이후 예외 거래에 대한 이사회 의사록 양식이 더욱 엄격해질 것으로 내다봤다."
    ]
  },
  {
    id: "ART-20260301-002",
    slug: "ai-market-brief-kosdaq-midcap-flow",
    headline: "AI 마켓 브리프: 코스닥 중형주로 장 초반 수급 집중",
    subheadline:
      "자동화 초안을 데스크가 재검수해 정책 민감 섹터 쏠림 강도를 추적했다.",
    summary:
      "정책 연동 테마에 거래가 집중됐고 시장 전반 확산은 제한적이었다. 데스크는 단기 과열 경고 문구를 추가했다.",
    section: "economy",
    tags: ["코스닥", "수급", "AI초안"],
    reporterId: "ai-desk-01",
    publishedAt: "2026-03-01T07:30:00+09:00",
    updatedAt: "2026-03-01T08:10:00+09:00",
    editLevel: "L2",
    correctionNote:
      "08:10 KST 기준 중복 집계된 거래 버킷을 제거해 유입 총액을 정정했습니다.",
    imageUrl: "/images/mock/market-flow.svg",
    imageCaption: "장 시작 직후 시장 단말기 화면.",
    body: [
      "장 초반에는 정책 이슈와 연동된 코스닥 중형주로 신규 자금 유입이 집중됐다.",
      "데스크 검수 과정에서 자동화 출력의 중복 버킷을 제거했고, 이에 따라 합산 수치도 함께 조정됐다.",
      "애널리스트들은 정책 뉴스 강도가 완화되면 단일 세션 수급 쏠림은 빠르게 반전될 수 있다고 진단했다."
    ]
  },
  {
    id: "ART-20260228-011",
    slug: "tax-tribunal-guidance-transfer-pricing",
    headline: "조세심판원, 이전가격 입증자료 작성 기준 제시",
    subheadline:
      "의사결정 시점별 기록과 이사회 검토 추적 가능성이 핵심이라고 판단했다.",
    summary:
      "심판원은 내부 메모와 신고 문서의 시간순 정합성을 중점 검토 기준으로 제시했다.",
    section: "policy",
    tags: ["조세", "심판", "이전가격"],
    reporterId: "han-seo-jin",
    publishedAt: "2026-02-28T14:05:00+09:00",
    updatedAt: "2026-02-28T14:05:00+09:00",
    editLevel: "L1",
    imageUrl: "/images/mock/tax-brief.svg",
    imageCaption: "행정심판 심리실 내부.",
    body: [
      "최근 조세심판 결정은 이전가격 분쟁에서 동시대 문서화의 중요성을 한층 강화했다.",
      "심판부는 신고 기록과 이사회 자료를 대조하며, 시점이 명확한 내부 검토 흔적이 판단의 핵심이 될 수 있다고 밝혔다.",
      "실무 현장에서는 연간 신고 마감 전 표준화된 증빙 관리표 도입이 확대될 가능성이 커졌다."
    ]
  }
];

export function getReporterById(id: string): Reporter | undefined {
  return reporters.find((reporter) => reporter.id === id);
}

export function getAllArticles(): Article[] {
  return [...articles].sort(
    (left, right) =>
      new Date(right.publishedAt).getTime() - new Date(left.publishedAt).getTime()
  );
}

export function getArticleBySlug(slug: string): Article | undefined {
  return articles.find((article) => article.slug === slug);
}

export function getArticlesBySection(section: SectionKey): Article[] {
  return getAllArticles().filter((article) => article.section === section);
}

export function getArticlesByReporter(reporterId: string): Article[] {
  return getAllArticles().filter((article) => article.reporterId === reporterId);
}

export function getCorrectionArticles(): Article[] {
  return getAllArticles().filter(
    (article) => article.editLevel !== "L1" || Boolean(article.correctionNote)
  );
}

export function getLatestArticle(): Article | undefined {
  return getAllArticles()[0];
}

export function getNewsSitemapTargets(now: Date = new Date()): Article[] {
  const cutoff = now.getTime() - 48 * 60 * 60 * 1000;
  const list = getAllArticles().filter(
    (article) => new Date(article.publishedAt).getTime() >= cutoff
  );
  return list.length > 0 ? list : getAllArticles().slice(0, 2);
}

export function absoluteArticleUrl(slug: string): string {
  return `${SITE_URL}/articles/${slug}`;
}

type CmsArticlePayload = {
  id: string;
  slug: string;
  status?: string;
  headline: string;
  subheadline?: string;
  summary?: string;
  section: string;
  tags?: string[];
  reporterId?: string;
  reporterName?: string;
  publishedAt?: string;
  updatedAt?: string;
  editLevel?: string;
  correctionNote?: string;
  imageUrl?: string;
  imageCaption?: string;
  body?: string[];
};

function normalizeCmsApiBase(value: string | undefined): string {
  if (!value) {
    return "";
  }
  const trimmed = value.trim();
  if (!trimmed) {
    return "";
  }
  return trimmed.endsWith("/") ? trimmed.slice(0, -1) : trimmed;
}

const CMS_API_BASE_URL = normalizeCmsApiBase(process.env.CMS_API_BASE_URL);
const PUBLIC_WORKFLOW_STATUSES = new Set(["published", "published_updated"]);

function toSection(value: string): SectionKey {
  if (value === "economy" || value === "society" || value === "policy") {
    return value;
  }
  return "policy";
}

function toEditLevel(value?: string): EditLevel {
  if (value === "L1" || value === "L2" || value === "L3") {
    return value;
  }
  return "L1";
}

function toReporterId(value?: string): string {
  if (!value) {
    return "ai-desk-01";
  }
  return value;
}

function isPublicCmsArticle(payload: CmsArticlePayload): boolean {
  if (payload.status) {
    return PUBLIC_WORKFLOW_STATUSES.has(payload.status);
  }
  return Boolean(payload.publishedAt);
}

function normalizeCmsArticle(payload: CmsArticlePayload): Article {
  const publishedAt = payload.publishedAt || payload.updatedAt || new Date().toISOString();
  const updatedAt = payload.updatedAt || publishedAt;

  return {
    id: payload.id,
    slug: payload.slug,
    headline: payload.headline,
    subheadline: payload.subheadline || payload.summary || "",
    summary: payload.summary || payload.subheadline || payload.headline,
    section: toSection(payload.section),
    tags: payload.tags ?? [],
    reporterId: toReporterId(payload.reporterId),
    publishedAt,
    updatedAt,
    editLevel: toEditLevel(payload.editLevel),
    correctionNote: payload.correctionNote || undefined,
    imageUrl: payload.imageUrl || "",
    imageCaption: payload.imageCaption || "",
    body: payload.body && payload.body.length > 0 ? payload.body : [payload.summary || ""]
  };
}

async function fetchCmsArticles(limit = 100): Promise<Article[] | null> {
  if (!CMS_API_BASE_URL) {
    return null;
  }

  try {
    let response = await fetch(
      `${CMS_API_BASE_URL}/articles/?status=published,published_updated&limit=${limit}`,
      {
        next: { revalidate: 60 }
      }
    );
    if (!response.ok) {
      response = await fetch(`${CMS_API_BASE_URL}/articles/?limit=${limit}`, {
        next: { revalidate: 60 }
      });
    }
    if (!response.ok) {
      return null;
    }

    const data = (await response.json()) as { items?: CmsArticlePayload[] };
    const publicItems = (data.items ?? []).filter(isPublicCmsArticle);
    return publicItems.map(normalizeCmsArticle).sort((left, right) => {
      return new Date(right.publishedAt).getTime() - new Date(left.publishedAt).getTime();
    });
  } catch {
    return null;
  }
}

export async function resolveAllArticles(): Promise<Article[]> {
  const remote = await fetchCmsArticles();
  if (remote !== null) {
    return remote;
  }
  return getAllArticles();
}

export async function resolveArticleBySlug(slug: string): Promise<Article | undefined> {
  if (CMS_API_BASE_URL) {
    try {
      const response = await fetch(`${CMS_API_BASE_URL}/articles/${slug}/`, {
        next: { revalidate: 60 }
      });
      if (response.status === 404) {
        return undefined;
      }
      if (response.ok) {
        const data = (await response.json()) as { item?: CmsArticlePayload };
        if (data.item && isPublicCmsArticle(data.item)) {
          return normalizeCmsArticle(data.item);
        }
      }
    } catch {
      // Fallback to local content.
    }
  }
  return getArticleBySlug(slug);
}

export async function resolveArticlesBySection(section: SectionKey): Promise<Article[]> {
  const list = await resolveAllArticles();
  return list.filter((article) => article.section === section);
}

export async function resolveArticlesByReporter(reporterId: string): Promise<Article[]> {
  const list = await resolveAllArticles();
  return list.filter((article) => article.reporterId === reporterId);
}

export async function resolveCorrectionArticles(): Promise<Article[]> {
  const list = await resolveAllArticles();
  return list.filter((article) => article.editLevel !== "L1" || Boolean(article.correctionNote));
}

export async function resolveNewsSitemapTargets(now: Date = new Date()): Promise<Article[]> {
  const list = await resolveAllArticles();
  const cutoff = now.getTime() - 48 * 60 * 60 * 1000;
  const fresh = list.filter((article) => new Date(article.publishedAt).getTime() >= cutoff);
  return fresh.length > 0 ? fresh : list.slice(0, 2);
}
