# AI Designer Prompt Engineering Overhaul

## Plan for Transforming listing_genie's Image Generation Pipeline

**Date:** February 3, 2026
**Status:** Ready for Implementation
**Target File:** `listing_genie/app/prompts/ai_designer.py`

---

## Executive Summary

Transform the AI Designer from a **template-following system** to a **principle-understanding creative partner**. Replace 799 lines of rigid scaffolding with concise, evocative guidance that leverages the AI's trained intelligence.

**Core Philosophy:** Teach the AI to think like a master designer, not follow a checklist.

---

## Part 1: How Artists Think

### The Artist's Mindset

Artists don't think in templates. They think in:

1. **Light** - Where it falls, how it wraps, what it reveals
2. **Tension** - Visual weight, balance, deliberate imbalance
3. **Breath** - Negative space, room for the eye to rest
4. **Story** - What moment are we capturing? What comes before/after?
5. **Feeling** - What emotion should this evoke?
6. **Truth** - Is this authentic or forced?

### The Artist's Vocabulary

Words carry weight. The AI has seen millions of images tagged with specific terms. These terms trigger quality distributions:

**Camera Triggers** (implies technical excellence):
- "Hasselblad H6D-100c" → Medium format, extreme detail
- "Phase One IQ4 150MP" → Ultimate resolution, commercial quality
- "shot on large format" → Deliberate, considered, premium
- "medium format film" → Organic, rich tones

**Publication Triggers** (implies editorial standards):
- "Architectural Digest" → Clean, premium, aspirational spaces
- "Kinfolk magazine" → Warm, authentic, lived-in beauty
- "Vogue Living" → Fashion-forward interiors
- "Sotheby's catalog" → Museum-worthy presentation
- "Cereal Magazine" → Minimal, quiet, thoughtful

**Quality Language** (implies craftsmanship):
- "museum-quality" → Worthy of preservation
- "gallery-worthy" → Art, not commerce
- "campaign imagery" → Big budget, high stakes
- "editorial" → Story-driven, not just product
- "tack-sharp" → Technical precision

**Lighting Language** (implies expertise):
- "diffused key light" → Soft, flattering
- "rim lighting" → Separation, drama
- "golden hour warmth" → Natural, inviting
- "studio strobes with modifiers" → Controlled perfection
- "natural window light" → Authentic, relatable

**Feeling Language** (implies intention):
- "aspirational but attainable" → Want it, believe you can have it
- "intimate" → Close, personal, trusted
- "elevated everyday" → Premium without pretense
- "curated" → Deliberately chosen, not random
- "breathing room" → Space, calm, considered

---

## Part 2: The Problem with Current System

### What's Wrong Now

**File:** `ai_designer.py` (799 lines)

1. **Over-scaffolded** - Rigid templates kill creativity
2. **Prescriptive** - "MUST have 7 building blocks" / "MINIMUM 300 words"
3. **Template-driven** - Exact structures for each image type
4. **Vocabulary-poor** - Uses weak terms like "professional Amazon listing quality"
5. **Rigid style handling** - "Extract exact hex codes" instead of capturing essence
6. **Distrust of AI** - Spells out everything instead of leveraging intelligence

### What to Remove

- Rigid "7 Essential Building Blocks" requirement
- Exact word count requirements (300-500 words per prompt)
- Pixel-level composition instructions
- Verbose template structures for each image type
- Repetitive "CRITICAL" and "NON-NEGOTIABLE" warnings
- Over-detailed font/color specifications

### What to Keep

- Product image reference system (Image 1 = THE product)
- Brand color palette input
- Basic image type differentiation (main, lifestyle, infographic, etc.)
- Amazon compliance rules (white background for main image)
- User input integration (title, features, audience, global notes)
- Style reference capability

---

## Part 3: The New Philosophy

### Principle-Based, Not Template-Based

**OLD:** "For lifestyle image, include hands at 45 degrees, product at center-left, wooden table, natural light from window at 5200K..."

**NEW:** "Lifestyle photography makes viewers imagine owning the product. It feels real, not staged. The product is being *used*, not displayed. Capture a genuine moment."

### Trust the AI's Intelligence

The AI has been trained on millions of images. It knows:
- What lifestyle photography looks like
- How to compose a product shot
- What "editorial quality" means
- How to create visual hierarchy

We don't need to teach these basics. We need to:
1. Set the quality bar (vocabulary triggers)
2. Protect the product's truth (identity, colors)
3. Provide brand context (colors, audience, voice)
4. Give creative direction (not rigid templates)

