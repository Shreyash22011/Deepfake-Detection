import os
import argparse
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm

from .dataset import DeepfakeVideoDataset
from .model import DeepfakeVideoModel
from .train import get_device

def extract_features(data_dir: str, cache_dir: str, config_path: str = "config.yaml"):
    device = get_device({"training": {"device": "auto"}})
    print(f"Using device: {device} for feature extraction")
    
    # Initialize the model to get the frozen backbone
    model = DeepfakeVideoModel(config_path=config_path).to(device)
    model.eval()
    
    for split in ['train', 'val', 'test']:
        split_data_dir = os.path.join(data_dir, split)
        if not os.path.exists(split_data_dir):
            continue
            
        print(f"Processing split: {split}")
        # The dataset reads real/fake directories inside the split
        dataset = DeepfakeVideoDataset(data_dir=split_data_dir, config_path=config_path, device=str(device))
        
        # Ensure output directories exist
        real_cache_dir = os.path.join(cache_dir, split, 'real')
        fake_cache_dir = os.path.join(cache_dir, split, 'fake')
        os.makedirs(real_cache_dir, exist_ok=True)
        os.makedirs(fake_cache_dir, exist_ok=True)
        
        for idx in tqdm(range(len(dataset)), desc=f"Extracting {split}"):
            video_path, label = dataset.videos[idx]
            
            # Determine output path
            video_filename = os.path.basename(video_path)
            cache_filename = os.path.splitext(video_filename)[0] + ".pt"
            
            if label == 0:
                out_path = os.path.join(real_cache_dir, cache_filename)
            else:
                out_path = os.path.join(fake_cache_dir, cache_filename)
                
            # Skip if valid cache exists
            if os.path.exists(out_path):
                try:
                    # Quick validity check
                    cached = torch.load(out_path, map_location='cpu', weights_only=True)
                    if cached.shape[1] == 512:
                        continue
                except:
                    pass # corrupted, recompute
            
            # Retrieve sequence from raw dataset (runs MTCNN)
            sequence_tensor, _ = dataset[idx]
            
            # Run through ResNet18 backbone
            with torch.no_grad():
                # sequence_tensor shape: (max_frames, C, H, W)
                sequence_tensor = sequence_tensor.to(device).unsqueeze(0) # (1, max_frames, C, H, W)
                
                batch_size, seq_len, c, h, w = sequence_tensor.size()
                x = sequence_tensor.view(batch_size * seq_len, c, h, w)
                
                features = model.backbone(x) # (max_frames, 512, 1, 1)
                features = features.view(seq_len, model.feature_dim) # (max_frames, 512)
                
            # Save to disk
            torch.save(features.cpu(), out_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract ResNet18 features for DFD dataset")
    parser.add_argument("--data_dir", type=str, required=True, help="Path to raw dataset")
    parser.add_argument("--cache_dir", type=str, required=True, help="Path to save extracted features")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to config.yaml")
    
    args = parser.parse_args()
    extract_features(args.data_dir, args.cache_dir, args.config)
