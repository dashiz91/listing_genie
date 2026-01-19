# Listing Genie

AI-powered Amazon listing image generator that creates professional product images for e-commerce sellers.

## Project Overview

This application uses a **two-step AI generation flow** to create complete Amazon listing image sets:

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

## Tech Stack

### Backend (Python/FastAPI)
- **Framework**: FastAPI with uvicorn
- **Database**: SQLite with SQLAlchemy ORM
- **AI Services**:
  - `gemini-3-flash-preview` - Vision analysis & prompt generation
  - `gemini-3-pro-image-preview` - Image generation
- **Storage**: Local file storage (`storage/uploads/`, `storage/generated/`)

### Frontend (React/TypeScript)
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: TailwindCSS
- **HTTP Client**: Axios

## Key Features

### 1. Color Mode System
Three modes for how AI handles colors:
- **`ai_decides`** - Full creative freedom, AI picks colors based on product
- **`suggest_primary`** - AI extracts colors from style reference image
- **`locked_palette`** - User locks exact hex colors, ALL 4 frameworks use them

Colors can be provided via:
- Brand Colors (Brand Identity section)
- Color Palette (Style & Color Options section)
- Either one triggers `locked_palette` mode

### 2. Style Reference Image
Upload a style reference and:
- AI sees it during framework analysis (extracts colors/style)
- All generated images follow that visual style
- Style ref is sent as reference image to Gemini with explicit instructions

### 3. Global Instructions
Add custom notes/instructions that apply to ALL 5 images:
- Processed by AI Designer (not appended raw to Gemini)
- Interpreted differently for each image type
- Example: "Make it feel premium" → different interpretation for Main vs Lifestyle

### 4. Edit & Regenerate
**Edit**: Modify an existing image while preserving layout
- Uses Gemini's edit capability with mask
- Good for: "Change headline", "Make background lighter"

**Regenerate**: Generate completely new image
- Can add notes/instructions for the regeneration
- AI Designer enhances the prompt based on feedback
- Tracks version history (v1, v2, etc.)

### 5. Prompt Viewer
View exactly what was sent to Gemini for any image:
- Full prompt text
- Designer context (framework, colors, typography)
- Reference images used (with previews)
- User feedback (for regenerations)

## Project Structure

```
listing_genie/
├── app/                              # Backend Python application
│   ├── api/
│   │   └── endpoints/
│   │       ├── generation.py         # Main generation endpoints
│   │       ├── images.py             # Image serving endpoints
│   │       ├── upload.py             # File upload endpoint
│   │       └── health.py             # Health check
│   ├── models/
│   │   └── database.py               # SQLAlchemy models
│   ├── prompts/
│   │   ├── ai_designer.py            # MAIN: All AI Designer prompts
│   │   ├── templates/                # Image-type specific templates
│   │   ├── styles.py                 # Style presets (legacy)
│   │   └── color_psychology.py       # Color theory reference
│   ├── services/
│   │   ├── generation_service.py     # Main orchestration logic
│   │   ├── gemini_service.py         # Gemini image generation
│   │   ├── gemini_vision_service.py  # Gemini vision analysis
│   │   ├── openai_vision_service.py  # OpenAI vision (backup)
│   │   ├── vision_service.py         # Vision service wrapper
│   │   └── storage_service.py        # File storage
│   ├── config.py                     # App configuration
│   └── main.py                       # FastAPI app entry point
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── client.ts             # API client methods
│   │   │   └── types.ts              # TypeScript types
│   │   ├── components/
│   │   │   ├── ProductForm.tsx       # Product info form
│   │   │   ├── ImageGallery.tsx      # Generated images display
│   │   │   ├── ImageUploader.tsx     # Multi-image uploader
│   │   │   └── FrameworkSelector.tsx # Framework selection UI
│   │   └── pages/
│   │       └── HomePage.tsx          # Main page (orchestrates flow)
│   └── package.json
├── storage/
│   ├── uploads/                      # Uploaded product images
│   └── generated/                    # AI-generated images
└── package.json                      # Root (runs both servers)
```

## Key Files

### Prompts (`app/prompts/ai_designer.py`)
All AI Designer prompts in one file for easy iteration:
- `PRINCIPAL_DESIGNER_VISION_PROMPT` - Framework analysis (Step 1)
- `GENERATE_IMAGE_PROMPTS_PROMPT` - 5 detailed prompts (Step 2)
- `ENHANCE_PROMPT_WITH_FEEDBACK_PROMPT` - Regeneration enhancement
- `GLOBAL_NOTE_INSTRUCTIONS` - How to apply user instructions
- `STYLE_REFERENCE_INSTRUCTIONS` - Style matching instructions
- `STYLE_REFERENCE_PROMPT_PREFIX` - Prepended to each Gemini call

