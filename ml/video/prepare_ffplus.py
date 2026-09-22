import os
import glob
import random
import shutil
import argparse
from pathlib import Path

def setup_directories(out_dir: str):
    """Creates the normalized dataset structure."""
    splits = ['train', 'val', 'test']
    classes = ['real', 'fake']
    
    for split in splits:
        for cls in classes:
            path = os.path.join(out_dir, split, cls)
            os.makedirs(path, exist_ok=True)
            
def get_video_files(directory: str) -> list:
    """Recursively finds all mp4 files in a directory."""
    files = []
    for ext in ('*.mp4', '*.avi', '*.mov'):
        files.extend(glob.glob(os.path.join(directory, '**', ext), recursive=True))
    return files

def hardlink_or_copy(src: str, dst: str):
    """Attempts to hardlink to save space, falls back to copy if across drives."""
    if os.path.exists(dst):
        return # Skip if already exists
        
    try:
        os.link(src, dst)
    except OSError:
        # Cross-device link or unsupported filesystem, fallback to copy
        shutil.copy2(src, dst)

def main():
    parser = argparse.ArgumentParser(description="Prepare Kaggle FF++ dataset for training.")
    parser.add_argument("--source", type=str, required=True, help="Path to extracted Kaggle FF++ root folder")
    parser.add_argument("--dest", type=str, required=True, help="Path to output normalized dataset folder")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for deterministic splitting")
    parser.add_argument("--train_ratio", type=float, default=0.8, help="Train split ratio")
    parser.add_argument("--val_ratio", type=float, default=0.1, help="Validation split ratio")
    
    args = parser.parse_args()
    
    # 1. Inspect source paths
    source_real = os.path.join(args.source, 'original')
    source_fake = os.path.join(args.source, 'Deepfakes')
    
    if not os.path.exists(source_real):
        raise FileNotFoundError(f"Expected REAL directory not found: {source_real}")
    if not os.path.exists(source_fake):
        raise FileNotFoundError(f"Expected FAKE directory not found: {source_fake}")
        
    print(f"Source REAL: {source_real}")
    print(f"Source FAKE: {source_fake}")
    print(f"Destination: {args.dest}")
    
    # 2. Setup output structure
    setup_directories(args.dest)
    
    # 3. Gather files
    real_files = get_video_files(source_real)
    fake_files = get_video_files(source_fake)
    
    print(f"Found {len(real_files)} real videos and {len(fake_files)} fake videos.")
    
    if len(real_files) == 0 or len(fake_files) == 0:
        print("Error: No videos found. Check your source path and ensure videos are extracted.")
        return
        
    # 4. Deterministic Splitting
    # We sort the files first to ensure the seed produces exactly the same split regardless of OS file traversal order
    real_files.sort()
    fake_files.sort()
    
    random.seed(args.seed)
    random.shuffle(real_files)
    random.shuffle(fake_files)
    
    def split_list(lst: list, train_pct: float, val_pct: float):
        n = len(lst)
        train_end = int(n * train_pct)
        val_end = train_end + int(n * val_pct)
        return lst[:train_end], lst[train_end:val_end], lst[val_end:]
        
    real_train, real_val, real_test = split_list(real_files, args.train_ratio, args.val_ratio)
    fake_train, fake_val, fake_test = split_list(fake_files, args.train_ratio, args.val_ratio)
    
    splits = {
        'train': {'real': real_train, 'fake': fake_train},
        'val': {'real': real_val, 'fake': fake_val},
        'test': {'real': real_test, 'fake': fake_test},
    }
    
    # 5. Process files
    print("\nCopying/Hardlinking files to normalized structure...")
    
    stats = {'train': 0, 'val': 0, 'test': 0}
    
    for split_name, categories in splits.items():
        for category, files in categories.items():
            dest_dir = os.path.join(args.dest, split_name, category)
            for f in files:
                basename = os.path.basename(f)
                dest_path = os.path.join(dest_dir, basename)
                hardlink_or_copy(f, dest_path)
                stats[split_name] += 1
                
    print("\n--- Preparation Complete ---")
    print("Dataset Split Statistics (Video Level):")
    print(f"  Train: {stats['train']} videos")
    print(f"  Validation: {stats['val']} videos")
    print(f"  Test: {stats['test']} videos")
    print("\nNext step: Run ml/video/validate_dataset.py on your destination directory!")

if __name__ == "__main__":
    main()
