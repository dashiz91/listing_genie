# Creative Blueprint for High-Conversion Amazon Listings

**Document Version:** 1.0
**Date:** December 20, 2024
**Purpose:** Core reference for AI prompt engineering and image generation

---

## Philosophy

> To maximize conversion through creative alone, you must move from **"showing a product"** to **"telling a visual story."**

This approach focuses on three pillars:
1. **Attention** - Stop the scroll
2. **Emotion** - Build desire
3. **Education** - Remove doubt

---

## 1. The Main Image: "The Visual Hook"

**Creative Goal:** Dominate search results by being the most visually "dense" and interesting object on the screen.

### Key Techniques

| Technique | Description | Example |
|-----------|-------------|---------|
| **Dynamic Composition** | Use "stacking" or diagonal layouts | Bottle + box behind + glass of liquid in front |
| **Depth Creation** | Fill the white frame more effectively than a flat shot | Layered product arrangement |
| **Ingredient Pop** | Visually communicate what's inside | Lemon-scented cleaner → vibrant lemon slice in frame |
| **Color Bypass** | Use literal imagery to bypass need for reading | Show ingredients, not just describe them |
| **Tactile Quality** | Make packaging look premium | High-quality textures, professional label design |
| **Premium Signal** | Physical product quality signaled to brain | Professional lighting, attention to detail |

### Prompt Engineering Notes

```
Main Image Prompt Structure:
- Pure white background (#FFFFFF)
- Product fills 85%+ of frame
- Dynamic composition with depth (stacking, layering)
- Include "ingredient pop" elements relevant to product
- Premium textures and professional quality
- No text, logos, or watermarks
- Professional studio lighting with subtle shadows
```

---

## 2. Secondary Imagery: "The Mobile Storyboard"

**Creative Goal:** Each image in the secondary set is a "slide" in your sales pitch. Mobile users scroll through these like a story.

### The "Instagramify" Effect

| Avoid | Do Instead |
|-------|------------|
| Clinical, sterile looks | High-end social media content feel |
| Stock photo aesthetics | Authentic, warm, relatable imagery |
| Empty backgrounds | Real people in real settings |
| Perfect, fake scenarios | Someone actually using product (sunlit kitchen, etc.) |

### Micro-Copywriting Rules

| Rule | Description |
|------|-------------|
| **Text as Design** | Use text overlays as a design element, not just a caption |
| **Bold & High-Contrast** | Fonts must be legible at thumbnail size |
| **Benefits Over Features** | "Sleep Better" not "10mg Melatonin" |
| **One Message Per Image** | Each infographic has ONE singular objective |

### The Comparison Visual

| Your Product | Generic Competitor |
|--------------|-------------------|
| Vibrant colors | Muted, grey-scale tones |
| Checkmarks (✓) | X-marks (✗) |
| Highlighted, prominent | Faded, less prominent |
| Positive associations | Negative associations |

**Color Psychology:** Use strong contrast to make your product "pop" as the obvious winner.

---

## 3. A+ Content: "Interactive Brand Immersion"

**Creative Goal:** Move the customer from "buyer" to "brand fan."

### Key Techniques (Phase 2)

| Technique | Description |
|-----------|-------------|
| **Full-Width Visuals** | Premium A+ "breakout" images spanning entire screen width |
| **Pattern Breaking** | Break monotonous scrolling pattern of Amazon app |
| **Theater Experience** | Short, punchy, TikTok-style clips showing product in motion |
| **Motion = Trust** | Motion creates higher trust than static images |
| **Iconography** | Consistent custom icons for technical specs |
| **Visual Language** | Easy-to-digest, professional, scannable |

---

## 4. Emotional Resonance & The "Avatar"

**Creative Goal:** Tailor creative to a specific person, not a general audience.

### Model Selection Rules

| Rule | Implementation |
|------|----------------|
| **Look Like Target** | Person in photos should look like target customer |
| **Aspirational Option** | Or who they aspire to be |
| **Expression = Result** | Expression mirrors result of using product |
| **Emotion Examples** | Relief, joy, focus, confidence, relaxation |

### Color Palette Psychology

| Product Type | Recommended Colors |
|--------------|-------------------|
| Organic/Natural | Earthy tones, greens, browns |
| Fitness/Energy | Bright, high-energy neons |
| Clinical/Tech | Deep blues and whites |
| Luxury/Premium | Gold, black, deep purple |
| Children/Baby | Soft pastels, warm yellows |
| Eco-Friendly | Greens, ocean blues |

---

## 5. Keyword Intent Alignment (Chris Rawlings' PPC Loop)

