# Video Deepfake Detection Module (Phase 4)

This module provides a complete, modular PyTorch pipeline for video deepfake detection. It is designed to integrate seamlessly with the FastAPI backend while maintaining isolation for ML research and experimentation.

## Architecture

The pipeline follows a modular sequence:
1. **Video Preprocessing** (`preprocessing.py`): Robust extraction of frames using OpenCV without loading the entire video into memory.
2. **Face Detection & Cropping** (`face_detection.py`): Uses MTCNN (`facenet-pytorch`) to isolate the most prominent face per frame. Includes a fallback mechanism if no face is found.
3. **Sequence Modeling** (`model.py`):
   - **Visual Backbone**: Pretrained CNN (`resnet18` or `efficientnet_b0` configurable).
   - **Temporal Model**: LSTM to model inter-frame relationships.
   - **Classifiers**: Frame-level classifier for evidence generation and video-level classifier for final prediction.
4. **Integration** (`inference.py` & `backend/app/services/analyzers/video_analyzer.py`): Adapts the ML outputs directly to the platform's `AnalysisResult` API schema.

## Currently Implemented

- Complete PyTorch Dataset abstraction supporting lazy loading.
- Preprocessing and MTCNN Face Cropping.
- Extensible ResNet18 + LSTM architecture.
- Full Training (`train.py`) and Evaluation (`evaluate.py`) loops.
- Inference pipeline generating structured prediction and suspicious frame ranges.
- Seamless backend API integration via `video_analyzer.py`.
- CPU and CUDA GPU support out-of-the-box.

## Future Work / Limitations

> [!WARNING]
> **No Pretrained Checkpoint Available**: The system architecture is fully implemented, but *without a trained deepfake checkpoint*, the `inference.py` script and the backend `VideoAnalyzer` will explicitly refuse to invent a prediction. They will return an `error` state stating that a trained model is required. **There is no trained deepfake detector currently committed.**

> [!TIP]
> **To ML Team**: You must train this model on a real dataset (like FaceForensics++ or DFDC) before deploying to production.
> Visual heatmap explainability (Grad-CAM) is planned as a future enhancement once the model weights are trained and stable.

## Configuration

Hyperparameters are managed via `config.yaml`:
- **preprocessing.target_fps**: FPS downsampling rate.
- **preprocessing.max_frames**: Max frames extracted (prevents memory overflow).
- **model.backbone_name**: CNN backbone (`resnet18`).
- **inference.suspicious_threshold**: Confidence threshold (default 0.5) to mark a frame as fake.

## Usage

### Dataset Structure
Ensure your dataset is structured before training:
```text
dataset/
├── train/
│   ├── real/
│   └── fake/
├── val/
│   ├── real/
│   └── fake/
└── test/
    ├── real/
    └── fake/
```

### Training
```bash
python ml/video/train.py --data_dir /path/to/dataset --config ml/video/config.yaml
```
Checkpoints will be saved automatically to `ml/video/checkpoints/` (which is git-ignored).

### Evaluation
```bash
python ml/video/evaluate.py --data_dir /path/to/dataset --checkpoint ml/video/checkpoints/best_model.pth
```
This generates Accuracy, Precision, Recall, F1, and a Confusion Matrix.

### Inference (Standalone)
```bash
python ml/video/inference.py --video sample.mp4
```
Outputs a JSON block compatible with the `AnalysisResult` contract.

## API Integration

The FastAPI backend automatically utilizes this pipeline. When a user uploads a video, `video_analyzer.py` executes `inference.py` in an asynchronous threadpool, ensuring the event loop remains unblocked.
