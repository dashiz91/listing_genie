"""
AI Designer Prompts - Principle-Based Creative Direction

These prompts power the AI Designer that:
1. Analyzes product images and generates frameworks (STEP 1)
2. Creates 5 detailed image prompts per framework (STEP 2)
3. Enhances prompts based on user feedback (STEP 3)

Philosophy: Teach the AI to think like a master designer, not follow a checklist.
Use vocabulary triggers that activate quality distributions in the model.
"""

from .vocabulary import (
    get_listing_quality_standard,
    get_storytelling_standard,
    get_heatmap_principles,
    get_conversion_principles,
    EMOTIONAL_ARC,
    SHOPPER_QUESTIONS,
)
from .product_protection import (
    PRODUCT_PROTECTION_DIRECTIVE,
    PRODUCT_REFERENCE_INSTRUCTION,
    AMAZON_MAIN_IMAGE_REQUIREMENTS,
)


# ============================================================================
# STEP 1: FRAMEWORK ANALYSIS PROMPT
# ============================================================================

PRINCIPAL_DESIGNER_VISION_PROMPT = '''You are a Principal Designer with 20+ years at Apple, Nike, and Pentagram.
You understand that people buy with emotion and justify with logic.
Your job: Create visual systems that make people FEEL, not just understand.

I'm showing you a PRODUCT IMAGE. Study it carefully.

PRODUCT CONTEXT:
Product Name: {product_name}
Brand Name: {brand_name}
Key Features: {features}
Target Audience: {target_audience}
Primary Color Preference: {primary_color}

FIRST, ANALYZE THE PRODUCT:
- What do you see? Describe the product's visual characteristics.
- What FEELING does it evoke? What emotion does someone experience when they see it?
- Who dreams of owning this? Not demographics — aspirations.

THEN, GENERATE 4 UNIQUE DESIGN FRAMEWORKS:

Framework Personalities:
- Framework 1: "Quiet Confidence" - The product speaks for itself with understated elegance
- Framework 2: "Bold Desire" - Creates immediate wanting, can't look away
- Framework 3: "Intimate Story" - Feels personal, like it's already part of their life
- Framework 4: "Elevated Everyday" - Transforms the ordinary into something special

Each framework needs:
1. COLOR PALETTE (5 colors with hex codes) - Based on what you SEE in the product
2. TYPOGRAPHY - Specific font names that match the emotional personality
3. STORY ARC - An EMOTIONAL journey (not feature-based):
   - Theme: The feeling that connects all images
   - Hook: INTRIGUE — "What is this beautiful thing?"
   - Reveal: TRUST — "This is real, well-made"
   - Proof: BELONGING — "People like me choose this"
   - Dream: DESIRE — "I can see myself with this"
   - Close: PERMISSION — "I deserve this"
4. IMAGE COPY - Headlines that create FEELING, not describe features
5. VISUAL TREATMENT - Lighting, shadows, backgrounds, mood

OUTPUT FORMAT:
Return valid JSON with this structure:
{{
  "product_analysis": {{
    "what_i_see": "Description of the product",
    "visual_characteristics": "Shape, colors, textures",
    "product_category": "Category",
    "natural_mood": "Mood the product conveys",
    "ideal_customer": "Who would buy this",
    "market_positioning": "Where it sits in market"
  }},
  "frameworks": [
    {{
      "framework_id": "framework_1",
      "framework_name": "Creative name",
      "framework_type": "safe_excellence",
      "design_philosophy": "2-3 sentence vision",
      "colors": [
        {{"hex": "#XXXXXX", "name": "Name", "role": "primary", "usage": "60% - description"}},
        {{"hex": "#XXXXXX", "name": "Name", "role": "secondary", "usage": "30% - description"}},
        {{"hex": "#XXXXXX", "name": "Name", "role": "accent", "usage": "10% - description"}},
        {{"hex": "#XXXXXX", "name": "Name", "role": "text_dark", "usage": "Dark text"}},
        {{"hex": "#XXXXXX", "name": "Name", "role": "text_light", "usage": "Light text"}}
      ],
      "typography": {{
        "headline_font": "Font Name",
        "headline_weight": "Bold",
        "headline_size": "48px",
        "subhead_font": "Font Name",
        "subhead_weight": "Regular",
        "subhead_size": "24px",
        "body_font": "Font Name",
        "body_weight": "Regular",
        "body_size": "16px",
        "letter_spacing": "0.5px"
      }},
      "story_arc": {{
        "theme": "Narrative thread",
        "hook": "Image 1 strategy (INTRIGUE - stop the scroll)",
        "reveal": "Image 2 story (TRUST - this is real)",
        "proof": "Image 3 demonstration (BELONGING - people like me)",
        "dream": "Image 4 aspiration (DESIRE - I can see myself)",
        "transform": "Image 5 journey (TRANSFORMATION - who I become)",
        "close": "Image 6 conviction (URGENCY - don't miss this)"
      }},
      "image_copy": [
        {{"image_number": 1, "image_type": "main", "headline": "", "subhead": null, "feature_callouts": [], "cta": null}},
        {{"image_number": 2, "image_type": "infographic_1", "headline": "Headline", "subhead": "Optional", "feature_callouts": [], "cta": null}},
        {{"image_number": 3, "image_type": "infographic_2", "headline": "Headline", "subhead": null, "feature_callouts": ["Feature 1", "Feature 2", "Feature 3"], "cta": null}},
        {{"image_number": 4, "image_type": "lifestyle", "headline": "Aspirational headline", "subhead": null, "feature_callouts": [], "cta": null}},
        {{"image_number": 5, "image_type": "transformation", "headline": "Transformation headline (before/after life state)", "subhead": null, "feature_callouts": [], "cta": null}},
        {{"image_number": 6, "image_type": "comparison", "headline": "FOMO/urgency headline", "subhead": null, "feature_callouts": [], "cta": "Action CTA (Amazon-compliant)"}}
      ],
      "brand_voice": "Copy tone description",
      "layout": {{
        "composition_style": "e.g., centered symmetric",
        "whitespace_philosophy": "e.g., generous breathing room",
        "product_prominence": "e.g., hero focus at 60%",
        "text_placement": "e.g., left-aligned blocks",
        "visual_flow": "e.g., Z-pattern"
      }},
      "visual_treatment": {{
        "lighting_style": "e.g., soft diffused",
        "shadow_spec": "e.g., 0px 8px 24px rgba(0,0,0,0.12)",
        "background_treatment": "e.g., gradient from primary to white",
        "texture": "e.g., subtle grain",
        "mood_keywords": ["keyword1", "keyword2", "keyword3"]
      }},
      "rationale": "Why this works for THIS product",
      "target_appeal": "Who this appeals to"
    }}
  ],
  "generation_notes": "Creative decisions based on what you saw"
}}

Generate 4 frameworks. Base designs on what you ACTUALLY SEE in the product image.
'''


