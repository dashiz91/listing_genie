"""
Main Product Image Prompt Template
Based on Creative Blueprint Section 1
"""

TEMPLATE = """
Create a premium Amazon main product image.

[REFERENCE IMAGE]
Use the provided product photo as the base reference.
Maintain product accuracy while applying creative direction.

[PRODUCT CONTEXT]
Product: {product_title}
Key Benefit: {key_feature}
Target Audience: {target_audience}

[COMPOSITION REQUIREMENTS]
- Pure white background (#FFFFFF)
- Product fills 85% of frame
- Use dynamic "stacking" composition with depth
- If applicable, show ingredient elements (fruits, herbs, etc.) arranged aesthetically
- Professional studio lighting with subtle natural shadows
- Premium, tactile texture quality

[STYLE DIRECTION]
- High-end commercial product photography
- Visually "dense" and interesting
- Must stand out in Amazon search results grid
- No text, logos, or watermarks

[INTENT ALIGNMENT]
{intent_modifiers}

[TECHNICAL REQUIREMENTS]
- Resolution: 2000x2000px minimum
- Format: PNG with RGB color mode
- Amazon compliant: white background, product-focused

Enhance and stage the product, do not alter the product itself.
"""
