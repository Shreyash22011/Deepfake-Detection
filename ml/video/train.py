import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from typing import Dict, Any

from .dataset import DeepfakeVideoDataset
from .model import DeepfakeVideoModel
from .preprocessing import load_config

def get_device(config: Dict[str, Any]) -> torch.device:
    device_cfg = config.get("training", {}).get("device", "auto")
    if device_cfg == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device(device_cfg)

def train_model(data_dir: str, config_path: str = "config.yaml"):
    config = load_config(config_path)
    train_cfg = config.get("training", {})
    
    device = get_device(config)
    print(f"Using device: {device}")
    
    batch_size = train_cfg.get("batch_size", 8)
    lr = train_cfg.get("learning_rate", 0.0001)
    epochs = train_cfg.get("epochs", 10)
    
    # Initialize Dataset and DataLoader
    train_dataset = DeepfakeVideoDataset(data_dir=os.path.join(data_dir, 'train'), config_path=config_path, device=str(device))
    val_dataset = DeepfakeVideoDataset(data_dir=os.path.join(data_dir, 'val'), config_path=config_path, device=str(device))
    
    if len(train_dataset) == 0:
        print("Warning: Train dataset is empty. Check data directory.")
        return
        
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    # Initialize Model, Loss, Optimizer
    model = DeepfakeVideoModel(config_path=config_path).to(device)
    criterion_video = nn.BCELoss()
    # For frames, we also use BCELoss. The target will just be the video label broadcasted to all frames
    criterion_frame = nn.BCELoss()
    
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    checkpoint_dir = os.path.join(os.path.dirname(__file__), 'checkpoints')
    os.makedirs(checkpoint_dir, exist_ok=True)
    
    best_val_loss = float('inf')
    
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        
        for i, (inputs, labels) in enumerate(train_loader):
            inputs, labels = inputs.to(device), labels.to(device).float().unsqueeze(1)
            
            optimizer.zero_grad()
            
            video_prob, frame_probs = model(inputs)
            
            # Loss computation
            loss_video = criterion_video(video_prob, labels)
            
            # Broadcast labels for frame loss calculation
            labels_frame = labels.unsqueeze(2).expand_as(frame_probs)
            loss_frame = criterion_frame(frame_probs, labels_frame)
            
            # Total loss (weighted)
            loss = 0.7 * loss_video + 0.3 * loss_frame
            
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            
        train_loss = running_loss / len(train_loader)
        
        # Validation Phase
        model.eval()
        val_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device).float().unsqueeze(1)
                video_prob, frame_probs = model(inputs)
                
                v_loss = criterion_video(video_prob, labels)
                f_loss = criterion_frame(frame_probs, labels.unsqueeze(2).expand_as(frame_probs))
                
                val_loss += (0.7 * v_loss + 0.3 * f_loss).item()
                
                predicted = (video_prob > 0.5).float()
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
                
        val_loss /= max(1, len(val_loader))
        accuracy = 100 * correct / max(1, total)
        
        print(f"Epoch [{epoch+1}/{epochs}] - Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | Val Acc: {accuracy:.2f}%")
        
        # Checkpoint saving
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), os.path.join(checkpoint_dir, 'best_model.pth'))
            print(f"Saved new best model with Val Loss: {best_val_loss:.4f}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Train Video Deepfake Model")
    parser.add_argument("--data_dir", type=str, required=True, help="Path to dataset directory (containing train/val folders)")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to config file")
    
    args = parser.parse_args()
    train_model(args.data_dir, args.config)
