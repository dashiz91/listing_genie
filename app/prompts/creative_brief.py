"""
MASTER Level Creative Brief Generator

Generates complete, professional creative briefs for Amazon listing image sets.
Each listing is a 5-image STORY with narrative arc, exact specifications,
copy strategy, and Amazon-specific intelligence.

Philosophy:
- 5 images = 1 narrative (Hook → Reveal → Proof → Dream → Close)
- Exact specifications, not vague labels
- Copy that builds with consistent voice
- Visual rhythm (punch, rest, info, feel, resolve)
- Amazon-specific intelligence (thumbnails, mobile-first)
- Micro-consistency (shadows, typography, spacing)
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple
from enum import Enum
import colorsys


class BrandVibe(Enum):
    """Core brand personality - drives all design decisions"""
    PREMIUM_LUXURY = "premium_luxury"      # Elegant, exclusive, aspirational
    CLEAN_MODERN = "clean_modern"          # Minimal, tech, sophisticated
    BOLD_ENERGETIC = "bold_energetic"      # Dynamic, confident, action
    NATURAL_ORGANIC = "natural_organic"    # Earthy, authentic, wholesome
    PLAYFUL_FUN = "playful_fun"           # Vibrant, youthful, joyful
    CLINICAL_TRUST = "clinical_trust"      # Professional, scientific, reliable


class ImageChapter(Enum):
    """Story arc chapter for each image"""
    HOOK = "hook"           # Image 1: Main - Grab attention, hero shot
    REVEAL = "reveal"       # Image 2: Hero - Introduce the product story
    PROOF = "proof"         # Image 3: Infographic - Features & benefits
    DREAM = "dream"         # Image 4: Lifestyle - Aspirational usage
    CLOSE = "close"         # Image 5: Comparison/Trust - Final persuasion


class VisualEnergy(Enum):
    """Energy level for visual rhythm across the set"""
    PUNCH = "punch"     # High impact, attention-grabbing
    REST = "rest"       # Calm, breathing room
    INFO = "info"       # Structured, educational
    FEEL = "feel"       # Emotional, aspirational
    RESOLVE = "resolve" # Confident, conclusive


@dataclass
class Typography:
    """Exact typography specifications"""
    headline_font: str          # e.g., "Montserrat Bold"
    headline_size: str          # e.g., "48px" or "large"
    headline_weight: str        # e.g., "700"
    subhead_font: str           # e.g., "Montserrat Regular"
    subhead_size: str           # e.g., "24px" or "medium"
    subhead_weight: str         # e.g., "400"
    body_font: str              # e.g., "Inter Regular"
    body_size: str              # e.g., "16px" or "small"
    letter_spacing: str         # e.g., "0.5px" or "normal"
    line_height: str            # e.g., "1.4"


@dataclass
class ColorPalette:
    """Exact color specifications with roles"""
    primary: str                # Dominant color (60%) - hex
    secondary: str              # Supporting color (30%) - hex
    accent: str                 # Highlight color (10%) - hex
    text_dark: str              # Dark text color - hex
    text_light: str             # Light text color - hex
    background: str             # Default background - hex
    gradient_from: Optional[str] = None  # Gradient start
    gradient_to: Optional[str] = None    # Gradient end
    gradient_direction: str = "top to bottom"


@dataclass
class ShadowSpec:
    """Exact shadow specifications for consistency"""
    enabled: bool = True
    x_offset: str = "0px"
    y_offset: str = "4px"
    blur: str = "12px"
    spread: str = "0px"
    color: str = "rgba(0,0,0,0.1)"
    direction: str = "bottom-right"  # Where light comes from


@dataclass
class SpacingSystem:
    """Consistent spacing ratios"""
    base_unit: str = "8px"
    content_padding: str = "40px"
    element_gap: str = "24px"
    section_gap: str = "48px"
    margin_ratio: str = "60-30-10"  # Primary-Secondary-Accent distribution


@dataclass
class CopyBlock:
    """Copy specifications for an image"""
    headline: str               # Main headline
    subhead: Optional[str] = None       # Optional subheadline
    body_copy: Optional[str] = None     # Optional body text
    cta: Optional[str] = None           # Call to action
    feature_callouts: List[str] = field(default_factory=list)  # Feature highlights


@dataclass
class LayoutSpec:
    """Layout specifications for an image"""
    composition: str            # e.g., "centered", "rule-of-thirds", "golden-ratio"
    product_position: str       # e.g., "center", "left-third", "right-60%"
    product_size: str           # e.g., "hero (60% of frame)", "supporting (30%)"
    text_position: str          # e.g., "top-left", "bottom-center", "right-side"
    whitespace: str             # e.g., "generous (40%)", "balanced (25%)", "minimal (15%)"
    visual_flow: str            # e.g., "Z-pattern", "F-pattern", "center-out"


@dataclass
class ImageBrief:
    """Complete creative brief for a single image"""
    # Identity
    image_type: str             # main, infographic_1, infographic_2, lifestyle, comparison
    chapter: ImageChapter       # Story arc position
    energy: VisualEnergy        # Visual rhythm role

    # The Brief
    creative_direction: str     # 2-3 sentence creative vision
    layout: LayoutSpec          # Layout specifications
    copy: CopyBlock             # All copy for this image

    # Visual Specs
    background_treatment: str   # e.g., "pure white", "lilac gradient #BDAEC9 to white"
    lighting_direction: str     # e.g., "soft from top-left", "dramatic side lighting"
    mood_keywords: List[str]    # 3-5 mood descriptors

    # Amazon-Specific
    thumbnail_focus: str        # What must be visible at 100px
    mobile_priority: str        # What's most important on mobile

    # Technical
    file_notes: str             # e.g., "1500x1500px, RGB, white background required"


@dataclass
class ListingBrief:
    """Complete creative brief for entire 5-image listing"""
    # Brand Context
    product_name: str
    brand_name: Optional[str]
    vibe: BrandVibe

    # Design System
    colors: ColorPalette
    typography: Typography
    shadows: ShadowSpec
    spacing: SpacingSystem

    # Story Arc
    story_theme: str            # The narrative thread connecting all images
    brand_voice: str            # Copy personality description

    # Individual Briefs
    briefs: Dict[str, ImageBrief]  # image_type -> brief

    # Cohesion Rules
    cohesion_elements: List[str]   # What MUST stay consistent
    forbidden_elements: List[str]  # What NEVER to include


class CreativeBriefGenerator:
    """
    Generates MASTER level creative briefs for Amazon listing image sets.
    """

    # Typography mappings for each vibe
    VIBE_TYPOGRAPHY: Dict[BrandVibe, Typography] = {
        BrandVibe.PREMIUM_LUXURY: Typography(
            headline_font="Playfair Display",
            headline_size="56px",
            headline_weight="600",
            subhead_font="Montserrat",
            subhead_size="20px",
            subhead_weight="300",
            body_font="Montserrat",
            body_size="14px",
            letter_spacing="1px",
            line_height="1.6",
        ),
        BrandVibe.CLEAN_MODERN: Typography(
            headline_font="Inter",
            headline_size="48px",
            headline_weight="600",
            subhead_font="Inter",
            subhead_size="18px",
            subhead_weight="400",
            body_font="Inter",
            body_size="14px",
            letter_spacing="0px",
            line_height="1.5",
        ),
        BrandVibe.BOLD_ENERGETIC: Typography(
            headline_font="Oswald",
            headline_size="64px",
            headline_weight="700",
            subhead_font="Roboto Condensed",
            subhead_size="24px",
            subhead_weight="500",
            body_font="Roboto",
            body_size="16px",
            letter_spacing="-0.5px",
            line_height="1.3",
        ),
        BrandVibe.NATURAL_ORGANIC: Typography(
            headline_font="Quicksand",
            headline_size="44px",
            headline_weight="600",
            subhead_font="Open Sans",
            subhead_size="18px",
            subhead_weight="400",
            body_font="Open Sans",
            body_size="14px",
            letter_spacing="0.5px",
            line_height="1.6",
        ),
        BrandVibe.PLAYFUL_FUN: Typography(
            headline_font="Poppins",
            headline_size="52px",
            headline_weight="700",
            subhead_font="Nunito",
            subhead_size="22px",
            subhead_weight="500",
            body_font="Nunito",
            body_size="16px",
            letter_spacing="0px",
            line_height="1.5",
        ),
        BrandVibe.CLINICAL_TRUST: Typography(
            headline_font="Source Sans Pro",
            headline_size="42px",
            headline_weight="600",
            subhead_font="Source Sans Pro",
            subhead_size="18px",
            subhead_weight="400",
            body_font="Source Sans Pro",
            body_size="14px",
            letter_spacing="0px",
            line_height="1.5",
        ),
    }

    # Shadow mappings for each vibe
    VIBE_SHADOWS: Dict[BrandVibe, ShadowSpec] = {
        BrandVibe.PREMIUM_LUXURY: ShadowSpec(
            enabled=True,
            x_offset="0px",
            y_offset="8px",
            blur="24px",
            spread="-4px",
            color="rgba(0,0,0,0.15)",
            direction="bottom",
        ),
        BrandVibe.CLEAN_MODERN: ShadowSpec(
            enabled=True,
            x_offset="0px",
            y_offset="4px",
            blur="16px",
            spread="0px",
            color="rgba(0,0,0,0.08)",
            direction="bottom",
        ),
        BrandVibe.BOLD_ENERGETIC: ShadowSpec(
            enabled=True,
            x_offset="4px",
            y_offset="8px",
            blur="0px",
            spread="0px",
            color="rgba(0,0,0,0.3)",
            direction="bottom-right",
        ),
        BrandVibe.NATURAL_ORGANIC: ShadowSpec(
            enabled=True,
            x_offset="0px",
            y_offset="6px",
            blur="20px",
            spread="0px",
            color="rgba(0,0,0,0.1)",
            direction="bottom",
        ),
        BrandVibe.PLAYFUL_FUN: ShadowSpec(
            enabled=True,
            x_offset="0px",
            y_offset="6px",
            blur="12px",
            spread="0px",
            color="rgba(0,0,0,0.12)",
            direction="bottom",
        ),
        BrandVibe.CLINICAL_TRUST: ShadowSpec(
            enabled=True,
            x_offset="0px",
            y_offset="2px",
            blur="8px",
            spread="0px",
            color="rgba(0,0,0,0.06)",
            direction="bottom",
        ),
    }

    # Brand voice descriptions
    VIBE_VOICES: Dict[BrandVibe, str] = {
        BrandVibe.PREMIUM_LUXURY: "Sophisticated, understated confidence. Speaks in refined, elegant language. Never shouty or desperate. Quality is assumed, not proclaimed.",
        BrandVibe.CLEAN_MODERN: "Crisp, clear, and intelligent. Direct without being cold. Facts over fluff. Respects the reader's time and intelligence.",
        BrandVibe.BOLD_ENERGETIC: "Confident and dynamic. Action-oriented language. Short, punchy statements. Excites and motivates. Energy in every word.",
        BrandVibe.NATURAL_ORGANIC: "Warm, genuine, and approachable. Conversational tone. Honest and transparent. Like advice from a trusted friend.",
        BrandVibe.PLAYFUL_FUN: "Joyful and lighthearted. Uses wordplay and charm. Never boring. Makes you smile. Approachable and memorable.",
        BrandVibe.CLINICAL_TRUST: "Authoritative yet accessible. Evidence-based messaging. Professional but not cold. Builds trust through expertise.",
    }

    # Story theme templates
    VIBE_STORY_THEMES: Dict[BrandVibe, str] = {
        BrandVibe.PREMIUM_LUXURY: "A journey of refined taste - from first impression to everyday elegance",
        BrandVibe.CLEAN_MODERN: "Simplicity meets performance - discover what thoughtful design delivers",
        BrandVibe.BOLD_ENERGETIC: "Unleash your potential - power through to your best self",
        BrandVibe.NATURAL_ORGANIC: "Nature's wisdom, your wellness - from earth to your everyday",
        BrandVibe.PLAYFUL_FUN: "Joy in the details - add a little magic to your routine",
        BrandVibe.CLINICAL_TRUST: "Science-backed solutions - trust in proven results",
    }

    def __init__(self):
        pass

    def generate_palette_from_primary(
        self,
        primary_hex: str,
        vibe: BrandVibe
    ) -> ColorPalette:
        """
        Generate a complete color palette from a primary color.
        Uses color theory and vibe-appropriate harmony.
        """
        # Parse primary color
        primary = primary_hex.lstrip('#')
        r, g, b = int(primary[0:2], 16), int(primary[2:4], 16), int(primary[4:6], 16)
        h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)

        # Generate colors based on vibe
        if vibe == BrandVibe.PREMIUM_LUXURY:
            # Muted, sophisticated palette
            secondary = self._adjust_color(h, l, s, hue_shift=0, lightness=0.95, saturation=0.1)
            accent = self._hex_from_hls(h, 0.5, s * 0.8)  # Darker, muted accent
            text_dark = "#1A1A1A"
            text_light = "#F8F5F0"
            background = "#FFFFFF"
            gradient_from = primary_hex
            gradient_to = "#FFFFFF"

        elif vibe == BrandVibe.BOLD_ENERGETIC:
            # High contrast, vibrant
            secondary = "#1A1A1A"
            # Complementary accent
            accent = self._hex_from_hls((h + 0.5) % 1.0, l, min(s * 1.2, 1.0))
            text_dark = "#FFFFFF"
            text_light = "#FFFFFF"
            background = primary_hex
            gradient_from = primary_hex
            gradient_to = self._hex_from_hls((h + 0.1) % 1.0, l, s)

        elif vibe == BrandVibe.NATURAL_ORGANIC:
            # Earthy, warm tones
            secondary = self._adjust_color(h, l, s, hue_shift=0, lightness=0.92, saturation=0.15)
            accent = self._hex_from_hls((h + 0.08) % 1.0, 0.35, s * 0.6)  # Earthy brown
            text_dark = "#2D2D2D"
            text_light = "#F5F1E8"
            background = "#FEFDFB"
            gradient_from = None
            gradient_to = None

        elif vibe == BrandVibe.PLAYFUL_FUN:
            # Vibrant, multi-color
            secondary = self._hex_from_hls((h + 0.33) % 1.0, l, s)  # Triadic
            accent = self._hex_from_hls((h + 0.66) % 1.0, l, s)  # Triadic
            text_dark = "#2D2D2D"
            text_light = "#FFFFFF"
            background = "#FFFFFF"
            gradient_from = primary_hex
            gradient_to = secondary

        elif vibe == BrandVibe.CLINICAL_TRUST:
            # Cool, professional
            secondary = "#FFFFFF"
            accent = self._hex_from_hls(h, l * 0.7, s)  # Darker version
            text_dark = "#1A365D"
            text_light = "#FFFFFF"
            background = "#FFFFFF"
            gradient_from = None
            gradient_to = None

        else:  # CLEAN_MODERN
            # Minimal, balanced
            secondary = "#F5F5F7"
            accent = primary_hex
            text_dark = "#1A1A2E"
            text_light = "#FFFFFF"
            background = "#FFFFFF"
            gradient_from = None
            gradient_to = None

        return ColorPalette(
            primary=primary_hex,
            secondary=secondary,
            accent=accent,
            text_dark=text_dark,
            text_light=text_light,
            background=background,
            gradient_from=gradient_from,
            gradient_to=gradient_to,
            gradient_direction="top to bottom" if gradient_from else "",
        )

    def _adjust_color(
        self, h: float, l: float, s: float,
        hue_shift: float = 0, lightness: float = None, saturation: float = None
    ) -> str:
        """Adjust a color in HLS space and return hex"""
        new_h = (h + hue_shift) % 1.0
        new_l = lightness if lightness is not None else l
        new_s = saturation if saturation is not None else s
        return self._hex_from_hls(new_h, new_l, new_s)

    def _hex_from_hls(self, h: float, l: float, s: float) -> str:
        """Convert HLS to hex color"""
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

    def generate_copy_for_image(
        self,
        image_type: str,
        chapter: ImageChapter,
        product_name: str,
        features: List[str],
        vibe: BrandVibe,
        brand_name: Optional[str] = None,
    ) -> CopyBlock:
        """
        Generate copy for a specific image based on its chapter role.
        """
        # Short product name for headlines
        short_name = product_name.split('-')[0].strip() if '-' in product_name else product_name
        if len(short_name) > 30:
            short_name = short_name[:30].rsplit(' ', 1)[0]

        # Feature extraction
        main_feature = features[0] if features else "Premium Quality"
        feature_2 = features[1] if len(features) > 1 else ""
        feature_3 = features[2] if len(features) > 2 else ""

        voice = self.VIBE_VOICES[vibe]

        if chapter == ImageChapter.HOOK:
            # Main image - minimal or no text (Amazon requirement)
            return CopyBlock(
                headline="",  # Main image should be clean
                subhead=None,
                body_copy=None,
                cta=None,
                feature_callouts=[],
            )

        elif chapter == ImageChapter.REVEAL:
            # Hero image - introduce the story
            headlines = {
                BrandVibe.PREMIUM_LUXURY: f"Introducing {short_name}",
                BrandVibe.CLEAN_MODERN: f"Meet {short_name}",
                BrandVibe.BOLD_ENERGETIC: f"This Changes Everything",
                BrandVibe.NATURAL_ORGANIC: f"Nature's Best, In Your Hands",
                BrandVibe.PLAYFUL_FUN: f"Say Hello to Your New Favorite",
                BrandVibe.CLINICAL_TRUST: f"The Science of {short_name}",
            }
            return CopyBlock(
                headline=headlines.get(vibe, f"Discover {short_name}"),
                subhead=main_feature,
                body_copy=None,
                cta=None,
                feature_callouts=[],
            )

        elif chapter == ImageChapter.PROOF:
            # Infographic - features and benefits
            callouts = [f for f in [main_feature, feature_2, feature_3] if f]
            headlines = {
                BrandVibe.PREMIUM_LUXURY: "Crafted for Excellence",
                BrandVibe.CLEAN_MODERN: "What Makes It Different",
                BrandVibe.BOLD_ENERGETIC: "Built to Perform",
                BrandVibe.NATURAL_ORGANIC: "Pure Ingredients, Real Results",
                BrandVibe.PLAYFUL_FUN: "The Good Stuff Inside",
                BrandVibe.CLINICAL_TRUST: "Proven Benefits",
            }
            return CopyBlock(
                headline=headlines.get(vibe, "Key Features"),
                subhead=None,
                body_copy=None,
                cta=None,
                feature_callouts=callouts,
            )

        elif chapter == ImageChapter.DREAM:
            # Lifestyle - aspirational
            headlines = {
                BrandVibe.PREMIUM_LUXURY: "Elevate Your Everyday",
                BrandVibe.CLEAN_MODERN: "Designed for Your Life",
                BrandVibe.BOLD_ENERGETIC: "Unleash Your Potential",
                BrandVibe.NATURAL_ORGANIC: "Live Well, Naturally",
                BrandVibe.PLAYFUL_FUN: "Add Joy to Every Day",
                BrandVibe.CLINICAL_TRUST: "Results You Can Trust",
            }
            return CopyBlock(
                headline=headlines.get(vibe, "Your Best Life"),
                subhead=None,
                body_copy=None,
                cta=None,
                feature_callouts=[],
            )

        else:  # CLOSE
            # Comparison/Trust - final persuasion
            brand_line = brand_name if brand_name else short_name
            headlines = {
                BrandVibe.PREMIUM_LUXURY: f"The {brand_line} Difference",
                BrandVibe.CLEAN_MODERN: "Why Choose Us",
                BrandVibe.BOLD_ENERGETIC: "Don't Settle for Less",
                BrandVibe.NATURAL_ORGANIC: "Honest Quality You Can Trust",
                BrandVibe.PLAYFUL_FUN: "Join the Fun",
                BrandVibe.CLINICAL_TRUST: "The Smart Choice",
            }
            return CopyBlock(
                headline=headlines.get(vibe, "Why Choose Us"),
                subhead=None,
                body_copy=None,
                cta="Order Now" if vibe == BrandVibe.BOLD_ENERGETIC else None,
                feature_callouts=[],
            )

    def generate_layout_for_image(
        self,
        image_type: str,
        chapter: ImageChapter,
        energy: VisualEnergy,
        vibe: BrandVibe,
    ) -> LayoutSpec:
        """Generate layout specifications for an image"""

        if chapter == ImageChapter.HOOK:
            # Main image - product hero, clean
            return LayoutSpec(
                composition="centered" if vibe in [BrandVibe.PREMIUM_LUXURY, BrandVibe.CLEAN_MODERN] else "rule-of-thirds",
                product_position="center, filling 70-80% of frame",
                product_size="hero (dominant)",
                text_position="none (clean main image)",
                whitespace="generous (pure white background required by Amazon)",
                visual_flow="center focus",
            )

        elif chapter == ImageChapter.REVEAL:
            # Hero with copy
            return LayoutSpec(
                composition="golden-ratio" if vibe == BrandVibe.PREMIUM_LUXURY else "asymmetric",
                product_position="left-40% or right-40%",
                product_size="large (50-60% of frame)",
                text_position="opposite side from product",
                whitespace="balanced (30%)",
                visual_flow="product to headline to subhead",
            )

        elif chapter == ImageChapter.PROOF:
            # Infographic - structured
            return LayoutSpec(
                composition="modular grid",
                product_position="center or top",
                product_size="medium (30-40%)",
                text_position="around product in clear zones",
                whitespace="minimal but organized (20%)",
                visual_flow="top to bottom or radial from product",
            )

        elif chapter == ImageChapter.DREAM:
            # Lifestyle - environmental
            return LayoutSpec(
                composition="rule-of-thirds",
                product_position="integrated into scene, one-third",
                product_size="medium (30-40%), in context",
                text_position="corner overlay or bottom",
                whitespace="scene-dependent",
                visual_flow="scene first, then product, then text",
            )

        else:  # CLOSE
            # Comparison - side-by-side or trust badges
            return LayoutSpec(
                composition="split or centered grid",
                product_position="center with trust elements around",
                product_size="medium (40%)",
                text_position="top and bottom",
                whitespace="balanced (25%)",
                visual_flow="headline to product to proof points",
            )

    def generate_brief(
        self,
        product_name: str,
        features: List[str],
        vibe: BrandVibe,
        primary_color: str = "#2196F3",
        brand_name: Optional[str] = None,
        user_colors: Optional[List[str]] = None,
    ) -> ListingBrief:
        """
        Generate a complete creative brief for a 5-image Amazon listing.

        Args:
            product_name: Full product title
            features: List of key features (up to 3)
            vibe: Brand personality/vibe
            primary_color: Primary brand color (hex)
            brand_name: Optional brand name
            user_colors: Optional user-provided color palette

        Returns:
            Complete ListingBrief with all 5 image briefs
        """
        # Generate color palette
        if user_colors and len(user_colors) >= 2:
            colors = ColorPalette(
                primary=user_colors[0],
                secondary=user_colors[1] if len(user_colors) > 1 else "#F5F5F7",
                accent=user_colors[2] if len(user_colors) > 2 else user_colors[0],
                text_dark="#1A1A1A",
                text_light="#FFFFFF",
                background="#FFFFFF",
                gradient_from=user_colors[0],
                gradient_to=user_colors[1] if len(user_colors) > 1 else "#FFFFFF",
            )
        else:
            colors = self.generate_palette_from_primary(primary_color, vibe)

        # Get vibe-specific settings
        typography = self.VIBE_TYPOGRAPHY[vibe]
        shadows = self.VIBE_SHADOWS[vibe]
        voice = self.VIBE_VOICES[vibe]
        story_theme = self.VIBE_STORY_THEMES[vibe]

        # Image type to chapter/energy mapping
        image_chapters = {
            'main': (ImageChapter.HOOK, VisualEnergy.PUNCH),
            'infographic_1': (ImageChapter.REVEAL, VisualEnergy.REST),
            'infographic_2': (ImageChapter.PROOF, VisualEnergy.INFO),
            'lifestyle': (ImageChapter.DREAM, VisualEnergy.FEEL),
            'comparison': (ImageChapter.CLOSE, VisualEnergy.RESOLVE),
        }

        # Generate individual image briefs
        briefs: Dict[str, ImageBrief] = {}

        for image_type, (chapter, energy) in image_chapters.items():
            copy = self.generate_copy_for_image(
                image_type, chapter, product_name, features, vibe, brand_name
            )
            layout = self.generate_layout_for_image(image_type, chapter, energy, vibe)

            # Background treatment based on image type and vibe
            if image_type == 'main':
                background = "Pure white (#FFFFFF) - Amazon requirement"
            elif colors.gradient_from and colors.gradient_to:
                background = f"Gradient: {colors.gradient_from} to {colors.gradient_to}, {colors.gradient_direction}"
            else:
                background = f"Solid: {colors.background}"

            # Mood keywords based on vibe
            mood_map = {
                BrandVibe.PREMIUM_LUXURY: ["elegant", "refined", "exclusive", "sophisticated", "aspirational"],
                BrandVibe.CLEAN_MODERN: ["crisp", "minimal", "smart", "efficient", "sleek"],
                BrandVibe.BOLD_ENERGETIC: ["dynamic", "powerful", "confident", "action", "impact"],
                BrandVibe.NATURAL_ORGANIC: ["authentic", "warm", "honest", "earthy", "wholesome"],
                BrandVibe.PLAYFUL_FUN: ["joyful", "bright", "friendly", "cheerful", "vibrant"],
                BrandVibe.CLINICAL_TRUST: ["professional", "reliable", "scientific", "proven", "trustworthy"],
            }

            briefs[image_type] = ImageBrief(
                image_type=image_type,
                chapter=chapter,
                energy=energy,
                creative_direction=self._get_creative_direction(image_type, chapter, vibe, product_name),
                layout=layout,
                copy=copy,
                background_treatment=background,
                lighting_direction=self._get_lighting(vibe, chapter),
                mood_keywords=mood_map.get(vibe, ["professional", "quality"]),
                thumbnail_focus=self._get_thumbnail_focus(image_type, chapter),
                mobile_priority=self._get_mobile_priority(image_type, chapter),
                file_notes="1500x1500px minimum, RGB color, sRGB color profile",
            )

        # Cohesion elements
        cohesion = [
            f"Color palette: {colors.primary}, {colors.secondary}, {colors.accent}",
            f"Typography: {typography.headline_font} for headlines, {typography.body_font} for body",
            f"Shadow style: {shadows.y_offset} offset, {shadows.blur} blur, {shadows.direction} direction",
            f"Mood: Consistent {vibe.value.replace('_', ' ')} feeling throughout",
            "Visual rhythm: PUNCH → REST → INFO → FEEL → RESOLVE",
        ]

        # Forbidden elements based on vibe
        forbidden_map = {
            BrandVibe.PREMIUM_LUXURY: ["bright saturated colors", "casual fonts", "clipart", "busy patterns", "exclamation marks"],
            BrandVibe.CLEAN_MODERN: ["decorative fonts", "heavy textures", "ornate elements", "warm filters"],
            BrandVibe.BOLD_ENERGETIC: ["muted colors", "thin fonts", "excessive whitespace", "passive language"],
            BrandVibe.NATURAL_ORGANIC: ["neon colors", "geometric patterns", "artificial lighting", "tech aesthetic"],
            BrandVibe.PLAYFUL_FUN: ["dark moody colors", "corporate fonts", "formal language", "minimal designs"],
            BrandVibe.CLINICAL_TRUST: ["playful fonts", "bright colors", "casual language", "artistic abstraction"],
        }

        return ListingBrief(
            product_name=product_name,
            brand_name=brand_name,
            vibe=vibe,
            colors=colors,
            typography=typography,
            shadows=shadows,
            spacing=SpacingSystem(),
            story_theme=story_theme,
            brand_voice=voice,
            briefs=briefs,
            cohesion_elements=cohesion,
            forbidden_elements=forbidden_map.get(vibe, []),
        )

    def _get_creative_direction(
        self,
        image_type: str,
        chapter: ImageChapter,
        vibe: BrandVibe,
        product_name: str
    ) -> str:
        """Get 2-3 sentence creative direction for an image"""

        directions = {
            ImageChapter.HOOK: f"Hero product shot that stops the scroll. The {product_name} takes center stage on pure white, commanding attention through perfect lighting and composition. This is the first impression - make it count.",
            ImageChapter.REVEAL: f"Introduce the story. The product is presented with its key message, creating an emotional connection. Balance product visibility with compelling typography that speaks to the customer's aspirations.",
            ImageChapter.PROOF: f"Educate and convince. Structure key features and benefits in a clear, scannable format. Use icons, callouts, and visual hierarchy to make information digestible. The customer should quickly understand what makes this product special.",
            ImageChapter.DREAM: f"Show the product in its natural habitat. Create an aspirational scene where the customer can see themselves using the product. Lifestyle context that reinforces the brand promise and emotional benefit.",
            ImageChapter.CLOSE: f"Final persuasion. Reinforce trust through comparison, testimonials, or quality signals. Address any remaining hesitations. Make the purchase decision feel like the obvious choice.",
        }

        return directions.get(chapter, "Create a compelling product image.")

    def _get_lighting(self, vibe: BrandVibe, chapter: ImageChapter) -> str:
        """Get lighting direction based on vibe and chapter"""

        base_lighting = {
            BrandVibe.PREMIUM_LUXURY: "Dramatic side lighting with rich shadows",
            BrandVibe.CLEAN_MODERN: "Even, diffused lighting with soft shadows",
            BrandVibe.BOLD_ENERGETIC: "High contrast lighting with dynamic shadows",
            BrandVibe.NATURAL_ORGANIC: "Warm, natural light as if near a window",
            BrandVibe.PLAYFUL_FUN: "Bright, even lighting with minimal shadows",
            BrandVibe.CLINICAL_TRUST: "Clean, professional studio lighting",
        }

        # Main image needs consistent studio lighting
        if chapter == ImageChapter.HOOK:
            return "Professional studio lighting, soft from top-left, pure white background"

        return base_lighting.get(vibe, "Balanced studio lighting")

    def _get_thumbnail_focus(self, image_type: str, chapter: ImageChapter) -> str:
        """What must be visible at 100px thumbnail size"""

        focus = {
            ImageChapter.HOOK: "Product clearly recognizable, shape and colors distinct",
            ImageChapter.REVEAL: "Product visible, headline readable or clear visual hook",
            ImageChapter.PROOF: "Product visible, sense of 'information' without needing to read",
            ImageChapter.DREAM: "Lifestyle scene recognizable, product identifiable",
            ImageChapter.CLOSE: "Trust signals visible (badges, comparison format clear)",
        }

        return focus.get(chapter, "Product clearly visible")

    def _get_mobile_priority(self, image_type: str, chapter: ImageChapter) -> str:
        """What's most important for 70%+ mobile shoppers"""

        priority = {
            ImageChapter.HOOK: "Product fills frame, details visible without zooming",
            ImageChapter.REVEAL: "Headline large enough to read, product prominent",
            ImageChapter.PROOF: "Features scannable, icons clear, minimal text blocks",
            ImageChapter.DREAM: "Scene composition works in square format, product not lost",
            ImageChapter.CLOSE: "Key trust element immediately visible, easy to tap",
        }

        return priority.get(chapter, "Content readable without zooming")

    def to_prompt(self, brief: ImageBrief, listing_brief: ListingBrief) -> str:
        """
        Convert an ImageBrief to a complete prompt for the AI image generator.

        This is where the MASTER level detail becomes actual generation instructions.
        """
        sections = []

        # 1. Creative Brief Header
        sections.append(f"""[CREATIVE BRIEF: {brief.image_type.upper()}]
Chapter: {brief.chapter.value.upper()} (Image {['main', 'infographic_1', 'infographic_2', 'lifestyle', 'comparison'].index(brief.image_type) + 1} of 5)
Energy: {brief.energy.value.upper()}
Mood: {', '.join(brief.mood_keywords)}

CREATIVE DIRECTION:
{brief.creative_direction}""")

        # 2. Layout Specifications
        sections.append(f"""
[LAYOUT SPECIFICATIONS]
Composition: {brief.layout.composition}
Product Position: {brief.layout.product_position}
Product Size: {brief.layout.product_size}
Text Position: {brief.layout.text_position}
Whitespace: {brief.layout.whitespace}
Visual Flow: {brief.layout.visual_flow}""")

        # 3. Color System
        colors = listing_brief.colors
        sections.append(f"""
[COLOR SYSTEM - EXACT VALUES]
Primary Color: {colors.primary} (use for ~60% of design elements)
Secondary Color: {colors.secondary} (use for ~30%)
Accent Color: {colors.accent} (use sparingly, ~10%)
Text Dark: {colors.text_dark}
Text Light: {colors.text_light}
Background: {brief.background_treatment}""")

        if colors.gradient_from and colors.gradient_to:
            sections.append(f"Gradient: {colors.gradient_from} → {colors.gradient_to} ({colors.gradient_direction})")

        # 4. Typography System
        typo = listing_brief.typography
        sections.append(f"""
[TYPOGRAPHY SYSTEM]
Headlines: {typo.headline_font}, {typo.headline_weight} weight, {typo.headline_size}
Subheads: {typo.subhead_font}, {typo.subhead_weight} weight, {typo.subhead_size}
Body Text: {typo.body_font}, {typo.body_size}
Letter Spacing: {typo.letter_spacing}
Line Height: {typo.line_height}""")

        # 5. Copy (if any)
        if brief.copy.headline:
            sections.append(f"""
[COPY - EXACT TEXT TO USE]
Headline: "{brief.copy.headline}"
""")
            if brief.copy.subhead:
                sections.append(f'Subhead: "{brief.copy.subhead}"')
            if brief.copy.feature_callouts:
                sections.append("Feature Callouts:")
                for i, callout in enumerate(brief.copy.feature_callouts, 1):
                    sections.append(f"  {i}. {callout}")
            if brief.copy.cta:
                sections.append(f'CTA: "{brief.copy.cta}"')

        # 6. Shadow & Depth
        shadow = listing_brief.shadows
        if shadow.enabled:
            sections.append(f"""
[SHADOW SPECIFICATIONS]
Shadow: {shadow.x_offset} {shadow.y_offset} {shadow.blur} {shadow.spread} {shadow.color}
Light Direction: {shadow.direction}
Apply consistently to all floating elements.""")

        # 7. Lighting
        sections.append(f"""
[LIGHTING]
{brief.lighting_direction}""")

        # 8. Amazon-Specific Requirements
        sections.append(f"""
[AMAZON OPTIMIZATION]
Thumbnail (100px): {brief.thumbnail_focus}
Mobile Priority: {brief.mobile_priority}
Technical: {brief.file_notes}""")

        # 9. Story Arc Cohesion
        sections.append(f"""
[STORY ARC - THIS IS IMAGE {['main', 'infographic_1', 'infographic_2', 'lifestyle', 'comparison'].index(brief.image_type) + 1} OF 5]
Story Theme: {listing_brief.story_theme}
Brand Voice: {listing_brief.brand_voice}

MAINTAIN ACROSS ALL IMAGES:
{chr(10).join('- ' + elem for elem in listing_brief.cohesion_elements)}

NEVER INCLUDE:
{chr(10).join('- ' + elem for elem in listing_brief.forbidden_elements)}""")

        return '\n'.join(sections)


