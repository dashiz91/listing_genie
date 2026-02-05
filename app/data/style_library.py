"""
Pre-generated Style Library

A collection of curated design styles that users can browse and use without spending credits.
Each style has been pre-generated with sample images showing the aesthetic.
"""

from typing import List, Dict

# Style categories
CATEGORIES = {
    "seasonal": "Holiday and seasonal themes",
    "minimalist": "Clean, simple, modern designs",
    "luxury": "Premium, high-end aesthetics",
    "vibrant": "Bold, colorful, energetic styles",
    "natural": "Organic, earthy, eco-friendly looks",
    "iconic": "Inspired by world-famous brand aesthetics",
}

# Pre-generated styles
# Preview images are stored in frontend/public/styles/
STYLES: List[Dict] = [
    # === SEASONAL ===
    {
        "id": "christmas",
        "name": "Holiday Magic",
        "category": "seasonal",
        "description": "Festive red and green with golden accents",
        "colors": ["#C41E3A", "#165B33", "#D4AF37", "#FFFFFF"],
        "preview_image": "/styles/christmas.png",
        "tags": ["christmas", "holiday", "winter", "festive"],
    },

    # === MINIMALIST ===
    {
        "id": "clean-white",
        "name": "Pure & Simple",
        "category": "minimalist",
        "description": "Clean white backgrounds with subtle shadows",
        "colors": ["#FFFFFF", "#F5F5F5", "#333333", "#666666"],
        "preview_image": "/styles/clean-white.png",
        "tags": ["minimal", "clean", "white", "modern"],
    },

    # === LUXURY ===
    {
        "id": "gold-luxe",
        "name": "Golden Hour",
        "category": "luxury",
        "description": "Rich gold accents with deep black backgrounds",
        "colors": ["#D4AF37", "#1A1A2E", "#B8860B", "#000000"],
        "preview_image": "/styles/gold-luxe.png",
        "tags": ["gold", "luxury", "premium", "rich"],
    },

    # === VIBRANT ===
    {
        "id": "neon-pop",
        "name": "Neon Pop",
        "category": "vibrant",
        "description": "Bold neon colors that demand attention",
        "colors": ["#FF00FF", "#00FFFF", "#FFFF00", "#1A1A2E"],
        "preview_image": "/styles/neon-pop.png",
        "tags": ["neon", "bold", "bright", "energetic"],
    },

    # === NATURAL ===
    {
        "id": "earth-tones",
        "name": "Earth & Clay",
        "category": "natural",
        "description": "Warm terracotta and bohemian earth tones",
        "colors": ["#CC7351", "#D4A574", "#8B7355", "#3D2B1F"],
        "preview_image": "/styles/earth-tones.png",
        "tags": ["earth", "natural", "organic", "bohemian"],
    },

    # === ICONIC (Brand-Inspired) ===
    {
        "id": "tech-minimal",
        "name": "Tech Minimal",
        "category": "iconic",
        "description": "Ultra-clean premium tech aesthetic with perfect lighting",
        "colors": ["#FFFFFF", "#F5F5F5", "#86868B", "#1D1D1F"],
        "preview_image": "/styles/tech-minimal.png",
        "tags": ["tech", "minimal", "premium", "clean"],
    },
    {
        "id": "athletic-energy",
        "name": "Athletic Energy",
        "category": "iconic",
        "description": "Bold, dynamic, empowering sports aesthetic",
        "colors": ["#000000", "#FFFFFF", "#FF5722", "#1A1A1A"],
        "preview_image": "/styles/athletic-energy.png",
        "tags": ["athletic", "bold", "dynamic", "sports"],
    },
    {
        "id": "sport-stripes",
        "name": "Sport Stripes",
        "category": "iconic",
        "description": "Clean sporty design with iconic stripe elements",
        "colors": ["#000000", "#FFFFFF", "#1A1A1A", "#E0E0E0"],
        "preview_image": "/styles/sport-stripes.png",
        "tags": ["sporty", "stripes", "athletic", "fresh"],
    },
    {
        "id": "cosmic-dark",
        "name": "Cosmic Dark",
        "category": "iconic",
        "description": "Futuristic space-age aesthetic with sleek minimalism",
        "colors": ["#0A0A0A", "#1A1A2E", "#00D4FF", "#FFFFFF"],
        "preview_image": "/styles/cosmic-dark.png",
        "tags": ["futuristic", "space", "tech", "dark"],
    },
    {
        "id": "heritage-craft",
        "name": "Heritage Craft",
        "category": "iconic",
        "description": "Timeless luxury with rich heritage patterns",
        "colors": ["#5C4033", "#D4A574", "#C9A961", "#1A1A1A"],
        "preview_image": "/styles/heritage-craft.png",
        "tags": ["luxury", "heritage", "elegant", "premium"],
    },
    {
        "id": "playful-pop",
        "name": "Playful Pop",
        "category": "iconic",
        "description": "Bright, friendly, and approachable with primary colors",
        "colors": ["#4285F4", "#EA4335", "#FBBC05", "#34A853"],
        "preview_image": "/styles/playful-pop.png",
        "tags": ["playful", "colorful", "friendly", "fun"],
    },
]


def get_styles_by_category(category: str) -> List[Dict]:
    """Get all styles in a category."""
    return [s for s in STYLES if s["category"] == category]


def get_style_by_id(style_id: str) -> Dict | None:
    """Get a specific style by ID."""
    for style in STYLES:
        if style["id"] == style_id:
            return style
    return None


def get_all_styles() -> List[Dict]:
    """Get all styles."""
    return STYLES


def get_categories() -> Dict[str, str]:
    """Get all categories with descriptions."""
    return CATEGORIES
