import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.cuda.amp import autocast, GradScaler
from typing import Dict, Any

from .dataset import DeepfakeVideoDataset, CachedFeatureDataset
from .model import DeepfakeVideoModel
from .preprocessing import load_config

def get_device(config: Dict[str, Any]) -> torch.device:
    device_cfg = config.get("training", {}).get("device", "auto")
    if device_cfg == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device(device_cfg)

def train_model(data_dir: str, config_path: str = "config.yaml", cache_dir: str = None, init_checkpoint: str = None, smoke_test: bool = False):
    # Load configuration
    config = load_config(config_path)
    train_cfg = config.get("training", {})
    
    device = get_device(config)
    print(f"Using device: {device}")
    
    if smoke_test:
        print("--- SMOKE TEST MODE ACTIVATED ---")
        epochs = 1
    else:
        epochs = train_cfg.get("epochs", 10)
        
    batch_size = train_cfg.get("batch_size", 8)
    lr = train_cfg.get("learning_rate", 0.0001)
    
    # Initialize Dataset and DataLoader
    if cache_dir:
        print(f"Using cached features from: {cache_dir}")
        train_dataset = CachedFeatureDataset(data_dir=os.path.join(cache_dir, 'train'), device=str(device))
        val_dataset = CachedFeatureDataset(data_dir=os.path.join(cache_dir, 'val'), device=str(device))
    else:
        print(f"Using raw videos from: {data_dir}")
        train_dataset = DeepfakeVideoDataset(data_dir=os.path.join(data_dir, 'train'), config_path=config_path, device=str(device))
        val_dataset = DeepfakeVideoDataset(data_dir=os.path.join(data_dir, 'val'), config_path=config_path, device=str(device))
    
    if len(train_dataset) == 0:
        print("Warning: Train dataset is empty. Check data directory.")
        return
        
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    # Initialize Model, Loss, Optimizer
    # Initialize Model, Loss, Optimizer
    model = DeepfakeVideoModel(config_path=config_path)
    
    if init_checkpoint and os.path.exists(init_checkpoint):
        print(f"Loading initialization checkpoint: {init_checkpoint}")
        model.load_state_dict(torch.load(init_checkpoint, map_location='cpu'), strict=False)
        
    model = model.to(device)
    
    # Calculate pos_weight for class imbalance (363 Real/Negatives, 726 Fake/Positives -> pos_weight = 363 / 726 = 0.5)
    # This down-weights the majority Fake class to balance the loss.
    pos_weight = torch.tensor([0.5]).to(device)
    criterion_video = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    # For frames, we also use BCEWithLogitsLoss. The target will just be the video label broadcasted to all frames
    criterion_frame = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    
    
    if hasattr(model, 'backbone') and config.get("model", {}).get("fine_tune_layer4", False):
        optimizer = optim.Adam([
            {'params': model.backbone[7].parameters(), 'lr': 1e-5},
            {'params': model.lstm.parameters(), 'lr': lr},
            {'params': model.frame_classifier.parameters(), 'lr': lr},
            {'params': model.video_classifier.parameters(), 'lr': lr}
        ])
        print("Using dual learning rates (1e-5 for layer4, 1e-4 for LSTM/Classifier).")
    else:
        optimizer = optim.Adam(model.parameters(), lr=lr)
        
    if smoke_test:
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        frozen_params = sum(p.numel() for p in model.parameters() if not p.requires_grad)
        print(f"Trainable Parameters: {trainable_params:,}")
        print(f"Frozen Parameters:    {frozen_params:,}")
        print(f"AMP Active (cuda):    {device.type == 'cuda'}")
        
    scaler = GradScaler()
    
    checkpoint_dir = os.path.join(os.path.dirname(__file__), 'checkpoints')
    os.makedirs(checkpoint_dir, exist_ok=True)
    
    best_val_loss = float('inf')
    
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        
        for i, (inputs, labels) in enumerate(train_loader):
            if smoke_test and i >= 2:
                print("Smoke test: stopping train loop after 2 batches")
                break
                
            inputs, labels = inputs.to(device), labels.to(device).float().unsqueeze(1)
            
            optimizer.zero_grad()
            
            with autocast(enabled=(device.type == 'cuda')):
                if cache_dir:
                    video_prob, frame_probs = model.forward_features(inputs)
                else:
                    video_prob, frame_probs = model(inputs)
                
                # Loss computation
                loss_video = criterion_video(video_prob, labels)
                
                # Broadcast labels for frame loss calculation
                labels_frame = labels.unsqueeze(2).expand_as(frame_probs)
                loss_frame = criterion_frame(frame_probs, labels_frame)
                
                # Total loss (weighted)
                loss = 0.7 * loss_video + 0.3 * loss_frame
            
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            
            if smoke_test and i == 0 and hasattr(model, 'backbone') and config.get("model", {}).get("fine_tune_layer4", False):
                has_grad = model.backbone[7][0].conv1.weight.grad is not None
                print(f"Smoke test: layer4 conv1.weight receives gradients? {has_grad}")
            
            running_loss += loss.item()
            
        train_loss = running_loss / len(train_loader)
        
        # Validation Phase
        model.eval()
        val_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for i, (inputs, labels) in enumerate(val_loader):
                if smoke_test and i >= 2:
                    print("Smoke test: stopping val loop after 2 batches")
                    break
                    
                inputs, labels = inputs.to(device), labels.to(device).float().unsqueeze(1)
                
                with autocast(enabled=(device.type == 'cuda')):
                    if cache_dir:
                        video_prob, frame_probs = model.forward_features(inputs)
                    else:
                        video_prob, frame_probs = model(inputs)
                    
                    v_loss = criterion_video(video_prob, labels)
                    f_loss = criterion_frame(frame_probs, labels.unsqueeze(2).expand_as(frame_probs))
                    
                    val_loss += (0.7 * v_loss + 0.3 * f_loss).item()
                
                predicted = (torch.sigmoid(video_prob) > 0.5).float()
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
                
        val_loss /= max(1, len(val_loader))
        accuracy = 100 * correct / max(1, total)
        
        print(f"Epoch [{epoch+1}/{epochs}] - Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | Val Acc: {accuracy:.2f}%")
        
        if smoke_test and device.type == 'cuda':
            print(f"GPU Memory Allocated: {torch.cuda.memory_allocated()/1024**2:.2f} MB")
            print(f"GPU Memory Reserved:  {torch.cuda.memory_reserved()/1024**2:.2f} MB")
            
        # Checkpoint saving
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            
            # Differentiate baseline cache training, finetuning, and raw video training
            if smoke_test:
                checkpoint_name = 'best_smoketest_model.pth'
            elif cache_dir:
                checkpoint_name = 'best_cached_model.pth'
            elif config.get("model", {}).get("fine_tune_layer4", False):
                checkpoint_name = 'best_finetuned_model.pth'
            else:
                checkpoint_name = 'best_raw_model.pth'
            torch.save(model.state_dict(), os.path.join(checkpoint_dir, checkpoint_name))
            print(f"Saved new best model with Val Loss: {best_val_loss:.4f} as {checkpoint_name}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Train Deepfake Video Model")
    parser.add_argument("--data_dir", type=str, required=True, help="Path to raw dataset directory")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to config.yaml")
    parser.add_argument("--cache_dir", type=str, default=None, help="Path to cached features directory")
    parser.add_argument("--init_checkpoint", type=str, default=None, help="Path to initialization checkpoint")
    parser.add_argument("--smoke_test", action="store_true", help="Run a quick smoke test")
    
    args = parser.parse_args()
    train_model(args.data_dir, args.config, args.cache_dir, args.init_checkpoint, args.smoke_test)
