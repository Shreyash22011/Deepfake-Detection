import os
import torch
import numpy as np
import pytest

from ml.video.preprocessing import load_config
from ml.video.model import DeepfakeVideoModel
from ml.video.face_detection import FaceDetector
from ml.video.inference import group_suspicious_frames

def test_config_loading():
    # If this runs from tests/, it might not find config.yaml locally.
    # We'll use the robust fallback in load_config
    config = load_config()
    assert "preprocessing" in config
    assert "model" in config

def test_model_forward_pass():
    model = DeepfakeVideoModel()
    
    # Create a synthetic batch of frames (batch_size=2, seq_len=3, C=3, H=224, W=224)
    dummy_input = torch.randn((2, 3, 3, 224, 224))
    
    video_prob, frame_probs = model(dummy_input)
    
    assert video_prob.shape == (2, 1), "Video probability shape mismatch"
    assert frame_probs.shape == (2, 3, 1), "Frame probabilities shape mismatch"
    assert torch.all((video_prob >= 0.0) & (video_prob <= 1.0)), "Probabilities must be in [0, 1]"

def test_face_detector_fallback():
    detector = FaceDetector(device='cpu', image_size=(224, 224))
    
    # Create a synthetic noise image (very unlikely to have a face)
    dummy_image = np.random.randint(0, 255, (300, 400, 3), dtype=np.uint8)
    
    tensor, found = detector.detect_and_crop(dummy_image)
    
    assert not found, "Should not find a face in random noise"
    assert tensor.shape == (3, 224, 224), "Fallback crop shape mismatch"

def test_group_suspicious_frames():
    indices = [1, 2, 3, 5, 8, 9]
    ranges = group_suspicious_frames(indices)
    
    assert len(ranges) == 3
    assert ranges[0] == {"start_frame": 1, "end_frame": 3}
    assert ranges[1] == {"start_frame": 5, "end_frame": 5}
    assert ranges[2] == {"start_frame": 8, "end_frame": 9}
