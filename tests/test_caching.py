import os
import torch
import pytest

from ml.video.dataset import CachedFeatureDataset
from ml.video.model import DeepfakeVideoModel

def test_cache_loading_and_shape(tmp_path):
    # Setup dummy cache directory
    real_dir = tmp_path / "real"
    fake_dir = tmp_path / "fake"
    real_dir.mkdir()
    fake_dir.mkdir()
    
    # Create a dummy valid feature tensor (max_frames=30, features=512)
    dummy_tensor_real = torch.randn((30, 512))
    dummy_tensor_fake = torch.randn((30, 512))
    
    torch.save(dummy_tensor_real, real_dir / "vid1.pt")
    torch.save(dummy_tensor_fake, fake_dir / "vid2.pt")
    
    # Also add a corrupted file to test the exception handling fallback
    with open(real_dir / "corrupted.pt", "wb") as f:
        f.write(b"not a valid torch tensor")
        
    dataset = CachedFeatureDataset(data_dir=str(tmp_path))
    
    # We expect 3 videos
    assert len(dataset) == 3
    
    # Fetch them (order is glob dependent)
    for i in range(3):
        tensor, label = dataset[i]
        assert tensor.shape == (30, 512)
        assert label in [0, 1]

def test_forward_features():
    model = DeepfakeVideoModel()
    
    # Batch size 2, Seq length 30, Features 512
    dummy_features = torch.randn((2, 30, 512))
    
    video_prob, frame_probs = model.forward_features(dummy_features)
    
    assert video_prob.shape == (2, 1)
    assert frame_probs.shape == (2, 30, 1)
    assert torch.is_tensor(video_prob)
