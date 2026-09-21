# AI Media Authenticity Platform

## Project Purpose
Deepfake Detection and Classification from Image and Video using Deep Learning Techniques. This platform is designed as a modular system supporting image, video, and audio analysis to identify manipulated or AI-generated media.

## Technology Stack
- **Frontend**: Next.js, React, TypeScript, Tailwind CSS
- **Backend**: FastAPI (Python 3)
- **Database**: MongoDB
- **ML Frameworks**: PyTorch, OpenCV, (Librosa/FFmpeg planned)

## Repository Structure
```
/
├── frontend/         # Next.js web application
├── backend/          # FastAPI server and API endpoints
├── ml/               # Machine Learning modules
│   ├── image/        # Image analysis models
│   ├── video/        # Video analysis models
│   └── audio/        # Audio analysis models
├── metadata/         # Metadata extraction logic
├── explainability/   # Heatmap generation (e.g., Grad-CAM)
├── fusion/           # Multimodal fusion logic
├── reports/          # PDF forensic report generation
├── database/         # Database models and interactions
├── tests/            # Automated test suite
└── docs/             # Extensive project documentation
```

## Running the Application Locally

### Backend
1. `cd backend`
2. Create and activate a virtual environment: `python -m venv venv` and `source venv/bin/activate` (or `venv\Scripts\activate` on Windows)
3. Install dependencies: `pip install -r requirements.txt`
4. Run server: `uvicorn app.main:app --reload`
5. The API is available at `http://localhost:8000`

### Frontend
1. `cd frontend`
2. Install dependencies: `npm install`
3. Run dev server: `npm run dev`
4. The frontend is available at `http://localhost:3000`

## Environment Variables
- Backend requires `.env` with `DATABASE_URL` (currently defaults to local MongoDB).
- Frontend requires `.env.local` with `NEXT_PUBLIC_API_URL` pointing to the backend.

## Implementation Status
- **Phase 1 & 2 (Complete)**: Initial repository setup, API contracts, full frontend UI shell.
- **Phase 3 (Complete)**: Backend orchestration, MongoDB database integration, and `BaseAnalyzer` abstraction layer with mock models.
- **Phase 4 (Upcoming)**: ML Prototyping.

### Note for ML Team
The backend architecture is currently solid and ready for deep learning integration. You can immediately begin implementing real PyTorch/TensorFlow models by replacing the logic in `backend/app/services/analyzers/image_analyzer.py`, `video_analyzer.py`, and `audio_analyzer.py`. The `BaseAnalyzer` contract and `AnalysisResult` schemas are finalized and stable.

See `docs/PROJECT_STATUS.md` for more details on Technical Debt and Known Issues before proceeding.
