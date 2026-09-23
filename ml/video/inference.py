import os
import torch
import time
from typing import Dict, Any, List

from .preprocessing import VideoPreprocessor
from .face_detection import FaceDetector
from .model import DeepfakeVideoModel
from .train import get_device, load_config

def group_suspicious_frames(suspicious_indices: List[int], actual_frame_indices: List[int] = None) -> List[Dict[str, int]]:
    """Group consecutive suspicious frame indices into ranges."""
    if not suspicious_indices:
        return []
        
    if actual_frame_indices:
        # Map original frame index to its position in the sampled sequence
        seq_map = {orig: seq for seq, orig in enumerate(actual_frame_indices)}
        # Sort by sequence index
        sorted_suspicious = sorted(suspicious_indices, key=lambda x: seq_map.get(x, x))
        
        ranges = []
        start_orig = sorted_suspicious[0]
        prev_orig = start_orig
        
        for idx_orig in sorted_suspicious[1:]:
            # Check if they are adjacent in the actual sampled sequence
            if seq_map.get(idx_orig, -1) == seq_map.get(prev_orig, -2) + 1:
                prev_orig = idx_orig
            else:
                ranges.append({"start_frame": start_orig, "end_frame": prev_orig})
                start_orig = idx_orig
                prev_orig = idx_orig
                
        ranges.append({"start_frame": start_orig, "end_frame": prev_orig})
        return ranges
    else:
        # Fallback if no actual_frame_indices provided (legacy or un-strided)
        ranges = []
        start = suspicious_indices[0]
        prev = start
        
        for idx in suspicious_indices[1:]:
            if idx == prev + 1:
                prev = idx
            else:
                ranges.append({"start_frame": start, "end_frame": prev})
                start = idx
                prev = idx
                
        ranges.append({"start_frame": start, "end_frame": prev})
        return ranges

def run_inference(video_path: str, checkpoint_path: str = None, config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Run the complete video deepfake detection pipeline on a single video.
    Returns structured results compatible with the AnalysisResult API contract.
    """
    start_time = time.time()
    
    # Load Config and Device
    try:
        config = load_config(config_path)
    except FileNotFoundError:
        # Fallback to local config.yaml if paths are weird
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, "config.yaml")
        config = load_config(config_path)
        
    device = get_device(config)
    threshold = config.get("inference", {}).get("suspicious_threshold", 0.5)
    model_name = config.get("model", {}).get("backbone_name", "resnet18")
    image_size = config.get("preprocessing", {}).get("image_size", [224, 224])
    max_frames = config.get("preprocessing", {}).get("max_frames", 30)
    
    # Initialize Modules
    preprocessor = VideoPreprocessor(config_path)
    face_detector = FaceDetector(device=str(device), image_size=tuple(image_size))
    model = DeepfakeVideoModel(config_path=config_path)
    
    # Load Model Weights
    if checkpoint_path and os.path.exists(checkpoint_path):
        model.load_state_dict(torch.load(checkpoint_path, map_location=device))
    else:
        # Return explicitly that the model is untrained instead of inventing a random confidence
        return {
            "prediction": "error",
            "confidence": 0.0,
            "model_name": f"{model_name}_LSTM",
            "model_version": "untrained",
            "error": "Model checkpoint not found. Inference requires a trained deepfake model.",
            "evidence": {"note": "Deepfake model is architecturally implemented but not trained."},
            "processing_time_ms": int((time.time() - start_time) * 1000)
        }
        
    model = model.to(device)
    model.eval()
    
    # 1. Metadata & Frame Extraction
    try:
        metadata = preprocessor.extract_metadata(video_path)
        sampled_frames = preprocessor.sample_frames(video_path)
    except Exception as e:
        return {
            "prediction": "error",
            "confidence": 0.0,
            "error": str(e),
            "processing_time_ms": int((time.time() - start_time) * 1000)
        }
        
    if not sampled_frames:
        return {
            "prediction": "uncertain",
            "confidence": 0.0,
            "evidence": {"note": "No frames could be extracted from the video."},
            "processing_time_ms": int((time.time() - start_time) * 1000)
        }

    # 2. Face Detection & Cropping
    sequence = []
    actual_frame_indices = []
    
    face_detector.reset_tracking()
    
    for frame_idx, frame_rgb in sampled_frames:
        face_tensor, _ = face_detector.detect_and_crop(frame_rgb)
        sequence.append(face_tensor)
        actual_frame_indices.append(frame_idx)
        
    sequence_tensor = torch.stack(sequence)
    
    # Pad to max_frames for batch consistency if model expects fixed length, 
    # though our LSTM handles variable lengths via batch size 1 natively if we just unsqueeze.
    # We will pad just to be consistent with the dataset pipeline.
    if len(sequence_tensor) < max_frames:
        pad_size = max_frames - len(sequence_tensor)
        padding = torch.zeros((pad_size, 3, image_size[1], image_size[0]))
        sequence_tensor = torch.cat([sequence_tensor, padding], dim=0)

    # Add batch dimension -> (1, seq_len, C, H, W)
    sequence_tensor = sequence_tensor.unsqueeze(0).to(device)
    
    # 3. Model Forward Pass
    with torch.no_grad():
        video_prob_logits, frame_probs_logits = model(sequence_tensor)
        video_prob = torch.sigmoid(video_prob_logits)
        frame_probs = torch.sigmoid(frame_probs_logits)
        
    video_fake_prob = video_prob.item()
    confidence = max(video_fake_prob, 1 - video_fake_prob)
    prediction = "fake" if video_fake_prob > threshold else "real"
    
    # 4. Evidence Generation (Suspicious Frames)
    frame_probs_list = frame_probs.squeeze(0).squeeze(-1).cpu().numpy().tolist()
    
    suspicious_frames = []
    frame_scores = {}
    
    # Only evaluate the frames that actually came from the video (ignore padding)
    num_actual = len(actual_frame_indices)
    for i in range(num_actual):
        orig_idx = actual_frame_indices[i]
        prob = frame_probs_list[i]
        frame_scores[orig_idx] = prob
        
        if prob > threshold:
            suspicious_frames.append(orig_idx)
            
    suspicious_ranges = group_suspicious_frames(suspicious_frames, actual_frame_indices)
    
    processing_time = int((time.time() - start_time) * 1000)
    
    result = {
        "prediction": prediction,
        "confidence": round(float(confidence), 4),
        "model_name": f"{model_name}_LSTM",
        "model_version": "1.0.0-prototype",
        "evidence": {
            "total_frames_sampled": num_actual,
            "suspicious_frames": suspicious_frames,
            "suspicious_ranges": suspicious_ranges,
            "video_metadata": metadata,
            "note": "Visual heatmap explainability (Grad-CAM) is planned for a future enhancement."
        },
        "processing_time_ms": processing_time
    }
    
    return result

if __name__ == "__main__":
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Run Video Deepfake Inference")
    parser.add_argument("--video", type=str, required=True, help="Path to input video")
    parser.add_argument("--checkpoint", type=str, default=None, help="Path to model checkpoint")
    
    args = parser.parse_args()
    result = run_inference(args.video, args.checkpoint)
    
    print(json.dumps(result, indent=2))