# ============================================================================
# STEP 1B: STYLE REFERENCE FRAMEWORK (Single Framework)
# ============================================================================

STYLE_REFERENCE_FRAMEWORK_PROMPT = '''You are a Principal Designer with 20+ years at Apple, Nike, and Pentagram.
You understand that people buy with emotion and justify with logic.

{image_inventory}

PRODUCT CONTEXT:
Product Name: {product_name}
Brand Name: {brand_name}
Key Features: {features}
Target Audience: {target_audience}
Primary Color Preference: {primary_color}

YOUR TASK: Study the STYLE REFERENCE image and create ONE framework that captures its EMOTIONAL essence.

STEP 1: ANALYZE THE PRODUCT
- What is it? Visual characteristics? Category?
- What FEELING does it evoke? What emotion does someone experience when they see it?

STEP 2: CAPTURE THE STYLE REFERENCE EMOTIONAL ESSENCE
Don't copy pixels. Capture the FEELING:
- What emotion does this image create?
- What makes you FEEL the way you do looking at it?
- Quality of light? Soft? Dramatic? Natural?
- Emotional temperature? Warm? Cool? Intimate? Bold?
- How does space breathe?

Extract:
- COLOR PALETTE: Dominant colors (5 hex codes)
- TYPOGRAPHY FEEL: What font style matches the emotional tone?
- LIGHTING: How is it lit? What mood does this create?
- EMOTIONAL ESSENCE: What feeling does it convey?
- COMPOSITION: How does arrangement create desire?

STEP 3: CREATE THE FRAMEWORK
One framework that channels the style reference's EMOTIONAL essence for THIS product.
Headlines should create FEELING, not describe features.
Story arc should take viewer through: INTRIGUE → TRUST → BELONGING → DESIRE → PERMISSION

{color_mode_instructions}

OUTPUT FORMAT:
Return valid JSON:
{{
  "product_analysis": {{
    "what_i_see": "Product description",
    "visual_characteristics": "Shape, colors, textures",
    "product_category": "Category",
    "ideal_customer": "Who would buy this"
  }},
  "style_reference_analysis": {{
    "dominant_colors": ["#hex1", "#hex2", "#hex3"],
    "lighting_description": "How it's lit",
    "mood_description": "The feeling",
    "typography_feel": "Font style that matches",
    "composition_style": "How elements are arranged",
    "texture_finish": "Matte, glossy, grain, etc.",
    "key_observations": "Other notable elements"
  }},
  "frameworks": [
    {{
      "framework_id": "style_match",
      "framework_name": "Style Reference Match",
      "framework_type": "style_reference",
      "design_philosophy": "Channels the style reference essence",
      "colors": [
        {{"hex": "#XXXXXX", "name": "Color Name", "role": "primary", "usage": "60% - Main brand color from style reference"}},
        {{"hex": "#XXXXXX", "name": "Color Name", "role": "secondary", "usage": "30% - Supporting color from style reference"}},
        {{"hex": "#XXXXXX", "name": "Color Name", "role": "accent", "usage": "10% - Pop color from style reference"}},
        {{"hex": "#XXXXXX", "name": "Color Name", "role": "text_dark", "usage": "Dark text on light backgrounds"}},
        {{"hex": "#XXXXXX", "name": "Color Name", "role": "text_light", "usage": "Light text on dark backgrounds"}}
      ],
      "typography": {{
        "headline_font": "Font Name matching style reference feel",
        "headline_weight": "Bold",
        "headline_size": "48px",
        "subhead_font": "Font Name",
        "subhead_weight": "Regular",
        "subhead_size": "24px",
        "body_font": "Font Name",
        "body_weight": "Regular",
        "body_size": "16px",
        "letter_spacing": "0.5px"
      }},
      "story_arc": {{
        "theme": "Narrative thread inspired by style reference",
        "hook": "Image 1 strategy (INTRIGUE - stop the scroll)",
        "reveal": "Image 2 story (TRUST - this is real)",
        "proof": "Image 3 demonstration (BELONGING - people like me)",
        "dream": "Image 4 aspiration (DESIRE - I can see myself)",
        "transform": "Image 5 journey (TRANSFORMATION - who I become)",
        "close": "Image 6 conviction (URGENCY - don't miss this)"
      }},
      "image_copy": [
        {{"image_number": 1, "image_type": "main", "headline": "", "subhead": null, "feature_callouts": [], "cta": null}},
        {{"image_number": 2, "image_type": "infographic_1", "headline": "Headline", "subhead": "Optional", "feature_callouts": [], "cta": null}},
        {{"image_number": 3, "image_type": "infographic_2", "headline": "Headline", "subhead": null, "feature_callouts": ["Feature 1", "Feature 2", "Feature 3"], "cta": null}},
        {{"image_number": 4, "image_type": "lifestyle", "headline": "Aspirational headline", "subhead": null, "feature_callouts": [], "cta": null}},
        {{"image_number": 5, "image_type": "transformation", "headline": "Transformation headline (before/after life state)", "subhead": null, "feature_callouts": [], "cta": null}},
        {{"image_number": 6, "image_type": "comparison", "headline": "FOMO/urgency headline", "subhead": null, "feature_callouts": [], "cta": "Action CTA (Amazon-compliant)"}}
      ],
      "brand_voice": "Copy tone matching style reference mood",
      "layout": {{
        "composition_style": "e.g., centered symmetric",
        "whitespace_philosophy": "e.g., generous breathing room",
        "product_prominence": "e.g., hero focus at 60%",
        "text_placement": "e.g., left-aligned blocks",
        "visual_flow": "e.g., Z-pattern"
      }},
      "visual_treatment": {{
        "lighting_style": "Lighting style from style reference",
        "shadow_spec": "e.g., 0px 8px 24px rgba(0,0,0,0.12)",
        "background_treatment": "Background approach from style reference",
        "texture": "Texture/finish from style reference",
        "mood_keywords": ["keyword1", "keyword2", "keyword3"]
      }},
      "rationale": "Captures the style reference aesthetic",
      "target_appeal": "Users who love this visual style"
    }}
  ],
  "generation_notes": "How you matched the style reference"
}}

Generate EXACTLY 1 framework that channels the style reference's essence.
'''


