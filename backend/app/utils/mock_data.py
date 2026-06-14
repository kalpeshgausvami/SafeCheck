health_mock = {
    "verdict": "Likely Misinformation",
    "confidence": 97,
    "risk_level": "High",
    "reasoning": "The claim that lemon water cures cancer is scientifically unfounded and contradicts established medical guidelines. While lemons contain vitamins and antioxidants, there is no clinical evidence that lemon water destroys cancer cells or cures cancer in three days. Delaying conventional cancer treatment in favor of unproven natural remedies poses extreme health risks.",
    "uploader": "@health_hacks_daily",
    "duration": "0:45",
    "views": "1.2M",
    "likes": "124K",
    "caption_text": "🚨 THE TRUTH THEY ARE HIDING FROM YOU! 🚨 Did you know drinking hot lemon water on an empty stomach completely destroys cancer cells? Big Pharma doesn’t want you to know this simple trick. Share with everyone you love! 🍋✨\n\n#healthhacks #naturalcures #lemonwater #cancercure #bigpharma #holistichealth",
    "transcript": [
        {"time": "0:01", "text": "Hey guys, did you know that big pharma is hiding a cure from you?", "flagged": True},
        {"time": "0:10", "text": "All you need is fresh lemons and warm water every single morning.", "flagged": False},
        {"time": "0:18", "text": "The citric acid in lemons becomes alkaline inside your body and completely kills all cancer cells in 72 hours.", "flagged": True},
        {"time": "0:29", "text": "A Nobel prize winner proved this back in the 30s but they covered it up.", "flagged": True},
        {"time": "0:38", "text": "Stop taking chemotherapy and start drinking lemons. Share this to save a life!", "flagged": True}
    ],
    "ocr_text": [
        {"time": "0:02", "text": "LEMON WATER CURES CANCER"},
        {"time": "0:15", "text": "WHAT BIG PHARMA HIDES"},
        {"time": "0:25", "text": "KILLS CANCER CELLS IN 3 DAYS"},
        {"time": "0:35", "text": "SHARE TO SAVE LIVES"}
    ],
    "claims": [
        {
            "title": "Hot lemon water kills cancer cells in 3 days",
            "rating": "false",
            "analysis": "No scientific study or clinical trial supports this claim. Lemons contain beneficial antioxidants, but they cannot cure cancer or destroy tumors."
        },
        {
            "title": "Lemons create an alkaline environment that cancer cannot survive in",
            "rating": "false",
            "analysis": "Food and drink do not significantly alter blood pH. The human body tightly regulates its pH levels regardless of diet. Furthermore, cancer cells can grow in alkaline environments."
        },
        {
            "title": "A Nobel Prize winner proved this cure and it was covered up",
            "rating": "misleading",
            "analysis": "Otto Warburg won the Nobel Prize in 1931 for research showing cancer cells use glycolysis. He did not claim that lemons or an alkaline diet cure cancer. This is a common distortion of his work."
        }
    ],
    "sources": [
        {
            "name": "World Health Organization (WHO)",
            "url": "https://www.who.int",
            "snippet": "WHO cancer guidelines state that early diagnosis and scientifically validated treatments (chemotherapy, radiation, surgery) are key to cancer survival. Alternative dietary remedies are not replacements for medical care."
        },
        {
            "name": "National Cancer Institute (NCI)",
            "url": "https://www.cancer.gov",
            "snippet": "NCI provides comprehensive evidence debunking the alkaline diet myth and states there is no evidence that altering dietary pH affects cancer cell growth."
        },
        {
            "name": "FactCheck.org - Cancer Myths",
            "url": "https://www.factcheck.org",
            "snippet": "Detailed debunking of the viral \"lemon water cures cancer\" social media claims, tracing the myth back to emails circulating in the mid-2000s."
        }
    ]
}

