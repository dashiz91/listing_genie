# Listing Genie - Product Requirements Document (PRD)

**Document Version:** 1.0
**Date:** December 20, 2024
**Status:** Draft
**Author:** John (Product Manager)
**Reference:** [Project Brief v1.0](./brief.md)

---

## 1. Product Overview

### 1.1 Vision Statement

Listing Genie democratizes professional Amazon listing image creation by leveraging AI to transform a single product photo into a complete set of conversion-optimized listing images. The platform eliminates the traditional bottleneck of time, cost, and expertise required for professional product photography, enabling Amazon sellers to launch products faster and more cost-effectively.

### 1.2 Product Summary

| Attribute | Description |
|-----------|-------------|
| **Product Name** | Listing Genie |
| **Product Type** | Web Application (SaaS) |
| **Target Launch** | Q1 2025 |
| **Pricing Model** | Pay-per-use ($9.99 per listing) |
| **Core Technology** | Gemini 3 Pro Image Preview via google-genai SDK |
| **Architecture** | FastAPI backend + Static React frontend (single container) |

### 1.3 Problem We Solve

Amazon sellers currently face a critical bottleneck:

- **Time:** 3-5 days minimum turnaround for professional listing images
- **Cost:** $50-200 per listing for design services
- **Quality Variance:** Inconsistent results dependent on individual designers
- **Compliance Risk:** Manual verification against Amazon requirements

Listing Genie reduces this to **5 minutes** and **$9.99** while maintaining professional quality aligned with proven Amazon conversion frameworks.

### 1.4 Success Metrics (First 90 Days)

| Metric | Target |
|--------|--------|
| Listings Generated | 500+ |
| Paying Customers | 100+ unique |
| Revenue | $5,000+ |
| Generation Success Rate | >95% |
| Average Generation Time | <3 minutes |
| Customer Satisfaction | >4.0/5 stars |

---

## 2. User Personas & Stories

### 2.1 Primary Persona: Marcus (Solo FBA Seller)

**Profile:** 32-year-old entrepreneur running a private label brand with 15-30 active SKUs

**Goals:**
- Launch new products faster than competitors
- Maintain professional brand appearance
- Minimize per-product costs to protect margins

**Frustrations:**
- Spending $2,000-4,000 annually on listing images
- Waiting weeks for designers during peak seasons
- Explaining Amazon requirements to every new designer

### 2.2 Secondary Persona: Sarah (Amazon Marketing Agency)

**Profile:** Founder of a 5-person Amazon brand management agency managing 8-12 brands

**Goals:**
- Deliver faster turnaround to clients
- Standardize quality across all client brands
- Improve margins on listing creation services

**Frustrations:**
- Designer bottlenecks limiting client capacity
- Inconsistent quality from freelance designers
- Difficulty scaling operations

### 2.3 High-Level User Stories by Persona

#### Marcus (Solo Seller) Stories

| ID | User Story |
|----|------------|
| US-M1 | As a solo seller, I want to upload a photo of my product so that I can start the image generation process |
| US-M2 | As a solo seller, I want to describe my product's key features so that the AI can highlight them in the generated images |
| US-M3 | As a solo seller, I want to pay a one-time fee per listing so that I can control my costs without subscriptions |
| US-M4 | As a solo seller, I want to download all images at once so that I can quickly upload them to Amazon Seller Central |
| US-M5 | As a solo seller, I want images that meet Amazon's requirements so that my listings don't get rejected |

#### Sarah (Agency) Stories

| ID | User Story |
|----|------------|
| US-S1 | As an agency owner, I want to generate images for multiple clients efficiently so that I can scale my operations |
| US-S2 | As an agency owner, I want consistent quality across generations so that I can maintain client trust |
| US-S3 | As an agency owner, I want to preview images before downloading so that I can verify quality before delivery |
| US-S4 | As an agency owner, I want a history of past generations so that I can reference previous work |

---

## 3. Functional Requirements

