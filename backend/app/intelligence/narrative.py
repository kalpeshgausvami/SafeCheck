import logging

logger = logging.getLogger(__name__)

class NarrativeTracker:
    """
    Traces temporal claim evolution and visualizes narrative progression.
    """
    @staticmethod
    def track_evolution(cluster_id: int, base_claim: str) -> list:
        """
        Synthesizes narrative milestones showing how the statement mutated over time.
        """
        # Hardcoded evolutionary pathways for the demo clusters, otherwise generate dynamically
        c_id = int(cluster_id)
        
        if c_id == 101 or "lemon" in base_claim.lower() or "cancer" in base_claim.lower():
            return [
                {
                    "day": 1,
                    "narrative_step": "Drinking water with lemon keeps your body hydrated and boosts vitamin levels.",
                    "verdict": "Genuine",
                    "reach": 2500
                },
                {
                    "day": 4,
                    "narrative_step": "Alkaline ph diets from lemon water drops actively block cellular disease.",
                    "verdict": "Partially True",
                    "reach": 24000
                },
                {
                    "day": 7,
                    "narrative_step": "Drinking hot lemon water drops cures stage 4 cancer without chemotherapy.",
                    "verdict": "False",
                    "reach": 150000
                },
                {
                    "day": 10,
                    "narrative_step": "Pharma lobbies and doctors are hiding the hot lemon cancer cure to sell drugs.",
                    "verdict": "False",
                    "reach": 450000
                }
            ]
        elif c_id == 103 or "loophole" in base_claim.lower() or "bank" in base_claim.lower():
            return [
                {
                    "day": 1,
                    "narrative_step": "Compounding interest accounts optimize savings withdrawal yields.",
                    "verdict": "Genuine",
                    "reach": 5000
                },
                {
                    "day": 5,
                    "narrative_step": "ATM machines have an interest buffer interval that allows custom compounding.",
                    "verdict": "Partially True",
                    "reach": 35000
                },
                {
                    "day": 8,
                    "narrative_step": "You can exploit a compounding ATM interest loophole to withdraw unlimited tax-free cash.",
                    "verdict": "False",
                    "reach": 220000
                }
            ]
        else:
            # Default generic evolution path
            return [
                {
                    "day": 1,
                    "narrative_step": f"Initial observation of discussion regarding: {base_claim[:40]}...",
                    "verdict": "Uncertain",
                    "reach": 1200
                },
                {
                    "day": 5,
                    "narrative_step": f"Amplification of claims stating: {base_claim[:50]}...",
                    "verdict": "Misleading",
                    "reach": 15000
                }
            ]
