// ─── Instagram Account Safety Data Model ─────────────────────────────────────

export interface WarningIndicator {
  icon: string;
  label: string;
  description: string;
  severity: 'low' | 'medium' | 'high';
}

export interface AccountSafetyData {
  username: string;
  displayName: string;
  bio: string;
  profilePicUrl: string;
  followerCount: number;
  followingCount: number;
  postCount: number;
  accountAge: string;
  isVerified: boolean;

  // Safety Results
  safetyStatus: 'safe' | 'caution' | 'danger';
  trustScore: number;          // 0–100
  safetyLabel: string;
  safetySummary: string;

  // Warning indicators (plain-English cards)
  warningIndicators: WarningIndicator[];

  // Recommended actions
  recommendations: string[];
}

// ─── Example Accounts ─────────────────────────────────────────────────────────

export const mockAccountData: Record<string, AccountSafetyData> = {

  // ── HIGH RISK: Fake store scam ───────────────────────────────────────────────
  danger: {
    username: 'tech_shop_deals',
    displayName: 'TechShop Deals 🛍️',
    bio: '🔥 BEST PRICES GUARANTEED 🔥 DM to order | Shipping worldwide | Crypto accepted ✅ Link in bio 👇',
    profilePicUrl: 'https://images.unsplash.com/photo-1563013544-824ae1b704d3?auto=format&fit=crop&q=80&w=200',
    followerCount: 43,
    followingCount: 8921,
    postCount: 7,
    accountAge: '2 weeks',
    isVerified: false,

    safetyStatus: 'danger',
    trustScore: 12,
    safetyLabel: 'High Risk Account',
    safetySummary:
      'This account shows multiple serious warning signs commonly found in scam or fraudulent profiles. It was created very recently, has almost no followers, and is following thousands of accounts — a classic pattern used by fake accounts. We strongly recommend you do not purchase anything from this account or share any personal information.',

    warningIndicators: [
      {
        icon: '🕒',
        label: 'Brand New Account',
        description: 'This account was created just 2 weeks ago. Scam accounts are often newly created to avoid detection.',
        severity: 'high',
      },
      {
        icon: '👥',
        label: 'Almost No Followers',
        description: 'Only 43 people follow this account. Legitimate businesses typically have an established audience.',
        severity: 'high',
      },
      {
        icon: '📈',
        label: 'Suspicious Following Pattern',
        description: 'Following 8,921 accounts while having only 43 followers is a common tactic used by fake accounts to gain attention.',
        severity: 'high',
      },
      {
        icon: '📷',
        label: 'Very Few Posts',
        description: 'Only 7 posts exist on this account. Real shops and businesses usually have a consistent posting history.',
        severity: 'medium',
      },
      {
        icon: '💰',
        label: 'Requests Cryptocurrency Payments',
        description: 'The bio mentions "Crypto accepted". Scammers often ask for cryptocurrency because payments are hard to trace or reverse.',
        severity: 'high',
      },
      {
        icon: '🔗',
        label: 'Unverified External Link',
        description: 'The bio contains a link to an external site. This could lead to a phishing page or fake store.',
        severity: 'medium',
      },
    ],

    recommendations: [
      'Do not send money or cryptocurrency to this account',
      'Do not click any links shared by this account',
      'Do not share your personal or payment information',
      'Search for the business name online to verify it is real',
      'Report this account to Instagram as suspicious',
    ],
  },

  // ── SAFE: Genuine food blogger ───────────────────────────────────────────────
  safe: {
    username: 'food_blogger_maya',
    displayName: 'Maya Cooks 🍜',
    bio: 'Home chef & food photographer 📸 | Sharing simple, delicious recipes every week | Based in London 🇬🇧 | Business: maya@maycooks.com',
    profilePicUrl: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&q=80&w=200',
    followerCount: 84200,
    followingCount: 1103,
    postCount: 412,
    accountAge: '4 years',
    isVerified: false,

    safetyStatus: 'safe',
    trustScore: 91,
    safetyLabel: 'Safe Account',
    safetySummary:
      'This account appears to be a genuine and trustworthy profile. It has been active for 4 years, has a large and engaged following, posts regularly, and has a professional bio with a real contact email. No suspicious activity was detected. This account is safe to interact with.',

    warningIndicators: [],

    recommendations: [
      'This account looks genuine — feel free to interact',
      'Always verify any product promotions before purchasing',
      'Check that any links go to the official website',
    ],
  },

  // ── CAUTION: Suspicious crypto account ──────────────────────────────────────
  caution: {
    username: 'crypto_gains_daily',
    displayName: 'Crypto Gains Daily 📈',
    bio: '💸 Teaching you how to make $500/day with crypto! 🚀 DM "GAINS" for FREE course | 10,000+ students | Results not typical',
    profilePicUrl: 'https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?auto=format&fit=crop&q=80&w=200',
    followerCount: 1820,
    followingCount: 3450,
    postCount: 38,
    accountAge: '5 months',
    isVerified: false,

    safetyStatus: 'caution',
    trustScore: 41,
    safetyLabel: 'Needs Attention',
    safetySummary:
      'This account has several characteristics that are worth being careful about. While it is not an obvious scam, it makes bold financial promises, was created relatively recently, and promotes unrealistic income claims. Accounts that promise guaranteed financial returns are frequently associated with scams. We recommend verifying this account carefully before engaging.',

    warningIndicators: [
      {
        icon: '💰',
        label: 'Unrealistic Income Claims',
        description: 'Promising "$500/day" from a free course is an extremely common scam tactic. No investment or course can guarantee such returns.',
        severity: 'high',
      },
      {
        icon: '🕒',
        label: 'Relatively New Account',
        description: 'This account is only 5 months old. Combined with bold financial claims, this is a warning sign.',
        severity: 'medium',
      },
      {
        icon: '📈',
        label: 'Unbalanced Followers/Following',
        description: 'Following almost twice as many accounts as followers is sometimes a sign of artificial growth tactics.',
        severity: 'medium',
      },
      {
        icon: '🎓',
        label: 'Unverifiable Claims',
        description: '"10,000+ students" cannot be independently verified. Be cautious of accounts that use large unverifiable numbers to build trust.',
        severity: 'medium',
      },
    ],

    recommendations: [
      'Do not pay for any course or "exclusive access" without verifying the seller',
      'Be very skeptical of guaranteed financial returns — they do not exist',
      'Search the account name online to find reviews or complaints',
      'Never share your crypto wallet details or passwords',
      'Check if the account has genuine comments from real followers',
    ],
  },
};