### Quality Through Vocabulary

Instead of verbose instructions, use trigger words that activate quality distributions:

```
DON'T SAY: "High-resolution catalog photography with professional
           lighting and clean composition suitable for Amazon listings"

SAY:       "Hasselblad H6D-100c. Architectural Digest. Museum-quality."
```

The second version triggers better outputs because those specific terms are associated with high-quality training examples.

---

## Part 4: User Inputs & How to Handle Them

The system receives these inputs from users:

### 1. Product Image(s)
**What it is:** The actual product photo(s) to reference
**How to handle:**
- Establish as THE source of truth
- "Image 1 is the product. Reproduce it faithfully. Its colors are sacred."
- Never let AI "interpret" or "improve" the product itself

### 2. Product Title & Description
**What it is:** Name and basic description
**How to handle:**
- Use for context, not rigid text placement
- Let AI understand what it's photographing
- Don't force title into every image

### 3. Product Features/Specifications
**What it is:** Key selling points, dimensions, materials
**How to handle:**
- Infographics should highlight these naturally
- Not a checklist to mechanically include
- AI decides which features matter visually

### 4. Target Audience
**What it is:** Who will buy this product
**How to handle:**
- This shapes the entire visual language
- "Speak to their aspirations, not their demographics"
- Influences lifestyle scenes, styling, mood

### 5. Brand Colors
**What it is:** Hex codes for brand palette
**How to handle:**
- Available for backgrounds, UI, accents
- **NEVER applied to the product itself**
- Use as atmosphere, not paint
- "The brand colors create context, not contamination"

### 6. Global Rules (User Preferences)
**What it is:** User's specific instructions for all images
**How to handle:**
- Interpret intelligently, don't copy-paste
- "If user says 'use plants' - lifestyle gets real plants, infographic gets plant icons, main image stays pure"
- Adapt the spirit to each context

### 7. Style Reference (Optional)
**What it is:** An inspiration image showing desired aesthetic
**How to handle:**
- **Two modes:**
  - **Exact Match:** "Recreate this style precisely" (for brand consistency)
  - **Essence Capture:** "Channel the feeling of this" (for inspiration)
- Default to essence unless user specifies exact
- "Capture the warmth, the breathing room, the quiet confidence - not the pixel coordinates"

---

## Part 5: The New Prompt Structure

### GENERATE_IMAGE_PROMPTS_PROMPT (Replacement)

Replace the current 500-line behemoth with this principle-based structure:

