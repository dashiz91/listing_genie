"""
Infographic Image Prompt Templates
Based on Creative Blueprint Section 2
"""

TEMPLATE_1 = """
Create an Amazon infographic image highlighting a key benefit.

[REFERENCE IMAGE]
Use the provided product photo for accurate product representation.

[PRODUCT CONTEXT]
Product: {product_title}
Key Benefit: {feature_1}
Target Audience: {target_audience}

[COMPOSITION REQUIREMENTS]
- Product visible and prominent (center-left placement)
- Large, bold headline text highlighting the benefit
- Text is a DESIGN element, not just a caption
- High-contrast, legible at thumbnail size
- Text covers less than 20% of image area
- F-pattern reading flow consideration

[STYLE DIRECTION]
- Modern, clean infographic design
- Benefit-focused language (e.g., "Sleep Better" not "10mg Melatonin")
- Color palette matching product aesthetic
- Professional but approachable

[INTENT ALIGNMENT]
{intent_modifiers}

[KEYWORD ALIGNMENT]
Top keywords: {top_keywords}
Ensure visual elements prove the claims implied by these search terms.

[TECHNICAL REQUIREMENTS]
- Resolution: 2000x2000px
- Text readable at mobile thumbnail size
"""

TEMPLATE_2 = """
Create an Amazon infographic image highlighting a secondary key benefit.

[REFERENCE IMAGE]
Use the provided product photo for accurate product representation.

[PRODUCT CONTEXT]
Product: {product_title}
Key Benefit: {feature_2}
Target Audience: {target_audience}

[COMPOSITION REQUIREMENTS]
- Product visible and prominent
- Large, bold headline text highlighting the benefit
- Text as design element with visual hierarchy
- High-contrast for mobile visibility
- Text density under 20%

[STYLE DIRECTION]
- Consistent with first infographic styling
- Different visual approach to avoid repetition
- Benefit-focused messaging
- Modern, scannable layout

[INTENT ALIGNMENT]
{intent_modifiers}

[TECHNICAL REQUIREMENTS]
- Resolution: 2000x2000px
- Maintains visual cohesion with other listing images
"""
