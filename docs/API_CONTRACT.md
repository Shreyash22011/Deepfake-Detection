# API and Model Result Contract

## API Endpoints

### `GET /api/health`
Checks if the backend is running.
**Response:**
```json
{
  "status": "ok",
  "message": "Backend is running"
}
```

### `POST /api/analyze`
Submits media for analysis.
**Request Body:**
```json
{
  "media_url": "optional string or file upload depending on implementation",
  "media_type": "image | video | audio"
}
```
**Response:** `AnalysisResult` (see below)

### `GET /api/analyses`
Retrieves a list of previous analyses.

### `GET /api/analyses/{analysis_id}`
Retrieves details of a specific analysis.

### `GET /api/reports/{analysis_id}`
Retrieves or generates a PDF report for a specific analysis.

## Model Result Contract (`AnalysisResult`)

All ML models, regardless of modality (image, video, audio), must eventually return data conceptually equivalent to the following schema:

```json
{
  "prediction": "real | fake | synthetic | uncertain",
  "confidence": 0.85,
  "model_name": "efficientnet_v2",
  "model_version": "1.0.0",
  "evidence": {
    "suspicious_regions": [ [10, 20, 50, 60] ],
    "frame_scores": [],
    "heatmap_url": "..."
  },
  "processing_time_ms": 1250
}
```

### Modality-Specific Evidence
- **Image**: Bounding boxes, heatmaps (Grad-CAM), structural similarity metrics.
- **Video**: Temporal consistency scores, frame-by-frame confidence, specific suspicious frames.
- **Audio**: Spectrogram anomalies, deep voice artifacts, specific timestamp segments.
