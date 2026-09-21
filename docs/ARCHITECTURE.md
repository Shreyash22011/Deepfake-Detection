# Architecture Overview

This document describes the architectural foundation for the **AI Media Authenticity Platform**. The architecture is designed to be highly modular, allowing separate teams to work independently on different modalities (image, video, audio) and integrate seamlessly.

## High-Level Architecture

The platform follows a standard client-server architecture with separation of concerns:
- **Frontend**: A Next.js (React) application for the user interface.
- **Backend**: A FastAPI (Python) service that handles API requests, database interactions, and orchestrates the ML models.
- **Database**: MongoDB for storing analyses, metadata, and reports.
- **ML Modules**: Independent modules for deepfake detection (image, video, audio).

## Core Principles

1. **Separation of Concerns**: Frontend handles only UI/UX. Backend handles business logic and API routing. ML modules handle only inference and evidence extraction.
2. **Standardized Contracts**: ML modules must return results conforming to a unified contract, regardless of the underlying model or modality.
3. **Modularity**: New ML models can be plugged in without changing the core backend API or frontend architecture.
4. **Asynchronous Processing**: (Planned) Media processing will eventually move to an asynchronous task queue (e.g., Celery or background tasks) to avoid blocking the main API thread during heavy inference.

## Directory Structure
- `frontend/`: Next.js web application.
- `backend/`: FastAPI application.
- `ml/`: Subdirectories for `image`, `video`, and `audio` machine learning models.
- `metadata/`: Modules for extracting and analyzing file metadata.
- `explainability/`: Modules for generating heatmaps (Grad-CAM) and other visual explanations.
- `fusion/`: Logic for combining predictions from multiple modalities or models.
- `reports/`: PDF report generation logic.
- `database/`: Database connection and repository layer (currently MongoDB setup planned).