### 3.1 Product Input Requirements

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| FR-1.1 | System shall accept single image upload (JPEG, PNG) | Must Have | Max 10MB file size |
| FR-1.2 | System shall validate image format and dimensions | Must Have | Minimum 1000x1000px |
| FR-1.3 | System shall provide product title input field | Must Have | Max 200 characters |
| FR-1.4 | System shall provide 3 key features input fields | Must Have | Max 100 characters each |
| FR-1.5 | System shall provide target audience input field | Must Have | Max 150 characters |
| FR-1.6 | System shall display upload progress indicator | Should Have | For UX feedback |
| FR-1.7 | System shall preview uploaded image before proceeding | Should Have | Confirm correct image |

### 3.2 Keyword Intent Requirements

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| FR-2.1 | System shall accept bulk keyword input (5-20 keywords) | Must Have | Text area or paste |
| FR-2.2 | System shall classify keywords by intent type | Must Have | Durability, Use Case, Style, Problem/Solution, Comparison |
| FR-2.3 | System shall display intent classification to user | Must Have | Editable groupings |
| FR-2.4 | System shall incorporate intents into image prompts | Must Have | Intent-aligned generation |
| FR-2.5 | System shall optimize composition for heatmap attention | Should Have | Mobile-first eye-tracking |
| FR-2.6 | System shall save keywords with generation session | Should Have | For reference/iteration |

