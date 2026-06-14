import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Try Sentry SDK setup
try:
    import sentry_sdk
    SENTRY_DSN = os.getenv("SENTRY_DSN", "")
    if SENTRY_DSN:
        sentry_sdk.init(dsn=SENTRY_DSN, traces_sample_rate=1.0)
        logger.info("Successfully initialized Sentry SDK monitoring.")
except ImportError:
    logger.warning("sentry-sdk is not installed. Error tracking bypassed.")

# Try PostHog setup
try:
    import posthog
    POSTHOG_KEY = os.getenv("POSTHOG_API_KEY", "")
    POSTHOG_HOST = os.getenv("POSTHOG_API_HOST", "https://app.posthog.com")
    if POSTHOG_KEY:
        posthog.project_api_key = POSTHOG_KEY
        posthog.host = POSTHOG_HOST
        logger.info("Successfully initialized PostHog analytics.")
except ImportError:
    logger.warning("posthog is not installed. Product analytics bypassed.")

class TelemetryService:
    @staticmethod
    def capture_event(user_id: str, event_name: str, properties: Dict[str, Any] = None):
        """
        Sends product analytics events to PostHog.
        """
        properties = properties or {}
        # Add baseline stats
        properties.update({"environment": os.getenv("ENV", "development")})
        
        logger.info(f"Telemetry Event: User '{user_id}' triggered '{event_name}' - {properties}")
        
        # Call PostHog client if loaded
        try:
            if 'posthog' in globals() and os.getenv("POSTHOG_API_KEY"):
                posthog.capture(user_id, event_name, properties)
        except Exception as e:
            logger.error(f"PostHog capture failed: {str(e)}")

    @staticmethod
    def capture_exception(exc: Exception):
        """
        Sends exception details to Sentry.
        """
        logger.error(f"Captured Exception in Telemetry: {str(exc)}", exc_info=True)
        try:
            if 'sentry_sdk' in globals() and os.getenv("SENTRY_DSN"):
                sentry_sdk.capture_exception(exc)
        except Exception as e:
            logger.error(f"Sentry capture failed: {str(e)}")

telemetry = TelemetryService()
