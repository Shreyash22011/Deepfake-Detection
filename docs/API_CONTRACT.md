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
**Request:** `multipart/form-data`
- `file`: The media file to analyze (image, video, audio).

**Response:** `AnalysisRecord`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "video.mp4",
  "media_type": "video",
  "status": "completed",
  "result": {
    "prediction": "fake",
    "confidence": 0.88,
    "model_name": "MockVideoModel",
    "model_version": "1.1.0",
    "evidence": {
      "suspicious_frames": [12, 45, 112]
    },
    "processing_time_ms": 2000
  },
  "error_message": null,
  "created_at": "2026-09-21T12:00:00Z",
  "updated_at": "2026-09-21T12:00:02Z"
}
```

### `GET /api/analyses`
Retrieves a list of previous analyses from MongoDB.
**Response:** `List[AnalysisRecord]`

### `GET /api/analyses/{analysis_id}`
Retrieves details of a specific analysis from MongoDB.
**Response:** `AnalysisRecord`

### `GET /api/reports/{analysis_id}`
Retrieves or generates a PDF report for a specific analysis.

## Model Result Contract (`AnalysisResult`)

All ML models, regardless of modality (image, video, audio), must implement `BaseAnalyzer` and return data conceptually equivalent to the following schema:

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
