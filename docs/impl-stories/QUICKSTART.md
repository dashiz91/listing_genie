# Phase 1 Quick Start Guide

Get Listing Genie running in 30 minutes or less.

## Prerequisites

- Python 3.11+
- Node.js 20+
- Docker Desktop (optional)
- Gemini API key ([Get one free](https://ai.google.dev/))

---

## Option 1: Docker (Recommended - 5 minutes)

```bash
# 1. Clone and setup
git clone <repo>
cd listing_genie
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 2. Start everything
docker-compose up

# 3. Access app
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

**That's it!** Hot reload is enabled for both frontend and backend.

---

## Option 2: Local Development (15 minutes)

### Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env
cp .env.example .env
# Edit .env and add GEMINI_API_KEY

# Start backend
uvicorn app.main:app --reload
```

Backend now running at http://localhost:8000

### Frontend Setup (new terminal)

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend now running at http://localhost:5173

---

## Verify Installation

### Quick Health Check

```bash
# Backend health
curl http://localhost:8000/health
# Should return: {"status": "healthy", "service": "listing-genie"}

# API health with dependencies
curl http://localhost:8000/api/health
# Should return: {"status": "healthy", ..., "dependencies": {...}}
```

### Full Verification (30 seconds)

```bash
# Linux/Mac
chmod +x docs/impl-stories/verify-phase-1.sh
./docs/impl-stories/verify-phase-1.sh

# Windows PowerShell
powershell -ExecutionPolicy Bypass -File docs/impl-stories/verify-phase-1.ps1
```

Should show all green checkmarks ✓

---

## Project Structure Overview

```
listing_genie/
├── app/                      # Backend (FastAPI)
│   ├── main.py              # Entry point
│   ├── config.py            # Settings
│   ├── models/              # Database models
│   ├── services/            # Business logic
│   ├── api/endpoints/       # API routes
│   └── db/                  # Database session
│
├── frontend/                 # Frontend (React + Vite)
│   ├── src/
│   │   ├── App.tsx          # Main app
│   │   ├── api/             # API client
│   │   ├── pages/           # Route pages
│   │   └── components/      # UI components
│   └── package.json
│
├── storage/                  # File storage (gitignored)
│   ├── uploads/             # Uploaded images
│   └── generated/           # Generated images
│
├── docs/                     # Documentation
│   └── impl-stories/        # Implementation stories
│
├── docker-compose.yml        # Development environment
├── Dockerfile               # Production build
└── .env                     # Environment variables (gitignored)
```

---

## Key Endpoints

### Backend API

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Simple health check |
| `GET /api/health` | Health check with dependencies |
| `GET /docs` | Interactive API documentation (Swagger UI) |
| `POST /api/upload` | Upload product image (Story 2.1) |
| `POST /api/generate` | Start image generation (Story 2.2+) |
| `GET /api/generation/{id}` | Check generation status (Story 2.2+) |

### Frontend Routes

| Route | Description |
|-------|-------------|
| `/` | Landing page (implemented) |
| `/upload` | Upload product image (Story 1.1) |
| `/form` | Product info form (Story 1.2) |
| `/generate` | Generation progress (Story 3.x) |
| `/gallery` | View/download results (Story 3.x) |

---

## Development Workflow

### Making Backend Changes

1. Edit code in `app/` directory
2. uvicorn auto-reloads (watch console)
3. Test at http://localhost:8000

### Making Frontend Changes

1. Edit code in `frontend/src/` directory
2. Vite hot-reloads (instant in browser)
3. View at http://localhost:5173

### Database Changes

1. Edit `app/models/database.py`
2. Restart backend
3. Tables auto-update (SQLite)

For production migrations, use Alembic (Phase 2).

---

## Common Commands

### Backend

```bash
# Start backend
uvicorn app.main:app --reload

# Run Python shell with app context
python
>>> from app.db.session import SessionLocal
>>> from app.models.database import GenerationSession
>>> db = SessionLocal()
>>> # ... interact with database

# Run tests (when added)
pytest
```

### Frontend

```bash
cd frontend

# Start dev server
npm run dev

# Install new package
npm install <package-name>

# Build for production
npm run build

# Preview production build
npm run preview
```

### Docker

```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild containers
docker-compose build

# Clean everything
docker-compose down -v
rm -rf storage/*
```

---

## Environment Variables

### Required

```bash
GEMINI_API_KEY=your-api-key-here
```

### Optional (with defaults)

```bash
DEBUG=true
DATABASE_URL=sqlite:///./listing_genie.db
STORAGE_PATH=./storage
CORS_ORIGINS=["http://localhost:5173"]
```

### Frontend

```bash
VITE_API_URL=http://localhost:8000/api
```

---

## Troubleshooting

### Backend won't start

```bash
# Check Python version
python --version  # Should be 3.11+

# Reinstall dependencies
pip install -r requirements.txt

# Check for port conflicts
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows
```

### Frontend won't start

```bash
# Check Node version
node --version  # Should be 20+

# Delete node_modules and reinstall
rm -rf node_modules
npm install

# Check for port conflicts
lsof -i :5173  # Mac/Linux
netstat -ano | findstr :5173  # Windows
```

### CORS errors

```bash
# Check .env has correct CORS_ORIGINS
CORS_ORIGINS=["http://localhost:5173"]

# Restart backend after changing .env
```

### Database errors

```bash
# Delete database and restart (dev only!)
rm listing_genie.db
uvicorn app.main:app --reload
```

### Docker issues

```bash
# Clean Docker cache
docker system prune -a

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

---

## Next Steps

After Phase 1 is complete:

1. **Verify everything works:** Run verification script
2. **Explore API docs:** Visit http://localhost:8000/docs
3. **Test the landing page:** Visit http://localhost:5173
4. **Start Phase 2:** Begin implementing image generation features

---

## Getting Help

### Story-Specific Help

Each story in `docs/impl-stories/` has:
- Complete code implementations
- Test gates to verify it works
- Notes for developers
- Troubleshooting tips

### Check These First

1. **Architecture:** `docs/architecture.md` - System design
2. **PRD:** `docs/prd.md` - Product requirements
3. **README:** Story-specific README files

### Common Issues

| Issue | Fix |
|-------|-----|
| Import errors | Check virtual environment is activated |
| Port already in use | Kill existing process or change port |
| CORS errors | Update CORS_ORIGINS in .env |
| Database locked | Close other connections to .db file |
| Hot reload not working | Check file watchers aren't at limit |

---

## Development Tips

### VS Code Extensions (Recommended)

- Python
- Pylance
- ESLint
- Prettier
- Tailwind CSS IntelliSense
- Docker

### Productivity Shortcuts

```bash
# Backend: Auto-format Python
pip install black
black app/

# Frontend: Auto-format TypeScript
npm run format  # (add to package.json)

# Git hooks (pre-commit)
pip install pre-commit
pre-commit install
```

### Debug Mode

```bash
# Backend: Enable debug logging
DEBUG=true uvicorn app.main:app --reload --log-level debug

# Frontend: Enable source maps
# Already enabled in Vite dev mode
```

---

## Success Criteria

Phase 1 is complete when:

✅ Backend starts without errors
✅ Frontend loads and displays landing page
✅ Health endpoints return success
✅ Can create database records
✅ Can save files to storage
✅ API calls work from frontend
✅ Docker environment runs both services
✅ Hot reload works for both

**Time estimate:** 2-4 hours to implement all 5 stories

**Ready for Phase 2:** Image generation, upload UI, form handling, and gallery!