```
You are a principal designer with two decades at the world's best agencies.
You don't follow templates. You've internalized what makes imagery exceptional.

═══════════════════════════════════════════════════════════════════════════════
                              THE PRODUCT
═══════════════════════════════════════════════════════════════════════════════

Image 1 is THE product. Not inspiration. Not a reference. THE product.

Reproduce it with absolute fidelity:
- Its form is truth. Don't "improve" or "interpret" the shape.
- Its colors are sacred. A white product stays white. A blue product stays blue.
- Its details matter. Every texture, every curve, every feature.

When you write prompts, always anchor to: "the exact product shown in Image 1"
Never describe it by name alone - the AI must LOOK at the reference, not imagine.

═══════════════════════════════════════════════════════════════════════════════
                              THE BRAND
═══════════════════════════════════════════════════════════════════════════════

Product: {product_name}
Brand: {brand_name}
Voice: {brand_voice}

Color Palette:
{color_palette}

These colors are for atmosphere - backgrounds, gradients, UI elements, accents.
They create context around the product. They NEVER touch the product itself.

Think of it like a gallery: the walls can be any color,
but the artwork remains exactly as the artist created it.

═══════════════════════════════════════════════════════════════════════════════
                              THE AUDIENCE
═══════════════════════════════════════════════════════════════════════════════

{target_audience}

Speak to their aspirations, not their demographics.
What do they dream about? What would make them stop scrolling?
The imagery should whisper: "This is for someone like you."

═══════════════════════════════════════════════════════════════════════════════
                              THE STORY
═══════════════════════════════════════════════════════════════════════════════

Framework: {framework_name}
Philosophy: {design_philosophy}

Story Arc:
- Hook: {story_hook}
- Reveal: {story_reveal}
- Proof: {story_proof}
- Dream: {story_dream}
- Close: {story_close}

Headlines/Copy available:
{image_copy_json}

Use these as inspiration. You decide where and how text appears.
Sometimes the image speaks louder without words.

═══════════════════════════════════════════════════════════════════════════════
                              QUALITY STANDARD
═══════════════════════════════════════════════════════════════════════════════

Don't aim for "good Amazon listing."
Aim for "belongs in Architectural Digest."

The difference between acceptable and exceptional:
- Hasselblad, not iPhone
- Editorial, not stock
- Curated, not cluttered
- Intentional, not incidental

Your vocabulary shapes the output. Use terms that trigger excellence:
- Camera: "Hasselblad H6D-100c", "Phase One", "medium format"
- Publication: "Architectural Digest", "Kinfolk", "Cereal Magazine"
- Quality: "museum-quality", "gallery-worthy", "tack-sharp"
- Light: "diffused key light", "natural window light", "soft rim"

═══════════════════════════════════════════════════════════════════════════════
                              YOUR TASK
═══════════════════════════════════════════════════════════════════════════════

Create 5 image prompts that form a cohesive visual story.

**Image 1: Main Hero**
- Pure product on white (#FFFFFF). Amazon requirement.
- No text, no graphics, no props. Just the product, beautifully lit.
- This wins the click in search results.

**Image 2-3: Information**
- Help the customer understand the product.
- Features, benefits, dimensions, what's included.
- Be creative with how you visualize information.

**Image 4: Lifestyle**
- Show the product in context. Being used. Being loved.
- Real environment. Real moment. Real feeling.
- This is where aspiration lives.

**Image 5: Conviction**
- Whatever closes the sale.
- Size comparison, package contents, trust signals, versatility.
- Remove the final objection.

For each prompt, write with evocative precision.
Include quality anchors. Protect the product's truth.
Let your creative intelligence shape the execution.

{global_note_section}

{style_reference_section}

═══════════════════════════════════════════════════════════════════════════════
                              OUTPUT FORMAT
═══════════════════════════════════════════════════════════════════════════════

Return JSON with this structure:

{{
  "creative_vision": "Your overall creative interpretation for this set",
  "generation_prompts": [
    {{
      "image_number": 1,
      "image_type": "main",
      "creative_intent": "What this image accomplishes in the story",
      "prompt": "Your evocative, quality-anchored prompt"
    }},
    // ... images 2-5
  ]
}}

Each prompt should feel like creative direction from a master photographer,
not a technical specification sheet.
```

---

## Part 6: Style Reference Handling

### The Problem with Current Approach

Current system says: "Extract exact hex codes, match lighting exactly, copy composition..."

This produces rigid, lifeless copies.

### The New Approach: Essence Capture

```
═══════════════════════════════════════════════════════════════════════════════
                         STYLE REFERENCE
═══════════════════════════════════════════════════════════════════════════════

The user has provided a style reference image.

{style_mode_instruction}

**If "capture essence" (default):**
Don't copy pixels. Capture the feeling.
- What makes this image feel the way it does?
- What's the quality of light? Soft? Dramatic? Natural?
- What's the emotional temperature? Warm? Cool? Intimate? Bold?
- What's the rhythm? Quiet? Energetic? Contemplative?
- How does space breathe?

Channel these qualities into your prompts.
The result should feel like a sibling, not a clone.

**If "match exactly" (user-specified):**
Recreate the style precisely for brand consistency.
- Match the lighting setup
- Match the color treatment
- Match the compositional approach
- Match the mood exactly

Even in exact matching, the PRODUCT remains sacred -
only the surrounding style is matched.
```

---

## Part 7: Implementation Steps

### Step 1: Backup Current System
```bash
cp app/prompts/ai_designer.py app/prompts/ai_designer.py.backup
```

### Step 2: Create New Constants Section
After line 10, add vocabulary constants:

```python
# ============================================================================
# QUALITY VOCABULARY (Words that trigger excellence)
# ============================================================================

CAMERA_ANCHORS = [
    "Hasselblad H6D-100c",
    "Phase One IQ4 150MP",
    "medium format",
    "large format"
]

PUBLICATION_ANCHORS = {
    "editorial": "Architectural Digest",
    "lifestyle": "Kinfolk magazine",
    "luxury": "Sotheby's catalog",
    "minimal": "Cereal Magazine"
}

QUALITY_TERMS = [
    "museum-quality",
    "gallery-worthy",
    "editorial",
    "tack-sharp",
    "campaign imagery"
]

PRODUCT_PROTECTION_DIRECTIVE = """
The product's colors are sacred. A white product stays white.
A blue product stays blue. Brand colors create atmosphere
around the product - they never touch the product itself.
"""
```

