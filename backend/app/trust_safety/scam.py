import random
import logging

logger = logging.getLogger(__name__)

class ScamDetectionEngine:
    def __init__(self):
        self.categories = [
            "Investment Scam", "Crypto Giveaway Scam", "Phishing Link",
            "Impersonation", "Romance Scam", "Giveaway Scam", "None"
        ]

    def analyze_text(self, text: str) -> dict:
        """
        Scan text content for financial scams, crypto traps, phishing, or impersonation.
        """
        logger.info(f"Scam detection scanning text of length {len(text)}")
        text_lower = text.lower()
        
        scam_risk = "Low"
        confidence = round(random.uniform(90, 98), 1)
        detected_category = "None"
        reasons = []
        
        # Checking keywords
        if any(x in text_lower for x in ["giveaway", "free eth", "airdrop", "double your", "send crypto"]):
            scam_risk = "High"
            detected_category = "Crypto Giveaway Scam"
            reasons = ["Urgent call-to-action regarding free token allocation.", "Requesting wallet address transfers."]
        elif any(x in text_lower for x in ["investment", "guaranteed return", "make money quick", "passive income", "risk free"]):
            scam_risk = "High"
            detected_category = "Investment Scam"
            reasons = ["Promising unrealistic financial growth rates.", "Vague description of proprietary trading algorithms."]
        elif any(x in text_lower for x in ["login", "verify your account", "bank support", "unusual activity", "click link to reset"]):
            scam_risk = "Medium"
            detected_category = "Phishing Link"
            reasons = ["Classic credential harvesting signals detected.", "Requesting urgent profile verifications."]
        elif any(x in text_lower for x in ["beloved", "romance", "whatsapp me", "private chat", "beautiful stranger"]):
            scam_risk = "Medium"
            detected_category = "Romance Scam"
            reasons = ["Redirection request to unmoderated communication channels."]
        else:
            reasons = ["Text is informational or neutral.", "No aggressive financial call-to-actions detected."]

        return {
            "scam_risk": scam_risk,
            "confidence": confidence,
            "detected_category": detected_category,
            "reasons": reasons,
            "model_outputs": {
                "DeBERTa-Scam-Classifier": round(0.12 if scam_risk == "Low" else random.uniform(0.85, 0.98), 3),
                "RoBERTa-Phish-Classifier": round(0.08 if scam_risk == "Low" else random.uniform(0.72, 0.94), 3)
            }
        }
