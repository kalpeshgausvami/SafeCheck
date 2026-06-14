// ─── Reel Fact-Check Data Model ───────────────────────────────────────────────

export type FactVerdict = 'TRUE' | 'FALSE' | 'PARTIALLY TRUE' | 'NOT ENOUGH INFORMATION';

export interface FactClaimData {
  reelUrl: string;           // original Instagram Reel URL
  reelId: string;            // short ID extracted from URL
  thumbnailEmoji: string;    // visual stand-in for a reel thumbnail
  claimFound: string;        // the claim extracted from the reel
  claimSummary: string;      // one-line plain-English description of what the reel says
  account: string;           // @handle that posted it
  category: string;
  verdict: FactVerdict;
  reason: string;
  confidenceLabel: string;
  keyFacts: KeyFact[];
  sources: FactSource[];
  tips: string[];
}

export interface KeyFact {
  point: string;
  status: 'confirmed' | 'disputed' | 'unknown';
}

export interface FactSource {
  name: string;
  url: string;
  type: 'government' | 'scientific' | 'news' | 'factcheck';
}

// ─── Example Reel Fact-Check Scenarios ───────────────────────────────────────

export const mockFactData: Record<string, FactClaimData> = {

  // ── FALSE: Lemon water cancer cure ──────────────────────────────────────────
  health: {
    reelUrl: 'https://www.instagram.com/reel/healthFake123/',
    reelId: 'healthFake123',
    thumbnailEmoji: '🍋',
    claimFound: 'Drinking hot lemon water on an empty stomach completely destroys cancer cells. Big Pharma is hiding this cure. Stop chemotherapy — lemons kill cancer in 3 days.',
    claimSummary: 'Reel claims lemon water cures cancer and advises stopping chemotherapy.',
    account: '@natural_health_tips',
    category: 'Health & Medicine',
    verdict: 'FALSE',
    reason: 'There is no scientific or clinical evidence that lemon water destroys cancer cells in any time frame. While lemons contain antioxidants, they cannot alter blood pH in a way that affects tumours. The "Nobel Prize proof" cited in this reel is a well-documented distortion of Otto Warburg\'s 1931 research — which never mentioned lemon water. Advising viewers to stop chemotherapy is medically dangerous and irresponsible.',
    confidenceLabel: 'Very Likely False',
    keyFacts: [
      { point: 'Lemon water has real health benefits (hydration, vitamin C)', status: 'confirmed' },
      { point: 'Lemon water can destroy cancer cells or cure cancer', status: 'disputed' },
      { point: 'Drinks can meaningfully change your blood pH level', status: 'disputed' },
      { point: 'A Nobel Prize winner endorsed lemon water as a cancer cure', status: 'disputed' },
      { point: 'Stopping chemotherapy in favour of lemon water is safe', status: 'disputed' },
    ],
    sources: [
      { name: 'World Health Organization', url: 'https://www.who.int/cancer', type: 'government' },
      { name: 'National Cancer Institute', url: 'https://www.cancer.gov', type: 'government' },
      { name: 'FactCheck.org – Cancer Myths', url: 'https://www.factcheck.org', type: 'factcheck' },
      { name: 'American Cancer Society', url: 'https://www.cancer.org', type: 'scientific' },
    ],
    tips: [
      'Health "cures" that promise results in days are almost always false',
      'Any reel that says "Big Pharma is hiding this" is a major red flag',
      'Never stop prescribed medical treatment based on social media content',
      'Nobel Prize citations in viral reels are very frequently distorted',
    ],
  },

  // ── TRUE: Transparent solar glass ───────────────────────────────────────────
  tech: {
    reelUrl: 'https://www.instagram.com/reel/techTrue456/',
    reelId: 'techTrue456',
    thumbnailEmoji: '🏢',
    claimFound: 'Researchers have created transparent solar glass that turns skyscrapers into solar energy generators by absorbing UV and infrared light while staying fully see-through.',
    claimSummary: 'Reel claims scientists invented transparent solar windows that can power buildings.',
    account: '@sciencedailyfeed',
    category: 'Science & Technology',
    verdict: 'TRUE',
    reason: 'Transparent luminescent solar concentrators (TLSCs) are a real, peer-reviewed technology. Institutions like Michigan State University and companies like Ubiquitous Energy have built working prototypes. These materials absorb non-visible wavelengths (UV and near-infrared) while letting visible light through — appearing clear. Commercial efficiency is 2–10%, lower than traditional panels, but the technology is genuine and actively developing.',
    confidenceLabel: 'Very Likely True',
    keyFacts: [
      { point: 'Transparent solar concentrator technology has working prototypes', status: 'confirmed' },
      { point: 'It absorbs UV and infrared light while staying visually clear', status: 'confirmed' },
      { point: 'It can be applied to building windows to generate electricity', status: 'confirmed' },
      { point: 'It is currently less efficient than traditional solar panels', status: 'confirmed' },
    ],
    sources: [
      { name: 'Nature Energy Journal', url: 'https://www.nature.com/nenergy/', type: 'scientific' },
      { name: 'U.S. Dept. of Energy – NREL', url: 'https://www.nrel.gov', type: 'government' },
      { name: 'Michigan State University Research', url: 'https://www.msu.edu', type: 'scientific' },
    ],
    tips: [
      'True technology claims may still be years from mass-market availability',
      'Check if a tech claim has peer-reviewed papers or only viral videos',
      '"Can generate energy" is not the same as "replaces all solar panels"',
    ],
  },

  // ── PARTIALLY TRUE: 5G conspiracy ───────────────────────────────────────────
  conspiracy: {
    reelUrl: 'https://www.instagram.com/reel/conspPartial789/',
    reelId: 'conspPartial789',
    thumbnailEmoji: '📡',
    claimFound: '5G towers emit radiation that causes headaches, cancer, and infertility. Governments installed them during lockdown while no one was watching.',
    claimSummary: 'Reel claims 5G towers cause cancer and infertility, and were secretly installed during COVID lockdowns.',
    account: '@truth_uncensored',
    category: 'Health & Technology',
    verdict: 'PARTIALLY TRUE',
    reason: '5G towers do emit non-ionising electromagnetic radiation — this part is factually correct and publicly documented. However, current scientific consensus (WHO, ICNIRP) confirms that 5G radiation at regulated levels does not cause cancer, headaches, or infertility. Many countries did accelerate tower installations during COVID lockdowns (less traffic disruption), making that part partially accurate. However, framing this as a "secret" conspiracy is misleading — permits, planning permissions, and installation reports were all public documents.',
    confidenceLabel: 'Partially Accurate, Mostly Misleading',
    keyFacts: [
      { point: '5G towers emit electromagnetic radiation', status: 'confirmed' },
      { point: 'Some 5G rollouts were accelerated during COVID lockdowns', status: 'confirmed' },
      { point: '5G radiation at regulated levels causes cancer or infertility', status: 'disputed' },
      { point: 'The rollout was hidden from the public or done "secretly"', status: 'disputed' },
      { point: 'WHO and ICNIRP have confirmed 5G is safe at regulated limits', status: 'confirmed' },
    ],
    sources: [
      { name: 'World Health Organization – EMF Project', url: 'https://www.who.int/peh-emf', type: 'government' },
      { name: 'ICNIRP Guidelines 2020', url: 'https://www.icnirp.org', type: 'scientific' },
      { name: 'Reuters Fact Check – 5G', url: 'https://www.reuters.com/fact-check', type: 'factcheck' },
      { name: 'UK Ofcom 5G Rollout Reports', url: 'https://www.ofcom.org.uk', type: 'government' },
    ],
    tips: [
      'Claims mixing real facts with false conclusions are the hardest to spot',
      'Check the WHO and your government\'s health authority on tech safety claims',
      '"Secretly installed" loses credibility when the planning documents are public',
      'Look up the actual scientific body (ICNIRP) that sets radiation safety limits',
    ],
  },
};