### Step 3: Replace GENERATE_IMAGE_PROMPTS_PROMPT
Replace lines 299-799 with the new principle-based prompt from Part 5.

**Key changes:**
- Remove "7 Essential Building Blocks" (rigid structure)
- Remove word count requirements
- Remove verbose template examples
- Add quality vocabulary guidance
- Add principle-based creative direction
- Simplify image type descriptions

### Step 4: Update Style Reference Handling
Replace STYLE_REFERENCE_INSTRUCTIONS with essence-based approach:

**Key changes:**
- Default to "capture essence" mode
- Add "match exactly" as optional mode
- Remove pixel-level matching language
- Add feeling/emotion vocabulary

### Step 5: Simplify Image Type Templates
Current templates in lines 433-654 are over-detailed. Replace with brief principles:

```python
IMAGE_TYPE_PRINCIPLES = {
    "main": """
        Pure product. White background. No distractions.
        This is the click-winner. Hasselblad quality.
        Let the product's form speak for itself.
    """,

    "infographic": """
        Information, beautifully organized.
        Help them understand what they're buying.
        Clean, clear, but never boring.
    """,

    "lifestyle": """
        Context. Aspiration. Reality.
        Someone is using this. Loving this. Living with this.
        Real environment, real moment, editorial quality.
    """,

    "comparison": """
        Remove the final objection.
        Size context, package contents, versatility, trust.
        Whatever closes the sale.
    """
}
```

### Step 6: Update Global Note Handling
Current GLOBAL_NOTE_INSTRUCTIONS is verbose. Simplify to:

```python
GLOBAL_NOTE_INSTRUCTIONS = """
The user has additional guidance:
"{global_note}"

Interpret this intelligently across all 5 images.
Adapt the spirit to each context - don't copy-paste.
"""
```

### Step 7: Test & Iterate
1. Generate prompts for 3-5 different products
2. Compare output quality to current system
3. Check for:
   - Product color fidelity
   - Quality vocabulary usage
   - Creative variety
   - Brand color containment
4. Adjust vocabulary/principles as needed

---

## Part 8: Before/After Example

### Current System Output (verbose, rigid):
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

### New System Output (evocative, principle-based):
```
Hasselblad H6D-100c. Architectural Digest product photography.

The exact product from Image 1, commanding attention on pure white.
Museum-quality presentation - every texture visible, every curve
intentional. Soft studio light wraps the form, a whisper of shadow
grounds it to reality.

The product fills the frame with quiet confidence.
Nothing else. No text. No distraction. Just truth, beautifully lit.

Tack-sharp. Gallery-worthy. The hero shot.
```

**Same intent. More evocative. Better vocabulary triggers. Trusts the AI.**

---

## Part 9: Success Metrics

After implementation, measure:

| Metric | Current | Target |
|--------|---------|--------|
| Prompt length | 400-500 words each | 100-200 words each |
| Color contamination rate | 33% | <5% |
| Output variety | Low (template-driven) | High (principle-driven) |
| Quality vocabulary usage | Rare | Every prompt |
| Time to generate prompts | Baseline | Similar or faster |

---

## Part 10: Risks & Mitigations

### Risk 1: Too Vague, Inconsistent Results
**Mitigation:** Quality vocabulary anchors provide consistency without rigidity.

### Risk 2: AI Ignores Product Protection
**Mitigation:** Keep product protection directive explicit and prominent.

### Risk 3: Amazon Compliance Broken
**Mitigation:** Main image requirements remain explicit (white background, no text).

### Risk 4: User Inputs Get Lost
**Mitigation:** Dedicated sections for each input type, clearly formatted.

---

## Summary

**The Shift:**
- FROM: 799 lines of templates, scaffolding, rigid requirements
- TO: ~200 lines of principles, vocabulary triggers, creative direction

**The Philosophy:**
- Trust the AI's intelligence
- Use vocabulary that triggers quality
- Protect product truth
- Guide with principles, not templates
- Allow creative interpretation

**The Outcome:**
- Shorter prompts, better results
- More variety, consistent quality
- Less maintenance, more flexibility

---

## Ready for Implementation

This plan can be handed to an implementing AI with the instruction:

> "Refactor `listing_genie/app/prompts/ai_designer.py` according to this plan.
> Replace the verbose template-based system with a principle-based approach.
> Keep the essential structure (product reference, brand colors, user inputs)
> but remove the scaffolding. Use evocative vocabulary that triggers quality."

---

*Plan created: February 3, 2026*
*Based on prompt engineering research with 47+ controlled image generations*
