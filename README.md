# Glimmora Reach Backend

FastAPI + MongoDB auth API for Glimmora Reach (Campaign Engine).

## Run locally

**1. Create virtual environment and install dependencies**

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**2. Start MongoDB** (e.g. local install or Docker: `docker run -d -p 27017:27017 --name mongo mongo:7`)

**Redis** is not required for the current auth system (can be added later for rate limiting if needed).

**3. Copy `.env.example` to `.env`** and set `SECRET_KEY`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` if using Google OAuth.

**4. Start the server**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API: http://localhost:8000  
- Docs: http://localhost:8000/docs  
- Health: http://localhost:8000/health  

See `AUTH_REPORT.md` for auth routes and details.
