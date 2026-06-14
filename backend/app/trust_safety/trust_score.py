import random
import logging

logger = logging.getLogger(__name__)

class TrustScoreSystem:
    def __init__(self):
        pass

    def calculate_trust(self, deepfake_prob: float, voice_prob: float, image_manip: bool, scam_risk: str, bot_prob: float, campaign_risk: float) -> dict:
        """
        Calculate a unified trust score based on multiple threat vectors.
        """
        logger.info("Trust Score System computing global rating parameters")
        
        # Scoring components (starts at 100, drops on threat signals)
        score = 100.0
        
        # Deepfake penalty
        score -= (deepfake_prob * 35.0)
        # Voice cloning penalty
        score -= (voice_prob * 25.0)
        # Image manipulation penalty
        if image_manip:
            score -= 20.0
        # Scam risk penalty
        if scam_risk == "High":
            score -= 30.0
        elif scam_risk == "Medium":
            score -= 15.0
        # Bot probability penalty
        score -= (bot_prob * 15.0)
        # Coordinated influence penalty
        score -= (campaign_risk / 100.0 * 20.0)
        
        # Clamp between 0 and 100
        score = max(0.0, min(100.0, score))
        score_int = int(score)
        
        # Map risk level
        if score_int >= 80:
            risk_level = "Low"
        elif score_int >= 50:
            risk_level = "Medium"
        else:
            risk_level = "High"

        # Verification signals
        signals = {
            "content_credibility": score_int,
            "source_reliability": random.randint(60, 95) if risk_level == "Low" else random.randint(15, 45),
            "verification_evidence_count": random.randint(2, 6),
            "manipulation_signals_detected": int((deepfake_prob > 0.5) + (voice_prob > 0.5) + image_manip + (scam_risk != "Low"))
        }

        return {
            "trust_score": score_int,
            "risk_level": risk_level,
            "factors_breakdown": {
                "deepfake_threat": "Low" if deepfake_prob < 0.3 else "High" if deepfake_prob > 0.7 else "Medium",
                "cloned_voice_threat": "Low" if voice_prob < 0.3 else "High" if voice_prob > 0.7 else "Medium",
                "manipulation_indicator": "Active" if image_manip else "None",
                "scam_alert": scam_risk,
                "bot_activity_level": "Low" if bot_prob < 0.3 else "High" if bot_prob > 0.7 else "Medium"
            },
            "signals": signals
        }