# Singleton instance
_generator: Optional[CreativeBriefGenerator] = None


def get_brief_generator() -> CreativeBriefGenerator:
    """Get or create the creative brief generator singleton"""
    global _generator
    if _generator is None:
        _generator = CreativeBriefGenerator()
    return _generator


def generate_listing_brief(
    product_name: str,
    features: List[str],
    vibe: str,
    primary_color: str = "#2196F3",
    brand_name: Optional[str] = None,
    user_colors: Optional[List[str]] = None,
) -> ListingBrief:
    """
    Convenience function to generate a complete listing brief.

    Args:
        product_name: Product title
        features: Key features (up to 3)
        vibe: Brand vibe string (e.g., "clean_modern", "premium_luxury")
        primary_color: Primary brand color (hex)
        brand_name: Optional brand name
        user_colors: Optional user-specified color palette

    Returns:
        Complete ListingBrief
    """
    generator = get_brief_generator()

    # Convert vibe string to enum
    try:
        vibe_enum = BrandVibe(vibe.lower().replace(' ', '_').replace('-', '_'))
    except ValueError:
        vibe_enum = BrandVibe.CLEAN_MODERN  # Default

    return generator.generate_brief(
        product_name=product_name,
        features=features,
        vibe=vibe_enum,
        primary_color=primary_color,
        brand_name=brand_name,
        user_colors=user_colors,
    )
