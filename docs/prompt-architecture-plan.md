# AI Designer Prompt Architecture Overhaul

**Date:** February 3, 2026
**Status:** Ready for Implementation
**Author:** Claude (with Architect review)

---

## Executive Summary

Transform the AI Designer from a **template-following system** (799+ lines of rigid scaffolding) to a **principle-understanding creative partner** (~300 lines of evocative guidance). The same vocabulary-trigger philosophy will apply to both **Listing Images** and **A+ Content** for consistent quality across all generated images.

---

## 1. Current State Analysis

### Problems Identified

| Issue | Current State | Impact |
|-------|---------------|--------|
| **Over-scaffolded** | "7 Essential Building Blocks", word count requirements | Kills creativity, confuses model |
| **Weak vocabulary** | "professional Amazon listing quality" | Triggers generic outputs |
| **Template-driven** | 500-word prompts with pixel-level specs | Inconsistent, verbose |
| **Rigid style handling** | "Extract exact hex codes" | Lifeless copies |
| **Product color contamination** | Brand colors sometimes applied to product | ~33% failure rate |
| **Distrust of AI** | Spells out everything | Wastes context, worse results |

### Files to Refactor

1. `app/prompts/ai_designer.py` - Listing image prompts (799 lines)
2. `app/prompts/templates/aplus_modules.py` - A+ content prompts (669 lines)

---

## 2. Target Architecture

### New File Structure

```
app/prompts/
├── vocabulary.py              # NEW: Quality triggers, camera names, publications
├── product_protection.py      # NEW: Sacred product rules (shared)
├── ai_designer.py             # REFACTORED: Listing images (~300 lines)
├── templates/
│   └── aplus_modules.py       # REFACTORED: A+ content (~400 lines)
└── [other existing files unchanged]
```

### Core Philosophy

1. **Vocabulary Triggers** - Use terms that activate quality distributions in Gemini
2. **Product Protection** - Product colors are sacred, never modified
3. **Principle-Based** - Guide with principles, not pixel specs
4. **Trust the Model** - Gemini knows what "Architectural Digest" means

---

## 3. Implementation Phases

### Phase 1: Create Shared Foundation (vocabulary.py, product_protection.py)

**vocabulary.py** - Quality anchors used by both listing and A+ prompts:

```python
# Camera vocabulary - triggers technical excellence
CAMERA_ANCHORS = {
    "medium_format": "Hasselblad H6D-100c",
    "ultimate": "Phase One IQ4 150MP",
    "film": "medium format film",
}

# Publication vocabulary - triggers editorial standards
PUBLICATION_ANCHORS = {
    "editorial": "Architectural Digest",
    "lifestyle": "Kinfolk magazine",
    "luxury": "Sotheby's catalog",
    "minimal": "Cereal Magazine",
}

# Quality descriptors
QUALITY_TERMS = [
    "museum-quality",
    "gallery-worthy",
    "campaign imagery",
    "editorial",
    "tack-sharp",
]

def get_quality_anchor(style: str = "editorial") -> str:
    """Generate a quality anchor string."""
    return f"Hasselblad H6D-100c. {PUBLICATION_ANCHORS.get(style, 'Architectural Digest')}. Museum-quality."
```

**product_protection.py** - Sacred rules shared across all prompts:

```python
PRODUCT_PROTECTION_DIRECTIVE = """
═══════════════════════════════════════════════════════════════════════════════
                              THE PRODUCT IS SACRED
═══════════════════════════════════════════════════════════════════════════════

Image 1 is THE product. Not inspiration. Not reference. THE product.

ABSOLUTE RULES:
1. FORM - Reproduce exactly. Never "improve" or "interpret" the shape.
2. COLOR - The product's colors are immutable. A white product stays white.
   A blue product stays blue. Brand colors NEVER touch the product itself.
3. DETAIL - Every texture, curve, and feature matters.

Brand colors create CONTEXT (backgrounds, gradients, UI elements).
They NEVER contaminate the product itself.

Think of it like a gallery: the walls can be any color,
but the artwork remains exactly as the artist created it.
"""
```

### Phase 2: Refactor Listing Image Prompts (ai_designer.py)

**Key Changes:**

| Section | Before | After |
|---------|--------|-------|
| Building blocks | "7 Essential Building Blocks" (rigid) | Principles only |
| Word count | "MINIMUM 300 words" | "100-200 words of evocative direction" |
| Image templates | 200+ lines per type | 30-50 lines of principles |
| Quality anchor | "professional Amazon listing" | "Hasselblad H6D-100c. Architectural Digest." |
| Style reference | "Extract exact hex codes" | "Capture the essence, not pixels" |

**New GENERATE_IMAGE_PROMPTS_PROMPT structure:**

```
1. Principal Designer persona (brief)
2. Product Protection directive (from shared module)
3. Brand context (colors for atmosphere only)
4. Audience direction (aspirations, not demographics)
5. Quality standard (vocabulary triggers)
6. Image type principles (brief, not templates)
7. Output format (simplified JSON)
```

