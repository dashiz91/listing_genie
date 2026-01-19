# Implementation Stories - Phase 1: Foundation

Implementation-ready story files with complete, copy-paste code for rapid development.

## Overview

These stories contain **complete, production-ready code** that can be copied directly into your project. Each story includes:

- Full code implementations
- Project structure
- Test gates with exact commands
- Dependencies and blockers
- Definition of Done checklist

## Phase 1 Stories

### 1.1 - FastAPI Backend Setup ✅
**File:** `1.1-fastapi-backend.md` (ALREADY EXISTS)

**What it does:**
- FastAPI application with proper project structure
- CORS configuration
- Health check endpoints
- Error handling and logging middleware
- Swagger UI documentation

**Key deliverables:**
- `app/main.py` - FastAPI entry point
- `app/config.py` - Settings management
- `app/core/middleware.py` - Request logging and error handling
- `requirements.txt` - Python dependencies

**Test:** `uvicorn app.main:app --reload` → Health checks work

---

### 1.2 - Database Setup
**File:** `1.2-database-setup.md`

**What it does:**
- SQLAlchemy models for sessions, keywords, and images
- Database session management with dependency injection
- Automatic table creation on startup
- Health check with DB connection verification

**Key deliverables:**
- `app/models/database.py` - GenerationSession, SessionKeyword, ImageRecord models
- `app/db/session.py` - Database session factory and initialization
- Enums for GenerationStatus, ImageType, IntentType

**Test:** Create session in Python REPL → Database queries work

---

### 1.3 - Storage Setup
**File:** `1.3-storage-setup.md`

**What it does:**
- Local file storage service for uploads and generated images
- UUID-based file naming for security
- Image re-encoding to strip EXIF data
- Session-based organization for generated images

**Key deliverables:**
- `app/services/storage_service.py` - StorageService class
- `app/dependencies.py` - Dependency injection setup
- `storage/uploads/` - Upload directory
- `storage/generated/` - Generated images directory

**Test:** Save/retrieve images via Python REPL → Storage works

---

### 1.4 - React Frontend Setup
**File:** `1.4-react-frontend-setup.md`

**What it does:**
- Vite + React + TypeScript project
- Tailwind CSS for styling
- API client with axios
- React Router with placeholder pages
- Landing page fully implemented

**Key deliverables:**
- `frontend/src/App.tsx` - Main app with routing
- `frontend/src/api/client.ts` - Axios API client
- `frontend/src/pages/LandingPage.tsx` - Complete landing page
- `frontend/vite.config.ts` - Vite configuration with proxy

**Test:** `npm run dev` → Landing page loads, API calls work

---

### 1.5 - Development Environment
**File:** `1.5-dev-environment.md`

**What it does:**
- Docker multi-stage build for production
- docker-compose for local development
- Hot reload for both backend and frontend
- Environment variable management
- Complete README with Docker instructions

**Key deliverables:**
- `Dockerfile` - Production build
- `Dockerfile.dev` - Development build
- `docker-compose.yml` - Development orchestration
- `.env.example` - All environment variables
- `Makefile` - Convenient commands (optional)

**Test:** `docker-compose up` → Full stack runs with hot reload

---

## Implementation Order

**RECOMMENDED SEQUENCE:**

```
1.1 (FastAPI) → 1.2 (Database) → 1.3 (Storage) → 1.4 (Frontend) → 1.5 (Docker)
```

**Why this order:**
1. **1.1 First:** Foundation for all API work
2. **1.2 Second:** Database needed for all features
3. **1.3 Third:** Storage needed for image handling
4. **1.4 Fourth:** Frontend can develop against working backend
5. **1.5 Last:** Docker wraps everything together

**Alternative (Parallel):**
- Backend team: 1.1 → 1.2 → 1.3 → 1.5
- Frontend team: 1.4 (can start immediately)

---

## Dependencies Graph

```
1.1 (FastAPI)
 ├─→ 1.2 (Database)
 ├─→ 1.3 (Storage)
 └─→ 1.4 (Frontend)
      └─→ 1.5 (Docker)
           └─→ PHASE 2 READY ✅
```

---

## Story Format

Each story follows this structure:

1. **Header** - ID, title, priority, complexity, status
2. **User Story** - What and why
3. **Acceptance Criteria** - Checklist of requirements
4. **Project Structure** - Exact folder/file layout
5. **Code to Implement** - Complete, copy-paste ready code
6. **Test Gate** - Exact commands to verify it works
7. **Dependencies** - What it depends on / what it blocks
8. **Definition of Done** - Final checklist
9. **Notes for Developer** - Tips and context

---

## How to Use These Stories

### For Solo Developer:
```bash
# 1. Read story file completely
# 2. Copy code sections into your project
# 3. Run test gate commands
# 4. Check off Definition of Done
# 5. Move to next story
```

### For Team:
```bash
# 1. Assign stories to developers
# 2. Each dev implements their story independently
# 3. Use test gates to verify before merging
# 4. Definition of Done = PR approval criteria
```

### For AI Assistant (Claude/GPT):
```bash
# Give the story file to AI:
"Implement Story 1.2 from 1.2-database-setup.md"

# AI will:
# - Create all files
# - Copy all code
# - Run test gates
# - Verify Definition of Done
```

---

## Test Gates Summary

Each story has test gates that MUST pass:

| Story | Key Test Command | Expected Result |
|-------|------------------|-----------------|
| 1.1 | `uvicorn app.main:app --reload` | Server starts, health checks work |
| 1.2 | `curl http://localhost:8000/api/health` | Database status "connected" |
| 1.3 | Python REPL storage test | Can save/retrieve images |
| 1.4 | `npm run dev` | Frontend loads, API calls work |
| 1.5 | `docker-compose up` | Full stack runs with hot reload |

---

## Common Issues & Solutions

### Story 1.1 - FastAPI
**Issue:** CORS errors
**Fix:** Check `CORS_ORIGINS` in `.env` includes frontend URL

### Story 1.2 - Database
**Issue:** Tables not created
**Fix:** Ensure `init_db()` called in `startup_event`

### Story 1.3 - Storage
**Issue:** Permission denied
**Fix:** Check `storage/` directory permissions

### Story 1.4 - Frontend
**Issue:** API calls fail
**Fix:** Verify Vite proxy config and backend is running

### Story 1.5 - Docker
**Issue:** Hot reload not working
**Fix:** Check volumes mounted correctly in docker-compose.yml

---

## After Phase 1 Complete

Once all 5 stories are done, you'll have:

✅ Working FastAPI backend with health checks
✅ Database with all models
✅ Local file storage
✅ React frontend with routing
✅ Docker development environment
✅ Hot reload for rapid development

**Ready for Phase 2:** Image generation features!

---

## Reference Patterns

All stories reference existing patterns from:
- **Architecture:** `docs/architecture.md`
- **PRD:** `docs/prd.md`
- **Python patterns:** `C:\Nebula Colors\software\gemini_mcp\`

---

## Questions?

Each story is self-contained and implementation-ready. If you need clarification:

1. Check the **Notes for Developer** section
2. Review the **Test Gate** for expected behavior
3. Look at **Dependencies** to ensure prerequisites are met
4. Refer to `docs/architecture.md` for system design context
