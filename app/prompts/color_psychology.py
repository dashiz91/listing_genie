"""
Color Psychology for Product Categories
Based on Creative Blueprint Section 4
"""
from typing import List

CATEGORY_PALETTES = {
    'health_supplements': {
        'primary': ['earthy greens', 'natural browns', 'soft whites'],
        'accent': ['gold', 'amber'],
        'mood': 'natural, trustworthy, organic'
    },
    'fitness': {
        'primary': ['bold blacks', 'energetic reds', 'electric blues'],
        'accent': ['neon green', 'orange'],
        'mood': 'powerful, energetic, motivating'
    },
    'baby_kids': {
        'primary': ['soft pastels', 'warm yellows', 'gentle blues'],
        'accent': ['white', 'cream'],
        'mood': 'safe, gentle, nurturing'
    },
    'tech_electronics': {
        'primary': ['deep blues', 'clean whites', 'sleek grays'],
        'accent': ['electric blue', 'silver'],
        'mood': 'modern, innovative, premium'
    },
    'home_kitchen': {
        'primary': ['warm neutrals', 'natural wood tones', 'white'],
        'accent': ['copper', 'brass', 'green'],
        'mood': 'warm, inviting, reliable'
    },
    'beauty_skincare': {
        'primary': ['soft pinks', 'clean whites', 'rose gold'],
        'accent': ['gold', 'lavender'],
        'mood': 'luxurious, gentle, sophisticated'
    },
    'outdoor_sports': {
        'primary': ['forest greens', 'earth browns', 'sky blues'],
        'accent': ['orange', 'yellow'],
        'mood': 'adventurous, rugged, natural'
    },
    'default': {
        'primary': ['professional blues', 'clean whites'],
        'accent': ['gold', 'green'],
        'mood': 'professional, trustworthy'
    }
}


def get_color_guidance(category: str) -> str:
    """Generate color palette guidance for prompts"""
    palette = CATEGORY_PALETTES.get(category, CATEGORY_PALETTES['default'])

    return f"""
[COLOR PSYCHOLOGY]
- Primary palette: {', '.join(palette['primary'])}
- Accent colors: {', '.join(palette['accent'])}
- Overall mood: {palette['mood']}
"""


def infer_category(product_title: str, keywords: List[str]) -> str:
    """Infer product category from title and keywords"""
    title_lower = product_title.lower()
    keywords_lower = [k.lower() for k in keywords]
    all_text = title_lower + ' ' + ' '.join(keywords_lower)

    category_keywords = {
        'health_supplements': ['vitamin', 'supplement', 'gummy', 'gummies', 'organic', 'natural', 'health', 'probiotic', 'collagen', 'omega'],
        'fitness': ['fitness', 'workout', 'gym', 'protein', 'exercise', 'sport', 'athletic', 'muscle'],
        'baby_kids': ['baby', 'kid', 'child', 'infant', 'toddler', 'nursery', 'newborn'],
        'tech_electronics': ['tech', 'electronic', 'gadget', 'smart', 'device', 'digital', 'wireless', 'bluetooth'],
        'home_kitchen': ['kitchen', 'home', 'cooking', 'utensil', 'organizer', 'storage', 'cleaning'],
        'beauty_skincare': ['beauty', 'skincare', 'cosmetic', 'serum', 'cream', 'moisturizer', 'anti-aging'],
        'outdoor_sports': ['outdoor', 'camping', 'hiking', 'fishing', 'hunting', 'sports', 'adventure'],
    }

    for category, cat_keywords in category_keywords.items():
        if any(kw in all_text for kw in cat_keywords):
            return category

    return 'default'