### Phase 3: Refactor A+ Content Prompts (aplus_modules.py)

**Key Changes:**

| Section | Before | After |
|---------|--------|-------|
| VISUAL_SCRIPT_PROMPT | 350+ lines, very prescriptive | 200 lines, principle-based |
| APLUS_MODULE_WITH_SCRIPT | Template-heavy | Creative direction |
| Quality language | "premium Amazon A+" | "Sotheby's catalog. Campaign imagery." |
| Typography handling | Verbose rules about font placement | Trust model + brief guidance |

**Shared vocabulary triggers with listing images** - ensures visual consistency.

### Phase 4: Update Enhancement/Regeneration Prompt

**ENHANCE_PROMPT_WITH_FEEDBACK_PROMPT** - Same philosophy:
- Remove verbose interpretation instructions
- Add vocabulary triggers
- Keep product protection directive
- Trust model to understand feedback

---

## 4. Detailed File Specifications

### 4.1 vocabulary.py (NEW)

```python
"""
Vocabulary triggers that activate quality distributions in Gemini.
Shared across listing images and A+ content for consistent quality.
"""

CAMERA_ANCHORS = {
    "medium_format": "Hasselblad H6D-100c",
    "ultimate": "Phase One IQ4 150MP",
    "film": "medium format film",
    "large": "shot on large format",
}

PUBLICATION_ANCHORS = {
    "editorial": "Architectural Digest",
    "lifestyle": "Kinfolk magazine",
    "luxury": "Sotheby's catalog",
    "minimal": "Cereal Magazine",
    "fashion": "Vogue Living",
}

QUALITY_VOCABULARY = [
    "museum-quality",
    "gallery-worthy",
    "campaign imagery",
    "editorial",
    "tack-sharp",
]

LIGHTING_VOCABULARY = {
    "soft": "diffused key light",
    "dramatic": "rim lighting with separation",
    "natural": "golden hour warmth",
    "studio": "studio strobes with modifiers",
    "window": "natural window light",
}

FEELING_VOCABULARY = {
    "aspirational": "aspirational but attainable",
    "intimate": "intimate and personal",
    "elevated": "elevated everyday",
    "curated": "deliberately curated",
    "breathing": "breathing room and calm",
}

def get_quality_anchor(style: str = "editorial") -> str:
    """Generate a quality anchor string based on desired style."""
    camera = CAMERA_ANCHORS["medium_format"]
    publication = PUBLICATION_ANCHORS.get(style, "Architectural Digest")
    return f"{camera}. {publication}. Museum-quality."

def get_listing_quality_standard() -> str:
    """Quality standard for listing images."""
    return """
QUALITY STANDARD
Don't aim for "good Amazon listing." Aim for "belongs in Architectural Digest."

Your vocabulary shapes the output. Use terms that trigger excellence:
- Camera: "Hasselblad H6D-100c", "Phase One", "medium format"
- Publication: "Architectural Digest", "Kinfolk", "Cereal Magazine"
- Quality: "museum-quality", "gallery-worthy", "tack-sharp"
- Light: "diffused key light", "natural window light", "soft rim"
"""

def get_aplus_quality_standard() -> str:
    """Quality standard for A+ content."""
    return """
QUALITY STANDARD
This isn't a product photo. This is a brand moment. Sotheby's catalog quality.

Vocabulary that triggers excellence:
- "campaign imagery" - big budget, high stakes
- "editorial" - story-driven, not stock
- "cinematic" - frame from a luxury brand film
- "tack-sharp" - technical precision
"""
```

### 4.2 product_protection.py (NEW)

```python
"""
Product fidelity is the immutable constraint.
Shared across all prompt types.
"""

PRODUCT_PROTECTION_DIRECTIVE = """
═══════════════════════════════════════════════════════════════════════════════
                              THE PRODUCT IS SACRED
═══════════════════════════════════════════════════════════════════════════════

The product photo shows THE EXACT PRODUCT. Not inspiration. Not reference. THE product.

ABSOLUTE RULES:
1. FORM - Reproduce exactly. Never "improve" or "interpret" the shape.
2. COLOR - The product's colors are immutable. A white product stays white.
   A blue product stays blue. Brand colors NEVER touch the product itself.
3. DETAIL - Every texture, curve, and feature matters.
4. REFERENCE - Always anchor to "the exact product shown in Image 1"

Brand colors create CONTEXT around the product (backgrounds, gradients, UI).
They NEVER contaminate the product itself.

Think of it like a gallery: the walls can be any color,
but the artwork remains exactly as the artist created it.
"""

PRODUCT_REFERENCE_INSTRUCTION = """
In EVERY prompt:
- Reference the product as "the exact product shown in Image 1" or "the product from the reference photo"
- NEVER describe by name alone - the AI must LOOK at the reference, not imagine
- End with "Reproduce this specific product faithfully from the reference photo"
"""

def get_product_protection_block() -> str:
    """Get the full product protection block for prompts."""
    return PRODUCT_PROTECTION_DIRECTIVE + "\n" + PRODUCT_REFERENCE_INSTRUCTION
```

