"""
Comparison Chart Prompt Template
Based on Creative Blueprint Section 2
"""

TEMPLATE = """
Create a comparison chart image for Amazon.

[REFERENCE IMAGE]
Use the provided product photo on the "our product" side.
Represent competitor as generic/unnamed alternative.

[PRODUCT CONTEXT]
Product: {product_title}
Our Advantages: {feature_2}, {feature_3}

[COMPOSITION REQUIREMENTS]
- "Us vs. Them" two-column layout
- Our product: vibrant colors, checkmarks (green)
- Generic competitor: muted/greyscale, X-marks (red/grey)
- 3-4 comparison points based on features
- Clear visual hierarchy showing our product as winner

[STYLE DIRECTION]
- Professional infographic design
- Strong color contrast (green vs. red/grey)
- Text legible at thumbnail size
- Color psychology: warm/positive for us, cool/negative for them

[INTENT ALIGNMENT]
{intent_modifiers}

[COMPARISON POINTS]
1. {feature_2} (Us: Yes, Them: No)
2. {feature_3} (Us: Yes, Them: Limited)
3. Quality/Premium (Us: Superior, Them: Basic)

[TECHNICAL REQUIREMENTS]
- Resolution: 2000x2000px
- Clear, scannable layout
- Winner should be immediately obvious
"""
