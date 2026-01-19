"""
Professional Design Framework
Captures what design teams think about when creating cohesive visual identities.
Each dimension can be combined to create unique but professional styles.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum
import random


class LayoutGrid(Enum):
    """How elements are positioned in the composition"""
    CENTERED = "centered"           # Symmetrical, formal, stable
    RULE_OF_THIRDS = "rule_of_thirds"  # Dynamic, professional
    GOLDEN_RATIO = "golden_ratio"   # Naturally pleasing proportions
    ASYMMETRIC = "asymmetric"       # Modern, edgy, dynamic
    MODULAR = "modular"             # Clean, organized, tech-feel


class ColorHarmony(Enum):
    """Color relationship strategy"""
    MONOCHROMATIC = "monochromatic"     # Single hue, varying saturation/brightness
    COMPLEMENTARY = "complementary"      # Opposite colors (high contrast)
    ANALOGOUS = "analogous"              # Adjacent colors (harmonious)
    TRIADIC = "triadic"                  # Three equidistant colors (vibrant)
    SPLIT_COMPLEMENTARY = "split_complementary"  # Softer than complementary


class ColorTemperature(Enum):
    """Warm vs cool color feeling"""
    WARM = "warm"           # Reds, oranges, yellows - energy, appetite, urgency
    COOL = "cool"           # Blues, greens, purples - trust, calm, professional
    NEUTRAL = "neutral"     # Grays, whites, blacks - sophisticated, timeless
    MIXED = "mixed"         # Warm accents on cool base or vice versa


class SaturationLevel(Enum):
    """How vivid the colors are"""
    MUTED = "muted"         # Sophisticated, elegant, understated
    BALANCED = "balanced"   # Professional, approachable
    VIBRANT = "vibrant"     # Exciting, youthful, attention-grabbing
    PASTEL = "pastel"       # Soft, gentle, feminine, baby products


class TypographyStyle(Enum):
    """Font personality"""
    MODERN_SANS = "modern_sans"         # Clean, minimal, tech
    ELEGANT_SERIF = "elegant_serif"     # Premium, traditional, luxury
    BOLD_DISPLAY = "bold_display"       # Impactful, confident, sports
    FRIENDLY_ROUNDED = "friendly_rounded"  # Approachable, fun, kids
    GEOMETRIC = "geometric"              # Contemporary, design-forward
    HANDWRITTEN = "handwritten"          # Personal, artisanal, organic


class ShadowStyle(Enum):
    """Depth and dimension approach"""
    FLAT = "flat"           # No shadows, modern, minimal
    SOFT = "soft"           # Subtle depth, professional
    DRAMATIC = "dramatic"   # Strong shadows, premium, moody
    LONG = "long"           # Extended shadows, retro, stylized
    FLOATING = "floating"   # Objects appear to hover, tech, modern


class BackgroundStyle(Enum):
    """What's behind the product"""
    PURE_WHITE = "pure_white"       # Clean, Amazon standard
    GRADIENT = "gradient"           # Modern, dynamic
    TEXTURE = "texture"             # Adds interest, craft/artisanal
    GEOMETRIC = "geometric"         # Shapes, patterns, tech
    ENVIRONMENTAL = "environmental"  # Lifestyle context
    COLOR_BLOCK = "color_block"     # Bold, graphic


class ShapeLanguage(Enum):
    """What kind of decorative shapes"""
    GEOMETRIC = "geometric"     # Circles, squares, triangles - tech, modern
    ORGANIC = "organic"         # Blobs, waves, natural curves - friendly, natural
    ANGULAR = "angular"         # Sharp edges, dynamic - sports, energy
    MINIMAL = "minimal"         # Almost no decoration - luxury, clean
    DECORATIVE = "decorative"   # Ornate, detailed - premium, artisanal


