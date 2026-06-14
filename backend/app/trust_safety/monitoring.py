import time
import random
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class RealTimeMonitoringSystem:
    def __init__(self):
        self.alert_types = ["Deepfake Alert", "Misinformation Alert", "Scam Alert", "Campaign Alert"]
        self.severities = ["Green", "Yellow", "Orange", "Red"]

    def generate_alerts(self, limit: int = 10) -> list:
        """
        Generate a list of simulated recent warning alerts.
        """
        logger.info(f"Monitoring system generating {limit} telemetry alert items")
        
        claims = [
            "New synthetic video showing politician endorsing unauthorized investment scheme.",
            "Coordinated bot network propagating vaccine narrative mutations.",
            "Phishing site disguised as cryptocurrency claims verification portal.",
            "Voice cloned audio of CEO announcing false company bankruptcy circulating on Reddit.",
            "AI-generated image showing fake flood disaster in metropolitan area.",
            "Giveaway scam claiming free token distribution of major enterprise.",
            "Deepfake lip-sync video of local news anchor declaring regional lockdown.",
            "Romance scam ring targeting senior citizens across messaging networks."
        ]
        
        alerts = []
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        
        for i in range(limit):
            claim = random.choice(claims)
            
            # Map type and level
            if "synthetic" in claim.lower() or "deepfake" in claim.lower():
                alert_type = "Deepfake Alert"
                level = random.choice(["Orange", "Red"])
            elif "bot" in claim.lower() or "coordinated" in claim.lower():
                alert_type = "Campaign Alert"
                level = random.choice(["Yellow", "Orange"])
            elif "phishing" in claim.lower() or "scam" in claim.lower():
                alert_type = "Scam Alert"
                level = random.choice(["Orange", "Red"])
            else:
                alert_type = "Misinformation Alert"
                level = random.choice(["Yellow", "Orange"])
                
            alerts.append({
                "alert_id": f"TS-ALERT-{random.randint(1000, 9999)}",
                "type": alert_type,
                "claim": claim,
                "level": level,
                "message": f"Critical {alert_type} detected. Ingestion metrics indicate growth rate at {random.randint(150, 600)}% velocity.",
                "growth_rate": random.randint(120, 580),
                "timestamp": now
            })
            
        return alerts

    def get_stream_items(self, count: int = 15) -> list:
        """
        Simulate a stream of ingesting social media/news posts.
        """
        platforms = ["X (Twitter)", "Instagram", "Reddit", "Telegram", "YouTube", "DailyNews"]
        users = ["@news_tracker", "@crypto_expert", "@tech_guru", "@citizen_reporter", "@alpha_trading", "@bot_detector"]
        
        items = []
        for i in range(count):
            items.append({
                "item_id": f"item_{random.randint(100000, 999999)}",
                "platform": random.choice(platforms),
                "user": random.choice(users),
                "content": f"Simulated post content {i}: discussing trending topics with custom hashtag #verify",
                "ingested_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "reach": random.randint(500, 25000)
            })
        return items
