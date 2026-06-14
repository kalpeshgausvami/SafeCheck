import os
import cv2
import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import logging

logger = logging.getLogger(__name__)

class MultimodalFusion(nn.Module):
    """
    Multimodal verification model using CLIP and OpenCV.
    Matches video frames with transcripts to detect mismatch or splicing.
    """
    def __init__(self, model_name: str = "openai/clip-vit-base-patch32"):
        super().__init__()
        try:
            self.processor = CLIPProcessor.from_pretrained(model_name)
            self.clip = CLIPModel.from_pretrained(model_name)
            self.has_clip = True
        except Exception as e:
            logger.warning(f"Could not load CLIP model: {str(e)}. Using OpenCV fallback frame analysis.")
            self.has_clip = False

    def forward(self, pixel_values, input_ids, attention_mask):
        if self.has_clip:
            outputs = self.clip(input_ids=input_ids, attention_mask=attention_mask, pixel_values=pixel_values, return_dict=True)
            return outputs
        return None

    def analyze_video_consistency(self, video_path: str, transcript_text: str) -> dict:
        """
        Samples video frames, extracts visual CLIP features, and computes alignment 
        against the speech transcript. Also runs frame-difference checks to find splices.
        """
        if not os.path.exists(video_path):
            return {
                "mismatch_detected": False,
                "visual_manipulation_score": 0.0,
                "frame_details": "Video file not found."
            }

        # 1. Sample frames using OpenCV
        cap = cv2.VideoCapture(video_path)
        frames = []
        frame_indices = []
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Sample 5 frames across the video duration
        step = max(total_frames // 5, 1)
        for i in range(5):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i * step)
            ret, frame = cap.read()
            if not ret:
                break
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(rgb_frame)
            frame_indices.append(i * step)
            
        cap.release()

        if not frames:
            return {
                "mismatch_detected": False,
                "visual_manipulation_score": 0.1,
                "reasoning": "Could not extract video frames."
            }

        # 2. Check for visual splicing using structural differences in consecutive frames
        frame_diffs = []
        for j in range(len(frames) - 1):
            gray_a = cv2.cvtColor(frames[j], cv2.COLOR_RGB2GRAY)
            gray_b = cv2.cvtColor(frames[j+1], cv2.COLOR_RGB2GRAY)
            # Resize to same size for comparison
            gray_a = cv2.resize(gray_a, (128, 128))
            gray_b = cv2.resize(gray_b, (128, 128))
            
            diff = cv2.absdiff(gray_a, gray_b)
            mean_diff = np.mean(diff)
            frame_diffs.append(float(mean_diff))

        # High frame difference variance indicates abrupt cuts or splices
        max_diff = max(frame_diffs) if frame_diffs else 0.0
        manipulation_detected = max_diff > 45.0 # Threshold for extreme visual shift

        # 3. Text-image alignment check using CLIP
        alignment_score = 0.5
        mismatch_detected = False
        
        if self.has_clip and transcript_text.strip():
            try:
                pil_images = [Image.fromarray(f) for f in frames]
                inputs = self.processor(
                    text=[transcript_text[:100]], # Clip text input limit
                    images=pil_images,
                    return_tensors="pt",
                    padding=True
                )
                
                with torch.no_grad():
                    outputs = self.clip(
                        input_ids=inputs["input_ids"],
                        attention_mask=inputs["attention_mask"],
                        pixel_values=inputs["pixel_values"]
                    )
                
                # Cosine similarity logits
                logits_per_image = outputs.logits_per_image # Image-text similarity logits
                probs = logits_per_image.softmax(dim=0).squeeze().tolist()
                alignment_score = float(np.mean(probs)) if isinstance(probs, list) else float(probs)
                
                # Low average similarity suggests mismatch between what is spoken and shown
                if alignment_score < 0.20:
                    mismatch_detected = True
            except Exception as e:
                logger.error(f"CLIP alignment calculation error: {str(e)}")

        return {
            "mismatch_detected": mismatch_detected,
            "visual_manipulation_score": round(max_diff / 100.0, 2),
            "alignment_score": round(alignment_score, 2),
            "reasoning": f"Analyzed {len(frames)} frames. Splicing variance index: {round(max_diff, 2)}. "
                         f"Text-image semantic alignment score: {round(alignment_score, 2)}."
        }