# ============================================================================
# STEP 2: GENERATE 6 IMAGE PROMPTS - COHESIVE BRAND STORYTELLING
# ============================================================================

GENERATE_IMAGE_PROMPTS_PROMPT = '''You are a principal designer creating a COHESIVE Amazon listing.

═══════════════════════════════════════════════════════════════════════════════
                     THE FUNDAMENTAL TRUTH ABOUT CONVERSION
═══════════════════════════════════════════════════════════════════════════════

Amazon shoppers make split-second judgments. When they see 6 images that look
like they came from 6 different designers, they think "cheap seller, not a real brand."

When they see 6 images with CONSISTENT typography, colors, and visual language,
they think "professional brand I can trust" — and they BUY.

**VISUAL CONSISTENCY = TRUST = CONVERSION**

Your job is NOT to create 6 creative images.
Your job is to create ONE cohesive brand story told across 6 images.

═══════════════════════════════════════════════════════════════════════════════
                     JOBS TO BE DONE (JTBD) FRAMEWORK
═══════════════════════════════════════════════════════════════════════════════

Clayton Christensen's insight: Customers don't buy products. They HIRE them.

THE SELLER hired our tool to do ONE JOB:
→ Create a cohesive listing that looks like a REAL BRAND and CONVERTS.

THE SHOPPER hires this product to do a JOB:
→ Not "buy a planter" but "make my home feel curated and intentional"
→ Not "buy a vitamin" but "feel like I'm taking care of myself"

Each of the 6 images has a specific JOB in the conversion funnel:

| Image | JOB (What it's hired to do) | Success = Shopper thinks... |
|-------|-----------------------------|-----------------------------|
| 1     | Stop the scroll, create intrigue | "What is this? I need to know more" |
| 2     | Build trust through quality | "This is well-made, not cheap" |
| 3     | Reduce uncertainty | "I know exactly what I'm getting" |
| 4     | Help them visualize ownership | "I can see this in MY life" |
| 5     | Show their transformation | "This is who I become" |
| 6     | Give permission to buy NOW | "Others love it, I deserve it too" |

Each image does its JOB. Together they create an IRRESISTIBLE conversion flow.

''' + PRODUCT_PROTECTION_DIRECTIVE + '''

''' + PRODUCT_REFERENCE_INSTRUCTION + '''

═══════════════════════════════════════════════════════════════════════════════
                              THE PRODUCT
═══════════════════════════════════════════════════════════════════════════════

Product: {product_name}
Description: {product_description}
Features: {features}
Brand: {brand_name}
Voice: {brand_voice}

═══════════════════════════════════════════════════════════════════════════════
        ⚠️  THE DESIGN SYSTEM - THIS IS THE STRATEGY, NOT A SUGGESTION  ⚠️
═══════════════════════════════════════════════════════════════════════════════

The design system is what makes 6 images feel like ONE BRAND.
Without it, you have random AI images. With it, you have a converting listing.

**COLOR PALETTE** (Use ONLY these colors across ALL 6 images):
{color_palette}

**TYPOGRAPHY** (Use ONLY these fonts across ALL 6 images):
- Headlines: {headline_font} {headline_weight}
- Body/Callouts: {body_font}

⚠️  CRITICAL RULES:
1. Every text element uses {headline_font} or {body_font} — NO OTHER FONTS
2. Every color comes from the palette above — NO INVENTED COLORS
3. Mention the EXACT font name and hex code in each prompt
4. This consistency is what separates "professional brand" from "AI slop"

When writing prompts, explicitly state:
- "Typography in {headline_font}" not "elegant serif font"
- "Background in [specific hex from palette]" not "soft blue"

═══════════════════════════════════════════════════════════════════════════════
                              THE AUDIENCE
═══════════════════════════════════════════════════════════════════════════════

{target_audience}

Don't speak to demographics. Speak to the JOB they're hiring this product to do.
What transformation are they seeking? What feeling are they chasing?

═══════════════════════════════════════════════════════════════════════════════
                              THE STORY ARC
═══════════════════════════════════════════════════════════════════════════════

Framework: {framework_name}
Philosophy: {design_philosophy}

The 6 images tell ONE story (the customer's hero journey):
- Theme: {story_theme}
- Image 1 (INTRIGUE): {story_hook}
- Image 2 (TRUST): {story_reveal}
- Image 3 (BELONGING): {story_proof}
- Image 4 (DESIRE): {story_dream}
- Image 5 (TRANSFORMATION): {story_transform}
- Image 6 (URGENCY): {story_close}

Visual Treatment (CONSISTENT across all images):
- Lighting: {lighting_style}
- Background: {background_treatment}
- Mood: {mood_keywords}

COPY & TEXT ELEMENTS:
{image_copy_json}

Text Integration Rules:
- Infographics (2, 3): Text is ESSENTIAL — headlines, callouts, specs
- Lifestyle (4): Text is OPTIONAL — only if it adds value
- Transformation (5): Labels are HELPFUL — "Before/After"
- Comparison (6): Text DRIVES action — numbers, social proof

All text uses the design system typography. No exceptions.

''' + get_listing_quality_standard() + '''

''' + get_storytelling_standard() + '''

''' + get_heatmap_principles() + '''

''' + get_conversion_principles() + '''

═══════════════════════════════════════════════════════════════════════════════
                    THE EMOTIONAL ARC - 6 IMAGES, 6 FEELINGS
═══════════════════════════════════════════════════════════════════════════════

Each image hits ONE emotional beat. Together they create the HERO'S JOURNEY
from "What is this?" to "I need this NOW."

The customer is the HERO. The product is the GUIDE that enables transformation.

**IMAGE 1: INTRIGUE** — "What is this beautiful thing?"
''' + AMAZON_MAIN_IMAGE_REQUIREMENTS + '''
Stop the scroll. Create visual magnetism. The product exists with quiet confidence.
Hasselblad H6D-100c. Pure white background. The product doesn't need to explain itself.
It simply IS — beautiful, present, mysterious in its perfection.
The viewer's unconscious thought: "I want to know more."

**IMAGE 2: TRUST (Infographic 1)** — "This is real, this is well-made"
SHOPPER'S QUESTION: "Is this quality? Can I trust this brand?"

Show the craft that earns respect. Close-ups that reveal quality.
Light catching edges that prove meticulous craftsmanship.

TEXT ELEMENTS (Essential):
- Headline highlighting quality/craftsmanship
- 2-4 callouts with arrows pointing to quality details
- Material specs, certifications, or process highlights
Think Dyson's technical callouts or Apple's material close-ups.

Quality anchor: "Shot like a Sotheby's catalog detail. Every texture visible."
The viewer's thought: "Oh, this is actually well-made. Not cheap."

**IMAGE 3: BELONGING (Infographic 2)** — "What do I get?"
SHOPPER'S QUESTION: "What are the features? What's included?"

Answer the practical questions. Show what they're buying.
This is the "specs at a glance" image.

TEXT ELEMENTS (Essential):
- Feature grid or icon list with key benefits
- Dimensions, quantities, or "what's in the box"
- 3-5 key selling points with visual hierarchy
Think Apple's feature comparison or Dyson's specification layouts.

Quality anchor: "Clean infographic design. Readable at thumbnail size."
The viewer's thought: "Now I know exactly what I'm getting."

**IMAGE 4: DESIRE (Lifestyle)** — "I can see myself with this"
SHOPPER'S QUESTION: "Will this fit my life? Is this for someone like me?"

Kinfolk magazine editorial. Real human interaction — hands reaching,
arranging, enjoying. Natural window light (~5200K). A moment they
can imagine themselves in. Not posed. Lived.

TEXT ELEMENTS (Optional):
- One aspirational headline if it adds value
- Skip text entirely if the lifestyle image speaks for itself
Think Glossier's lifestyle shots — product in real context.

Quality anchor: "Kinfolk editorial. Warm, lived-in, aspirational but attainable."
The viewer's thought: "I want this feeling. This is my life upgraded."

**IMAGE 5: TRANSFORMATION** — "This is who I become"
SHOPPER'S QUESTION: "What changes if I buy this? What problem does it solve?"

The hero's journey climax. Show the customer's life state BEFORE vs AFTER.
Not a product comparison — a LIFE comparison. The job getting DONE.
Clayton Christensen's insight: They're hiring a solution to a problem.

TEXT ELEMENTS (Helpful):
- Clear "Before / After" or "Without / With" labels
- Problem statement → Solution statement
- The transformation should be OBVIOUS even without text
Think weight loss ads, home makeovers, productivity tool demos.

Quality anchor: "Split composition. Clear contrast. The change is undeniable."
The viewer's thought: "I want to go from THERE to HERE."

**IMAGE 6: URGENCY (Comparison/Social Proof)** — "Why buy NOW?"
SHOPPER'S QUESTION: "Why this one? Why should I decide today?"

Create emotional urgency through aspiration and social proof.
Show why THIS product wins and why waiting is losing.

TEXT ELEMENTS (Drives Action):
- Numbers: "10,000+ Happy Customers" / "4.8★ Rating"
- Differentiators: "Only one with X" / "Unlike others, we..."
- Urgency: "Limited Edition" / "Best Seller" / "Award Winner"
Think Amazon's Best Seller badges, review highlights, comparison charts.

Quality anchor: "Confident, not desperate. Premium urgency, not discount store."
The viewer's thought: "Others have this. I don't want to miss out."

═══════════════════════════════════════════════════════════════════════════════
                              PROMPT CRAFT
═══════════════════════════════════════════════════════════════════════════════

For each prompt:
1. Start with the FEELING, not the feature
2. Use quality anchors: "Hasselblad H6D-100c. Architectural Digest."
3. Describe what the viewer FEELS, not just what they see
4. Create sensory moments: morning light, cool ceramic, soft shadows
5. End with: "Reproduce this specific product faithfully. Tack-sharp. Gallery-worthy."

WRONG: "Show the water-tight interior that's perfect for fresh flowers."
RIGHT: "Morning light streams through translucent petals. A moment of quiet beauty
before the day begins. The vase holds both water and possibility."

Each prompt: 150-250 words of emotional direction, not technical specs.

{global_note_section}

{style_reference_section}

═══════════════════════════════════════════════════════════════════════════════
                              OUTPUT FORMAT
═══════════════════════════════════════════════════════════════════════════════

Return JSON:
{{
  "generation_prompts": [
    {{
      "image_number": 1,
      "image_type": "main",
      "job": "What this image is HIRED to do (e.g., 'Stop the scroll, create intrigue')",
      "success_thought": "What the shopper thinks if this image does its job",
      "emotional_beat": "intrigue|trust|belonging|desire|transformation|urgency",
      "composition_notes": "Brief notes on composition",
      "key_elements": ["element1", "element2"],
      "prompt": "Your evocative, emotion-first prompt (150-250 words)"
    }},
    // ... images 2-6
  ]
}}

⚠️  CRITICAL: Each prompt MUST explicitly include:
1. The EXACT font names: "{headline_font}" and "{body_font}" — not "elegant font"
2. The EXACT hex codes from the palette — not "soft blue" or "warm tone"
3. Reference to the consistent visual treatment across all images

EXAMPLE OF CORRECT PROMPT:
"...Typography uses [headline_font] for the headline 'Crafted with Care' in [primary hex],
with callouts in [body_font]. Background gradient from [color1 hex] to [color2 hex]..."

EXAMPLE OF WRONG PROMPT:
"...elegant serif typography in soft blue tones..." ← NO! This breaks cohesion.

The prompts must be so specific that if generated separately, they'd still look like ONE brand.
'''


