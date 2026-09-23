import os
import csv
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from typing import Dict, Any

from .dataset import DeepfakeVideoDataset, CachedFeatureDataset
from .model import DeepfakeVideoModel
from .train import get_device, load_config

def evaluate_model(data_dir: str, checkpoint_path: str, config_path: str = "config.yaml", cache_dir: str = None, export_csv: str = None):
    config = load_config(config_path)
    device = get_device(config)
    print(f"Evaluating on device: {device}")
    
    batch_size = config.get("training", {}).get("batch_size", 8)
    
    # Initialize Dataset and DataLoader
    if cache_dir:
        print(f"Using cached features from: {cache_dir}")
        test_dataset = CachedFeatureDataset(data_dir=os.path.join(cache_dir, 'test'), device=str(device))
    else:
        print(f"Using raw videos from: {data_dir}")
        test_dataset = DeepfakeVideoDataset(data_dir=os.path.join(data_dir, 'test'), config_path=config_path, device=str(device))
    
    if len(test_dataset) == 0:
        print("Warning: Test dataset is empty. Check data directory.")
        return
        
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    
    # Initialize Model
    model = DeepfakeVideoModel(config_path=config_path)
    
    # Load checkpoint
    if os.path.exists(checkpoint_path):
        model.load_state_dict(torch.load(checkpoint_path, map_location=device))
        print(f"Loaded checkpoint: {checkpoint_path}")
    else:
        print(f"Warning: Checkpoint {checkpoint_path} not found. Evaluating with random weights.")
        
    model = model.to(device)
    model.eval()
    
    # Metrics
    tp = 0
    tn = 0
    fp = 0
    fn = 0
    total_videos = 0
    
    csv_file = None
    csv_writer = None
    if export_csv:
        csv_file = open(export_csv, mode='w', newline='', encoding='utf-8')
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["filename", "path", "true_label", "predicted_label", "confidence", "correct", "error_type"])
        
    global_idx = 0
    
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs, labels = inputs.to(device), labels.to(device).float()
            if cache_dir:
                video_prob, _ = model.forward_features(inputs)
            else:
                video_prob, _ = model(inputs)
            
            predictions = (torch.sigmoid(video_prob.squeeze(-1)) > 0.5).float()
            
            for i in range(len(labels)):
                pred = int(predictions[i].item())
                truth = int(labels[i].item())
                
                if csv_writer:
                    prob = float(torch.sigmoid(video_prob.squeeze(-1))[i].item())
                    if cache_dir:
                        video_path = test_dataset.features[global_idx][0]
                    else:
                        video_path = test_dataset.videos[global_idx][0]
                        
                    filename = os.path.basename(video_path)
                    correct = (pred == truth)
                    
                    error_type = ""
                    if truth == 0 and pred == 1:
                        error_type = "false_positive"
                    elif truth == 1 and pred == 0:
                        error_type = "false_negative"
                        
                    csv_writer.writerow([
                        filename,
                        video_path,
                        "fake" if truth == 1 else "real",
                        "fake" if pred == 1 else "real",
                        f"{prob:.4f}",
                        correct,
                        error_type
                    ])
                    
                global_idx += 1
                
                if truth == 1 and pred == 1:
                    tp += 1
                elif truth == 0 and pred == 0:
                    tn += 1
                elif truth == 0 and pred == 1:
                    fp += 1
                elif truth == 1 and pred == 0:
                    fn += 1
                    
                total_videos += 1
                
    accuracy = (tp + tn) / max(1, total_videos)
    precision = tp / max(1, tp + fp)
    recall = tp / max(1, tp + fn)
    f1 = 2 * (precision * recall) / max(1e-7, precision + recall)
    
    print("\n--- Evaluation Results ---")
    print(f"Total Videos Evaluated: {total_videos}")
    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print("\nConfusion Matrix:")
    print(f"True Positive (Fake detected as Fake):  {tp}")
    print(f"True Negative (Real detected as Real):  {tn}")
    print(f"False Positive (Real detected as Fake): {fp}")
    print(f"False Negative (Fake detected as Real): {fn}")
    print("--------------------------")
    
    if csv_file:
        csv_file.close()
        print(f"\nExported {total_videos} rows to {export_csv}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Evaluate Video Deepfake Model")
    parser.add_argument("--data_dir", type=str, required=True, help="Path to raw dataset directory")
    parser.add_argument("--checkpoint", type=str, required=True, help="Path to model checkpoint")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to config file")
    parser.add_argument("--cache_dir", type=str, default=None, help="Path to cached features directory")
    parser.add_argument("--export_csv", type=str, default=None, help="Path to export per-video results to CSV")
    
    args = parser.parse_args()
    evaluate_model(args.data_dir, args.checkpoint, args.config, args.cache_dir, args.export_csv)
