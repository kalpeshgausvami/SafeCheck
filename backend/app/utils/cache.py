import json
import logging
from typing import Any, Optional
from redis import Redis
from app.core.config import settings

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        self.redis: Optional[Redis] = None
        self._local_fallback: dict = {}
        try:
            self.redis = Redis.from_url(
                settings.REDIS_URL,
                socket_timeout=2,
                decode_responses=True
            )
            self.redis.ping()
            logger.info("Successfully connected to Redis cache.")
        except Exception as e:
            logger.warning(f"Could not connect to Redis: {str(e)}. Falling back to in-memory dictionary caching.")
            self.redis = None

    def get(self, key: str) -> Optional[Any]:
        if self.redis:
            try:
                data = self.redis.get(key)
                if data:
                    return json.loads(data)
            except Exception as e:
                logger.error(f"Redis get error for key {key}: {str(e)}")
        
        # In-memory fallback
        return self._local_fallback.get(key)

    def set(self, key: str, value: Any, expire_seconds: int = 86400) -> bool:
        serialized = json.dumps(value)
        if self.redis:
            try:
                self.redis.setex(key, expire_seconds, serialized)
                return True
            except Exception as e:
                logger.error(f"Redis setex error for key {key}: {str(e)}")
        
        # In-memory fallback
        self._local_fallback[key] = value
        return True

cache_service = CacheService()