**Core Concept:** "Close the loop" between buyer search intent and visual assets. If keywords don't match what images show, shoppers won't convert.

### Intent Classification System

| Intent Category | Example Keywords | Visual Proof Required |
|-----------------|------------------|----------------------|
| **Durability/Quality** | "long-lasting", "premium", "heavy-duty", "professional grade" | Rugged textures, stress tests, premium materials, quality comparisons |
| **Use Case** | "for camping", "office use", "travel size", "outdoor" | Product shown in that exact context/environment |
| **Style/Aesthetic** | "modern", "minimalist", "vintage", "boho" | Match visual aesthetic to style keywords |
| **Problem/Solution** | "pain relief", "easy clean", "quick setup", "no mess" | Before/after, relief expression, solved problem state |
| **Comparison** | "best", "vs", "alternative to", "upgraded" | Side-by-side superiority, check vs. X charts |

### Image-to-Intent Mapping

| Image Type | Primary Intent Focus | Secondary Intent |
|------------|---------------------|------------------|
| **Main Image** | Quality/Premium | Style/Aesthetic |
| **Infographic 1** | Problem/Solution | Durability |
| **Infographic 2** | Problem/Solution | Use Case |
| **Lifestyle** | Use Case | Style/Aesthetic |
| **Comparison** | Comparison | Durability/Quality |

### Prompt Integration Pattern

```
[KEYWORD INTENT INJECTION]
Top converting keywords: {keyword_list}
Primary intent detected: {intent_category}
Visual proof required: {proof_description}

Generate an image that VISUALLY PROVES the intent behind these search terms.
A shopper searching for "{top_keyword}" should immediately see proof of that claim.
```

### Heatmap Optimization

Based on eye-tracking data for mobile Amazon browsing:

```
┌─────────────────────────────────┐
│  ████ HIGH ATTENTION ZONE ████  │ ← Key benefit text
│                                 │
│     ┌───────────────────┐       │
│     │                   │       │
│     │     PRODUCT       │ ← Center-left focus
│     │    (Primary)      │
│     │                   │       │
│     └───────────────────┘       │
│                                 │
│  Supporting info / proof points │ ← F-pattern reading
└─────────────────────────────────┘
```

**Composition Rules:**
- Product: Center-left (primary attention)
- Key benefit text: Top-right (secondary attention)
- Supporting points: Follow F-pattern reading flow
- Mobile-first: Larger elements, higher contrast
- Negative space: Direct attention, don't clutter

---

## 6. Image Type Specifications

### MVP Image Set (5 Images)

| # | Type | Creative Objective | Key Tactic | Prompt Focus |
|---|------|-------------------|------------|--------------|
| 1 | **Main Image** | Stop the scroll | Stacked products & "action" elements (pours, slices) | Dynamic composition, ingredient pop, premium texture |
| 2 | **Infographic 1** | Educate quickly | Large, bold text; key benefit #1 | Benefit-focused headline, product visible, <20% text |
| 3 | **Infographic 2** | Educate quickly | Large, bold text; key benefit #2 | Benefit-focused headline, product visible, <20% text |
| 4 | **Lifestyle** | Build desire | "Instagram-style" authentic photography | Real context, target audience match, warm/authentic |
| 5 | **Comparison** | Remove doubt | Visual "check vs. X" charts using color contrast | Us vs. Them, color psychology, clear winner |

### Phase 2 Image Set (5 A+ Images)

| # | Type | Creative Objective | Key Tactic |
|---|------|-------------------|------------|
| 6 | **Brand Story Hero** | Immerse in brand | Full-width cinematic shot |
| 7 | **Feature Deep-Dive** | Technical education | Icons + specs grid |
| 8 | **Social Proof** | Build trust | Reviews/testimonials visual |
| 9 | **Usage Scenario** | Show versatility | Multiple use cases |
| 10 | **Brand Values** | Emotional connection | Mission/sustainability visual |

---

## 6. Technical Implementation

### Reference Image Usage (from Gemini MCP)

The system uses reference images to maintain product accuracy:

```python
# From gemini_mcp/src/tools/image_generator.py

# Prepare contents for the API
contents = [prompt]

# Add reference images if provided
if reference_image_paths:
    for ref_path in reference_image_paths:
        reference_image = PILImage.open(ref_path)
        contents.append(reference_image)

# Generate with reference
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=contents,  # prompt + reference images
    config=types.GenerateContentConfig(
        response_modalities=['Image'],
        image_config=types.ImageConfig(
            aspect_ratio="1:1"
        )
    )
)
```

### Prompt Template Structure

Each image type should use this structure:

