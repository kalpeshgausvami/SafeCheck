import datetime
import httpx
import logging
from backend.app.intelligence.config import (
    YELLOW_ALERT_THRESHOLD, ORANGE_ALERT_THRESHOLD, RED_ALERT_THRESHOLD,
    SLACK_WEBHOOK_URL, ALERTS_WEBHOOK_URL
)

logger = logging.getLogger(__name__)

class AlertSystem:
    """
    Evaluates claim trends against thresholds and dispatches notifications.
    """
    @staticmethod
    async def evaluate_and_dispatch(trend: dict, bot_density: float) -> dict:
        growth = trend.get("growth_rate", 0.0)
        claim = trend.get("claim_cluster", "Unknown Claim")
        c_id = trend.get("cluster_id", 0)
        
        # Decide Alert Level
        if growth >= RED_ALERT_THRESHOLD or bot_density >= 0.70:
            level = "Red"
            msg = f"CRITICAL THREAT: Emerging misinformation narrative '{claim[:40]}...' growing at {int(growth * 100)}% with high coordinated bot activity ({int(bot_density * 100)}% density)."
        elif growth >= ORANGE_ALERT_THRESHOLD:
            level = "Orange"
            msg = f"HIGH ALERT: Rapidly propagating narrative '{claim[:40]}...' growing at {int(growth * 100)}% across {len(trend.get('platforms', []))} platforms."
        elif growth >= YELLOW_ALERT_THRESHOLD:
            level = "Yellow"
            msg = f"MODERATE WARNING: Emerging claim '{claim[:40]}...' is showing growth velocity ({int(growth * 100)}%)."
        else:
            level = "Green"
            msg = f"MONITORING: Claim '{claim[:40]}...' shows stable baseline activity."

        alert_payload = {
            "alert_id": f"alt_{c_id}_{int(datetime.datetime.now().timestamp()) % 10000}",
            "cluster_id": c_id,
            "claim": claim,
            "level": level,
            "message": msg,
            "growth_rate": growth,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Dispatch webhook warnings (simulate or run HTTP requests defensively)
        if level in ["Orange", "Red"]:
            try:
                # Trigger webhook post
                async with httpx.AsyncClient(timeout=2.0) as client:
                    await client.post(ALERTS_WEBHOOK_URL, json=alert_payload)
                    logger.info(f"Dispatched webhook alert to {ALERTS_WEBHOOK_URL}")
            except Exception as e:
                # Silently catch offline sinks in sandbox runs
                logger.debug(f"Webhook alerts endpoint offline: {str(e)}")

        return alert_payload
