# REDDSTUDIO.AI

AI-powered Amazon listing image generator that creates complete, visually cohesive product listings from a single set of product photos.

**Live:** https://reddstudio.ai

![REDDSTUDIO](frontend/public/logo/fox-icon.png)

## What It Does

Upload your product photos and REDDSTUDIO generates:
- **6 Listing Images** — Hero, infographics, lifestyle, comparison, transformation shots
- **6 A+ Content Modules** — Desktop + mobile versions with seamless transitions
- **Cohesive Design** — All images follow a unified visual framework

Unlike generic AI image tools, REDDSTUDIO uses a multi-stage Art Director pipeline that ensures every image works together as a complete listing.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, TypeScript, Vite, TailwindCSS, shadcn/ui |
| Backend | Python, FastAPI, SQLAlchemy |
| AI | Google Gemini (vision analysis + image generation) |
| Auth | Supabase Auth (JWT/JWKS) |
| Storage | Supabase Storage |
| Database | PostgreSQL (prod/staging), SQLite (local) |
| Hosting | Vercel (frontend), Railway (backend) |

## Credits System

REDDSTUDIO uses a credit-based system for image generation:

| Operation | Credits | Notes |
|-----------|---------|-------|
| Framework Analysis | 1 | Vision analysis |
| Framework Previews | 4 | 4 style previews |
| Listing Image (Pro) | 3 | Best quality |
| Listing Image (Flash) | 1 | Faster |
| A+ Module (Pro) | 3 | Best quality |
| A+ Mobile Transform | 1 | Desktop → Mobile |
| Edit Image | 1 | Modifications |

**Full Listing Cost:** ~47 credits (Pro) or ~23 credits (Flash)

### Pricing Plans

| Plan | Credits | Price |
|------|---------|-------|
| Free | 30/day | $0 |
| Starter | 300/mo | $15/mo |
| Pro | 1000/mo | $49/mo |
| Business | 3000/mo | $149/mo |

### Credit UI

The app displays credits in three places:
- **Sidebar Widget** — Shows current balance with color-coded status
- **Generate Buttons** — Shows cost preview before actions
- **Usage Toasts** — Confirms credits used after generation

Admin users (configured via `ADMIN_EMAILS` env var) have unlimited credits.

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.12+
- Gemini API key
- Supabase project (for auth & storage)

### Installation

```bash
# Clone the repo
git clone https://github.com/your-org/listing_genie.git
cd listing_genie

# Install dependencies
npm install
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
cp frontend/.env.example frontend/.env
# Edit both .env files with your credentials
```

### Environment Variables

**Backend (`.env`):**
```bash
GEMINI_API_KEY=your_gemini_api_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
DATABASE_URL=sqlite:///./listing_genie.db  # Local dev
```

**Frontend (`frontend/.env`):**
```bash
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key
```

### Running Locally

```bash
# Start both frontend and backend
npm run dev

# Or run separately:
# Backend (Terminal 1)
uvicorn app.main:app --reload --port 8000

# Frontend (Terminal 2)
cd frontend && npm run dev
```

**URLs:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Project Structure

```
listing_genie/
├── app/                    # FastAPI backend
│   ├── api/endpoints/      # REST endpoints
│   ├── core/               # Auth, middleware
│   ├── models/             # SQLAlchemy models
│   ├── prompts/            # AI prompts
│   └── services/           # Business logic
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── pages/          # Route pages
│   │   └── contexts/       # React contexts
│   └── public/             # Static assets
├── docs/                   # Documentation
├── CLAUDE.md               # Full dev documentation
└── README.md               # This file
```

## Environments

| Environment | Frontend | Backend | Branch |
|-------------|----------|---------|--------|
| Production | reddstudio.ai | Railway | `main` |
| Staging | staging.reddstudio.ai | Railway | `develop` |
| Local | localhost:5173 | localhost:8000 | any |

## Development Workflow

> **NEVER DEPLOY DIRECTLY TO PRODUCTION.** All changes must go through staging first and get user approval.

```
LOCAL → STAGING → USER APPROVAL → PRODUCTION
```

1. **Develop locally** on feature branch from `develop`
2. **PR to `develop`** → auto-deploys to `staging.reddstudio.ai`
3. **User tests** on staging
4. **User approves** the changes
5. **PR `develop` to `main`** → auto-deploys to `reddstudio.ai`

Breaking this rule risks breaking production for real users.

## Documentation

See [CLAUDE.md](CLAUDE.md) for comprehensive documentation including:
- Architecture overview
- API endpoints
- Design system
- Deployment details
- AI generation flow

## License

Proprietary - All rights reserved.
