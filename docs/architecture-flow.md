# Listing Genie - Architecture & Data Flow

## Overview Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              USER INPUT (Frontend)                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Product Images (1-5)  │  Product Info         │  Optional Inputs              │
│  ├─ Primary image      │  ├─ Product title     │  ├─ Primary color (#hex)      │
│  └─ Additional images  │  ├─ Features (1-3)    │  ├─ Logo image                │
│                        │  ├─ Target audience   │  ├─ Style reference image     │
│                        │  └─ Brand name        │  └─ Global note (instructions)│
└────────────────────────┴──────────────────────┴───────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    STEP 1: Framework Analysis                                    │
│                    Endpoint: POST /api/generate/frameworks/analyze               │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ┌───────────────────┐     ┌─────────────────────────────────────────────┐     │
│   │   Product Image   │────▶│         VISION AI (Principal Designer)       │     │
│   │   (Primary only)  │     │         (Gemini 3 Flash or GPT-4o)          │     │
│   └───────────────────┘     │                                             │     │
│                              │  Receives:                                  │     │
│   ┌───────────────────┐     │  • Product image (SEES it)                  │     │
│   │   Text Context    │────▶│  • Product title, features, audience        │     │
│   │   product_title   │     │  • Brand name                               │     │
│   │   features        │     │  • Primary color (SUGGESTION, not mandate)  │     │
│   │   target_audience │     │                                             │     │
│   │   primary_color   │     │  Outputs:                                   │     │
│   └───────────────────┘     │  • Product analysis (what AI sees)          │     │
│                              │  • 4 Design Frameworks with:                │     │
│                              │    - Color palette (5 hex codes)            │     │
│                              │    - Typography specs                       │     │
│                              │    - Story arc (5-image narrative)          │     │
│                              │    - Image copy (headlines, callouts)       │     │
│                              │    - Layout & visual treatment              │     │
│                              └─────────────────────────────────────────────┘     │
│                                                │                                 │
│                                                ▼                                 │
│                              ┌─────────────────────────────────────────────┐     │
│                              │     PREVIEW IMAGE GENERATION (Gemini)       │     │
│                              │     Generate 4 preview images (parallel)    │     │
│                              │                                             │     │
│                              │  For each framework:                        │     │
│                              │  ├─ Text prompt: framework_to_prompt()      │     │
│                              │  └─ Reference: [product_image]              │     │
│                              └─────────────────────────────────────────────┘     │
│                                                                                  │
└────────────────────────────────────────────────────────────────────────────────┬┘
                                                                                  │
                                      ┌───────────────────────────────────────────┘
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    USER SELECTS A FRAMEWORK                                      │
│                    (Sees 4 preview images with different styles)                 │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    STEP 2: Full Image Generation                                 │
│                    Endpoint: POST /api/generate/frameworks/generate              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   STEP 2A: Generate 5 Detailed Image Prompts                                     │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                    VISION AI (Prompt Generator)                          │   │
│   │                                                                          │   │
│   │   Receives:                                                              │   │
│   │   • Selected framework (colors, typography, story_arc, copy, etc.)       │   │
│   │   • Product name, features, target audience                              │   │
│   │                                                                          │   │
│   │   Outputs 5 DETAILED text prompts (~500 words each):                     │   │
│   │   ├─ Image 1 (MAIN): Pure product on white                               │   │
│   │   ├─ Image 2 (INFOGRAPHIC_1): Technical breakdown with callouts          │   │
│   │   ├─ Image 3 (INFOGRAPHIC_2): Benefits grid with icons                   │   │
│   │   ├─ Image 4 (LIFESTYLE): Real person using product                      │   │
│   │   └─ Image 5 (COMPARISON): Multiple uses / package contents              │   │
│   │                                                                          │   │
│   │   Each prompt EMBEDS:                                                    │   │
│   │   • Exact hex colors from framework: "Primary color #1E3A5F"             │   │
│   │   • Typography: "Use Montserrat Bold for headline"                       │   │
│   │   • Specific headlines from framework's image_copy                       │   │
│   │   • Lighting, mood, composition instructions                             │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                      │                                           │
│                                      ▼                                           │
│   STEP 2B: Generate 5 Final Images (Parallel)                                    │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                    GEMINI IMAGE GENERATOR                                │   │
│   │                    (gemini-3-pro-image-preview)                          │   │
│   │                                                                          │   │
│   │   For EACH of the 5 images, receives:                                    │   │
│   │                                                                          │   │
│   │   TEXT PROMPT (from Vision AI):                                          │   │
│   │   ├─ Detailed scene description                                          │   │
│   │   ├─ Color codes EMBEDDED in text                                        │   │
│   │   ├─ Typography EMBEDDED in text                                         │   │
│   │   ├─ Composition rules                                                   │   │
│   │   ├─ + Global Note (if provided)                                         │   │
│   │   └─ + Regeneration Note (if regenerating)                               │   │
│   │                                                                          │   │
│   │   REFERENCE IMAGES (passed directly to Gemini):                          │   │
│   │   ├─ 1. Primary product image (ALWAYS)                                   │   │
│   │   ├─ 2. Additional product images (if any)                               │   │
│   │   ├─ 3. Style reference image (framework preview or user-provided)       │   │
│   │   └─ 4. Logo image (for non-MAIN images only)                            │   │
│   │                                                                          │   │
│   │   OUTPUT: 5 Generated 1000x1000 images                                   │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## How Each Input Is Used

### 1. Product Images

| Input | Goes To | How It's Used |
|-------|---------|---------------|
| Primary Image | Vision AI (Step 1) | AI SEES and ANALYZES the product to understand colors, shape, category |
| Primary Image | Gemini Image Gen | Passed as REFERENCE IMAGE - Gemini tries to recreate the product |
| Additional Images | Gemini Image Gen | Passed as additional REFERENCE IMAGES for better product understanding |

### 2. Primary Color Preference

```
User provides: primary_color = "#2196F3"
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                     VISION AI (Framework Analysis)               │
│                                                                  │
│  Prompt includes:                                                │
│  "Primary Color Preference: #2196F3"                             │
│                                                                  │
│  AI's behavior:                                                  │
│  • Treats this as a SUGGESTION, not a mandate                    │
│  • Considers it alongside what it SEES in the product            │
│  • May incorporate it as primary, or use a complementary color   │
│  • Generates a COMPLETE palette (5 colors) that works together   │
│                                                                  │
│  Output framework may have:                                      │
│  colors: [                                                       │
│    { hex: "#2196F3", role: "primary" },    ← May honor user's    │
│    { hex: "#1565C0", role: "secondary" },  ← AI decided          │
│    { hex: "#FF5722", role: "accent" },     ← AI decided          │
│    { hex: "#212121", role: "text_dark" },  ← AI decided          │
│    { hex: "#FFFFFF", role: "text_light" }  ← AI decided          │
│  ]                                                               │
└─────────────────────────────────────────────────────────────────┘
```

**Without primary_color**: Vision AI decides ALL colors based purely on product image analysis.

**With primary_color**: Vision AI uses it as a starting point but still creates a harmonious palette.

### 3. Style Reference Image

```
User provides: style_reference_path = "uploads/style_ref.png"
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                DIRECT TO GEMINI IMAGE GENERATOR                  │
│                                                                  │
│  reference_image_paths = [                                       │
│    "uploads/product.png",      ← Product (always first)          │
│    "uploads/product2.png",     ← Additional product images       │
│    "uploads/style_ref.png",    ← Style reference (if provided)   │
│    "uploads/logo.png",         ← Logo (for non-main images)      │
│  ]                                                               │
│                                                                  │
│  Gemini's behavior:                                              │
│  • VISUALLY matches the style, colors, lighting, mood            │
│  • Works alongside the text prompt's color instructions          │
│  • Stronger influence than text for overall "feel"               │
└─────────────────────────────────────────────────────────────────┘
```

**Without style_reference**: Gemini relies purely on text prompt descriptions.

**With style_reference**: Gemini visually copies the style from the reference image. The framework's preview_path is automatically used as style_reference when user selects a framework.

### 4. Global Note / Instructions

```
User provides: global_note = "Use warm lighting, avoid text overlays"
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    TEXT PROMPT MODIFICATION                      │
│                                                                  │
│  For EACH of the 5 images:                                       │
│                                                                  │
│  base_prompt = [Generated by Vision AI - 500+ words]             │
│                                                                  │
│  if global_note:                                                 │
│      base_prompt += """                                          │
│      === USER INSTRUCTIONS (IMPORTANT) ===                       │
│      Use warm lighting, avoid text overlays                      │
│      """                                                         │
│                                                                  │
│  → Sent to Gemini as text prompt                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Note**: Global note is TEXT-based instruction, appended to each prompt. It does NOT affect the framework's colors or typography (those were already decided in Step 1).

### 5. Logo Image

```
User provides: logo_path = "uploads/logo.png"
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CONDITIONAL REFERENCE IMAGE                   │
│                                                                  │
│  if image_type != MAIN:                                          │
│      reference_paths.append(logo_path)                           │
│                                                                  │
│  MAIN image: NO logo (Amazon requires clean product-only)        │
│  Other images: Logo passed as reference for Gemini to include    │
└─────────────────────────────────────────────────────────────────┘
```

## Comparison: With vs Without Inputs

### Color Palette Flow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          WITHOUT PRIMARY COLOR                                │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│   Product Image ──▶ Vision AI ──▶ "I see a green product with gold accents"  │
│                          │                                                    │
│                          ▼                                                    │
│                  Framework colors:                                            │
│                  • Primary: #2E7D32 (Forest Green - from product)             │
│                  • Secondary: #C9A227 (Gold - from product)                   │
│                  • Accent: #1565C0 (Contrasting blue)                         │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                          WITH PRIMARY COLOR = #FF5722                         │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│   Product Image ──▶ Vision AI ──▶ "User prefers #FF5722, product is green"   │
│   primary_color         │                                                     │
│                         ▼                                                     │
│                  Framework colors:                                            │
│                  • Primary: #FF5722 (User's preference - honored)             │
│                  • Secondary: #2E7D32 (Product green - complementary)         │
│                  • Accent: #FFC107 (Warm accent to match primary)             │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Style Reference Flow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          WITHOUT STYLE REFERENCE                              │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│   Text Prompt ─────────────────────────────────────▶ Gemini ──▶ Image        │
│   "Professional e-commerce photo,                                             │
│    soft lighting, primary color #2E7D32..."                                   │
│                                                                               │
│   Reference Images: [product.png]                                             │
│                                                                               │
│   Result: Gemini interprets text instructions (more variable)                 │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                          WITH STYLE REFERENCE                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│   Text Prompt ─────────────────────────────────────▶ Gemini ──▶ Image        │
│   "Professional e-commerce photo,                                             │
│    soft lighting, primary color #2E7D32..."                                   │
│                                                                               │
│   Reference Images: [product.png, style_ref.png]                              │
│                         ▲                                                     │
│                         │                                                     │
│   Style reference provides VISUAL example of:                                 │
│   • Lighting style                                                            │
│   • Color treatment                                                           │
│   • Overall mood/aesthetic                                                    │
│   • Composition style                                                         │
│                                                                               │
│   Result: More consistent styling across all 5 images                         │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Summary: What Goes Where

| User Input | Vision AI (Framework Gen) | Vision AI (Prompt Gen) | Gemini (Image Gen) |
|------------|---------------------------|------------------------|---------------------|
| Product Image (primary) | ✅ SEES it | ❌ | ✅ Reference |
| Additional Product Images | ❌ | ❌ | ✅ Reference |
| Product Title | ✅ Text context | ✅ Text context | ❌ (embedded in prompt) |
| Features | ✅ Text context | ✅ Text context | ❌ (embedded in prompt) |
| Target Audience | ✅ Text context | ✅ Text context | ❌ (embedded in prompt) |
| Primary Color | ✅ Suggestion | ❌ (already in framework) | ❌ (embedded in prompt) |
| Style Reference Image | ❌ | ❌ | ✅ Reference |
| Logo Image | ❌ | ❌ | ✅ Reference (non-main) |
| Global Note | ❌ | ❌ | ✅ Appended to prompt |
| Selected Framework | ❌ | ✅ Full framework | ❌ (embedded in prompt) |

## Key Insights

1. **Colors are TEXT, not pixels**: Color palette is converted to text instructions ("Use primary color #2E7D32") and embedded in prompts. Gemini interprets these textually.

2. **Style reference is VISUAL**: Unlike colors, the style reference image is passed directly to Gemini, providing a visual example to match.

3. **Two-stage AI process**: Vision AI is the "brain" that plans, Gemini Image Gen is the "artist" that executes. They communicate via detailed text prompts + reference images.

4. **Framework preview = style consistency**: When user selects a framework, its preview image becomes the style reference, ensuring all 5 final images have consistent styling.

5. **Primary color is a suggestion**: Vision AI considers it but also looks at the product to create a harmonious palette. It's not a hard constraint.
