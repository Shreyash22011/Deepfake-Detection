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
- **Phase 1 (Complete)**: Initial repository setup, API contracts, frontend/backend boilerplate.
- **Phase 2 (Upcoming)**: ML model integration and database connectivity.

See `docs/PROJECT_STATUS.md` for more details.
