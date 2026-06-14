import os
import sys
import datetime
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Optional

# Set up system path so import works under different run configurations
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.intelligence.clustering import ClaimClusteringEngine
from backend.app.intelligence.trends import TrendDetector
from backend.app.intelligence.network import NetworkPropagator
from backend.app.intelligence.forecasting import ViralityForecaster
from backend.app.intelligence.narrative import NarrativeTracker
from backend.app.intelligence.alerts import AlertSystem
from backend.app.intelligence.reports import IntelligenceReportCompiler
from backend.app.intelligence.config import MONITOR_KEYWORDS

router = APIRouter(prefix="/api/intelligence", tags=["Intelligence"])

# In-memory mock streams for social media posts
MOCK_STREAM_POSTS = [
    {"id": "p1", "text": "Drinking hot lemon water cures stage 4 cancer without chemotherapy", "platform": "Instagram", "author": "@health_guru_99", "views": 150000, "likes": 12000, "timestamp": "2026-06-12 10:00:00"},
    {"id": "p2", "text": "Doctors hide turmeric and lemon cure because of pharma lobbying", "platform": "X (Twitter)", "author": "@truth_seeker_99", "views": 250000, "likes": 32000, "timestamp": "2026-06-12 10:15:00"},
    {"id": "p3", "text": "Drinking water with lemon is good for health", "platform": "Reddit", "author": "@water_guy", "views": 4000, "likes": 350, "timestamp": "2026-06-12 10:20:00"},
    {"id": "p4", "text": "Compounding interest ATM loophole allows unlimited tax-free cash withdrawals", "platform": "Reddit", "author": "@finance_loophole_master", "views": 520000, "likes": 75000, "timestamp": "2026-06-12 10:30:00"},
    {"id": "p5", "text": "Federal Reserve cash loophole lets you withdraw unlimited money", "platform": "X (Twitter)", "author": "@bank_insider", "views": 120000, "likes": 8400, "timestamp": "2026-06-12 10:45:00"},
    {"id": "p6", "text": "Rigged voting machines discovered in local precinct municipal election", "platform": "Instagram", "author": "@precinct_watcher", "views": 45000, "likes": 2200, "timestamp": "2026-06-12 11:00:00"},
    {"id": "p7", "text": "The election counting machines suffered a system reset delay", "platform": "Reddit", "author": "@election_tracker", "views": 85000, "likes": 4800, "timestamp": "2026-06-12 11:15:00"}
]

# Engine instances
cluster_engine = ClaimClusteringEngine()

class MonitorRequest(BaseModel):
    keyword: str

@router.get("/trending")
async def get_trending_claims():
    """
    Groups posts, identifies growing trends, and runs virality predictions.
    """
    try:
        clustered = cluster_engine.cluster_posts(MOCK_STREAM_POSTS)
        trends = TrendDetector.identify_trends(clustered)
        
        # Hydrate with forecasts and network metrics
        hydrated_trends = []
        for t in trends:
            c_posts = [p for p in clustered if p["cluster_id"] == t["cluster_id"]]
            net_graph = NetworkPropagator.build_influence_graph(c_posts)
            bot_density = net_graph["metrics"]["density"]
            
            forecast = ViralityForecaster.forecast_virality(
                posts_count=t["posts_count"],
                growth_rate=t["growth_rate"],
                platforms_count=len(t["platforms"]),
                bot_density=bot_density
            )
            
            hydrated_trends.append({
                **t,
                "forecast": forecast,
                "bot_density": round(bot_density, 2)
            })
            
        return {"trends": hydrated_trends}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts")
async def get_alerts():
    """
    Analyzes trends and returns dispatched warnings.
    """
    try:
        clustered = cluster_engine.cluster_posts(MOCK_STREAM_POSTS)
        trends = TrendDetector.identify_trends(clustered)
        
        alerts_list = []
        for t in trends:
            c_posts = [p for p in clustered if p["cluster_id"] == t["cluster_id"]]
            net_graph = NetworkPropagator.build_influence_graph(c_posts)
            bot_density = net_graph["metrics"]["density"]
            
            # Evaluate alert payload
            alert_payload = await AlertSystem.evaluate_and_dispatch(t, bot_density)
            alerts_list.append(alert_payload)
            
        return {"alerts": alerts_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clusters")
async def get_clusters():
    try:
        clustered = cluster_engine.cluster_posts(MOCK_STREAM_POSTS)
        return {"posts": clustered}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/{cluster_id}")
async def get_trend_report(cluster_id: int):
    """
    Compiles PDF-like investigation summaries with narrative timelines and network metrics.
    """
    try:
        clustered = cluster_engine.cluster_posts(MOCK_STREAM_POSTS)
        trends = TrendDetector.identify_trends(clustered)
        
        # Find matching cluster
        trend_info = next((t for t in trends if t["cluster_id"] == cluster_id), None)
        if not trend_info:
            raise HTTPException(status_code=404, detail="Claim cluster not found.")
            
        c_posts = [p for p in clustered if p["cluster_id"] == cluster_id]
        net_graph = NetworkPropagator.build_influence_graph(c_posts)
        narrative_timeline = NarrativeTracker.track_evolution(cluster_id, trend_info["claim_cluster"])
        
        report_md = await IntelligenceReportCompiler.compile_cluster_report(
            trend_info=trend_info,
            verifications=narrative_timeline,
            network_metrics=net_graph["metrics"]
        )
        
        return {
            "cluster_id": cluster_id,
            "claim": trend_info["claim_cluster"],
            "network": net_graph,
            "narrative": narrative_timeline,
            "report_markdown": report_md
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/monitor")
async def add_monitor_keyword(req: MonitorRequest):
    kw = req.keyword.strip()
    if not kw:
        raise HTTPException(status_code=400, detail="Keyword cannot be empty.")
    
    if kw not in MONITOR_KEYWORDS:
        MONITOR_KEYWORDS.append(kw)
        
    return {
        "status": "success",
        "monitoring_list": MONITOR_KEYWORDS
    }