### 4.3 ai_designer.py (REFACTORED)

**Target: ~300 lines** (down from 799)

Key sections:
1. Imports from vocabulary.py and product_protection.py
2. PRINCIPAL_DESIGNER_VISION_PROMPT - Simplified framework analysis
3. GENERATE_IMAGE_PROMPTS_PROMPT - Principle-based, vocabulary-triggered
4. ENHANCE_PROMPT_WITH_FEEDBACK_PROMPT - Simplified enhancement
5. Style reference handling - "Essence capture" by default

### 4.4 aplus_modules.py (REFACTORED)

**Target: ~400 lines** (down from 669)

Key sections:
1. Imports from vocabulary.py and product_protection.py
2. VISUAL_SCRIPT_PROMPT - Same vocabulary triggers as listing images
3. Module prompts - Principle-based creative direction
4. Canvas continuity - Keep technical accuracy, simplify language

---

## 5. Before/After Examples

### Listing Image Prompt

**BEFORE (verbose, rigid):**
```
Professional e-commerce product photography on pure white background (#FFFFFF).
Use the EXACT product shown in Image 1 (the product photo) - do not generate a
similar or generic version. The product (from Image 1) should be reproduced
faithfully in terms of shape, color, design details, and proportions. Studio
lighting setup with soft diffused key light from top-left at 45 degrees,
subtle fill light from the right side opening shadows by 1 stop, and small
accent light highlighting the sculptural details. The product positioned at
a 3/4 hero angle showing depth and dimension, filling 85% of the frame.
No text, no graphics, no props, no logos. Pure product on pure white.
Reproduce this specific product faithfully from the reference photo.
High-resolution catalog photography, Apple product photography quality,
professional Amazon listing standards.
```

**AFTER (evocative, vocabulary-triggered):**
```
Hasselblad H6D-100c. Architectural Digest product photography.

The exact product from Image 1, commanding attention on pure white.
Museum-quality presentation — every texture visible, every curve intentional.
Soft studio light wraps the form, a whisper of shadow grounds it to reality.

The product fills the frame with quiet confidence.
Nothing else. No text. No distraction. Just truth, beautifully lit.

Tack-sharp. Gallery-worthy. The hero shot.
```

### A+ Module Prompt

**BEFORE:**
```
You are an award-winning commercial photographer and art director shooting a premium
Amazon A+ Content banner for {product_title}... [150 more words of setup]
```

**AFTER:**
```
Sotheby's catalog. Campaign imagery. Cinematic.

A wide frame from a luxury brand film — {product_title} as the undeniable star.
The product from PRODUCT_PHOTO, honored exactly. The mood from STYLE_REFERENCE.

Brand colors live in the atmosphere — lighting, surfaces, gradients.
Never flat graphic overlays. Never touching the product itself.

This banner stops the scroll. Editorial, not catalog.
```

---

## 6. Migration Strategy

1. **Create new files first** - vocabulary.py, product_protection.py
2. **Update ai_designer.py** - Import shared modules, refactor prompts
3. **Update aplus_modules.py** - Import shared modules, add vocabulary triggers
4. **Test on staging** - Generate sample listings, compare quality
5. **User approval** - Manual comparison of old vs new outputs
6. **Deploy to production** - Only after staging approval

---

## 7. Rollback Plan

If quality regresses:
1. Revert to git commit before changes
2. Redeploy previous version
3. Analyze what went wrong
4. Iterate on prompts

Backup files will be created:
- `ai_designer.py.backup`
- `aplus_modules.py.backup`

---

## 8. Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Prompt length (listing) | 400-500 words | 100-200 words |
| Prompt length (A+) | 300-500 words | 150-250 words |
| Color contamination | ~33% | <5% |
| Vocabulary triggers/prompt | 0-1 | 3-5 |
| Code lines (ai_designer.py) | 799 | ~300 |
| Code lines (aplus_modules.py) | 669 | ~400 |

---

## 9. Definition of Done

- [ ] vocabulary.py created with quality anchors
- [ ] product_protection.py created with shared directives
- [ ] ai_designer.py refactored to ~300 lines
- [ ] aplus_modules.py refactored to ~400 lines
- [ ] All prompts use vocabulary triggers
- [ ] Product protection directive in all generation prompts
- [ ] Deployed to staging
- [ ] User has compared old vs new outputs
- [ ] User has approved quality
- [ ] Merged to production

---

## 10. Implementation Order

```
1. Create app/prompts/vocabulary.py
2. Create app/prompts/product_protection.py
3. Backup ai_designer.py
4. Refactor ai_designer.py
5. Backup aplus_modules.py
6. Refactor aplus_modules.py
7. Test locally (syntax, imports)
8. Commit to develop branch
9. Deploy to staging
10. Generate test images on staging
11. User comparison and approval
12. Merge to main (production)
```
