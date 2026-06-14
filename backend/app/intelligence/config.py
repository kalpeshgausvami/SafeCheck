import os

# Clustering parameters
DBSCAN_EPS = float(os.getenv("DBSCAN_EPS", 0.25))
DBSCAN_MIN_SAMPLES = int(os.getenv("DBSCAN_MIN_SAMPLES", 2))

# Alert Thresholds (Growth rates)
YELLOW_ALERT_THRESHOLD = 0.20  # 20% growth rate
ORANGE_ALERT_THRESHOLD = 0.50  # 50% growth rate
RED_ALERT_THRESHOLD = 1.00     # 100% growth rate

# Keywords to monitor in social streams
MONITOR_KEYWORDS = [
    "lemon water", "cancer cure", "chemotherapy alternative",
    "solar glass", "skyscraper energy", "grid power window",
    "bank loophole", "unlimited withdrawal", "interest ATM",
    "vaccine chip", "election rigged", "drought laser"
]

# Webhook URLs
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "https://hooks.slack.com/services/mock/slack/webhook")
ALERTS_WEBHOOK_URL = os.getenv("ALERTS_WEBHOOK_URL", "https://api.reeltruthchecker.com/v1/alerts-sink")