class IconStyle(Enum):
    """How icons and small graphics look"""
    LINE = "line"               # Outline only - minimal, modern
    FILLED = "filled"           # Solid shapes - bold, clear
    DUOTONE = "duotone"         # Two-color icons - trendy, tech
    ILLUSTRATED = "illustrated"  # Hand-drawn feel - friendly, artisanal
    NONE = "none"               # No icons, just type - luxury, minimal


class BadgeStyle(Enum):
    """How callouts and highlights appear"""
    RIBBON = "ribbon"           # Classic, promotional
    CIRCLE = "circle"           # Clean, modern
    STARBURST = "starburst"     # Attention-grabbing, value
    TAG = "tag"                 # E-commerce feel
    BANNER = "banner"           # Bold, promotional
    SUBTLE = "subtle"           # Underlined or minimal highlight
    NONE = "none"               # No badges


class LightingMood(Enum):
    """Photography lighting style"""
    HIGH_KEY = "high_key"       # Bright, airy, optimistic
    LOW_KEY = "low_key"         # Dramatic, moody, premium
    NATURAL = "natural"         # Soft, authentic, organic
    STUDIO = "studio"           # Professional, clean, commercial
    DRAMATIC = "dramatic"       # Strong contrasts, luxury


@dataclass
class DesignFramework:
    """
    Complete design system that captures all the technical details
    professional designers consider for a cohesive visual identity.
    """
    # Layout & Composition
    layout_grid: LayoutGrid = LayoutGrid.RULE_OF_THIRDS
    visual_hierarchy: str = "product_first"  # What draws attention
    balance: str = "asymmetric"  # symmetric, asymmetric
    whitespace: str = "generous"  # minimal, balanced, generous

    # Color System
    color_harmony: ColorHarmony = ColorHarmony.ANALOGOUS
    color_temperature: ColorTemperature = ColorTemperature.NEUTRAL
    saturation: SaturationLevel = SaturationLevel.BALANCED
    accent_ratio: str = "60-30-10"  # dominant-secondary-accent

    # Suggested color palette (hex codes)
    primary_color: str = "#2C3E50"
    secondary_color: str = "#ECF0F1"
    accent_color: str = "#3498DB"
    text_color: str = "#2C3E50"

    # Typography
    typography_style: TypographyStyle = TypographyStyle.MODERN_SANS
    type_scale: str = "modular"  # modular, linear
    letter_spacing: str = "normal"  # tight, normal, loose

    # Texture & Depth
    shadow_style: ShadowStyle = ShadowStyle.SOFT
    background_style: BackgroundStyle = BackgroundStyle.PURE_WHITE
    texture_intensity: str = "none"  # none, subtle, medium, strong

    # Decorative Elements
    shape_language: ShapeLanguage = ShapeLanguage.GEOMETRIC
    icon_style: IconStyle = IconStyle.LINE
    badge_style: BadgeStyle = BadgeStyle.CIRCLE

    # Photography
    lighting_mood: LightingMood = LightingMood.STUDIO

    # Overall Personality
    mood: str = "professional"
    energy: str = "calm"  # calm, moderate, energetic
    formality: str = "professional"  # casual, professional, formal

    def to_prompt_instructions(self) -> str:
        """Convert design framework to prompt instructions"""
        return f"""
[DESIGN FRAMEWORK - PROFESSIONAL SPECIFICATIONS]

LAYOUT & COMPOSITION:
- Grid System: {self.layout_grid.value} - position elements using this principle
- Visual Hierarchy: {self.visual_hierarchy} - this should draw the eye first
- Balance: {self.balance} composition
- Whitespace: {self.whitespace} - {"lots of breathing room" if self.whitespace == "generous" else "efficient use of space"}

COLOR SYSTEM:
- Harmony: {self.color_harmony.value} color scheme
- Temperature: {self.color_temperature.value} tones
- Saturation: {self.saturation.value} colors
- Primary Color: {self.primary_color} (dominant ~60%)
- Secondary Color: {self.secondary_color} (supporting ~30%)
- Accent Color: {self.accent_color} (highlights ~10%)

TYPOGRAPHY:
- Style: {self.typography_style.value} fonts
- Letter Spacing: {self.letter_spacing}
- Create clear type hierarchy with size and weight contrast

TEXTURE & DEPTH:
- Shadows: {self.shadow_style.value} style
- Background: {self.background_style.value}
- Texture: {self.texture_intensity} intensity

DECORATIVE ELEMENTS:
- Shapes: {self.shape_language.value} forms
- Icons: {self.icon_style.value} style
- Badges/Callouts: {self.badge_style.value} style

PHOTOGRAPHY & LIGHTING:
- Mood: {self.lighting_mood.value} lighting

OVERALL FEELING:
- Mood: {self.mood}
- Energy Level: {self.energy}
- Formality: {self.formality}
"""


