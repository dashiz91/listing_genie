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
}

# Pre-generated styles
# Preview images are stored in frontend/public/styles/
STYLES: List[Dict] = [
    # === SEASONAL ===
    {
        "id": "christmas",
        "name": "Holiday Magic",
        "category": "seasonal",
        "description": "Festive red and green with golden accents, perfect for holiday products",
        "colors": ["#C41E3A", "#165B33", "#D4AF37", "#FFFFFF"],
        "preview_image": "/styles/christmas.png",
        "tags": ["christmas", "holiday", "winter", "festive"],
    },
    {
        "id": "valentines",
        "name": "Love Story",
        "category": "seasonal",
        "description": "Romantic pinks and reds with soft, dreamy aesthetics",
        "colors": ["#FF69B4", "#DC143C", "#FFB6C1", "#FFFFFF"],
        "preview_image": "/styles/valentines.png",
        "tags": ["valentines", "love", "romantic", "pink"],
    },
    {
        "id": "mothers-day",
        "name": "Bloom & Cherish",
        "category": "seasonal",
        "description": "Soft florals and nurturing pastels for Mother's Day",
        "colors": ["#DDA0DD", "#98D8C8", "#F7CAC9", "#FFFFFF"],
        "preview_image": "/styles/mothers-day.png",
        "tags": ["mothers day", "spring", "floral", "pastel"],
    },
    {
        "id": "halloween",
        "name": "Spooky Season",
        "category": "seasonal",
        "description": "Dark and mysterious with orange accents",
        "colors": ["#FF6600", "#1A1A2E", "#4A0E4E", "#000000"],
        "preview_image": "/styles/halloween.png",
        "tags": ["halloween", "spooky", "autumn", "dark"],
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
    {
        "id": "nordic",
        "name": "Nordic Calm",
        "category": "minimalist",
        "description": "Scandinavian-inspired with muted tones",
        "colors": ["#E8E4E1", "#B8B5B0", "#6B6B6B", "#2C2C2C"],
        "preview_image": "/styles/nordic.png",
        "tags": ["scandinavian", "nordic", "calm", "neutral"],
    },
    {
        "id": "mono-black",
        "name": "Noir Elegance",
        "category": "minimalist",
        "description": "Sophisticated black and white contrast",
        "colors": ["#000000", "#1A1A1A", "#FFFFFF", "#CCCCCC"],
        "preview_image": "/styles/mono-black.png",
        "tags": ["black", "monochrome", "elegant", "contrast"],
    },

    # === LUXURY ===
    {
        "id": "gold-luxe",
        "name": "Golden Hour",
        "category": "luxury",
        "description": "Rich gold accents with deep backgrounds",
        "colors": ["#D4AF37", "#1A1A2E", "#B8860B", "#000000"],
        "preview_image": "/styles/gold-luxe.png",
        "tags": ["gold", "luxury", "premium", "rich"],
    },
    {
        "id": "marble",
        "name": "Marble & Stone",
        "category": "luxury",
        "description": "Elegant marble textures with sophisticated grays",
        "colors": ["#F5F5F5", "#A9A9A9", "#696969", "#2F4F4F"],
        "preview_image": "/styles/marble.png",
        "tags": ["marble", "stone", "elegant", "sophisticated"],
    },
    {
        "id": "rose-gold",
        "name": "Rose Gold Dreams",
        "category": "luxury",
        "description": "Feminine luxury with rose gold and blush tones",
        "colors": ["#B76E79", "#F7CAC9", "#FFF0F5", "#2C2C2C"],
        "preview_image": "/styles/rose-gold.png",
        "tags": ["rose gold", "feminine", "luxury", "blush"],
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
    {
        "id": "sunset",
        "name": "Sunset Vibes",
        "category": "vibrant",
        "description": "Warm gradient from orange to purple",
        "colors": ["#FF6B6B", "#FFA07A", "#9370DB", "#4B0082"],
        "preview_image": "/styles/sunset.png",
        "tags": ["sunset", "gradient", "warm", "colorful"],
    },
    {
        "id": "tropical",
        "name": "Tropical Paradise",
        "category": "vibrant",
        "description": "Lush greens and vibrant tropical colors",
        "colors": ["#00CED1", "#32CD32", "#FF6347", "#FFD700"],
        "preview_image": "/styles/tropical.png",
        "tags": ["tropical", "summer", "beach", "vibrant"],
    },

    # === NATURAL ===
    {
        "id": "earth-tones",
        "name": "Earth & Clay",
        "category": "natural",
        "description": "Warm terracotta and natural earth tones",
        "colors": ["#CC7351", "#D4A574", "#8B7355", "#3D2B1F"],
        "preview_image": "/styles/earth-tones.png",
        "tags": ["earth", "natural", "organic", "terracotta"],
    },
    {
        "id": "forest",
        "name": "Forest Green",
        "category": "natural",
        "description": "Deep forest greens with natural textures",
        "colors": ["#228B22", "#2E8B57", "#6B8E23", "#3D2B1F"],
        "preview_image": "/styles/forest.png",
        "tags": ["forest", "green", "nature", "eco"],
    },
    {
        "id": "ocean",
        "name": "Ocean Breeze",
        "category": "natural",
        "description": "Calming blues inspired by the sea",
        "colors": ["#006994", "#40E0D0", "#87CEEB", "#FFFFFF"],
        "preview_image": "/styles/ocean.png",
        "tags": ["ocean", "blue", "calm", "water"],
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
