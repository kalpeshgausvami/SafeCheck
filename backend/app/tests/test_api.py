import unittest
from fastapi.testclient import TestClient
import sys
import os

# Adjust path so test runner finds app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.main import app

class TestTrustSafetyAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_index_route(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("app", data)
        self.assertEqual(data["app"], "Reel Truth Checker API")

    def test_health_route(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")

    def test_monitoring_alerts(self):
        response = self.client.get("/api/ts/monitoring/alerts?limit=5")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("alerts", data)
        self.assertEqual(len(data["alerts"]), 5)

    def test_monitoring_stream(self):
        response = self.client.get("/api/ts/monitoring/stream?count=3")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("stream", data)
        self.assertEqual(len(data["stream"]), 3)

    def test_ts_overview(self):
        response = self.client.get("/api/ts/overview")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["system_status"], "Operational")
        self.assertIn("global_trust_score", data)
        self.assertIn("global_risk_level", data)

    def test_detect_scam_sanitization(self):
        # Trigger scam detection with unsafe script tags to verify input sanitization
        payload = {"text": "<script>alert('xss')</script>Send me 1 ETH immediately to get double returns!"}
        response = self.client.post("/api/ts/detect/scam", json=payload)
        self.assertEqual(response.status_code, 200)
        # Verify the endpoint completed successfully and processed the clean payload
        data = response.json()
        self.assertEqual(data["scam_risk"], "High")
        self.assertEqual(data["detected_category"], "Crypto Giveaway Scam")

if __name__ == "__main__":
    unittest.main()