tech_mock = {
    "verdict": "Likely Genuine",
    "confidence": 92,
    "risk_level": "Low",
    "reasoning": "The video describes transparent solar cell technology (often called photovoltaic glass or solar windows). This is an active field of scientific research and development, with working prototypes created by institutions like Michigan State University and companies like Ubiquitous Energy. The video accurately presents the operating mechanism (absorbing ultraviolet and near-infrared light while letting visible light pass) and its potential applications.",
    "uploader": "@tech_future_now",
    "duration": "0:58",
    "views": "850K",
    "likes": "82K",
    "caption_text": "This transparent solar glass could turn every skyscraper into a vertical solar farm! 🏢☀️ Developed by researchers, this technology captures non-visible wavelengths of light so it looks just like normal glass. The future of clean energy is here!\n\n#solar #cleanenergy #renewables #futuretech #engineering #sustainableliving",
    "transcript": [
        {"time": "0:02", "text": "This is not standard glass. It is actually a fully functional transparent solar panel.", "flagged": False},
        {"time": "0:12", "text": "Researchers have created materials that absorb only ultraviolet and near-infrared light.", "flagged": False},
        {"time": "0:24", "text": "Because it doesn’t absorb visible light, it looks completely clear to the human eye.", "flagged": False},
        {"time": "0:35", "text": "It can be fitted onto windows of skyscrapers, generating clean power from empty surfaces.", "flagged": False},
        {"time": "0:48", "text": "While the efficiency is currently lower than traditional panels, the sheer scale of building glass could make it huge.", "flagged": False}
    ],
    "ocr_text": [
        {"time": "0:05", "text": "TRANSPARENT SOLAR GLASS"},
        {"time": "0:22", "text": "HOW IT WORKS: ABSORBS UV & INFRARED"},
        {"time": "0:42", "text": "VERTICAL SOLAR FARMS"}
    ],
    "claims": [
        {
            "title": "Solar cells can be made transparent to look like window glass",
            "rating": "true",
            "analysis": "Transparent luminescent solar concentrators (TLSCs) use organic salts to absorb non-visible light wavelengths, making them transparent to human eyes while generating energy."
        },
        {
            "title": "They can turn skyscrapers into solar generators",
            "rating": "true",
            "analysis": "By coating large windows with photovoltaic materials, skyscrapers can produce significant supplementary energy, helping offset their carbon footprints."
        },
        {
            "title": "Solar windows are currently less efficient than rooftop solar panels",
            "rating": "true",
            "analysis": "Commercial transparent panels typically range from 2% to 10% efficiency, compared to 18% to 22% for traditional silicon solar panels."
        }
    ],
    "sources": [
        {
            "name": "Nature Energy Journal",
            "url": "https://www.nature.com/nenergy/",
            "snippet": "Scientific publication on the development of highly efficient transparent organic photovoltaics, outlining recent advances reaching up to 10% transparency-to-efficiency ratio."
        },
        {
            "name": "U.S. Department of Energy (NREL)",
            "url": "https://www.nrel.gov",
            "snippet": "NREL reports on building-integrated photovoltaics (BIPV) highlighting solar windows as a key emerging technology for net-zero carbon building architectures."
        }
    ]
}