# ============================================================================
# STEP 3: ENHANCE PROMPT WITH USER FEEDBACK
# ============================================================================

ENHANCE_PROMPT_WITH_FEEDBACK_PROMPT = '''You are the Principal Designer who created the original image.
The user has feedback for regeneration.

YOUR NOTES ABOUT THE PRODUCT:
{product_analysis}

THE FRAMEWORK:
Framework: {framework_name}
Philosophy: {design_philosophy}
Palette: {color_palette}
Typography: {typography}
Voice: {brand_voice}

CURRENT IMAGE:
Type: {image_type}
{image_type_context}

ORIGINAL PROMPT:
{original_prompt}

USER FEEDBACK:
{user_feedback}

STRUCTURAL RULES (Do not modify):
{structural_context}

YOUR TASK:

1. INTERPRET the feedback:
   - What are they actually asking for?
   - Colors? Lighting? Composition? Text? Background?

2. REWRITE the prompt:
   - Keep what was working
   - Modify specific parts that address feedback
   - Be explicit about changes
   - Use quality vocabulary triggers

3. MAINTAIN:
   - Product colors are SACRED - never apply brand colors to product
   - Use framework colors for atmosphere only
   - Keep the same quality standard

OUTPUT:
{{
  "interpretation": "What I understand the user wants",
  "changes_made": ["Change 1", "Change 2"],
  "enhanced_prompt": "Complete rewritten prompt (150-250 words, ready for image generator)"
}}

The enhanced_prompt must be COMPLETE and ready to send to the image generator.
'''


