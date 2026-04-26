# HuddleBoard

Real-time collaborative board for teams.

## Tech Stack

- **Backend**: FastAPI + PostgreSQL + WebSocket
- **Database**: Neon (PostgreSQL)
- **Frontend**: Vue 3 + Netlify
- **Deployment**: Koyeb + Netlify

## Local Development

```bash
# Backend
cd backend
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
cp .env.example .env
npm install
npm run dev
```

## Deployment

### Backend → Koyeb
1. Connect GitHub repo to Koyeb
2. Build: `pip install -r requirements.txt`
3. Run: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Root: `backend`

Add env vars:
- `DATABASE_URL` (Neon PostgreSQL)
- `CORS_ORIGINS` (Netlify URL)
- `SECRET_KEY` (random 32-char string)

### Frontend → Netlify
1. Connect GitHub repo to Netlify
2. Root: `frontend`
3. Build: `npm run build`
4. Publish: `dist`

Add env var:
- `VITE_API_URL` (Koyeb URL)

## Rate Limits

- Board create: 5/min
- Board fetch: 10/min
- Vote: 10/min

## Free Tier Capacity

- ~500-1,000 concurrent users
- ~200-300 active boards
- Cold start: 5-10s (Koyeb)