import os
import glob
import torch
from torch.utils.data import Dataset
from typing import List, Tuple, Dict, Any

from .preprocessing import VideoPreprocessor
from .face_detection import FaceDetector

class DeepfakeVideoDataset(Dataset):
    def __init__(self, data_dir: str, config_path: str = "config.yaml", device: str = 'cpu'):
        """
        Assumes directory structure:
        data_dir/
            real/
                vid1.mp4
                vid2.mp4
            fake/
                vid3.mp4
                ...
        """
        super().__init__()
        self.data_dir = data_dir
        self.preprocessor = VideoPreprocessor(config_path)
        
        # Load config to get image size
        self.image_size = self.preprocessor.config.get("preprocessing", {}).get("image_size", [224, 224])
        self.max_frames = self.preprocessor.config.get("preprocessing", {}).get("max_frames", 30)
        
        self.face_detector = FaceDetector(device=device, image_size=tuple(self.image_size))
        
        self.videos: List[Tuple[str, int]] = []
        self._load_dataset()
        
    def _load_dataset(self):
        real_dir = os.path.join(self.data_dir, 'real')
        fake_dir = os.path.join(self.data_dir, 'fake')
        
        if os.path.exists(real_dir):
            for ext in ('*.mp4', '*.avi', '*.mov'):
                for path in glob.glob(os.path.join(real_dir, ext)):
                    self.videos.append((path, 0)) # 0 = real
                    
        if os.path.exists(fake_dir):
            for ext in ('*.mp4', '*.avi', '*.mov'):
                for path in glob.glob(os.path.join(fake_dir, ext)):
                    self.videos.append((path, 1)) # 1 = fake
                    
    def __len__(self) -> int:
        return len(self.videos)
        
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        video_path, label = self.videos[idx]
        
        # Extract frames (RGB)
        try:
            sampled_frames = self.preprocessor.sample_frames(video_path)
        except Exception as e:
            print(f"Warning: Failed to read {video_path}: {e}")
            sampled_frames = []
            
        sequence = []
        for frame_idx, frame_rgb in sampled_frames:
            # Detect and crop face
            face_tensor, found = self.face_detector.detect_and_crop(frame_rgb)
            sequence.append(face_tensor)
            
        # Pad or truncate sequence
        if len(sequence) == 0:
            # Return empty/zero tensor if video is completely unreadable
            sequence_tensor = torch.zeros((self.max_frames, 3, self.image_size[1], self.image_size[0]))
        else:
            sequence_tensor = torch.stack(sequence)
            
            # Truncate if too long (shouldn't happen due to preprocessor, but safe)
            if len(sequence_tensor) > self.max_frames:
                sequence_tensor = sequence_tensor[:self.max_frames]
                
            # Pad if too short
            if len(sequence_tensor) < self.max_frames:
                pad_size = self.max_frames - len(sequence_tensor)
                padding = torch.zeros((pad_size, 3, self.image_size[1], self.image_size[0]))
                sequence_tensor = torch.cat([sequence_tensor, padding], dim=0)
                
        return sequence_tensor, label

if __name__ == "__main__":
    print("Dataset module loaded.")
