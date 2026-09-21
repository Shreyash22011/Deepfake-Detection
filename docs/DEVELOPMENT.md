# Development Guide

This guide provides instructions for setting up the development environment and contributing to the AI Media Authenticity Platform.

## Prerequisites
- Node.js (v18+)
- Python (3.10+)
- MongoDB (Local or Docker)

## Backend Setup
1. Navigate to the `backend/` directory.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   The API will be available at `http://localhost:8000`. Swagger UI documentation is available at `http://localhost:8000/docs`.

## Frontend Setup
1. Navigate to the `frontend/` directory.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:3000`.

## Configuration
- The backend defaults to `mongodb://localhost:27017` if `DATABASE_URL` is not provided.
- The frontend defaults to `http://localhost:8000` for API calls if `NEXT_PUBLIC_API_URL` is not provided.

## Git Guidelines & Known Issues
- **CRITICAL**: If you used `create-next-app` to generate the frontend, it may have created a `.git` folder inside `/frontend`. This will cause Git to treat the frontend as a submodule, and your frontend code won't push to GitHub!
  - **Fix**: Run `rm -rf frontend/.git` (Mac/Linux) or `rmdir /s /q frontend\.git` (Windows) and then `git rm --cached frontend` from the root directory before committing.
- Do not commit `.env` files, model weights, or large datasets.
- Ensure the code passes type checking and linting before pushing.
