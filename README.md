# MindBalance - AI Powered Study Budgeting

## Quick Start (Backend)

We use a local SQLite database for the prototype, but the code is production-ready for PostgreSQL.

1. **Install Dependencies:**
   ```bash
   cd mindbalance/backend
   pip install -r requirements.txt
   ```

2. **Run Server:**
   ```bash
   uvicorn main:app --reload
   ```

3. **Explore API:**
   Open `http://127.0.0.1:8000/docs`.
   The system auto-creates a demo user (`demo@mindbalance.ai`) and default projects (Python, Database, English) on first run.

## API Key Features
- **Smart Variance:** GET `/analysis/variance` calculates your study balance.
- **Dual Tracking:** POST `/timelogs` supports both `TIMER` (start/stop) and `MANUAL` entries.

## Project Structure
- `backend/` - FastAPI application
- `frontend/` - (Coming Soon) Next.js application
