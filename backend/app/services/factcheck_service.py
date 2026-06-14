import os
import logging
import urllib.parse
from typing import List, Dict, Any
import httpx
from app.utils.cache import cache_service
from app.utils.mock_data import health_mock, tech_mock, finance_mock, default_mock

logger = logging.getLogger(__name__)

GOOGLE_API_KEY = os.getenv("GOOGLE_FACTCHECK_API_KEY", "")
FACTCHECK_API_URL = "https://factchecktools.googleapis.com/v1alpha1/claims:search"

class FactCheckService:
    @staticmethod
    async def search_fact_checks(claim: str) -> List[Dict[str, Any]]:
        """
        Queries Google Fact Check Tools API for a claim. Caches result in Redis.
        """
        cache_key = f"fc:{urllib.parse.quote(claim[:60])}"
        
        # 1. Try Redis cache
        try:
            cached_data = cache_service.get(cache_key)
            if cached_data is not None:
                logger.info(f"Cache hit for claim: '{claim[:30]}...'")
                return cached_data
        except Exception as e:
            logger.warning(f"Cache read error: {str(e)}")

        # 2. Match Mock context if API key is not set
        if not GOOGLE_API_KEY:
            logger.warning("Google Fact Check API Key is missing. Using local mock verification engine.")
            mock_results = FactCheckService._local_mock_search(claim)
            
            # Save in cache
            cache_service.set(cache_key, mock_results, expire_seconds=86400)
            return mock_results

        # 3. Call Google API
        try:
            logger.info(f"Querying Google Fact Check API for: '{claim[:40]}...'")
            params = {
                "query": claim,
                "key": GOOGLE_API_KEY,
                "languageCode": "en"
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(FACTCHECK_API_URL, params=params)
                
                if response.status_code != 200:
                    logger.error(f"Google Fact Check API returned error status {response.status_code}")
                    return FactCheckService._local_mock_search(claim)
                
                data = response.json()
                claims_found = data.get("claims", [])
                
                results = []
                for item in claims_found[:3]:  # Limit to top 3 sources
                    claim_reviews = item.get("claimReview", [])
                    if claim_reviews:
                        review = claim_reviews[0]
                        publisher = review.get("publisher", {}).get("name", "Fact Checker")
                        results.append({
                            "name": publisher,
                            "url": review.get("url", "https://google.com"),
                            "snippet": f"Claim: {item.get('text')}. Rating: {review.get('textualRating')}. Review: {review.get('title', '')}"
                        })
                
                # If Google returns empty, merge with a local fallback search
                if not results:
                    results = FactCheckService._local_mock_search(claim)
                    
                # Cache results for 24 hours
                cache_service.set(cache_key, results, expire_seconds=86400)
                return results

        except Exception as e:
            logger.error(f"Google Fact Check API query failed: {str(e)}. Falling back to local search.")
            return FactCheckService._local_mock_search(claim)

    @staticmethod
    def _local_mock_search(claim: str) -> List[Dict[str, Any]]:
        """
        Local search fallback that matches claims against our mock dataset based on keywords.
        """
        claim_lower = claim.lower()
        
        if any(w in claim_lower for w in ["lemon", "cancer", "alkaline", "pharma"]):
            mock = health_mock
        elif any(w in claim_lower for w in ["solar", "glass", "window", "panel", "skyscraper"]):
            mock = tech_mock
        elif any(w in claim_lower for w in ["bank", "loophole", "arbitrage", "compound", "savings"]):
            mock = finance_mock
        else:
            mock = default_mock

        return [
            {
                "name": src["name"],
                "url": src["url"],
                "snippet": src["snippet"]
            }
            for src in mock["sources"]
        ]
