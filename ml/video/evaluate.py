import os
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from typing import Dict, Any

from .dataset import DeepfakeVideoDataset
from .model import DeepfakeVideoModel
from .train import get_device, load_config

def evaluate_model(data_dir: str, checkpoint_path: str, config_path: str = "config.yaml"):
    config = load_config(config_path)
    device = get_device(config)
    print(f"Evaluating on device: {device}")
    
    batch_size = config.get("training", {}).get("batch_size", 8)
    
    # Initialize Dataset and DataLoader
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
    
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs, labels = inputs.to(device), labels.to(device).float()
            video_prob, _ = model(inputs)
            
            predictions = (video_prob.squeeze(-1) > 0.5).float()
            
            for i in range(len(labels)):
                pred = int(predictions[i].item())
                truth = int(labels[i].item())
                
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

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Evaluate Video Deepfake Model")
    parser.add_argument("--data_dir", type=str, required=True, help="Path to dataset directory (containing test folder)")
    parser.add_argument("--checkpoint", type=str, required=True, help="Path to model checkpoint")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to config file")
    
    args = parser.parse_args()
    evaluate_model(args.data_dir, args.checkpoint, args.config)
