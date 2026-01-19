# Listing Genie - Implementation Plan

**Version:** 1.0
**Date:** December 20, 2024
**Purpose:** Ordered implementation with test gates between phases

---

## Implementation Philosophy

Each phase must be **fully tested and working** before proceeding to the next.
No phase begins until the previous phase passes its test gate.

---

## Phase Overview

```
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 1: Foundation                                             │
│ Stories: 1.1 - 1.5                                              │
│ TEST GATE: Server runs, DB works, storage works                 │
├─────────────────────────────────────────────────────────────────┤
│ PHASE 2: AI Core                                                │
│ Stories: 2.1 - 2.8                                              │
│ TEST GATE: Can generate 1 image via API call                    │
├─────────────────────────────────────────────────────────────────┤
│ PHASE 3: User Input                                             │
│ Stories: 3.1 - 3.3                                              │
│ TEST GATE: Can upload image and fill form in browser            │
├─────────────────────────────────────────────────────────────────┤
│ PHASE 4: Keyword Intelligence                                   │
│ Stories: 4.1 - 4.4                                              │
│ TEST GATE: Keywords classified and injected into prompts        │
├─────────────────────────────────────────────────────────────────┤
│ PHASE 5: Output & Delivery                                      │
│ Stories: 5.1 - 5.4                                              │
│ TEST GATE: Full flow works, images downloadable                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## PHASE 1: Foundation

**Goal:** Backend and frontend infrastructure running and communicating.

### Stories

| ID | Title | Description | Complexity |
|----|-------|-------------|------------|
| 1.1 | FastAPI Backend Setup | Project structure, CORS, health endpoint | M |
| 1.2 | Database Setup | SQLite + SQLAlchemy models | M |
| 1.3 | Storage Setup | Local file storage for images | M |
| 1.4 | React Frontend Setup | Vite + React + API client | M |
| 1.5 | Dev Environment | Docker, .env, hot reload | S |

### Test Gate 1

Before proceeding to Phase 2, verify:

```bash
# Backend tests
□ GET /health returns 200
□ Database tables created (sessions, keywords, images)
□ Can write/read file to storage directory
□ API docs accessible at /docs

# Frontend tests
□ React app loads in browser
□ API client can call /health and get response
□ No console errors

# Integration test
□ Frontend can communicate with backend (CORS works)
```

**Command to verify:**
```bash
# Start backend
uvicorn app.main:app --reload

# Start frontend
npm run dev

# Test health endpoint
curl http://localhost:8000/health
```

---

## PHASE 2: AI Core

**Goal:** Generate images using Gemini API with prompt templates.

### Stories

| ID | Title | Description | Complexity |
|----|-------|-------------|------------|
| 2.1 | Gemini API Connection | Authenticate with google-genai SDK | M |
| 2.2 | Prompt Template System | Load and populate prompt templates | L |
| 2.3 | Main Image Generation | Generate main product image | L |
| 2.4 | Infographic Generation | Generate 2 infographic images | L |
| 2.5 | Lifestyle Generation | Generate lifestyle image | L |
| 2.6 | Comparison Generation | Generate comparison chart | L |
| 2.7 | Error Handling & Retry | Retry logic, error messages | M |
| 2.8 | Image Persistence | Save generated images to storage | M |

### Test Gate 2

Before proceeding to Phase 3, verify:

```bash
# Unit tests
□ Gemini API authenticates successfully
□ Prompt templates load without error
□ Each prompt template has required variables

# Integration tests (use test image)
□ Generate Main Image → saves to storage
□ Generate Infographic 1 → saves to storage
□ Generate Infographic 2 → saves to storage
□ Generate Lifestyle → saves to storage
□ Generate Comparison → saves to storage

# API tests
□ POST /api/generate with test data returns 5 image URLs
□ Retry logic works (mock a failure)
□ Error response is user-friendly
```

**Command to verify:**
```bash
# Run generation test
python -m pytest tests/test_generation.py -v

# Manual API test
curl -X POST http://localhost:8000/api/generate \
  -F "image=@test_product.jpg" \
  -F "title=Test Product" \
  -F "features=Feature 1, Feature 2, Feature 3" \
  -F "audience=Health conscious adults"
```

---

## PHASE 3: User Input

**Goal:** User can upload image and enter product info in browser.

### Stories

| ID | Title | Description | Complexity |
|----|-------|-------------|------------|
| 3.1 | Image Upload Component | Drag-drop, preview, validation | M |
| 3.2 | Product Info Form | Title, features, audience fields | S |
| 3.3 | Input Validation | Client + server validation | S |

### Test Gate 3

Before proceeding to Phase 4, verify:

```bash
# UI tests
□ Can drag-drop image onto upload zone
□ Can click to select image
□ Image preview displays after upload
□ Rejects files > 10MB with error message
□ Rejects non-image files with error message
□ Rejects images < 1000x1000px

# Form tests
□ All fields render correctly
□ Character counters work
□ Required field validation works
□ Form submits to backend

