import cv2
import yaml
import os
import math
from typing import List, Tuple, Dict, Any
import numpy as np

def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file."""
    if not os.path.exists(config_path):
        # Fallback to absolute path relative to this file if running from elsewhere
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, "config.yaml")
        
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

class VideoPreprocessor:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = load_config(config_path)
        self.prep_config = self.config.get("preprocessing", {})
        self.target_fps = self.prep_config.get("target_fps", 5)
        self.max_frames = self.prep_config.get("max_frames", 30)
        
    def extract_metadata(self, video_path: str) -> Dict[str, Any]:
        """Extract basic metadata from the video without loading all frames."""
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
            
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
            
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Handle cases where FPS or frame count cannot be read
        if fps <= 0 or math.isnan(fps):
            fps = 30.0  # fallback assumption
            
        duration = frame_count / fps if fps > 0 else 0.0
        
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        cap.release()
        
        return {
            "fps": fps,
            "frame_count": frame_count,
            "duration_seconds": duration,
            "resolution": (width, height)
        }
        
    def sample_frames(self, video_path: str) -> List[Tuple[int, np.ndarray]]:
        """
        Extracts frames from the video at the target FPS, up to max_frames.
        Returns a list of tuples: (frame_index, frame_image_rgb).
        Does not load the entire video into memory.
        """
        metadata = self.extract_metadata(video_path)
        original_fps = metadata["fps"]
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
            
        # Calculate frame skip interval
        # E.g., if original is 30 fps and target is 5 fps, we take every 6th frame
        frame_skip = max(1, int(round(original_fps / self.target_fps)))
        
        sampled_frames = []
        frame_idx = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Only keep frames that align with our target FPS
            if frame_idx % frame_skip == 0:
                # Convert BGR (OpenCV) to RGB (Standard for ML)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                sampled_frames.append((frame_idx, frame_rgb))
                
                # Stop if we hit the maximum number of frames to save memory
                if len(sampled_frames) >= self.max_frames:
                    break
                    
            frame_idx += 1
            
        cap.release()
        
        return sampled_frames

if __name__ == "__main__":
    # Simple self-test if run directly
    print("Video Preprocessor loaded.")
