import logging
import math

logger = logging.getLogger(__name__)

class ViralityForecaster:
    """
    Simulates ML forecasting to project future propagation and risk levels.
    """
    @staticmethod
    def forecast_virality(posts_count: int, growth_rate: float, platforms_count: int, bot_density: float) -> dict:
        """
        Uses a math-model regression to predict 7-day future reach, virality probability,
        and projected risk.
        """
        # Base virality score equation
        # High growth rate, multiple platforms, and bot density boost the virality index
        virality_logit = (-2.5 + 
                          (3.2 * growth_rate) + 
                          (0.8 * platforms_count) + 
                          (4.5 * bot_density))
        
        # Sigmoid function for probability (0-1.0)
        probability = 1.0 / (1.0 + math.exp(-max(min(virality_logit, 10), -10)))
        
        # Calculate projected 7-day reach
        base_reach = posts_count * 500 # assume 500 views average per post
        projected_reach = base_reach * math.exp(min(growth_rate * 7.0, 5.0))
        
        # Map projected risk
        if probability >= 0.85:
            projected_risk = "Critical"
        elif probability >= 0.60:
            projected_risk = "High"
        elif probability >= 0.30:
            projected_risk = "Medium"
        else:
            projected_risk = "Low"

        return {
            "virality_probability": round(probability, 4),
            "projected_7d_reach": int(projected_reach),
            "projected_risk": projected_risk,
            "confidence_interval_low": int(projected_reach * 0.7),
            "confidence_interval_high": int(projected_reach * 1.4)
        }