# Predefined professional design frameworks
DESIGN_PRESETS: Dict[str, DesignFramework] = {
    "tech_minimal": DesignFramework(
        layout_grid=LayoutGrid.CENTERED,
        balance="symmetric",
        whitespace="generous",
        color_harmony=ColorHarmony.MONOCHROMATIC,
        color_temperature=ColorTemperature.COOL,
        saturation=SaturationLevel.MUTED,
        primary_color="#1A1A2E",
        secondary_color="#F5F5F7",
        accent_color="#0071E3",
        typography_style=TypographyStyle.MODERN_SANS,
        letter_spacing="tight",
        shadow_style=ShadowStyle.SOFT,
        background_style=BackgroundStyle.PURE_WHITE,
        shape_language=ShapeLanguage.MINIMAL,
        icon_style=IconStyle.LINE,
        badge_style=BadgeStyle.NONE,
        lighting_mood=LightingMood.HIGH_KEY,
        mood="sophisticated",
        energy="calm",
        formality="professional",
    ),

    "bold_energetic": DesignFramework(
        layout_grid=LayoutGrid.ASYMMETRIC,
        balance="asymmetric",
        whitespace="minimal",
        color_harmony=ColorHarmony.COMPLEMENTARY,
        color_temperature=ColorTemperature.WARM,
        saturation=SaturationLevel.VIBRANT,
        primary_color="#FF4500",
        secondary_color="#1A1A1A",
        accent_color="#FFD700",
        typography_style=TypographyStyle.BOLD_DISPLAY,
        letter_spacing="tight",
        shadow_style=ShadowStyle.DRAMATIC,
        background_style=BackgroundStyle.COLOR_BLOCK,
        shape_language=ShapeLanguage.ANGULAR,
        icon_style=IconStyle.FILLED,
        badge_style=BadgeStyle.STARBURST,
        lighting_mood=LightingMood.DRAMATIC,
        mood="exciting",
        energy="energetic",
        formality="casual",
    ),

    "luxury_elegant": DesignFramework(
        layout_grid=LayoutGrid.GOLDEN_RATIO,
        balance="symmetric",
        whitespace="generous",
        color_harmony=ColorHarmony.ANALOGOUS,
        color_temperature=ColorTemperature.NEUTRAL,
        saturation=SaturationLevel.MUTED,
        primary_color="#0D0D0D",
        secondary_color="#F8F5F0",
        accent_color="#C9A962",
        typography_style=TypographyStyle.ELEGANT_SERIF,
        letter_spacing="loose",
        shadow_style=ShadowStyle.DRAMATIC,
        background_style=BackgroundStyle.GRADIENT,
        shape_language=ShapeLanguage.MINIMAL,
        icon_style=IconStyle.NONE,
        badge_style=BadgeStyle.SUBTLE,
        lighting_mood=LightingMood.LOW_KEY,
        mood="luxurious",
        energy="calm",
        formality="formal",
    ),

    "natural_organic": DesignFramework(
        layout_grid=LayoutGrid.RULE_OF_THIRDS,
        balance="asymmetric",
        whitespace="balanced",
        color_harmony=ColorHarmony.ANALOGOUS,
        color_temperature=ColorTemperature.WARM,
        saturation=SaturationLevel.MUTED,
        primary_color="#2D5016",
        secondary_color="#F5F1E8",
        accent_color="#8B7355",
        typography_style=TypographyStyle.FRIENDLY_ROUNDED,
        letter_spacing="normal",
        shadow_style=ShadowStyle.SOFT,
        background_style=BackgroundStyle.TEXTURE,
        texture_intensity="subtle",
        shape_language=ShapeLanguage.ORGANIC,
        icon_style=IconStyle.ILLUSTRATED,
        badge_style=BadgeStyle.TAG,
        lighting_mood=LightingMood.NATURAL,
        mood="authentic",
        energy="calm",
        formality="casual",
    ),

    "playful_fun": DesignFramework(
        layout_grid=LayoutGrid.MODULAR,
        balance="asymmetric",
        whitespace="balanced",
        color_harmony=ColorHarmony.TRIADIC,
        color_temperature=ColorTemperature.MIXED,
        saturation=SaturationLevel.VIBRANT,
        primary_color="#FF6B6B",
        secondary_color="#4ECDC4",
        accent_color="#FFE66D",
        typography_style=TypographyStyle.FRIENDLY_ROUNDED,
        letter_spacing="normal",
        shadow_style=ShadowStyle.FLOATING,
        background_style=BackgroundStyle.GEOMETRIC,
        shape_language=ShapeLanguage.ORGANIC,
        icon_style=IconStyle.FILLED,
        badge_style=BadgeStyle.CIRCLE,
        lighting_mood=LightingMood.HIGH_KEY,
        mood="playful",
        energy="energetic",
        formality="casual",
    ),

    "clinical_trust": DesignFramework(
        layout_grid=LayoutGrid.CENTERED,
        balance="symmetric",
        whitespace="generous",
        color_harmony=ColorHarmony.ANALOGOUS,
        color_temperature=ColorTemperature.COOL,
        saturation=SaturationLevel.BALANCED,
        primary_color="#0077B6",
        secondary_color="#FFFFFF",
        accent_color="#00B4D8",
        typography_style=TypographyStyle.MODERN_SANS,
        letter_spacing="normal",
        shadow_style=ShadowStyle.SOFT,
        background_style=BackgroundStyle.PURE_WHITE,
        shape_language=ShapeLanguage.GEOMETRIC,
        icon_style=IconStyle.DUOTONE,
        badge_style=BadgeStyle.CIRCLE,
        lighting_mood=LightingMood.STUDIO,
        mood="trustworthy",
        energy="calm",
        formality="professional",
    ),
}


