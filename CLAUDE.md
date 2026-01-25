# REDDAI.CO

AI-powered Amazon listing image generator that creates professional product images for e-commerce sellers.

**Brand:** REDDAI.CO — Geometric fox logo, orange (#C85A35) + slate (#1A1D21) color palette.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         REDDAI.CO                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ROUTES                                                        │
│   /          → Landing Page (marketing site)                    │
│   /auth      → Authentication (login/signup)                    │
│   /app       → Listing Generator (protected, requires auth)     │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   FRONTEND (React + Vite + Tailwind + shadcn/ui)                │
│   └── src/                                                      │
│       ├── components/landing/   # Landing page sections         │
│       ├── components/ui/        # shadcn/ui components          │
│       ├── components/           # App components                │
│       ├── contexts/             # Auth context (Supabase)       │
│       ├── pages/LandingPage.tsx # Marketing landing             │
│       ├── pages/AuthPage.tsx    # Login/Signup                  │
│       └── pages/HomePage.tsx    # Generator tool (protected)    │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   BACKEND (Python + FastAPI)                                    │
│   └── app/                                                      │
│       ├── api/endpoints/        # REST endpoints                │
│       ├── core/auth.py          # Supabase JWT verification     │
│       ├── services/             # Business logic                │
│       ├── prompts/              # AI prompts                    │
│       └── models/               # SQLAlchemy models             │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   SUPABASE (Backend-as-a-Service)                               │
│   ├── Auth        → Email/password authentication               │
│   └── Storage     → Image storage (uploads, generated)          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Design System

**IMPORTANT:** See `docs/design_MUSTREAD.md` for the complete design system including:
- Color tokens (redd-400/500/600, slate-100/600/800/900)
- Typography (Inter font)
- Component patterns (buttons, cards, inputs)
- Layout guidelines
- Responsive breakpoints

All new UI should follow the design system to maintain visual consistency.

## Tech Stack

### Backend (Python/FastAPI)
- **Framework**: FastAPI with uvicorn
- **Database**: SQLite with SQLAlchemy ORM
- **AI Services**:
  - `gemini-3-flash-preview` - Vision analysis & prompt generation
  - `gemini-3-pro-image-preview` - Image generation
- **Auth**: Supabase Auth with JWT verification
- **Storage**: Supabase Storage (buckets: `uploads`, `generated`)

### Frontend (React/TypeScript)
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: TailwindCSS + shadcn/ui components
- **Routing**: React Router DOM
- **HTTP Client**: Axios
- **Auth**: Supabase JS client

### External Services
- **Supabase**: Authentication + Cloud Storage
- **Google AI (Gemini)**: Vision analysis + Image generation

## Project Structure

```
listing_genie/
├── app/                              # Backend Python application
│   ├── api/endpoints/
│   │   ├── generation.py             # Main generation endpoints
│   │   ├── images.py                 # Image serving (Supabase signed URLs)
│   │   ├── upload.py                 # File upload to Supabase
│   │   └── health.py                 # Health check
│   ├── core/
│   │   ├── auth.py                   # Supabase JWT verification
│   │   ├── exceptions.py             # Custom exceptions
│   │   ├── logging_config.py         # Logging setup
│   │   └── middleware.py             # Request logging middleware
│   ├── models/
│   │   └── database.py               # SQLAlchemy models (includes user_id)
│   ├── prompts/
│   │   ├── ai_designer.py            # AI Designer prompts
│   │   ├── color_psychology.py       # Color theory prompts
│   │   ├── creative_brief.py         # Creative brief system
│   │   ├── design_framework.py       # Framework generation
│   │   ├── engine.py                 # Prompt engine
│   │   ├── intent_modifiers.py       # Keyword intent modifiers
│   │   ├── styles.py                 # Style presets
│   │   └── templates/                # Image-type specific templates
│   │       ├── main_image.py
│   │       ├── infographic.py
│   │       ├── lifestyle.py
│   │       └── comparison.py
│   ├── services/
│   │   ├── generation_service.py     # Main orchestration logic
│   │   ├── gemini_service.py         # Gemini image generation
│   │   ├── gemini_vision_service.py  # Gemini vision analysis
│   │   ├── openai_vision_service.py  # OpenAI vision (backup)
│   │   ├── vision_service.py         # Unified vision service
│   │   ├── design_architect_service.py # Design framework service
│   │   └── supabase_storage_service.py # Supabase Storage integration
│   ├── config.py                     # App configuration
│   ├── dependencies.py               # Dependency injection
│   └── main.py                       # FastAPI app entry point
│
├── frontend/
│   ├── public/
│   │   ├── logo/
│   │   │   └── fox-icon.png          # Transparent logo
│   │   └── images/
│   │       └── hero-mockup.png       # Landing page hero image
│   ├── src/
│   │   ├── api/
│   │   │   ├── client.ts             # API client (includes auth token)
│   │   │   └── types.ts              # TypeScript types
│   │   ├── components/
│   │   │   ├── landing/              # Landing page components
│   │   │   │   ├── navbar.tsx
│   │   │   │   ├── hero.tsx
│   │   │   │   ├── social-proof.tsx
│   │   │   │   ├── features.tsx
│   │   │   │   ├── how-it-works.tsx
│   │   │   │   ├── pricing.tsx
│   │   │   │   └── cta-footer.tsx
│   │   │   ├── ui/                   # shadcn/ui components (button, card, etc.)
│   │   │   ├── ProtectedRoute.tsx    # Auth guard component
│   │   │   ├── Layout.tsx            # App layout wrapper
│   │   │   ├── ProductForm.tsx       # Product info form
│   │   │   ├── ImageGallery.tsx      # Generated images display
│   │   │   ├── ImageUploader.tsx     # Multi-image uploader
│   │   │   ├── FrameworkSelector.tsx # Framework selection UI
│   │   │   └── StyleSelector.tsx     # Style preset selector
│   │   ├── contexts/
│   │   │   └── AuthContext.tsx       # Supabase auth state
│   │   ├── lib/
│   │   │   ├── supabase.ts           # Supabase client
│   │   │   └── utils.ts              # Utility functions (cn helper)
│   │   ├── pages/
│   │   │   ├── LandingPage.tsx       # Marketing landing (/)
│   │   │   ├── AuthPage.tsx          # Login/Signup (/auth)
│   │   │   └── HomePage.tsx          # Generator tool (/app)
│   │   ├── styles/index.css          # Global styles + Tailwind
│   │   ├── App.tsx                   # Router setup with auth
│   │   └── main.tsx                  # Entry point
│   ├── components.json               # shadcn/ui config
│   ├── index.html                    # HTML with meta tags
│   ├── tailwind.config.js            # Color tokens, fonts
│   └── package.json
│
├── docs/
│   └── design_MUSTREAD.md            # Design system documentation
│
├── .env                              # Backend environment variables
├── frontend/.env                     # Frontend environment variables
├── requirements.txt                  # Python dependencies
└── package.json                      # Root (runs both servers)
```

## Core Features

### Authentication (Supabase Auth)
- Email/password signup and login
- JWT tokens verified on backend
- Protected routes on frontend
- User sessions linked to generation sessions

### Two-Step AI Generation Flow

**Step 1: Framework Analysis** (Gemini Vision)
- AI analyzes product photos
- Generates 4 unique design frameworks with different styles
- Creates preview images for each framework
- User selects their preferred framework

**Step 2: Image Generation** (Gemini Image)
- AI generates 5 detailed prompts specific to the selected framework
- Creates 5 radically different listing images:
  - **Main/Hero** - Clean product shot on white background
  - **Infographic 1** - Technical features with callouts
  - **Infographic 2** - Benefits grid with icons
  - **Lifestyle** - Product in use with real person
  - **Comparison** - Multiple uses or package contents

### Color Mode System
- **`ai_decides`** - Full creative freedom
- **`suggest_primary`** - AI extracts colors from style reference
- **`locked_palette`** - User locks exact hex colors

### Style Reference
Upload a style reference image and AI matches that visual style across all generated images.

### Edit & Regenerate
- **Edit**: Modify existing image while preserving layout
- **Regenerate**: Generate completely new image with feedback

### Cloud Storage (Supabase)
- Uploads stored in `supabase://uploads/{uuid}.png`
- Generated images in `supabase://generated/{session_id}/{image_type}.png`
- Images served via signed URLs (1-hour expiry)

## API Endpoints

### Upload
```
POST /api/upload/              Upload image to Supabase
DELETE /api/upload/{id}        Delete uploaded image
```

### Generation
```
POST /api/generate/frameworks/analyze    Step 1: Analyze + frameworks
POST /api/generate/frameworks/generate   Step 2: Generate 5 images
POST /api/generate/single                Regenerate single image
POST /api/generate/edit                  Edit image
GET  /api/generate/{session_id}          Get session status
GET  /api/generate/{session_id}/prompts  Get all prompts
```

### Images
```
GET /api/images/{session_id}/{image_type}  Get image (redirects to signed URL)
```

### Health
```
GET /api/health                 Health check (DB, storage, AI services)
```

## Environment Variables

### Backend `.env`
```bash
# Required
GEMINI_API_KEY=your_gemini_api_key

# Supabase (Required)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Optional
DATABASE_URL=sqlite:///./listing_genie.db
VISION_PROVIDER=gemini                # or "openai"
OPENAI_API_KEY=your_openai_key        # For OpenAI vision (backup)
```

### Frontend `frontend/.env`
```bash
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key
```

## Running the Application

### Quick Start
```bash
npm install
npm run dev        # Runs both backend and frontend
```

### Manual Start
```bash
# Backend (Terminal 1)
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (Terminal 2)
cd frontend
npm install
npm run dev
```

### URLs
- Landing Page: http://localhost:5173/
- Auth Page: http://localhost:5173/auth
- Generator App: http://localhost:5173/app (requires login)
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Key Files for Development

### Design
- `docs/design_MUSTREAD.md` - Complete design system
- `frontend/tailwind.config.js` - Color tokens, fonts
- `frontend/src/styles/index.css` - Global styles

### Authentication
- `frontend/src/lib/supabase.ts` - Supabase client
- `frontend/src/contexts/AuthContext.tsx` - Auth state provider
- `frontend/src/components/ProtectedRoute.tsx` - Route guard
- `app/core/auth.py` - Backend JWT verification

### Landing Page
- `frontend/src/pages/LandingPage.tsx` - Composes all sections
- `frontend/src/components/landing/*.tsx` - Individual sections

### Generator App
- `frontend/src/pages/HomePage.tsx` - Main app flow
- `frontend/src/components/*.tsx` - App components

### Backend Services
- `app/prompts/ai_designer.py` - All AI prompts
- `app/services/generation_service.py` - Main orchestration
- `app/services/gemini_service.py` - Image generation
- `app/services/supabase_storage_service.py` - Cloud storage

## Supabase Setup

### Required Buckets
Create these buckets in Supabase Storage:
1. `uploads` - For user-uploaded product images
2. `generated` - For AI-generated listing images

### Auth Configuration
- Enable Email provider in Supabase Auth settings
- Disable email confirmation for development (optional)

## Future Scope
- Restyle `/app` to match landing page design system
- Credit-based pricing system
- A+ Content (Enhanced Brand Content) images
- Batch generation for multiple products
- Social login (Google, GitHub)
