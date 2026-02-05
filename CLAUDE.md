# REDDSTUDIO.AI

AI-powered Amazon listing image generator that creates complete, visually cohesive product listings — 5 listing images + A+ Content modules (desktop & mobile) — from a single set of product photos.

**Brand:** REDDSTUDIO — Geometric fox logo, orange (#C85A35) + slate (#1A1D21) color palette.
**Live:** https://reddstudio.ai

## What Makes This Different

Unlike generic AI image wrappers, REDDAI uses a multi-stage Art Director pipeline:
1. **Vision Analysis** — AI sees the product photos, understands category/features
2. **Design Framework** — Creates a cohesive visual system (colors, typography, layout strategy)
3. **Visual Script** — Plans each image's content, role, and how modules connect
4. **Coordinated Generation** — Every image follows the script, not random generation
5. **Canvas Continuity** — A+ modules use gradient inpainting so they stitch together seamlessly
6. **Desktop + Mobile** — One-click transform per module, both variants side by side

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                       REDDSTUDIO.AI                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ROUTES                                                        │
│   /          → Landing Page (marketing site)                    │
│   /auth      → Authentication (login/signup)                    │
│   /app       → Listing Generator (protected, requires auth)     │
│   /app/projects → Projects page (saved listings history)        │
│   /app/assets   → Assets library (logos, style refs, generated) │
│   /app/settings → Settings (brand presets, credits, account)    │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   FRONTEND (React + Vite + Tailwind + shadcn/ui)                │
│   └── src/                                                      │
│       ├── components/split-layout/   # Split-screen experience  │
│       ├── components/live-preview/   # Real-time preview        │
│       ├── components/amazon-preview/ # Amazon listing mockup UI │
│       ├── components/preview-slots/  # A+ module rendering      │
│       ├── components/landing/        # Landing page sections    │
│       ├── components/ui/             # shadcn/ui components     │
│       ├── components/FocusImagePicker.tsx # Ref image selector  │
│       ├── contexts/                  # Auth context (Supabase)  │
│       ├── pages/LandingPage.tsx      # Marketing landing        │
│       ├── pages/AuthPage.tsx         # Login/Signup             │
│       ├── pages/HomePage.tsx         # Split-screen generator   │
│       ├── pages/ProjectsPage.tsx     # Saved projects history   │
│       ├── pages/AssetsPage.tsx       # Assets library           │
│       └── pages/SettingsPage.tsx     # Settings & credits       │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   BACKEND (Python + FastAPI)                                    │
│   └── app/                                                      │
│       ├── api/endpoints/        # REST endpoints                │
│       ├── core/auth.py          # Supabase JWT verification     │
│       ├── services/             # Business logic                │
│       │   ├── generation_service.py      # Listing image orchestration    │
│       │   ├── gemini_service.py          # Gemini API (generate/edit)     │
│       │   ├── gemini_vision_service.py   # Vision analysis + frameworks   │
│       │   ├── design_architect_service.py # Framework generation          │
│       │   ├── credits_service.py         # Credits system & pricing       │
│       │   ├── image_utils.py             # Canvas compositor, resizing    │
│       │   └── supabase_storage_service.py # Cloud storage                 │
│       ├── prompts/              # AI prompts & templates        │
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
- **Database**: PostgreSQL (prod/staging) / SQLite (local) with SQLAlchemy ORM
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
│   │   ├── projects.py               # Projects CRUD (list, rename, delete)
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
│   │   ├── generation_service.py     # Listing image orchestration
│   │   ├── gemini_service.py         # Gemini API (generate/edit/text)
│   │   ├── gemini_vision_service.py  # Vision analysis + framework gen
│   │   ├── openai_vision_service.py  # OpenAI vision (backup)
│   │   ├── vision_service.py         # Unified vision service
│   │   ├── design_architect_service.py # Framework generation
│   │   ├── image_utils.py            # Canvas compositor, A+ resizing
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
│   │   │   ├── split-layout/         # Split-screen layout system
│   │   │   │   ├── SplitScreenLayout.tsx     # Two-panel responsive container
│   │   │   │   ├── WorkshopPanel.tsx         # Left: form sections (accordion)
│   │   │   │   ├── ShowroomPanel.tsx         # Right: live preview wrapper
│   │   │   │   └── index.ts                  # Exports
│   │   │   ├── live-preview/         # Real-time preview component
│   │   │   │   ├── LivePreview.tsx           # Always-visible preview (5 states)
│   │   │   │   └── index.ts                  # Exports
│   │   │   ├── landing/              # Landing page components
│   │   │   │   ├── navbar.tsx
│   │   │   │   ├── hero.tsx
│   │   │   │   ├── social-proof.tsx
│   │   │   │   ├── features.tsx
│   │   │   │   ├── how-it-works.tsx
│   │   │   │   ├── pricing.tsx
│   │   │   │   └── cta-footer.tsx
│   │   │   ├── amazon-preview/       # Amazon listing mockup (post-generation)
│   │   │   │   ├── AmazonListingPreview.tsx  # Full preview with edit/regen
│   │   │   │   ├── ThumbnailGallery.tsx      # Draggable thumbnails
│   │   │   │   ├── MainImageViewer.tsx       # Large image with zoom
│   │   │   │   ├── ProductInfoPanel.tsx      # Product details mockup
│   │   │   │   ├── PreviewToolbar.tsx        # Device toggle, actions
│   │   │   │   ├── QuickEditBar.tsx          # Edit/regen buttons
│   │   │   │   └── CelebrationOverlay.tsx    # Success confetti
│   │   │   ├── preview-slots/        # A+ Content module components
│   │   │   │   ├── AplusSection.tsx         # Full A+ section with modules
│   │   │   │   ├── ImageSlot.tsx            # Individual image slot
│   │   │   │   └── index.ts
│   │   │   ├── shared/               # Shared UI components
│   │   │   │   └── ImageActionOverlay.tsx   # Hover action overlay
│   │   │   ├── ui/                   # shadcn/ui components
│   │   │   ├── ProtectedRoute.tsx    # Auth guard component
│   │   │   ├── Layout.tsx            # App layout wrapper
│   │   │   ├── ImageUploader.tsx     # Multi-image uploader
│   │   │   ├── FocusImagePicker.tsx  # Reference image selector for edits
│   │   │   ├── PromptModal.tsx       # View/copy generation prompts
│   │   │   └── FrameworkSelector.tsx # Framework selection UI
│   │   ├── contexts/
│   │   │   └── AuthContext.tsx       # Supabase auth state
│   │   ├── lib/
│   │   │   ├── supabase.ts           # Supabase client
│   │   │   └── utils.ts              # Utility functions (cn helper)
│   │   ├── pages/
│   │   │   ├── LandingPage.tsx       # Marketing landing (/)
│   │   │   ├── AuthPage.tsx          # Login/Signup (/auth)
│   │   │   ├── HomePage.tsx          # Generator tool (/app)
│   │   │   └── ProjectsPage.tsx      # Saved projects (/app/projects)
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

### Living Preview Experience (Split-Screen UI)
The generator uses an immersive split-screen layout where the Amazon listing preview is ALWAYS visible:

```
┌─────────────────────────────┬───────────────────────────────────┐
│     THE WORKSHOP            │         THE SHOWROOM              │
│     (Form & Controls)       │         (Live Preview)            │
│                             │                                   │
│  📸 Product Photos          │   [Thumbnails] [Main Image]       │
│  📝 Product Info (title,    │                                   │
│     features, audience)     │   BRAND NAME                      │
│  🎨 Brand Identity          │   Product Title (real-time)       │
│  🖌️ Style & Colors          │   ★★★★☆ 4.5 (1,247)              │
│  📋 Global Instructions     │   $XX.XX                          │
│  🖼️ Design Framework        │   • Feature 1 (real-time)         │
│                             │   • Feature 2 (real-time)         │
│  [Analyze] [Generate]       │   • Feature 3 (real-time)         │
└─────────────────────────────┴───────────────────────────────────┘
```

**Preview States:**
- `empty` - No uploads yet, shows upload prompt
- `photos_only` - Photos uploaded, prompts for product details
- `filling` - Real-time updates as user types title/features
- `framework_selected` - Styled preview with framework colors
- `generating` - Progress indicator, images appear one-by-one
- `complete` - Full Amazon mockup with edit/regenerate options

**Responsive Layout:**
- Desktop (>1024px): 40/60 split
- Tablet (768-1024px): 50/50 split
- Mobile (<768px): Stacked with collapsible mini-preview

### Authentication (Supabase Auth)
- Email/password signup and login
- JWT tokens verified on backend
- Protected routes on frontend
- User sessions linked to generation sessions

### Three-Stage AI Generation Flow

**Step 1: Framework Analysis** (gemini-3-flash-preview)
- AI vision analyzes product photos (supports multiple uploads)
- Generates up to 4 unique design frameworks with different styles
- Each framework includes: color palette, typography, layout strategy, mood
- Creates preview images for each framework
- User selects their preferred framework

**Step 2: Listing Image Generation** (gemini-3-pro-image-preview)
- AI Art Director generates 5 detailed prompts specific to the product + framework
- Creates 5 radically different listing images:
  - **Main/Hero** — Clean product shot on white background
  - **Infographic 1** — Technical features with callouts
  - **Infographic 2** — Benefits grid with icons
  - **Lifestyle** — Product in use with real person
  - **Comparison** — Multiple uses or package contents
- Named image references (product photos, style ref) sent with each generation

**Step 3: A+ Content Generation** (gemini-3-pro-image-preview)
- AI Art Director writes a complete visual script for 5-6 A+ modules
- **Hero pair** — Modules 0+1 generated as one tall image, split at midpoint
- **Subsequent modules** — Canvas continuity technique:
  1. Takes bottom portion of previous module as gradient canvas
  2. Sends canvas + product photo + style ref as named images
  3. Gemini completes the canvas, maintaining visual flow
  4. Result split into refined previous + new module (no visible seam)
- **Mobile transforms** — Each desktop module can be recomposed to 4:3 mobile via edit API
- Per-module versioning with full version history

### Canvas Continuity Technique (Key Differentiator)
Each A+ module is generated with visual context from its neighbor:
```
Module N (bottom 25%) → gradient fade → blank canvas
                         ↓
Gemini receives: [canvas_to_complete, product_photo, style_ref]
                         ↓
Output: tall 4:3 image split into:
  - Top half → overwrites Module N (refined, seamless)
  - Bottom half → Module N+1 (new content, continuous flow)
```
This ensures modules stitch together with invisible transitions.

### Color Mode System
- **`ai_decides`** — Full creative freedom
- **`suggest_primary`** — AI extracts colors from style reference
- **`locked_palette`** — User locks exact hex colors

### Style Reference
Upload a style reference image and AI matches that visual style across all generated images.

### Edit & Regenerate with Focus Images
- **Edit**: Modify existing image while preserving layout
- **Regenerate**: Generate completely new image with feedback
- **Focus Image Picker**: When editing, user can select which reference images (product uploads, style ref, logo) to include as visual context. All off by default (pure text edit). "+" button allows ad-hoc reference image upload.
- Focus images are inserted before the source image in the Gemini contents array so Gemini treats the source as the edit target.

### Amazon Preview Experience
Results display as an authentic Amazon product listing mockup:
- **Thumbnail Gallery**: Draggable reorder, click to select
- **Main Image Viewer**: Large preview with hover zoom lens
- **Product Info Panel**: Title, bullets, price, buy button mockup
- **Device Toggle**: Switch between Desktop and Mobile layouts
- **Version History**: Navigate between regenerated versions with arrows
- **Quick Edit Bar**: Fast access to edit/regenerate/view-prompt per image
- **Export**: Download all images or export mockup as PNG

### A+ Content Preview
Below the listing images, a dedicated A+ section shows:
- All modules in sequence (desktop or mobile viewport)
- Per-module actions: generate, regenerate, edit, download, view prompt
- Desktop/mobile viewport toggle
- One-click "Generate All Mobile" to transform all desktop modules
- Visual script regeneration

### Projects Management
- **Projects Page**: View all saved generation sessions
- **Project Cards**: Thumbnail preview, status, date
- **Rename/Delete**: Manage saved projects
- **Detail Modal**: View all images from a project

### Cloud Storage (Supabase)
- Uploads stored in `supabase://uploads/{uuid}.png`
- Generated images in `supabase://generated/{session_id}/{image_type}.png`
- Versioned images: `{image_type}_v{N}.png`
- Images served via signed URLs (1-hour expiry)

## API Endpoints

### Upload
```
POST /api/upload/              Upload image to Supabase
DELETE /api/upload/{id}        Delete uploaded image
```

### Generation
```
POST /api/generate/frameworks/analyze    Step 1: Analyze + generate frameworks
POST /api/generate/frameworks/generate   Step 2: Generate 5 listing images
POST /api/generate/single                Regenerate single image
POST /api/generate/edit                  Edit image (supports reference_image_paths)
POST /api/generate/aplus/module          Generate single A+ module
POST /api/generate/aplus/hero            Generate A+ hero pair (modules 0+1)
POST /api/generate/aplus/mobile          Generate mobile version of A+ module
POST /api/generate/aplus/script          Generate/regenerate A+ visual script
GET  /api/generate/{session_id}          Get session status
GET  /api/generate/{session_id}/prompts  Get all prompts
```

### Images
```
GET /api/images/{session_id}/{image_type}  Get image (redirects to signed URL)
```

### Projects
```
GET    /api/projects/                   List user's projects (paginated)
GET    /api/projects/{session_id}       Get project details
PATCH  /api/projects/{session_id}       Rename project
DELETE /api/projects/{session_id}       Delete project and images
```

### Assets
```
GET /api/assets/                        List user's assets (logos, style-refs, products, generated)
```

### Settings & Credits
```
GET   /api/settings/                    Get all settings (brand presets, usage, credits)
GET   /api/settings/brand-presets       Get brand presets
PATCH /api/settings/brand-presets       Update brand presets
GET   /api/settings/usage               Get usage statistics
GET   /api/settings/credits             Get credits balance and plan info
GET   /api/settings/plans               Get available pricing plans
POST  /api/settings/credits/estimate    Estimate cost for an operation
GET   /api/settings/credits/model-costs Get credit costs per model/operation
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
- Projects: http://localhost:5173/app/projects (requires login)
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## DEPLOYMENT RULES (READ FIRST)

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║  NEVER DEPLOY DIRECTLY TO PRODUCTION                                          ║
║                                                                               ║
║  ALL changes MUST go through staging first:                                   ║
║    1. Push to develop branch                                                  ║
║    2. Test on staging.reddstudio.ai                                           ║
║    3. Get user approval                                                       ║
║    4. Only then merge to main                                                 ║
║                                                                               ║
║  Breaking this rule risks breaking production for real users.                 ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

**Why this matters:**
- Production has real user data and active sessions
- Staging has separate database - safe to break
- Users test on staging before approving changes
- No "hotfixes" to prod - always go through staging

**Emergency exception:** Only if production is completely down AND staging is also down, you may hotfix `main` directly. Document why in the commit message.

---

## ENGINEERING RULES (MANDATORY)

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║  ALWAYS TEST BEFORE DECLARING COMPLETE                                        ║
║                                                                               ║
║  Every feature/bugfix MUST be verified:                                       ║
║    1. Deploy to staging first (never directly to production)                  ║
║    2. Test the change works (browser, API call, or logs)                      ║
║    3. Get user confirmation if possible                                       ║
║    4. Only then consider it complete                                          ║
║                                                                               ║
║  "Code compiles" ≠ "It works". PROVE it works.                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

### Deployment Defaults
- **ALWAYS deploy to staging** unless explicitly told to deploy to production
- Use `railway up --service reddstudio-staging-backend --environment staging`
- Check Railway logs after deployment: `railway logs -s reddstudio-staging-backend --environment staging`
- Verify health: `curl https://reddstudio-staging-backend-staging.up.railway.app/health`

### Testing Requirements
- **UI changes**: Use Chrome DevTools MCP to navigate and verify visually
- **API changes**: Hit the endpoint to verify response (curl or browser)
- **Database changes**: Check logs for migration success
- **Bug fixes**: Reproduce the original issue first, then verify the fix resolves it

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║  NEVER ASK USER TO TEST - TEST IT YOURSELF                                    ║
║                                                                               ║
║  If Chrome MCP fails, FIX IT (kill chrome, retry). Don't punt to user.        ║
║  If Vercel didn't deploy, DEPLOY MANUALLY and alias to staging.               ║
║  If something blocks testing, SOLVE IT. Testing is YOUR job.                  ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

### Definition of Done
A task is NOT complete until:
1. ✅ Code is committed and pushed to `develop`
2. ✅ Deployed to staging successfully
3. ✅ Verified working (tested, not just "should work")
4. ✅ No errors in Railway logs
5. ✅ User approved (for significant changes)

### Root Cause, Not Bandaids
- Find and fix the actual cause, not symptoms
- Don't add fallbacks/defaults to mask broken data
- If AI returns incomplete data, fix the prompt
- If enum is missing, add it properly to the database

---

## STORY QUEUE WORKFLOW

```
todo_list/
├── backlog.md      ← Raw ideas (user dumps here)
├── ready/          ← Refined stories ready to implement
│   └── 001-feature-name.md
└── done/           ← Completed stories (for reference)
```

### How It Works

1. **User** adds raw ideas to `backlog.md`
2. **Before coding** - refine ONE task into a story in `ready/`
3. **Work the story** - implement, test on staging, commit
4. **Complete** - move story to `done/`, **update backlog.md** (move item to Completed section), pick next from `ready/`

**IMPORTANT:** Always update `backlog.md` when completing a task - move the item to the "Completed" section at the bottom. This prevents confusion about what's done vs pending.

### Starting a Session

```
1. Check `todo_list/ready/` for stories ready to implement
2. If empty, ask user which backlog item to refine
3. Work ONE story at a time to completion
4. Follow Definition of Done (deploy staging, test, verify)
```

### Story Format (in `ready/`)

```markdown
# NNN: Feature Name

**Priority:** High/Medium/Low
**Complexity:** Small/Medium/Large

## What
Clear description of the change

## Why
User value / problem being solved

## Acceptance Criteria
- [ ] Checkable requirements
- [ ] Tested on staging

## Files Likely Touched
- path/to/file.tsx

## Out of Scope
- What this story does NOT include
```

### Commands for Workflow

| User Says | Agent Does |
|-----------|------------|
| "refine task X" | Create story in `ready/` from backlog item |
| "what's next" | Check `ready/` folder, pick highest priority |
| "work on 001" | Read story, implement, test, complete |
| "status" | List in-progress and ready stories |

### Cleanup (End of Session or When Tasks Complete)

When finishing tasks or ending a session, **always clean up the todo_list folder**:

1. **Move completed stories** from `ready/` to `done/`
2. **Update `backlog.md`** - move completed items to the "Completed" section at the bottom
3. **Remove stale files** - delete any orphaned `.txt` files or duplicates in the todo_list folder
4. **Verify `ready/` is clean** - only stories actively being worked should be here

This prevents confusion about what's done vs pending and keeps the workflow organized.

---

## Deployment & Environments

### Environment Overview

| Environment | Frontend | Backend | Database | Branch |
|-------------|----------|---------|----------|--------|
| **Production** | `reddstudio.ai` | Railway (`reddstudio-backend`) | Supabase Prod PostgreSQL | `main` |
| **Staging** | `staging.reddstudio.ai` | Railway (`reddstudio-staging-backend`) | Supabase Staging PostgreSQL | `develop` |
| **Local** | `localhost:5173` | `localhost:8000` | SQLite | any |

### Infrastructure

```
┌─────────────────────────────────────────────────────────────────┐
│                      PRODUCTION                                  │
├─────────────────────────────────────────────────────────────────┤
│  Vercel (Frontend)          Railway (Backend)                   │
│  ├── reddstudio.ai          ├── reddstudio-backend              │
│  └── www.reddstudio.ai      └── PostgreSQL (Supabase Pooler)    │
│                                                                 │
│  Supabase (qkosgwvqczfjnkdmcumb)                                │
│  ├── Auth (JWKS verification)                                   │
│  ├── Storage (uploads, generated buckets)                       │
│  └── PostgreSQL (via Supavisor pooler)                          │
├─────────────────────────────────────────────────────────────────┤
│                       STAGING                                    │
├─────────────────────────────────────────────────────────────────┤
│  Vercel (Frontend)          Railway (Backend)                   │
│  └── staging.reddstudio.ai  └── reddstudio-staging-backend      │
│                                                                 │
│  Supabase (ovjexeavaaajxrmqpxle)                                │
│  ├── Auth (separate user pool)                                  │
│  ├── Storage (uploads, generated buckets)                       │
│  └── PostgreSQL (via Supavisor pooler)                          │
└─────────────────────────────────────────────────────────────────┘
```

### Development Workflow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Feature    │     │   Staging    │     │  Production  │
│   Branch     │────▶│   (develop)  │────▶│    (main)    │
└──────────────┘     └──────────────┘     └──────────────┘
      │                    │                     │
      │                    ▼                     ▼
      │              Auto-deploy           Auto-deploy
      │              to staging            to production
      ▼
   Local dev
   (localhost)
```

**Workflow Steps:**

```
LOCAL DEVELOPMENT
─────────────────
1. Create feature branch from `develop`
   git checkout develop && git pull
   git checkout -b feature/my-feature

2. Develop and test locally
   npm run dev  # Runs frontend + backend
   # Test at http://localhost:5173

3. Commit and push feature branch
   git add . && git commit -m "Add feature"
   git push -u origin feature/my-feature

STAGING (User Acceptance Testing)
─────────────────────────────────
4. Create PR: feature/* → develop
   # Review code, then merge

5. Auto-deploys to staging
   # Wait ~2 min for Railway + Vercel deploy

6. TEST on staging.reddstudio.ai
   # User tests the feature
   # Fix issues? Go back to step 2

7. USER APPROVES ✓
   # Only proceed when user confirms it works

PRODUCTION RELEASE
──────────────────
8. Create PR: develop → main
   # Final review

9. Merge to main → Auto-deploys to production
   # Wait ~2 min for deploy

10. Verify on reddstudio.ai
    # Confirm feature works in production
```

**Key Rule:** Never merge to `main` without user approval on staging first.

### Quick Git Commands

```bash
# Start new feature
git checkout develop && git pull
git checkout -b feature/my-feature

# Push feature for staging
git push -u origin feature/my-feature
# Then create PR to develop on GitHub, merge it
# → Auto-deploys to staging.reddstudio.ai

# After user approval, promote to production
git checkout main && git pull
git merge develop
git push
# → Auto-deploys to reddstudio.ai
```

### Deployment Commands

**Railway CLI:**
```bash
# Login
railway login

# Link to project (one-time)
railway link

# Deploy manually (usually auto-deploys on git push)
railway up -s reddstudio-backend --environment production

# Check logs
railway logs -s reddstudio-backend --environment production

# Set environment variable
railway variables set KEY=value -s reddstudio-backend --environment production
```

**Vercel CLI:**
```bash
# Login
vercel login

# Deploy preview (staging)
cd frontend && vercel

# Deploy production
cd frontend && vercel --prod

# Set environment variable
vercel env add VITE_API_URL production
```

### Environment Variables by Environment

**Production (Railway + Vercel):**
```bash
# Railway (backend)
DATABASE_URL=postgresql://postgres.PROJECT_ID:PASSWORD@aws-1-us-east-1.pooler.supabase.com:5432/postgres
GEMINI_API_KEY=xxx
SUPABASE_URL=https://qkosgwvqczfjnkdmcumb.supabase.co
SUPABASE_ANON_KEY=xxx
SUPABASE_SERVICE_ROLE_KEY=xxx
ALLOWED_EMAILS=robertoxma@hotmail.com  # Whitelist (empty = allow all)
APP_ENV=production

# Vercel (frontend)
VITE_API_URL=https://reddstudio-backend-production.up.railway.app
VITE_SUPABASE_URL=https://qkosgwvqczfjnkdmcumb.supabase.co
VITE_SUPABASE_ANON_KEY=xxx
```

**Staging (Railway + Vercel):**
```bash
# Railway (backend)
DATABASE_URL=postgresql://postgres.PROJECT_ID:PASSWORD@aws-1-us-east-1.pooler.supabase.com:5432/postgres
GEMINI_API_KEY=xxx
SUPABASE_URL=https://ovjexeavaaajxrmqpxle.supabase.co
SUPABASE_ANON_KEY=xxx
SUPABASE_SERVICE_ROLE_KEY=xxx
ALLOWED_EMAILS=  # Empty = allow all for testing
APP_ENV=staging

# Vercel (frontend - preview environment)
VITE_API_URL=https://reddstudio-staging-backend-staging.up.railway.app
VITE_SUPABASE_URL=https://ovjexeavaaajxrmqpxle.supabase.co
VITE_SUPABASE_ANON_KEY=xxx
```

### Health Check URLs

```bash
# Production
curl https://reddstudio-backend-production.up.railway.app/health
curl https://reddstudio-backend-production.up.railway.app/api/health  # Detailed

# Staging
curl https://reddstudio-staging-backend-staging.up.railway.app/health
curl https://reddstudio-staging-backend-staging.up.railway.app/api/health
```

### Database Notes

- **Production & Staging use PostgreSQL** via Supabase Supavisor connection pooler
- **Local uses SQLite** for simplicity
- SQLAlchemy handles both automatically based on `DATABASE_URL`
- Connection pooler region must be `aws-1` (not `aws-0`) for Supabase

**PostgreSQL URL format:**
```
postgresql://postgres.PROJECT_ID:PASSWORD@aws-1-us-east-1.pooler.supabase.com:5432/postgres
```

### Access Control (Email Whitelist)

The `ALLOWED_EMAILS` environment variable restricts access:
- **Set** (e.g., `robertoxma@hotmail.com`) → Only those emails can use the app
- **Empty** → All authenticated users allowed

Configured in `app/config.py`, enforced in `app/core/auth.py`.

### DNS Configuration (Porkbun)

| Type | Host | Value |
|------|------|-------|
| A | `@` | `76.76.21.21` (Vercel) |
| A | `www` | `76.76.21.21` (Vercel) |
| A | `staging` | `76.76.21.21` (Vercel) |

### Troubleshooting

**"Tenant or user not found" (PostgreSQL):**
- Wrong pooler region. Change `aws-0` to `aws-1` in DATABASE_URL

**"JWKS fetch failed" (Auth):**
- Check SUPABASE_URL and SUPABASE_ANON_KEY are correct
- Verify Supabase project is active

**"Gemini API not configured" (Frontend):**
- Vercel env vars not set. Use `vercel env add` command
- Redeploy after adding env vars

**CORS errors:**
- Add domain to `cors_origins` in `app/config.py`
- Redeploy backend

---

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

### Generator App (Split-Screen)
- `frontend/src/pages/HomePage.tsx` - Orchestrates split layout and state
- `frontend/src/components/split-layout/SplitScreenLayout.tsx` - Two-panel container
- `frontend/src/components/split-layout/WorkshopPanel.tsx` - Left panel (form sections)
- `frontend/src/components/split-layout/ShowroomPanel.tsx` - Right panel (preview wrapper)
- `frontend/src/components/live-preview/LivePreview.tsx` - Real-time preview (5 states)

### Amazon Preview (Post-Generation)
- `frontend/src/components/amazon-preview/AmazonListingPreview.tsx` - Full preview with editing
- `frontend/src/components/amazon-preview/*.tsx` - Thumbnails, zoom, edit bar, etc.

### Projects
- `frontend/src/pages/ProjectsPage.tsx` - Projects listing page
- `app/api/endpoints/projects.py` - Projects CRUD API

### A+ Content
- `frontend/src/components/preview-slots/AplusSection.tsx` - A+ section with modules, edit panel, focus images
- `app/api/endpoints/generation.py` - A+ endpoints (hero, module, mobile, script)
- `app/services/image_utils.py` - Canvas compositor, gradient inpainting, A+ resizing

### Backend Services
- `app/prompts/ai_designer.py` - All AI prompts (Art Director, visual script)
- `app/services/generation_service.py` - Listing image orchestration
- `app/services/gemini_service.py` - Gemini API (generate_image, edit_image, generate_text)
- `app/services/gemini_vision_service.py` - Vision analysis + framework generation
- `app/services/design_architect_service.py` - Framework text generation
- `app/services/supabase_storage_service.py` - Cloud storage

## Supabase Setup

### Required Buckets
Create these buckets in Supabase Storage:
1. `uploads` - For user-uploaded product images
2. `generated` - For AI-generated listing images

### Auth Configuration
- Enable Email provider in Supabase Auth settings
- Disable email confirmation for development (optional)

## AI Models & Cost

| Model | Role | API Cost | Credits |
|-------|------|----------|---------|
| `gemini-2.5-flash` | Fast image generation | ~$0.039/image | 1 credit |
| `gemini-3-pro-image-preview` | Best quality image generation | ~$0.134/image | 3 credits |
| `gemini-3-flash-preview` | Vision analysis, framework gen | ~$0.50/1M input | 1 credit |

## Credits System

Credits are the internal currency for image generation. Users purchase/earn credits, which are deducted when generating images.

### Credit Costs by Operation

| Operation | Credits | Notes |
|-----------|---------|-------|
| Framework Analysis | 1 | Vision/text analysis |
| Framework Preview | 1 | Always uses Flash |
| Listing Image (Flash) | 1 | Fast generation |
| Listing Image (Pro) | 3 | Best quality |
| A+ Module (Flash) | 1 | Fast generation |
| A+ Module (Pro) | 3 | Best quality |
| A+ Mobile Transform | 1 | Edit API |
| Edit Image | 1 | Edit API |

### Full Listing Cost

| Model | Total Credits | Breakdown |
|-------|---------------|-----------|
| **Pro (best)** | **47 credits** | 1 analysis + 4 previews + 18 listing (6×3) + 18 A+ (6×3) + 6 mobile |
| **Flash (fast)** | **23 credits** | 1 analysis + 4 previews + 6 listing + 6 A+ + 6 mobile |

### Pricing Plans

| Plan | Price | Credits | Full Listings (Pro) |
|------|-------|---------|---------------------|
| Free | $0 | 30/day | ~0.6/day |
| Starter | $15/mo | 300/mo | ~6/mo |
| Pro | $49/mo | 1000/mo | ~21/mo |
| Business | $149/mo | 3000/mo | ~64/mo |

### Admin Access

Admin users (configured in `ADMIN_EMAILS` env var) have unlimited credits and bypass all credit checks.

Default admin: `robertoxma@hotmail.com`

### Credit UI Components

The credits system includes a complete frontend experience:

**Credit Widget (Sidebar)**
- Always visible in sidebar showing current balance
- Admin users see "👑 ∞ UNLIMITED" with gold gradient styling
- Regular users see numeric balance with color-coded status:
  - Green (normal): >25% of plan credits remaining
  - Orange (warning): 10-25% remaining
  - Red (critical): <10% remaining
- Expandable panel shows progress bar and "View Plans" link
- Animated balance changes when credits are deducted

**Cost Preview (Generate Buttons)**
- Shows estimated credit cost below generate buttons
- Format: "5 credits" or "18 credits" depending on operation
- Updates based on selected AI model (Pro vs Flash)
- Helps users understand cost before committing

**Usage Toast (Post-Generation)**
- Appears after successful generation showing credits used
- Admin users see: "Admin mode - no credits deducted"
- Regular users see: "-5 credits • 25 remaining"
- Auto-dismisses after 4 seconds

**Credit Context**
- React context (`CreditContext`) provides credit state app-wide
- Exposes: `balance`, `isAdmin`, `planName`, `planTier`, `refetch()`
- `useCreditCost()` hook for estimating operation costs
- `recordUsage()` updates local state immediately for responsiveness

### Key Files

**Backend:**
- `app/services/credits_service.py` - Credit costs, plans, check/deduct logic
- `app/api/endpoints/settings.py` - `/credits`, `/plans`, `/credits/estimate` endpoints
- `app/config.py` - `admin_emails` configuration

**Frontend:**
- `frontend/src/contexts/CreditContext.tsx` - Credit state provider & hooks
- `frontend/src/components/CreditWidget.tsx` - Sidebar credit display
- `frontend/src/components/Layout.tsx` - Integrates CreditWidget in sidebar

## Generation Flow Summary

```
User uploads photos + fills product info
  → /frameworks/analyze (vision + 4 preview images)     ~5 credits
  → User picks framework
  → /frameworks/generate (6 listing images)              ~18 credits (Pro)
  → /aplus/script (visual script via text gen)           ~0 credits (text only)
  → /aplus/hero (hero pair, split into modules 0+1)      ~3 credits (Pro)
  → /aplus/module × 4 (canvas continuity for 2-5)        ~12 credits (Pro)
  → /aplus/mobile × 6 (desktop→mobile transforms)        ~6 credits
                                                    Total: ~47 credits (Pro)
```

## Future Scope / Roadmap
- ASIN import (scrape Amazon listing to pre-fill product info)
- Alt text generation per image (SEO)
- Seller Central export (ZIP with correct filenames/sizes)
- Stripe integration for paid plans
- More A+ section types (comparison tables, text+image)
- Batch generation for multiple products
- Social login (Google, GitHub)
- Team collaboration features