### 3.3 Image Generation Requirements

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| FR-3.1 | System shall generate exactly 5 images per listing | Must Have | As defined in brief |
| FR-3.2 | System shall generate Main Image (dynamic composition) | Must Have | White background |
| FR-3.3 | System shall generate Infographic 1 (feature #1) | Must Have | Bold text overlay |
| FR-3.4 | System shall generate Infographic 2 (feature #2) | Must Have | Bold text overlay |
| FR-3.5 | System shall generate Lifestyle Image | Must Have | Instagram aesthetic |
| FR-3.6 | System shall generate Comparison Chart | Must Have | Check vs X format |
| FR-3.7 | System shall output images at 2000x2000px minimum | Must Have | Amazon HD requirement |
| FR-3.8 | System shall complete generation in <3 minutes total | Should Have | User expectation |
| FR-3.9 | System shall display progress during generation | Must Have | Per-image status |
| FR-3.10 | System shall implement retry logic for failures | Must Have | Max 3 retries per image |
| FR-3.11 | System shall handle API rate limits gracefully | Should Have | Queue if needed |

### 3.4 Gallery & Download Requirements

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| FR-4.1 | System shall display all 5 generated images in gallery | Must Have | Grid layout |
| FR-4.2 | System shall provide image preview/zoom functionality | Should Have | Click to enlarge |
| FR-4.3 | System shall allow individual image download | Must Have | PNG format |
| FR-4.4 | System shall allow bulk download as ZIP | Must Have | All 5 images |
| FR-4.5 | System shall label images by type in download | Should Have | Filename convention |
| FR-4.6 | System shall maintain image availability for 7 days | Should Have | Cloud storage |

### 3.5 Error Handling Requirements

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| FR-5.1 | System shall display user-friendly error messages | Must Have | No technical jargon |
| FR-5.2 | System shall log all errors for debugging | Must Have | Backend logging |
| FR-5.3 | System shall provide retry option on failure | Must Have | User-initiated |
| FR-5.4 | System shall trigger refund on complete failure | Must Have | After max retries |
| FR-5.5 | System shall notify user of generation status | Must Have | Success/failure |

---

## 4. Non-Functional Requirements

### 4.1 Performance

| Requirement | Target | Notes |
|-------------|--------|-------|
| Image generation time | <60 seconds per image | Individual image target |
| Total listing time | <5 minutes | End-to-end user journey |
| Page load time | <3 seconds | Initial page render |
| Concurrent users | 20+ simultaneous | MVP scale target |

### 4.2 Reliability

| Requirement | Target | Notes |
|-------------|--------|-------|
| System uptime | 99.5% | Monthly availability |
| Generation success rate | >95% | Excluding user errors |
| Data persistence | 7 days | Generated image retention |

### 4.3 Security

| Requirement | Description |
|-------------|-------------|
| HTTPS | All traffic encrypted |
| Payment security | PCI-compliant via Stripe |
| Image storage | Secure cloud storage with expiring URLs |
| No credential storage | Stripe handles all payment data |

### 4.4 Compatibility

| Platform | Requirement |
|----------|-------------|
| Desktop browsers | Chrome, Firefox, Safari, Edge (latest 2 versions) |
| Mobile browsers | iOS Safari, Chrome Mobile (responsive design) |
| Image formats | JPEG, PNG input and output |

---

## 5. Epics & User Stories

### Epic 1: User Onboarding & Product Input

**Epic Description:** Enable users to upload their product photo and provide product information that will be used to generate listing images.

**Epic Goal:** Capture all necessary inputs for AI image generation with proper validation and user feedback.

---

#### Story 1.1: Product Photo Upload

**Title:** Upload Product Photo

**User Story:** As a user, I want to upload a photo of my product so that it can be used as the base for generating listing images.

**Acceptance Criteria:**
- [ ] User can drag-and-drop or click to select an image file
- [ ] System accepts JPEG and PNG formats only
- [ ] System rejects files larger than 10MB with clear error message
- [ ] System rejects images smaller than 1000x1000 pixels with clear error message
- [ ] Upload progress indicator displays during upload
- [ ] Uploaded image displays as preview after successful upload
- [ ] User can remove uploaded image and upload a different one

**Priority:** Must Have
**Complexity:** Medium
**Dependencies:** None

---

#### Story 1.2: Product Information Form

**Title:** Fill Product Information Form

**User Story:** As a user, I want to enter my product's title, key features, and target audience so that the AI can generate relevant listing images.

**Acceptance Criteria:**
- [ ] Form displays after successful image upload
- [ ] Product title field accepts up to 200 characters
- [ ] Three key feature fields each accept up to 100 characters
- [ ] Target audience field accepts up to 150 characters
- [ ] All fields are required before proceeding
- [ ] Character count displays for each field
- [ ] Form validates on blur and before submission
- [ ] Clear validation error messages display for empty/invalid fields

**Priority:** Must Have
**Complexity:** Small
**Dependencies:** Story 1.1

---

#### Story 1.3: Input Validation & Error Handling

**Title:** Validate Inputs Before Payment

**User Story:** As a user, I want to see clear error messages if my inputs are invalid so that I can correct them before paying.

**Acceptance Criteria:**
- [ ] System validates all inputs before enabling payment button
- [ ] Image validation includes format, size, and dimensions
- [ ] Text validation includes required fields and character limits
- [ ] Error messages are specific and actionable
- [ ] Errors display inline near the relevant field
- [ ] User cannot proceed to payment with validation errors
- [ ] Valid form displays visual confirmation (green checkmarks)

**Priority:** Must Have
**Complexity:** Small
**Dependencies:** Story 1.1, Story 1.2

---

### Epic 2: Image Generation Engine

**Epic Description:** Connect to Gemini API and generate 5 distinct Amazon-optimized listing images using specialized prompts for each image type.

**Epic Goal:** Produce high-quality, conversion-focused listing images that meet Amazon's requirements.

---

#### Story 2.1: Gemini API Integration

**Title:** Connect to Gemini API

**User Story:** As the system, I need to connect to the Gemini API so that I can generate images using AI.

**Acceptance Criteria:**
- [ ] System authenticates with Gemini API using google-genai SDK
- [ ] API credentials stored securely as environment variables
- [ ] Connection test endpoint available for health checks
- [ ] Proper error handling for authentication failures
- [ ] API timeout handling (60 second limit per request)
- [ ] Rate limit detection and handling
- [ ] Reference image support (pass uploaded product photo to API)

**Priority:** Must Have
**Complexity:** Medium
**Dependencies:** None

---

#### Story 2.1b: Prompt Engineering System

**Title:** Implement Creative Blueprint Prompt Templates

**User Story:** As the system, I need a prompt engineering system based on the Creative Blueprint so that generated images follow high-conversion Amazon listing best practices.

**Acceptance Criteria:**
- [ ] Prompt templates implement Creative Blueprint guidelines (docs/creative-blueprint.md)
- [ ] Main Image prompt includes: dynamic composition, stacking, ingredient pop, premium textures
- [ ] Infographic prompts include: benefit-focused headlines, bold text, <20% text density
- [ ] Lifestyle prompt includes: Instagram aesthetic, target audience matching, emotional resonance
- [ ] Comparison prompt includes: check vs. X format, color psychology, clear winner hierarchy
- [ ] All prompts pass uploaded product photo as reference image
- [ ] Prompts inject product title, features, and target audience dynamically
- [ ] Color palette selected based on product category (organic→earthy, fitness→neons, etc.)
- [ ] Prompt templates stored as configurable files (easy to iterate/improve)
- [ ] A/B testing capability for prompt variations (track which prompts perform best)

**Priority:** Must Have
**Complexity:** Large
**Dependencies:** Story 2.1

**Notes:** This story represents core IP. Prompt quality directly determines output quality and user satisfaction. Invest significant effort here.

**Reference:** See docs/creative-blueprint.md for full prompt templates and guidelines.

---

#### Story 2.2: Main Image Generation

**Title:** Generate Main Product Image

**User Story:** As a user, I want a professional main image with dynamic composition so that my product stands out in Amazon search results.

**Acceptance Criteria:**
- [ ] System generates main image using specialized prompt
- [ ] Image has pure white background (#FFFFFF)
- [ ] Product fills 85%+ of frame
- [ ] Image includes dynamic composition elements (stacking, textures)
- [ ] No text or watermarks on main image
- [ ] Output resolution is 2000x2000px minimum
- [ ] Image is saved to cloud storage with unique identifier

**Priority:** Must Have
**Complexity:** Large
**Dependencies:** Story 2.1

---

#### Story 2.3: Infographic Image Generation

**Title:** Generate Infographic Images (2)

**User Story:** As a user, I want infographic images that highlight my product's key features so that customers quickly understand my product's benefits.

**Acceptance Criteria:**
- [ ] System generates 2 infographic images
- [ ] Infographic 1 highlights key feature #1 with bold text
- [ ] Infographic 2 highlights key feature #2 with bold text
- [ ] Text is large and readable at thumbnail size
- [ ] Product is visible alongside feature callouts
- [ ] Text density is under 20% of image area
- [ ] Output resolution is 2000x2000px minimum
- [ ] Images saved to cloud storage with unique identifiers

**Priority:** Must Have
**Complexity:** Large
**Dependencies:** Story 2.1, Story 2.2

---

#### Story 2.4: Lifestyle Image Generation

**Title:** Generate Lifestyle Image

**User Story:** As a user, I want a lifestyle image with an Instagram-style aesthetic so that customers can envision using my product.

**Acceptance Criteria:**
- [ ] System generates lifestyle image using specialized prompt
- [ ] Image has authentic, Instagram-style photography feel
- [ ] Product shown in realistic usage context
- [ ] Context matches target audience description
- [ ] Professional lighting and composition
- [ ] Output resolution is 2000x2000px minimum
- [ ] Image saved to cloud storage with unique identifier

**Priority:** Must Have
**Complexity:** Large
**Dependencies:** Story 2.1

---

#### Story 2.5: Comparison Chart Generation

**Title:** Generate Comparison Chart Image

**User Story:** As a user, I want a comparison chart showing my product's advantages so that customers can see why my product is better.

**Acceptance Criteria:**
- [ ] System generates comparison chart using specialized prompt
- [ ] Chart uses visual check vs X format
- [ ] Features from key features #2 and #3 are highlighted
- [ ] Strong color contrast for readability
- [ ] Professional, clean design
- [ ] Output resolution is 2000x2000px minimum
- [ ] Image saved to cloud storage with unique identifier

**Priority:** Must Have
**Complexity:** Large
**Dependencies:** Story 2.1

---

#### Story 2.6: Generation Error Handling & Retry

**Title:** Handle Generation Errors with Retry Logic

**User Story:** As a user, I want the system to automatically retry if image generation fails so that I receive my images without manual intervention.

**Acceptance Criteria:**
- [ ] System implements retry logic with max 3 attempts per image
- [ ] Exponential backoff between retries (1s, 2s, 4s)
- [ ] Different prompts attempted on retry (prompt variation)
- [ ] User notified of retry attempts in progress UI
- [ ] Partial success handled (some images generated)
- [ ] Complete failure triggers refund process
- [ ] All failures logged with details for debugging

**Priority:** Must Have
**Complexity:** Medium
**Dependencies:** Stories 2.2-2.5

---

#### Story 2.7: Image Storage & Management

**Title:** Store Generated Images

**User Story:** As the system, I need to store generated images securely so that users can download them and reference them later.

**Acceptance Criteria:**
- [ ] Generated images stored in cloud storage (S3 or equivalent)
- [ ] Images organized by generation session ID
- [ ] Secure, expiring URLs generated for download
- [ ] Images retained for minimum 7 days
- [ ] Storage cleanup job for expired images
- [ ] Image metadata stored in database (type, generation date, etc.)

**Priority:** Must Have
**Complexity:** Medium
**Dependencies:** Stories 2.2-2.5

---

### Epic 3: Gallery & Download

**Epic Description:** Display generated images in an attractive gallery view and provide flexible download options for users.

**Epic Goal:** Enable users to preview, select, and download their generated images efficiently.

---

#### Story 3.1: Image Gallery Display

**Title:** Display Generated Images in Gallery

**User Story:** As a user, I want to see all my generated images in a gallery view so that I can review them before downloading.

**Acceptance Criteria:**
- [ ] Gallery displays all 5 generated images in grid layout
- [ ] Each image labeled by type (Main, Infographic 1, etc.)
- [ ] Images display in consistent, responsive grid
- [ ] Gallery loads with generation complete notification
- [ ] Skeleton loaders display while images load
- [ ] Gallery is scrollable on mobile devices

**Priority:** Must Have
**Complexity:** Small
**Dependencies:** Epic 2 complete

---

#### Story 3.2: Image Preview/Zoom

**Title:** Preview Full-Size Images

**User Story:** As a user, I want to click on an image to view it full-size so that I can check the quality and details.

**Acceptance Criteria:**
- [ ] Clicking image opens full-size preview modal
- [ ] Modal displays image at maximum screen-fitting size
- [ ] Modal includes image type label
- [ ] Close button clearly visible
- [ ] ESC key closes modal
- [ ] Click outside modal closes it
- [ ] Navigation between images in preview mode

**Priority:** Should Have
**Complexity:** Small
**Dependencies:** Story 3.1

---

#### Story 3.3: Individual Image Download

**Title:** Download Single Images

**User Story:** As a user, I want to download individual images so that I can choose which ones to use.

**Acceptance Criteria:**
- [ ] Download button visible for each image in gallery
- [ ] Download button visible in preview modal
- [ ] Images download as PNG format
- [ ] Filename includes image type (e.g., "listing_main_image.png")
- [ ] Download triggers browser's native download
- [ ] Download works on mobile devices

**Priority:** Must Have
**Complexity:** Small
**Dependencies:** Story 3.1

---

#### Story 3.4: Bulk Download (ZIP)

**Title:** Download All Images as ZIP

**User Story:** As a user, I want to download all images at once as a ZIP file so that I can quickly get all my listing images.

**Acceptance Criteria:**
- [ ] "Download All" button prominently displayed
- [ ] ZIP file contains all 5 images
- [ ] Each image in ZIP has descriptive filename
- [ ] ZIP file named with product title or session ID
- [ ] Download progress indicator for ZIP creation
- [ ] ZIP generation happens server-side
- [ ] Download works on mobile devices

**Priority:** Must Have
**Complexity:** Medium
**Dependencies:** Story 3.1

---

### Epic 4: Keyword Intent System

**Epic Description:** Enable users to input keywords and align image generation with buyer search intent, following Chris Rawlings' "closing the loop" strategy.

**Epic Goal:** Generate images that visually prove the intent behind the keywords, maximizing conversion by matching what searchers expect to see.

**Reference:** Chris Rawlings' PPC Data Loop strategy - aligning visual assets with keyword intent to convert traffic.

---

#### Story 4.1: Keyword Input Interface

**Title:** Add Keyword Input for Intent-Based Generation

**User Story:** As a user, I want to input my top-performing keywords so that the generated images align with what my customers are searching for.

**Acceptance Criteria:**
- [ ] Text area for bulk keyword input (one per line or comma-separated)
- [ ] Support for 5-20 keywords per generation
- [ ] Keywords parsed and validated
- [ ] Optional: paste directly from Amazon PPC reports
- [ ] Keywords displayed as tags after input
- [ ] Ability to remove individual keywords
- [ ] Keywords saved with generation session

**Priority:** Must Have
**Complexity:** Small
**Dependencies:** Story 1.2

---

#### Story 4.2: Keyword Intent Classification

**Title:** Classify Keywords by Buyer Intent

**User Story:** As the system, I need to classify keywords by intent type so that images can be tailored to specific buyer motivations.

**Acceptance Criteria:**
- [ ] System categorizes keywords into intent groups:
  - Durability/Quality (e.g., "long-lasting", "premium", "heavy-duty")
  - Use Case (e.g., "for camping", "office use", "travel size")
  - Style/Aesthetic (e.g., "modern", "minimalist", "vintage")
  - Problem/Solution (e.g., "pain relief", "easy clean", "quick setup")
  - Comparison (e.g., "best", "vs", "alternative to")
- [ ] AI-assisted classification using keyword analysis
- [ ] User can review and adjust classifications
- [ ] Intent groups inform prompt generation
- [ ] Multiple intents per keyword supported

**Priority:** Must Have
**Complexity:** Medium
**Dependencies:** Story 4.1

---

#### Story 4.3: Intent-Aligned Image Generation

**Title:** Generate Images Matching Keyword Intent

**User Story:** As a user, I want each image to visually prove the intent behind my keywords so that shoppers see exactly what they searched for.

**Acceptance Criteria:**
- [ ] Prompts dynamically incorporate keyword intent
- [ ] Durability intent → show rugged textures, stress tests, comparison to competitors
- [ ] Use case intent → show product in that exact context (camping scene, office desk, etc.)
- [ ] Style intent → match visual aesthetic to style keywords
- [ ] Problem/solution intent → show before/after or relief/result
- [ ] Each image type prioritizes different intent groups:
  - Main Image: Quality/Premium intents
  - Lifestyle: Use Case intents
  - Infographics: Problem/Solution intents
  - Comparison: Comparison intents
- [ ] Keywords visible in generation metadata for reference

**Priority:** Must Have
**Complexity:** Large
**Dependencies:** Story 4.2, Story 2.1b

---

#### Story 4.4: Heatmap Optimization

**Title:** Optimize Image Composition for Visual Attention

**User Story:** As a user, I want my images optimized for where shoppers look first so that key elements capture attention immediately.

**Acceptance Criteria:**
- [ ] Prompts include composition guidance based on eye-tracking heatmap data:
  - Primary focus zone: center-left for main product
  - Secondary zone: top-right for key benefit text
  - F-pattern reading flow for infographics
  - Mobile-first: larger elements, higher contrast
- [ ] Key selling points positioned in high-attention areas
- [ ] Text overlays placed in optimal reading zones
- [ ] Product positioned to maximize visual weight
- [ ] Negative space used strategically to direct attention

**Priority:** Should Have
**Complexity:** Medium
**Dependencies:** Story 2.1b

---

### Epic 5: Core Infrastructure

**Epic Description:** Set up the foundational backend and frontend infrastructure required to support all features.

**Epic Goal:** Establish a reliable, deployable infrastructure that supports the full user workflow.

---

#### Story 5.1: FastAPI Backend Setup

**Title:** Set Up FastAPI Backend

**User Story:** As a developer, I need a FastAPI backend set up so that the frontend can interact with APIs for all features.

**Acceptance Criteria:**
- [ ] FastAPI application with proper project structure
- [ ] Environment variable configuration (.env support)
- [ ] CORS configured for frontend origin
- [ ] Health check endpoint (/health)
- [ ] Error handling middleware
- [ ] Request logging middleware
- [ ] API documentation via Swagger UI (/docs)

**Priority:** Must Have
**Complexity:** Medium
**Dependencies:** None

---

#### Story 5.2: React Frontend Setup

**Title:** Set Up Static React Frontend

**User Story:** As a developer, I need a React frontend set up so that users can interact with the application.

**Acceptance Criteria:**
- [ ] React application with Vite or Create React App
- [ ] Responsive layout with mobile-first design
- [ ] Component structure for all major features
- [ ] API client for backend communication
- [ ] Environment variable configuration
- [ ] Production build configuration
- [ ] Static assets served by backend

**Priority:** Must Have
**Complexity:** Medium
**Dependencies:** Story 5.1

---

#### Story 5.3: Database Setup

**Title:** Set Up Database for Persistence

**User Story:** As the system, I need a database to store generation sessions, payment records, and image metadata.

**Acceptance Criteria:**
- [ ] PostgreSQL or SQLite database configured
- [ ] ORM setup (SQLAlchemy) with models
- [ ] Generation session model (id, status, created_at, etc.)
- [ ] Keywords model (keyword, intent_type, generation_id, etc.)
- [ ] Image metadata model (type, url, generation_id, etc.)
- [ ] Database migrations support
- [ ] Connection pooling configured

**Priority:** Must Have
**Complexity:** Medium
**Dependencies:** Story 5.1

---

#### Story 5.4: Cloud Storage Configuration

**Title:** Configure Cloud Storage

**User Story:** As the system, I need cloud storage configured so that generated images can be stored and retrieved.

**Acceptance Criteria:**
- [ ] Cloud storage provider configured (S3, GCS, or equivalent)
- [ ] Upload functionality implemented
- [ ] Signed URL generation for secure access
- [ ] URL expiration set (7 days default)
- [ ] Storage bucket/container properly secured
- [ ] Cleanup job for expired images

**Priority:** Must Have
**Complexity:** Medium
**Dependencies:** Story 5.1

---

#### Story 5.5: Deployment Configuration

**Title:** Configure Single Container Deployment

**User Story:** As a developer, I need deployment configuration so that the application can be deployed to production.

**Acceptance Criteria:**
- [ ] Dockerfile for single container deployment
- [ ] Frontend build integrated with backend serving
- [ ] Environment variable handling for production
- [ ] Health check endpoint for container orchestration
- [ ] Logging configuration for production
- [ ] Railway/Render deployment configuration
- [ ] CI/CD pipeline basics (optional for MVP)

**Priority:** Must Have
**Complexity:** Medium
**Dependencies:** Stories 5.1-5.4

---

## 6. User Flow Summary

```
[Landing Page]
     |
     v
[Upload Product Photo] --> [Validation Error] --> [Correct & Retry]
     |
     v
[Fill Product Info Form] --> [Validation Error] --> [Correct & Retry]
     |
     v
[Enter Keywords] --> [Intent Classification Preview]
     |
     v
[Review & Generate Button]
     |
     v
[Generation In Progress] --> [Generation Failed] --> [Retry]
  (per-image status)
     |
     v
[Gallery View]
     |
     +---> [Preview/Zoom Image]
     |
     +---> [Download Individual Images]
     |
     +---> [Download All as ZIP]
     |
     v
[Complete - User can generate new listing]
```

**Note:** Payment integration (Stripe) deferred to Phase 2. Current version is for internal use.

---

## 7. Out of Scope (Phase 2+)

The following features are explicitly out of scope for MVP:

**Deferred to Phase 2:**
- Payment integration (Stripe checkout, $9.99/listing)
- User accounts and authentication
- Generation history (requires accounts)
- Subscription pricing tiers

**Future Phases:**
- A+ Content / Brand Story images (5 additional images)
- Multiple product photo uploads
- Brand style customization
- White-label / API access for agencies
- Video generation or motion stills
- Multi-language support
- Direct Amazon Seller Central integration
- Regeneration of individual images
- Prompt customization by user
- PPC data import (direct Amazon API integration)

---

## 8. Technical Notes

### 8.1 Image Generation Prompts

**CRITICAL REFERENCE:** All prompt engineering MUST follow the [Creative Blueprint](./creative-blueprint.md).

The Creative Blueprint defines:
- Visual psychology principles for high-conversion images
- Specific techniques per image type (stacking, ingredient pop, etc.)
- Color psychology for emotional resonance
- Prompt template structures with examples
- Quality checklist for generated images

#### Summary Table

| Image Type | Creative Objective | Key Tactic |
|------------|-------------------|------------|
| Main Image | Stop the scroll | Stacked products, "action" elements (pours, slices), ingredient pop |
| Infographic 1 | Educate quickly | Large, bold text; key benefit #1; <20% text density |
| Infographic 2 | Educate quickly | Large, bold text; key benefit #2; <20% text density |
| Lifestyle | Build desire | "Instagram-style" authentic photography, target audience match |
| Comparison | Remove doubt | Visual "check vs. X" charts using color contrast |

### 8.2 Reference Image Implementation

Following the existing Gemini MCP pattern, the system uses the uploaded product photo as a reference image:

```python
# Pass product photo as reference to maintain accuracy
contents = [prompt, uploaded_product_image]

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=contents,
    config=types.GenerateContentConfig(
        response_modalities=['Image'],
        image_config=types.ImageConfig(aspect_ratio="1:1")
    )
)
```

This ensures:
- Generated images accurately represent the actual product
- AI enhances/stages the product without altering it
- Consistent product appearance across all 5 images

### 8.2 API Cost Estimates

| Component | Cost per Listing |
|-----------|------------------|
| Gemini API (5 images) | $1.34-2.40 |
| Stripe Fees | $0.59 |
| Infrastructure | ~$0.10 |
| **Total COGS** | ~$2.00-3.10 |
| **Gross Profit** | ~$6.90-8.00 (69-80% margin) |

### 8.3 Deployment Architecture

```
[Single Container]
  |
  +-- FastAPI Backend
  |     |-- API Endpoints
  |     |-- Static File Server (React build)
  |     +-- Background Tasks (generation)
  |
  +-- React Frontend (built static files)

[External Services]
  |
  +-- Gemini API (image generation)
  +-- Stripe (payments)
  +-- Cloud Storage (S3/GCS)
  +-- PostgreSQL (database)
```

---

## 9. Risks & Mitigations (Product Perspective)

| Risk | Mitigation |
|------|------------|
| Users expect instant results | Set clear expectations (3-5 min), show progress |
| Image quality not meeting expectations | Free regeneration offer, quality scoring before display |
| Amazon rejects generated images | Build compliance checks into prompts, document limitations |
| Payment friction | Stripe's trusted checkout reduces abandonment |
| Mobile experience | Responsive design, tested on iOS/Android browsers |

---

## 10. Story Summary Matrix

| Epic | Story ID | Title | Priority | Complexity |
|------|----------|-------|----------|------------|
| 1 | 1.1 | Upload Product Photo | Must Have | M |
| 1 | 1.2 | Fill Product Information Form | Must Have | S |
| 1 | 1.3 | Validate Inputs Before Payment | Must Have | S |
| 2 | 2.1 | Connect to Gemini API | Must Have | M |
| 2 | 2.1b | Implement Creative Blueprint Prompt Templates | Must Have | L |
| 2 | 2.2 | Generate Main Product Image | Must Have | L |
| 2 | 2.3 | Generate Infographic Images (2) | Must Have | L |
| 2 | 2.4 | Generate Lifestyle Image | Must Have | L |
| 2 | 2.5 | Generate Comparison Chart Image | Must Have | L |
| 2 | 2.6 | Handle Generation Errors with Retry | Must Have | M |
| 2 | 2.7 | Store Generated Images | Must Have | M |
| 3 | 3.1 | Display Generated Images in Gallery | Must Have | S |
| 3 | 3.2 | Preview Full-Size Images | Should Have | S |
| 3 | 3.3 | Download Single Images | Must Have | S |
| 3 | 3.4 | Download All Images as ZIP | Must Have | M |
| 4 | 4.1 | Add Keyword Input for Intent-Based Generation | Must Have | S |
| 4 | 4.2 | Classify Keywords by Buyer Intent | Must Have | M |
| 4 | 4.3 | Generate Images Matching Keyword Intent | Must Have | L |
| 4 | 4.4 | Optimize Image Composition for Visual Attention | Should Have | M |
| 5 | 5.1 | Set Up FastAPI Backend | Must Have | M |
| 5 | 5.2 | Set Up Static React Frontend | Must Have | M |
| 5 | 5.3 | Set Up Database for Persistence | Must Have | M |
| 5 | 5.4 | Configure Cloud Storage | Must Have | M |
| 5 | 5.5 | Configure Single Container Deployment | Must Have | M |

**Total Stories:** 24
**Must Have:** 21
**Should Have:** 3
**Complexity Distribution:** S: 8, M: 11, L: 5

**Core IP Stories:**
- Story 2.1b (Prompt Engineering) - Foundation of image quality
- Story 4.3 (Intent-Aligned Generation) - "Closing the loop" between keywords and visuals

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | December 20, 2024 | John (PM) | Initial PRD based on Project Brief v1.0 |

---

*This PRD serves as the product specification for Listing Genie MVP. All development work should reference this document for feature scope and acceptance criteria. Changes to scope require PRD version update and stakeholder approval.*