// ─── Key mapping for example selection ────────────────────────────────────────
export type ExampleKey = 'danger' | 'safe' | 'caution';

// ─── Username → data resolver ─────────────────────────────────────────────────
export function resolveAccountData(username: string): AccountSafetyData {
  const lower = username.toLowerCase().replace('@', '');

  if (lower.includes('tech') || lower.includes('shop') || lower.includes('deal') || lower.includes('scam')) {
    return mockAccountData.danger;
  }
  if (lower.includes('food') || lower.includes('maya') || lower.includes('cook') || lower.includes('recipe')) {
    return mockAccountData.safe;
  }
  if (lower.includes('crypto') || lower.includes('gain') || lower.includes('invest') || lower.includes('money')) {
    return mockAccountData.caution;
  }

  // Default: generate a slightly randomised caution result for unknown inputs
  return {
    username: lower,
    displayName: lower.charAt(0).toUpperCase() + lower.slice(1),
    bio: 'No bio provided.',
    profilePicUrl: 'https://images.unsplash.com/photo-1511367461989-f85a21fda167?auto=format&fit=crop&q=80&w=200',
    followerCount: Math.floor(Math.random() * 3000) + 50,
    followingCount: Math.floor(Math.random() * 2000) + 100,
    postCount: Math.floor(Math.random() * 80) + 2,
    accountAge: 'Unknown',
    isVerified: false,
    safetyStatus: 'caution',
    trustScore: 55,
    safetyLabel: 'Needs Attention',
    safetySummary:
      'We could not find enough information to fully verify this account. It may be genuine, but we recommend taking precautions before interacting with or trusting this profile.',
    warningIndicators: [
      {
        icon: '🔍',
        label: 'Limited Account History',
        description: 'We could not gather enough data to fully verify this account. Proceed with caution.',
        severity: 'medium',
      },
      {
        icon: '🌐',
        label: 'No Verified Information',
        description: 'This account has not been verified by Instagram and has limited public information available.',
        severity: 'low',
      },
    ],
    recommendations: [
      'Search for this account name online to learn more',
      'Check if any mutual followers can vouch for this account',
      'Be cautious before sharing personal information',
      'Verify any products or services independently before paying',
    ],
  };
}