def generate_random_framework(
    seed_colors: Optional[List[str]] = None,
    mood_preference: Optional[str] = None,
) -> DesignFramework:
    """
    Generate a random but cohesive design framework.
    Professional designers would call this "generative design."

    Args:
        seed_colors: Brand colors to incorporate
        mood_preference: Desired mood (calm, energetic, premium, etc.)

    Returns:
        A complete, coherent design framework
    """
    # Define compatible combinations (design rules)
    mood_mappings = {
        "premium": {
            "saturation": [SaturationLevel.MUTED],
            "whitespace": ["generous"],
            "shadow_style": [ShadowStyle.SOFT, ShadowStyle.DRAMATIC],
            "badge_style": [BadgeStyle.SUBTLE, BadgeStyle.NONE],
            "energy": "calm",
            "formality": "formal",
        },
        "energetic": {
            "saturation": [SaturationLevel.VIBRANT],
            "whitespace": ["minimal", "balanced"],
            "shadow_style": [ShadowStyle.DRAMATIC, ShadowStyle.FLOATING],
            "badge_style": [BadgeStyle.STARBURST, BadgeStyle.RIBBON],
            "energy": "energetic",
            "formality": "casual",
        },
        "trustworthy": {
            "saturation": [SaturationLevel.BALANCED],
            "color_temperature": [ColorTemperature.COOL],
            "whitespace": ["generous", "balanced"],
            "shadow_style": [ShadowStyle.SOFT],
            "energy": "calm",
            "formality": "professional",
        },
        "natural": {
            "saturation": [SaturationLevel.MUTED, SaturationLevel.BALANCED],
            "color_temperature": [ColorTemperature.WARM],
            "background_style": [BackgroundStyle.TEXTURE, BackgroundStyle.ENVIRONMENTAL],
            "shape_language": [ShapeLanguage.ORGANIC],
            "energy": "calm",
            "formality": "casual",
        },
        "playful": {
            "saturation": [SaturationLevel.VIBRANT, SaturationLevel.PASTEL],
            "color_harmony": [ColorHarmony.TRIADIC, ColorHarmony.COMPLEMENTARY],
            "shape_language": [ShapeLanguage.ORGANIC, ShapeLanguage.GEOMETRIC],
            "icon_style": [IconStyle.FILLED, IconStyle.ILLUSTRATED],
            "energy": "energetic",
            "formality": "casual",
        },
    }

    # Start with random choices
    framework = DesignFramework(
        layout_grid=random.choice(list(LayoutGrid)),
        color_harmony=random.choice(list(ColorHarmony)),
        color_temperature=random.choice(list(ColorTemperature)),
        saturation=random.choice(list(SaturationLevel)),
        typography_style=random.choice(list(TypographyStyle)),
        shadow_style=random.choice(list(ShadowStyle)),
        background_style=random.choice(list(BackgroundStyle)),
        shape_language=random.choice(list(ShapeLanguage)),
        icon_style=random.choice(list(IconStyle)),
        badge_style=random.choice(list(BadgeStyle)),
        lighting_mood=random.choice(list(LightingMood)),
        balance=random.choice(["symmetric", "asymmetric"]),
        whitespace=random.choice(["minimal", "balanced", "generous"]),
        letter_spacing=random.choice(["tight", "normal", "loose"]),
    )

    # Apply mood constraints if specified
    if mood_preference and mood_preference in mood_mappings:
        rules = mood_mappings[mood_preference]
        if "saturation" in rules:
            framework.saturation = random.choice(rules["saturation"])
        if "color_temperature" in rules:
            framework.color_temperature = random.choice(rules["color_temperature"])
        if "whitespace" in rules:
            framework.whitespace = random.choice(rules["whitespace"])
        if "shadow_style" in rules:
            framework.shadow_style = random.choice(rules["shadow_style"])
        if "background_style" in rules:
            framework.background_style = random.choice(rules["background_style"])
        if "shape_language" in rules:
            framework.shape_language = random.choice(rules["shape_language"])
        if "badge_style" in rules:
            framework.badge_style = random.choice(rules["badge_style"])
        if "icon_style" in rules:
            framework.icon_style = random.choice(rules["icon_style"])
        if "color_harmony" in rules:
            framework.color_harmony = random.choice(rules["color_harmony"])
        if "energy" in rules:
            framework.energy = rules["energy"]
        if "formality" in rules:
            framework.formality = rules["formality"]
        framework.mood = mood_preference

    # Incorporate seed colors if provided
    if seed_colors and len(seed_colors) > 0:
        framework.primary_color = seed_colors[0]
        if len(seed_colors) > 1:
            framework.accent_color = seed_colors[1]
        if len(seed_colors) > 2:
            framework.secondary_color = seed_colors[2]

    return framework


def get_design_preset(preset_id: str) -> Optional[DesignFramework]:
    """Get a predefined design framework"""
    return DESIGN_PRESETS.get(preset_id)


def get_all_presets() -> List[Dict]:
    """Get all preset frameworks for API response"""
    return [
        {
            "id": preset_id,
            "name": preset_id.replace("_", " ").title(),
            "mood": framework.mood,
            "energy": framework.energy,
            "primary_color": framework.primary_color,
            "accent_color": framework.accent_color,
            "description": f"{framework.mood.title()}, {framework.energy} energy with {framework.typography_style.value} typography",
        }
        for preset_id, framework in DESIGN_PRESETS.items()
    ]