# Integration
□ Upload image → fill form → click Generate → backend receives data
```

**Command to verify:**
```bash
# Run E2E test
npx playwright test tests/e2e/upload-form.spec.ts

# Manual: Open browser, complete upload + form flow
```

---

## PHASE 4: Keyword Intelligence

**Goal:** Keywords input, classified by intent, injected into prompts.

### Stories

| ID | Title | Description | Complexity |
|----|-------|-------------|------------|
| 4.1 | Keyword Input UI | Text area, tag display, validation | S |
| 4.2 | Intent Classification | Categorize keywords by intent type | M |
| 4.3 | Intent-Aligned Prompts | Modify prompts based on intents | L |
| 4.4 | Heatmap Optimization | Composition guidance in prompts | M |

### Test Gate 4

Before proceeding to Phase 5, verify:

```bash
# Classification tests
□ "long-lasting" → Durability intent
□ "for camping" → Use Case intent
□ "modern" → Style intent
□ "pain relief" → Problem/Solution intent
□ "best" → Comparison intent

# Prompt injection tests
□ Durability keywords add texture/quality language to prompt
□ Use Case keywords add context scene to lifestyle prompt
□ Comparison keywords enhance comparison chart prompt

# UI tests
□ Can enter 5-20 keywords
□ Keywords display as tags
□ Can remove individual keywords
□ Intent classification preview shows
```

**Command to verify:**
```bash
# Run classification tests
python -m pytest tests/test_intent_classification.py -v

# Compare prompt output with/without keywords
python scripts/test_prompt_injection.py
```

---

## PHASE 5: Output & Delivery

**Goal:** Full end-to-end flow with gallery and download.

### Stories

| ID | Title | Description | Complexity |
|----|-------|-------------|------------|
| 5.1 | Gallery Display | Show 5 generated images | S |
| 5.2 | Image Preview Modal | Click to zoom, navigate | S |
| 5.3 | Individual Download | Download single image | S |
| 5.4 | Bulk Download (ZIP) | Download all as ZIP | M |

### Test Gate 5 (FINAL)

Before declaring MVP complete, verify:

```bash
# Full E2E flow
□ Upload product image
□ Fill product info form
□ Enter keywords
□ Click Generate
□ See generation progress (per-image status)
□ Gallery displays 5 images
□ Click image → preview modal opens
□ Download single image works
□ Download ZIP works
□ ZIP contains 5 correctly named images

# Quality checks
□ Generated images are 2000x2000px+
□ Main image has white background
□ Infographics have readable text
□ Lifestyle matches target audience
□ Comparison shows clear winner

# Performance
□ Total generation time < 5 minutes
□ No console errors
□ No UI freezing during generation
```

**Command to verify:**
```bash
# Full E2E test
npx playwright test tests/e2e/full-flow.spec.ts

# Manual smoke test with real product
```

---

## Story Mapping (PRD → Implementation Plan)

| Implementation ID | PRD Epic.Story | Title |
|-------------------|----------------|-------|
| **Phase 1** | | |
| 1.1 | 5.1 | FastAPI Backend Setup |
| 1.2 | 5.3 | Database Setup |
| 1.3 | 5.4 | Storage Setup |
| 1.4 | 5.2 | React Frontend Setup |
| 1.5 | 5.5 | Dev Environment |
| **Phase 2** | | |
| 2.1 | 2.1 | Gemini API Connection |
| 2.2 | 2.1b | Prompt Template System |
| 2.3 | 2.2 | Main Image Generation |
| 2.4 | 2.3 | Infographic Generation |
| 2.5 | 2.4 | Lifestyle Generation |
| 2.6 | 2.5 | Comparison Generation |
| 2.7 | 2.6 | Error Handling & Retry |
| 2.8 | 2.7 | Image Persistence |
| **Phase 3** | | |
| 3.1 | 1.1 | Image Upload Component |
| 3.2 | 1.2 | Product Info Form |
| 3.3 | 1.3 | Input Validation |
| **Phase 4** | | |
| 4.1 | 4.1 | Keyword Input UI |
| 4.2 | 4.2 | Intent Classification |
| 4.3 | 4.3 | Intent-Aligned Prompts |
| 4.4 | 4.4 | Heatmap Optimization |
| **Phase 5** | | |
| 5.1 | 3.1 | Gallery Display |
| 5.2 | 3.2 | Image Preview Modal |
| 5.3 | 3.3 | Individual Download |
| 5.4 | 3.4 | Bulk Download (ZIP) |

---

## Critical Rules

1. **NO SKIPPING PHASES** - Each test gate must pass
2. **FIX BEFORE PROCEED** - If a test fails, fix it before moving on
3. **DOCUMENT ISSUES** - Log any blockers encountered
4. **VERIFY ON DEVICE** - Not just in tests, actually use the app
5. **SCREENSHOTS** - Take screenshots of working features as proof

---

## Quick Start

```bash
# Clone and setup
cd listing_genie
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
npm install

# Start Phase 1
# Begin with Story 1.1: FastAPI Backend Setup
```

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | December 20, 2024 | System | Initial implementation plan |
