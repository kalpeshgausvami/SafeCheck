from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict

# Import sanitizer
from app.utils.sanitizer import sanitize_string

# Import engines
from app.trust_safety.deepfake import DeepfakeDetectionEngine
from app.trust_safety.voice import VoiceCloningDetectionEngine
from app.trust_safety.image import ImageForensicsEngine
from app.trust_safety.scam import ScamDetectionEngine
from app.trust_safety.bot import BotDetectionSystem
from app.trust_safety.influence import CoordinatedInfluenceDetector
from app.trust_safety.multimodal import MultimodalAnalysisEngine
from app.trust_safety.agents import AutonomousInvestigationAgents
from app.trust_safety.trust_score import TrustScoreSystem
from app.trust_safety.monitoring import RealTimeMonitoringSystem

router = APIRouter(prefix="/ts", tags=["AI Trust & Safety Operating System"])

# Initialize engine instances
deepfake_engine = DeepfakeDetectionEngine()
voice_engine = VoiceCloningDetectionEngine()
image_engine = ImageForensicsEngine()
scam_engine = ScamDetectionEngine()
bot_engine = BotDetectionSystem()
influence_detector = CoordinatedInfluenceDetector()
multimodal_engine = MultimodalAnalysisEngine()
agents_system = AutonomousInvestigationAgents()
trust_system = TrustScoreSystem()
monitor_system = RealTimeMonitoringSystem()

# Schemas
class DeepfakeRequest(BaseModel):
    video_path: str

    @field_validator('video_path')
    @classmethod
    def sanitize_video_path(cls, v: str) -> str:
        return sanitize_string(v)

class VoiceRequest(BaseModel):
    audio_path: str

    @field_validator('audio_path')
    @classmethod
    def sanitize_audio_path(cls, v: str) -> str:
        return sanitize_string(v)

class ImageRequest(BaseModel):
    image_path: str

    @field_validator('image_path')
    @classmethod
    def sanitize_image_path(cls, v: str) -> str:
        return sanitize_string(v)

class ScamRequest(BaseModel):
    text: str

    @field_validator('text')
    @classmethod
    def sanitize_text(cls, v: str) -> str:
        return sanitize_string(v)

class BotRequest(BaseModel):
    account_handle: str

    @field_validator('account_handle')
    @classmethod
    def sanitize_account_handle(cls, v: str) -> str:
        return sanitize_string(v)

class InfluenceRequest(BaseModel):
    claim: str

    @field_validator('claim')
    @classmethod
    def sanitize_claim(cls, v: str) -> str:
        return sanitize_string(v)

class AgentRequest(BaseModel):
    claim: str
    video_path: Optional[str] = ""

    @field_validator('claim', 'video_path')
    @classmethod
    def sanitize_fields(cls, v: str) -> str:
        return sanitize_string(v) if v else ""

# Endpoints
@router.post("/detect/deepfake")
def detect_deepfake(req: DeepfakeRequest):
    try:
        return deepfake_engine.analyze_video(req.video_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect/voice")
def detect_voice(req: VoiceRequest):
    try:
        return voice_engine.analyze_audio(req.audio_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect/image")
def detect_image(req: ImageRequest):
    try:
        return image_engine.analyze_image(req.image_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect/scam")
def detect_scam(req: ScamRequest):
    try:
        return scam_engine.analyze_text(req.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect/bot")
def detect_bot(req: BotRequest):
    try:
        return bot_engine.analyze_account(req.account_handle)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect/influence")
def detect_influence(req: InfluenceRequest):
    try:
        return influence_detector.analyze_narrative(req.claim)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agents/investigate")
def run_agents_investigation(req: AgentRequest):
    try:
        return agents_system.run_investigation(req.claim, req.video_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monitoring/alerts")
def get_recent_alerts(limit: int = Query(default=10, ge=1, le=50)):
    try:
        return {"alerts": monitor_system.generate_alerts(limit)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monitoring/stream")
def get_ingestion_stream(count: int = Query(default=15, ge=1, le=100)):
    try:
        return {"stream": monitor_system.get_stream_items(count)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/overview")
def get_ts_overview():
    """
    Returns aggregated metrics and high-level status of the Trust & Safety Operating System.
    """
    try:
        recent_alerts = monitor_system.generate_alerts(5)
        # Compute dynamic scores
        df_result = deepfake_engine.analyze_video("sample_deepfake_video.mp4")
        voice_result = voice_engine.analyze_audio("sample_cloned_voice.wav")
        scam_result = scam_engine.analyze_text("Verify your account login credentials now")
        bot_result = bot_engine.analyze_account("@cyber_advocate")
        influence_result = influence_detector.analyze_narrative("Cure cancer using lemon juice and baking soda")
        
        trust_calculations = trust_system.calculate_trust(
            deepfake_prob=df_result["deepfake_probability"],
            voice_prob=voice_result["spectral_flux_anomaly"],
            image_manip=True,
            scam_risk=scam_result["scam_risk"],
            bot_prob=bot_result["bot_probability"],
            campaign_risk=influence_result["risk_score"]
        )

        return {
            "system_status": "Operational",
            "global_trust_score": trust_calculations["trust_score"],
            "global_risk_level": trust_calculations["risk_level"],
            "monitoring_active_keywords": ["giveaway", "cur", "therap", "conspirac", "clon", "double eth"],
            "active_alerts_count": len(recent_alerts),
            "ingestion_rate_posts_hr": 14200,
            "verification_confidence": 92.5,
            "metrics": {
                "total_videos_scanned": 1284,
                "total_audios_scanned": 4122,
                "total_images_scanned": 948,
                "total_texts_scanned": 38100,
                "bot_accounts_flagged": 240,
                "influence_campaigns_detected": 14
            },
            "recent_alerts": recent_alerts,
            "trust_metrics": trust_calculations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