// ─── URL Validator ────────────────────────────────────────────────────────────

export function isInstagramReelUrl(url: string): boolean {
  return /instagram\.com\/(reel|reels|p)\//i.test(url.trim());
}

export function extractReelId(url: string): string {
  const match = url.match(/\/(reel|reels|p)\/([A-Za-z0-9_-]+)/i);
  return match ? match[2] : url.slice(-12);
}

// ─── URL-based resolver ───────────────────────────────────────────────────────

export function resolveFactCheckByUrl(url: string): FactClaimData {
  const lower = url.toLowerCase();

  // Route example URLs to specific scenarios
  if (lower.includes('healthfake') || lower.includes('lemon') || lower.includes('cancer')) {
    return mockFactData.health;
  }
  if (lower.includes('techture') || lower.includes('solar') || lower.includes('tech')) {
    return mockFactData.tech;
  }
  if (lower.includes('consp') || lower.includes('5g') || lower.includes('truth')) {
    return mockFactData.conspiracy;
  }

  // Route by URL hash/ID pattern for variety
  const id = extractReelId(url);
  const charSum = [...id].reduce((sum, c) => sum + c.charCodeAt(0), 0);
  const scenarios = Object.values(mockFactData);
  const picked = scenarios[charSum % scenarios.length];

  // Return picked scenario but with the actual URL and extracted ID
  return {
    ...picked,
    reelUrl: url,
    reelId: id,
  };
}

export type FactExampleKey = 'health' | 'tech' | 'conspiracy';
