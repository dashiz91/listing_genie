"""
Lifestyle Image Prompt Template
Based on Creative Blueprint Section 2
"""

TEMPLATE = """
Create an Instagram-style lifestyle image for Amazon.

[REFERENCE IMAGE]
Use the provided product photo. Show it being used naturally in context.

[PRODUCT CONTEXT]
Product: {product_title}
Target Audience: {target_audience}
Key Features: {feature_1}, {feature_2}

[COMPOSITION REQUIREMENTS]
- Authentic, real-world setting
- Person using/enjoying product matches target demographic
- Warm, natural lighting (sunlit room, outdoor, etc.)
- Product clearly visible but naturally integrated
- Aspirational but relatable scene

[STYLE DIRECTION]
- High-end social media aesthetic
- Warm, inviting, authentic feel
- NOT clinical or stock-photo looking
- Model expression shows positive result of using product
- Emotional resonance with target audience

[INTENT ALIGNMENT]
{intent_modifiers}

[USE CASE VISUALIZATION]
Based on target audience "{target_audience}", show the product in a context
that matches their lifestyle and usage patterns.

[TECHNICAL REQUIREMENTS]
- Resolution: 2000x2000px
- Natural color grading
- Lifestyle context appropriate for product category
"""
