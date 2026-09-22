import os
import glob
import json
import time
from typing import Dict, Any

from ml.video.preprocessing import VideoPreprocessor
from ml.video.face_detection import FaceDetector

def validate_dataset(data_dir: str, config_path: str = "config.yaml"):
    """
    Validates a prepared dataset directory structure and contents.
    Reports statistics, unreadable files, missing faces, and potential leakage.
    """
    print(f"--- Dataset Validation Report ---")
    print(f"Target Directory: {data_dir}")
    
    if not os.path.exists(data_dir):
        print(f"ERROR: Directory {data_dir} does not exist.")
        return
        
    preprocessor = VideoPreprocessor(config_path)
    # Use CPU for validation to avoid blocking GPU memory
    face_detector = FaceDetector(device='cpu', image_size=tuple(preprocessor.prep_config.get("image_size", [224, 224])))
    
    splits = ['train', 'val', 'test']
    classes = ['real', 'fake']
    extensions = ('.mp4', '.avi', '.mov')
    
    stats = {
        'total_videos': 0,
        'by_split': {s: 0 for s in splits},
        'by_class': {c: 0 for c in classes},
        'unreadable': 0,
        'no_face_detected': 0,
        'duplicate_names': []
    }
    
    all_filenames = set()
    leakage_suspects = []
    
    # 1. Structural Validation
    for split in splits:
        split_dir = os.path.join(data_dir, split)
        if not os.path.exists(split_dir):
            print(f"Warning: Split directory missing: {split_dir}")
            continue
            
        for cls in classes:
            cls_dir = os.path.join(split_dir, cls)
            if not os.path.exists(cls_dir):
                print(f"Warning: Class directory missing: {cls_dir}")
                continue
                
            videos = []
            for ext in extensions:
                videos.extend(glob.glob(os.path.join(cls_dir, f"*{ext}")))
                
            stats['by_split'][split] += len(videos)
            stats['by_class'][cls] += len(videos)
            stats['total_videos'] += len(videos)
            
            # Check for name collisions (potential leakage indicator)
            for v in videos:
                basename = os.path.basename(v)
                if basename in all_filenames:
                    leakage_suspects.append(basename)
                all_filenames.add(basename)
                
    print(f"\n1. Structural Statistics:")
    print(f"  Total Supported Videos: {stats['total_videos']}")
    print(f"  By Split: Train={stats['by_split']['train']}, Val={stats['by_split']['val']}, Test={stats['by_split']['test']}")
    print(f"  By Class: Real={stats['by_class']['real']}, Fake={stats['by_class']['fake']}")
    
    if stats['total_videos'] == 0:
        print("ERROR: No valid video files found in the dataset structure.")
        return
        
    # Class imbalance check
    if stats['by_class']['real'] > 0 and stats['by_class']['fake'] > 0:
        ratio = stats['by_class']['fake'] / stats['by_class']['real']
        print(f"  Fake-to-Real Ratio: {ratio:.2f}x")
        if ratio < 0.5 or ratio > 2.0:
            print("  Warning: Significant class imbalance detected.")
            
    # Leakage check
    print(f"\n2. Leakage Analysis:")
    if leakage_suspects:
        print(f"  WARNING: Found {len(leakage_suspects)} filenames appearing in multiple locations.")
        print(f"  Example suspects: {leakage_suspects[:5]}")
        print("  This strongly indicates frame-level leakage or duplicate video placements across train/val/test splits!")
    else:
        print("  PASS: No duplicate filenames detected across splits. Video-level separation appears intact.")
        
    # 3. Content Validation (Sampling)
    print(f"\n3. Content Validation (Checking up to 5 random videos from each class for readability/faces)...")
    
    import random
    all_videos = []
    for split in splits:
        for cls in classes:
            path = os.path.join(data_dir, split, cls)
            if os.path.exists(path):
                for ext in extensions:
                    all_videos.extend(glob.glob(os.path.join(path, f"*{ext}")))
                    
    sample_size = min(10, len(all_videos))
    sample_videos = random.sample(all_videos, sample_size)
    
    for v in sample_videos:
        try:
            frames = preprocessor.sample_frames(v)
            if not frames:
                print(f"  [ERROR] Unreadable or empty video: {v}")
                stats['unreadable'] += 1
                continue
                
            # Check face detection on first frame
            _, found = face_detector.detect_and_crop(frames[0][1])
            if not found:
                print(f"  [WARN] No face detected in first sampled frame of: {v}")
                stats['no_face_detected'] += 1
            else:
                print(f"  [PASS] Read successful and face detected: {os.path.basename(v)}")
                
        except Exception as e:
            print(f"  [ERROR] Processing failed for {v}: {e}")
            stats['unreadable'] += 1
            
    print(f"\n--- Validation Complete ---")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, required=True, help="Path to normalized dataset directory")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to config file")
    
    args = parser.parse_args()
    validate_dataset(args.data_dir, args.config)