### Services
- **`generation_service.py`** - Main orchestration, retry logic, prompt building
- **`gemini_vision_service.py`** - Framework generation, prompt generation
- **`gemini_service.py`** - Actual image generation calls to Gemini

### Database Models (`app/models/database.py`)
- `GenerationSession` - Main session (product info, settings, framework)
- `ImageRecord` - Individual generated images with status
- `DesignContext` - AI Designer's knowledge about the project
- `PromptHistory` - Version tracking for regenerations

## API Endpoints

### Upload
```
POST /api/upload/              Upload image (PNG, JPEG, WebP, GIF)
DELETE /api/upload/{id}        Delete uploaded image
```

### Generation
```
POST /api/generate/frameworks/analyze    Step 1: Analyze product, generate 4 frameworks
POST /api/generate/frameworks/generate   Step 2: Generate all 5 images with framework
POST /api/generate/single                Regenerate single image with note
POST /api/generate/edit                  Edit image (preserve layout, change details)
GET  /api/generate/{session_id}          Get session status
GET  /api/generate/{session_id}/prompts  Get all prompts for session
GET  /api/generate/{session_id}/prompts/{image_type}  Get prompt for specific image
```

### Images
```
GET /api/images/{session_id}                    Get all session images
GET /api/images/{session_id}/{image_type}       Get specific image
GET /api/images/file?path=...                   Get image by storage path
```

## Environment Variables

Required in `.env`:
```bash
GEMINI_API_KEY=your_gemini_api_key    # From Google AI Studio
DATABASE_URL=sqlite:///./listing_genie.db
```

Optional:
```bash
OPENAI_API_KEY=your_openai_key        # For OpenAI vision (backup)
VISION_PROVIDER=gemini                # or "openai"
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
venv\Scripts\activate
uvicorn app.main:app --reload --port 8000

# Frontend (Terminal 2)
cd frontend
npm run dev
```

### URLs
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Development Notes

### Generation Flow
1. User uploads product images → stored in `storage/uploads/`
2. User fills form (title, features, colors, style ref)
3. `POST /frameworks/analyze` → Gemini Vision analyzes, generates 4 frameworks + previews
4. User selects framework
5. `POST /frameworks/generate` → AI Designer generates 5 prompts, then 5 images
6. Images stored in `storage/generated/{session_id}/`

### Color Mode Logic (Frontend)
```typescript
if (hasBrandColors || hasColorPalette) {
  colorMode = 'locked_palette';  // Lock user's colors
} else if (hasStyleReference) {
  colorMode = 'suggest_primary'; // Extract from style ref
} else {
  colorMode = 'ai_decides';      // Full creative freedom
}
```

### Style Reference Flow
1. Style ref uploaded BEFORE framework analysis
2. Included in images sent to Gemini Vision
3. Special instructions tell AI to extract colors/style
4. During image generation, style ref is passed as reference image
5. Prompt prefix tells Gemini which image is the style reference

### Prompt History
- v1 = Original generation
- v2+ = Regenerations with user feedback
- `PromptHistory` table tracks all versions
- Prompt viewer shows full context for any version

### Key Debugging Logs
```
[API ENDPOINT] /frameworks/analyze called
[API ENDPOINT] Request color_mode: locked_palette
[API ENDPOINT] Request locked_colors: ['#705baa', '#e4dce8']
[API ENDPOINT] Request style_reference_path: storage/uploads/xxx.png

[GEMINI COLOR MODE DEBUG] LOCKED PALETTE MODE ACTIVATED!
[GEMINI COLOR MODE DEBUG] Colors to lock: #705baa, #e4dce8

[MAIN] Using 3 reference images:
  [Image 1] storage/uploads/product.png (PRIMARY PRODUCT)
  [Image 2] storage/uploads/style.png (STYLE REFERENCE)
  [Image 3] storage/uploads/logo.png (LOGO)
```

## API Cost (Gemini Free Tier)
- 1,500 images/day via Google AI Studio
- Typical session: ~10 images (4 previews + 5 main + edits)
- Can do ~150 sessions/day on free tier

## Future Scope
- A+ Content (Enhanced Brand Content) images
- Brand story modules
- Batch generation for multiple products
- Cloud storage integration