```
[STYLE INJECTION]
{style_template_content}

[PRODUCT CONTEXT]
Product: {product_title}
Target Audience: {target_audience}
Key Features: {feature_1}, {feature_2}, {feature_3}

[IMAGE TYPE INSTRUCTIONS]
{specific_instructions_for_image_type}

[REFERENCE IMAGE]
Use the provided product photo as the base reference.
Maintain product accuracy while applying creative direction.

[TECHNICAL REQUIREMENTS]
- Resolution: 2000x2000px minimum
- Format: PNG with RGB color mode
- Amazon compliance: {specific_requirements}
```

---

## 7. Prompt Templates by Image Type

### Main Image Prompt Template

```
Create a premium Amazon main product image.

PRODUCT: {product_title}

COMPOSITION:
- Pure white background (#FFFFFF)
- Product fills 85% of frame
- Use dynamic "stacking" composition with depth
- If applicable, show ingredient elements (fruits, herbs, etc.) arranged aesthetically
- Professional studio lighting with subtle natural shadows
- Premium, tactile texture quality

STYLE:
- High-end commercial product photography
- Visually "dense" and interesting
- Must stand out in Amazon search results grid
- No text, logos, or watermarks

REFERENCE: Use uploaded product image for accurate product representation.
Enhance and stage it, do not alter the product itself.
```

### Infographic Prompt Template

```
Create an Amazon infographic image highlighting a key benefit.

PRODUCT: {product_title}
KEY BENEFIT: {feature_text}
TARGET AUDIENCE: {target_audience}

COMPOSITION:
- Product visible and prominent
- Large, bold headline text: "{benefit_headline}"
- Text is a DESIGN element, not just a caption
- High-contrast, legible at thumbnail size
- Text covers less than 20% of image area

STYLE:
- Modern, clean infographic design
- Benefit-focused (e.g., "Sleep Better" not "10mg Melatonin")
- Color palette matching product aesthetic
- Professional but approachable

REFERENCE: Use uploaded product image for accurate product representation.
```

### Lifestyle Prompt Template

```
Create an Instagram-style lifestyle image for Amazon.

PRODUCT: {product_title}
TARGET AUDIENCE: {target_audience}
USAGE CONTEXT: {inferred_from_product_and_audience}

COMPOSITION:
- Authentic, real-world setting
- Person using/enjoying product (matches target demographic)
- Warm, natural lighting (sunlit room, outdoor, etc.)
- Product clearly visible but naturally integrated

STYLE:
- High-end social media aesthetic
- Warm, relatable, aspirational
- NOT clinical or stock-photo looking
- Model expression shows result of using product (joy, relief, focus)

EMOTION TARGET: {emotion_based_on_product_category}

REFERENCE: Use uploaded product image. Show it being used naturally.
```

### Comparison Chart Prompt Template

```
Create a comparison chart image for Amazon.

PRODUCT: {product_title}
OUR ADVANTAGES: {feature_2}, {feature_3}

COMPOSITION:
- "Us vs. Them" two-column layout
- Our product: vibrant colors, checkmarks (✓)
- Generic competitor: muted/greyscale, X-marks (✗)
- 3-4 comparison points
- Clear visual hierarchy showing our product as winner

STYLE:
- Professional infographic design
- Strong color contrast
- Text legible at thumbnail size
- Color psychology: warm/positive for us, cool/negative for them

REFERENCE: Use uploaded product image on "our product" side.
Represent competitor as generic/unnamed alternative.
```

---

## 8. Quality Checklist

Before accepting generated images, verify:

### Main Image
- [ ] Pure white background
- [ ] Product fills 85%+ of frame
- [ ] Dynamic composition with depth
- [ ] Premium texture quality
- [ ] No text or watermarks
- [ ] Would stand out in search results

### Infographics
- [ ] One clear benefit message
- [ ] Text is bold and readable at thumbnail
- [ ] Text covers <20% of image
- [ ] Product is visible
- [ ] Benefit-focused (not feature-focused)

### Lifestyle
- [ ] Authentic, not stock-photo feel
- [ ] Matches target audience
- [ ] Product clearly visible
- [ ] Warm, inviting lighting
- [ ] Emotional resonance

### Comparison
- [ ] Clear winner visual hierarchy
- [ ] Color psychology applied correctly
- [ ] Checkmarks vs. X-marks
- [ ] 3-4 comparison points
- [ ] Our product more prominent

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | December 20, 2024 | System | Initial creative blueprint |

---

*This document serves as the core reference for all image generation prompts. Prompt engineering should directly implement these guidelines to ensure high-conversion Amazon listing images.*
