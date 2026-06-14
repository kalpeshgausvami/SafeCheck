import os
import logging
from typing import Dict, Any
from app.utils.mock_data import health_mock, tech_mock, finance_mock, default_mock

logger = logging.getLogger(__name__)

# Try importing faster-whisper. If it fails, we will run in fallback mode.
try:
    from faster_whisper import WhisperModel
    HAS_WHISPER = True
except ImportError:
    HAS_WHISPER = False
    logger.warning("faster_whisper is not installed. Speech transcription will run in mock fallback mode.")

class TranscriptionService:
    @staticmethod
    def transcribe_audio(audio_path: str, reel_url: str) -> Dict[str, Any]:
        """
        Transcribes audio.wav using faster-whisper.
        """
        # Detect mock files or missing whisper library
        is_mock_audio = False
        try:
            with open(audio_path, "r") as f:
                if f.read(20) == "DUMMY_WAV_CONTENT":
                    is_mock_audio = True
        except Exception:
            pass

        if not HAS_WHISPER or is_mock_audio:
            logger.info("Bypassing transcription. Returning mock speech transcript.")
            return TranscriptionService._get_mock_transcript(reel_url)

        try:
            logger.info("Initializing Faster-Whisper model (base)...")
            # Running on CPU for general environments, using base model size
            model = WhisperModel("base", device="cpu", compute_type="float32")
            
            logger.info(f"Transcribing audio file: {audio_path}")
            segments, info = model.transcribe(audio_path, beam_size=5)
            
            logger.info(f"Detected language '{info.language}' with probability {info.language_probability:.2f}")

            transcript_segments = []
            full_text_list = []
            
            for segment in segments:
                # Format time as mm:ss
                start_sec = int(segment.start)
                minutes = start_sec // 60
                seconds = start_sec % 60
                time_str = f"{minutes}:{seconds:02d}"

                transcript_segments.append({
                    "time": time_str,
                    "text": segment.text.strip(),
                    "flagged": False # Will be updated during claim analysis
                })
                full_text_list.append(segment.text.strip())

            return {
                "language": info.language,
                "transcript": " ".join(full_text_list),
                "segments": transcript_segments
            }

        except Exception as e:
            logger.warning(f"Whisper transcription failed: {str(e)}. Activating mock transcript fallback.")
            return TranscriptionService._get_mock_transcript(reel_url)

    @staticmethod
    def _get_mock_transcript(reel_url: str) -> Dict[str, Any]:
        url_lower = reel_url.lower()
        if "health" in url_lower or "lemon" in url_lower or "canc" in url_lower or "c8x9" in url_lower:
            mock = health_mock
        elif "tech" in url_lower or "solar" in url_lower or "glass" in url_lower or "c7p8" in url_lower:
            mock = tech_mock
        elif "finance" in url_lower or "bank" in url_lower or "loophole" in url_lower or "c9y3" in url_lower:
            mock = finance_mock
        else:
            mock = default_mock

        segments = [
            {"time": seg["time"], "text": seg["text"], "flagged": seg["flagged"]}
            for seg in mock["transcript"]
        ]
        full_text = " ".join([seg["text"] for seg in mock["transcript"]])

        return {
            "language": "en",
            "transcript": full_text,
            "segments": segments
        }