finance_mock = {
    "verdict": "Uncertain",
    "confidence": 68,
    "risk_level": "Medium",
    "reasoning": "The video blends basic, valid financial concepts (like compound interest and high-yield savings accounts) with exaggerated and potentially deceptive claims about \"bank loopholes\" and \"arbitrage.\" The creator implies that standard consumers can easily exploit these mechanisms to double their money overnight or with zero risk, which is misleading. While compound interest is real, the rate of return and risk levels are highly distorted.",
    "uploader": "@wealth_secrets_unlocked",
    "duration": "1:12",
    "views": "3.4M",
    "likes": "340K",
    "caption_text": "🏦 SECRET BANK LOOPHOLE! 🏦 How banks double their money using your savings and how you can do the exact same thing using compound interest arbitrate. Follow me for more secret money systems! 💸🔥\n\n#moneyhacks #bankingloophole #passiveincome #investing #compoundinterest #wealthhacks",
    "transcript": [
        {"time": "0:01", "text": "Here is a secret bank loophole they do not want you to know about.", "flagged": True},
        {"time": "0:12", "text": "When you put money in a savings account, the bank lends it out at 10 times the value using fractional reserve banking.", "flagged": False},
        {"time": "0:25", "text": "But you can bypass them by using a compound interest arbitrage account.", "flagged": True},
        {"time": "0:38", "text": "This guarantees a 25% return annually with absolutely zero risk.", "flagged": True},
        {"time": "0:55", "text": "Most people are losing money to inflation, but this loophole keeps you rich.", "flagged": False}
    ],
    "ocr_text": [
        {"time": "0:02", "text": "SECRET BANK LOOPHOLE"},
        {"time": "0:20", "text": "WHAT BANKS HIDE"},
        {"time": "0:40", "text": "25% RETURN GUARANTEED"},
        {"time": "1:00", "text": "ACT BEFORE IT IS CLOSED"}
    ],
    "claims": [
        {
            "title": "A \"compound interest arbitrage account\" guarantees a 25% annual return with zero risk",
            "rating": "false",
            "analysis": "There is no such financial instrument that guarantees a 25% return with zero risk. Any investment offering returns that high carries substantial risk of capital loss or is a fraudulent scheme."
        },
        {
            "title": "Banks lend out savings at 10 times the value using fractional reserve banking",
            "rating": "misleading",
            "analysis": "This is a misunderstanding of fractional reserve banking. Banks create money via lending, but individual retail customers cannot perform this process themselves, nor is it a \"loophole\" they can exploit."
        },
        {
            "title": "Standard savings accounts lose value due to inflation",
            "rating": "true",
            "analysis": "Correct. When inflation exceeds the interest rate of a savings account (e.g. inflation at 3-4% and savings interest at 0.01%), the real purchasing power of the saved money decreases over time."
        }
    ],
    "sources": [
        {
            "name": "Federal Reserve Board",
            "url": "https://www.federalreserve.gov",
            "snippet": "Educational material explaining fractional reserve requirements, monetary policy, and bank regulations. Refutes claims that fractional lending is a consumer-level loophole."
        },
        {
            "name": "SEC (Securities and Exchange Commission)",
            "url": "https://www.sec.gov",
            "snippet": "SEC warnings on high-yield investment programs (HYIPs) promising high guaranteed returns. The SEC advises that any promise of double-digit returns with zero risk is a classic warning sign of fraud."
        }
    ]
}

default_mock = {
    "verdict": "Uncertain",
    "confidence": 71,
    "risk_level": "Medium",
    "reasoning": "This Reel contains a mix of factual footage with non-verifiable commentary. The AI fact checking engine noted that the visual clips are authentic, but the causal connections drawn by the speaker lack peer-reviewed citation or official verification. Proceed with caution.",
    "uploader": "@reel_content_creator",
    "duration": "1:00",
    "views": "250K",
    "likes": "12K",
    "caption_text": "Video submitted via user interface analysis.\n\n#factcheck #verify #socialmedia #aidetector",
    "transcript": [
        {"time": "0:01", "text": "Hey guys, check out this video, they really don't want you to see this.", "flagged": True},
        {"time": "0:15", "text": "Look at the background, this is what is actually going on.", "flagged": False},
        {"time": "0:32", "text": "This clearly shows the truth about what happened last week.", "flagged": True},
        {"time": "0:50", "text": "Make sure you click the link in bio to learn the full secret.", "flagged": False}
    ],
    "ocr_text": [
        {"time": "0:05", "text": "THEY DONT WANT YOU TO SEE THIS"},
        {"time": "0:35", "text": "THE ACTUAL TRUTH"}
    ],
    "claims": [
        {
            "title": "Visual evidence proves the speaker's claim of staging",
            "rating": "misleading",
            "analysis": "The footage is real but taken out of context. The event depicted was a standard public exhibition, not a staged conspiracy as implied by the audio narration."
        },
        {
            "title": "The referenced events from \"last week\" are fully verified",
            "rating": "false",
            "analysis": "No reputable news agencies or local official sources have reports corresponding to the uploader's description of the event."
        }
    ],
    "sources": [
        {
            "name": "Associated Press (AP) Fact Check",
            "url": "https://apnews.com/hub/ap-fact-check",
            "snippet": "AP provides general guidelines and verification reports on trending social media media and out-of-context video footage."
        },
        {
            "name": "Snopes.com Fact Checker",
            "url": "https://www.snopes.com",
            "snippet": "Independent website specializing in researching and debunking urban legends, internet rumors, and stories of unknown origin."
        }
    ]
}