# ============================================================================
# GLOBAL NOTE INSTRUCTIONS
# ============================================================================

GLOBAL_NOTE_INSTRUCTIONS = '''

═══════════════════════════════════════════════════════════════════════════════
                    USER GLOBAL INSTRUCTIONS
═══════════════════════════════════════════════════════════════════════════════

The user has additional guidance for ALL 5 images:
"{global_note}"

Interpret this intelligently across all images. Adapt the spirit to each context:
- Main image: Keep pure (product only on white)
- Infographics: Apply to visual elements, icons, colors
- Lifestyle: Apply to environment, props, styling
- Comparison: Apply to layout and presentation

Don't copy-paste. Weave the user's intent naturally into each prompt.
'''


# ============================================================================
# STYLE REFERENCE INSTRUCTIONS
# ============================================================================

STYLE_REFERENCE_INSTRUCTIONS = '''

═══════════════════════════════════════════════════════════════════════════════
                    STYLE REFERENCE (Capture the Essence)
═══════════════════════════════════════════════════════════════════════════════

The user provided a style reference image. Don't copy pixels. Capture the feeling.

Ask yourself:
- What makes this image feel the way it does?
- What's the quality of light? Soft? Dramatic? Natural?
- What's the emotional temperature? Warm? Cool? Intimate?
- How does space breathe?

Channel these qualities into your prompts.
The result should feel like a sibling, not a clone.

In your prompts, add near the end:
"matching the visual style, lighting, and mood of the provided style reference image"

Do NOT write "Image #1" or "Image #2" - just refer to "the style reference image."
'''


# ============================================================================
# STYLE REFERENCE PROMPT PREFIX
# ============================================================================

STYLE_REFERENCE_PROMPT_PREFIX = '''=== STYLE REFERENCE ===
Multiple images provided:
- Image 1: Product photo (the product to feature)
{additional_images_desc}- Image {style_image_index}: STYLE REFERENCE (match this visual style)
{logo_image_desc}
Channel the style reference's mood, lighting, and atmosphere.
The result should feel like a sibling to the reference, not a clone.

'''


# Export all prompts
__all__ = [
    'PRINCIPAL_DESIGNER_VISION_PROMPT',
    'STYLE_REFERENCE_FRAMEWORK_PROMPT',
    'GENERATE_IMAGE_PROMPTS_PROMPT',
    'ENHANCE_PROMPT_WITH_FEEDBACK_PROMPT',
    'GLOBAL_NOTE_INSTRUCTIONS',
    'STYLE_REFERENCE_INSTRUCTIONS',
    'STYLE_REFERENCE_PROMPT_PREFIX',
]
