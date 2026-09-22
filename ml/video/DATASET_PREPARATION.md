# Dataset Preparation Specification

## 1. Dataset Selected: FaceForensics++ (Recommendation)
**Candidate Dataset**: [FaceForensics++ (FF++)](https://github.com/ondyari/FaceForensics)

## 2. Why it fits the current architecture
The current architecture uses a `ResNet18` visual backbone paired with an `LSTM` sequence model, focusing specifically on cropped faces via `MTCNN`. FF++ provides exactly the kind of data this architecture excels at detecting:
- It focuses strictly on facial manipulation (Deepfakes, Face2Face, FaceSwap).
- Videos feature clear, prominent faces, ensuring our `face_detection.py` (MTCNN) will easily succeed.
- It provides a massive amount of data in standard video formats (`.mp4`), which maps perfectly to our lazy-loading OpenCV `preprocessing.py` pipeline.

## 3. Dataset Access/Download Requirements
- Access requires submitting an explicit request form to the authors of FaceForensics++ via their GitHub repository.
- After approval, a download script is provided to pull the dataset. Note: The dataset is very large (~hundreds of GBs depending on quality). We recommend downloading the heavily compressed (`c40`) version for initial training on limited hardware.

## 4. Expected Raw Structure
When downloaded via the FF++ script, the raw structure separates original (real) videos and manipulated (fake) videos into different directories based on the manipulation technique, e.g.:
```text
FaceForensics++/
    original_sequences/
        youtube/c40/videos/
            000.mp4
            001.mp4
    manipulated_sequences/
        Deepfakes/c40/videos/
            000_001.mp4
        Face2Face/c40/videos/
            000_001.mp4
```

## 5. Normalized Project Structure
The `ml/video/dataset.py` script requires a strictly normalized structure:
```text
dataset/
    train/
        real/
            000.mp4
            001.mp4
        fake/
            000_001.mp4 (Deepfakes)
            000_001_f2f.mp4 (Face2Face)
    val/
        real/
        fake/
    test/
        real/
        fake/
```

## 6. Label Mapping
- All videos originating from `original_sequences` map to **Label 0 (Real)**.
- All videos originating from `manipulated_sequences` map to **Label 1 (Fake)**.

## 7. Train/Validation/Test Split Strategy
FaceForensics++ provides official JSON split files mapping video IDs to train/val/test buckets. 
- You MUST use the official FF++ splits. 
- A custom script must be written to read the official JSON and move/symlink the `.mp4` files from the raw download directories into our normalized `dataset/train|val|test/real|fake` structure.

## 8. Video-level Leakage Prevention
**CRITICAL**: Frame-level data leakage occurs if frames from the same video appear in both the training and test sets. 
- **Solution**: Because our pipeline uses video-level splits (entire `.mp4` files reside exclusively in `train/`, `val/`, or `test/`), frame-level leakage is structurally impossible.
- **Identity Leakage**: Deepfake datasets can leak identity (e.g., Actor A is in both train and test sets). By adhering strictly to the official FF++ split JSONs, identity leakage is inherently prevented by the dataset authors.

## 9. Frame Sampling Strategy
Our `config.yaml` controls this. 
- Default is `target_fps = 5` and `max_frames = 30`. 
- This means a 6-second chunk of the video is sampled. No pre-extraction of frames to disk is required.

## 10. Face Detection/Cropping Strategy
The MTCNN face detector runs lazily during data loading. It extracts the largest bounding box and falls back to a center crop if no face is detected. No offline face-cropping script is required.

## 11. Preprocessing
No physical image manipulation (resizing/cropping) on disk is required. The `dataset.py` pipeline handles everything directly from the `.mp4` via OpenCV.

## 12. Expected Dataset Statistics
- ~1,000 Real Videos.
- ~4,000 Fake Videos (across 4 manipulation techniques).
- **Class Imbalance**: Fake videos outnumber Real videos 4:1. The loss function in `train.py` may require class weights (e.g., `pos_weight`) if the model overfits to "Fake".

## 13. Known Limitations
- The lazy-loading pipeline (extracting frames and detecting faces *during* training) heavily bottlenecks the GPU data-loader. In production, caching the cropped face tensors to `.pt` files on disk prior to training is highly recommended.

## 14. Exact Next Command/Script Needed
To prepare this dataset, the ML team must run a custom script (to be written) that symlinks the downloaded FF++ videos into the normalized structure:
```bash
python ml/video/scripts/prepare_ffplus.py --source /path/to/raw/FF++ --dest /path/to/project/dataset
```
After normalization, run the validator:
```bash
python ml/video/validate_dataset.py --data_dir /path/to/project/dataset
```
