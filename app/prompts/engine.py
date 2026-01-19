"""
Prompt Engineering Engine
Based on Architecture Document Section 6 and Creative Blueprint
MASTER Level: Now uses intelligent Creative Brief system for complete specifications
"""
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from .templates import main_image, infographic, lifestyle, comparison
from .intent_modifiers import get_intent_modifiers
from .color_psychology import get_color_guidance, infer_category
from .styles import get_style_preset, build_brand_context, build_cohesion_reminder, StylePreset
from .creative_brief import (
    CreativeBriefGenerator,
    ListingBrief,
    BrandVibe,
    get_brief_generator,
    generate_listing_brief,
)


@dataclass
class ProductContext:
    """Context for generating prompts"""
    title: str
    features: List[str]  # 3 key features
    target_audience: str
    keywords: List[str]
    intents: Dict[str, List[str]]  # keyword -> list of intent types
    # Brand and style options
    brand_colors: List[str] = field(default_factory=list)
    brand_name: Optional[str] = None
    has_logo: bool = False  # Whether a logo image is provided
    style_id: Optional[str] = None  # Selected style preset (legacy)
    # NEW: Brand vibe for creative brief system
    brand_vibe: Optional[str] = None  # e.g., "clean_modern", "premium_luxury"
    primary_color: Optional[str] = None  # Primary brand color (hex)
    # Style reference image
    has_style_reference: bool = False  # Whether a style reference image is provided
    # Color palette options
    color_count: Optional[int] = None  # Number of colors (2-6), None = AI decides
    color_palette: List[str] = field(default_factory=list)  # Specific colors, empty = AI generates
    # Cached creative brief
    _creative_brief: Optional[ListingBrief] = field(default=None, repr=False)


class PromptEngine:
    """
    Constructs prompts for each image type.

    MASTER Level: Uses intelligent Creative Brief system that generates
    complete specifications with:
    - Story arc across 5 images
    - Exact typography specs (fonts, sizes, weights)
    - Precise color palette with 60-30-10 distribution
    - Shadow specifications for consistency
    - Copy strategy with headlines for each image
    - Amazon-specific optimizations
    """

    def __init__(self):
        self.templates = {
            'main': main_image.TEMPLATE,
            'infographic_1': infographic.TEMPLATE_1,
            'infographic_2': infographic.TEMPLATE_2,
            'lifestyle': lifestyle.TEMPLATE,
            'comparison': comparison.TEMPLATE,
        }
        self.brief_generator = get_brief_generator()

    def build_prompt(
        self,
        image_type: str,
        context: ProductContext,
        style_override: Optional[str] = None,
    ) -> str:
        """
        Build a complete prompt for the specified image type.

        MASTER Level: When brand_vibe is set, uses the Creative Brief system
        for detailed, professional specifications. Otherwise falls back to
        legacy template system.

        Args:
            image_type: One of main, infographic_1, infographic_2, lifestyle, comparison
            context: Product information and keyword intents
            style_override: Optional style ID to override context.style_id

        Returns:
            Complete prompt string ready for Gemini API
        """
        # MASTER LEVEL: Use Creative Brief system when brand_vibe is specified
        if context.brand_vibe:
            return self._build_creative_brief_prompt(image_type, context)

        # LEGACY: Fall back to template-based system
        return self._build_legacy_prompt(image_type, context, style_override)

    def _build_creative_brief_prompt(
        self,
        image_type: str,
        context: ProductContext,
    ) -> str:
        """
        Build prompt using MASTER level Creative Brief system.

        Generates complete specifications including:
        - Story arc position (Hook/Reveal/Proof/Dream/Close)
        - Exact typography (fonts, sizes, weights)
        - Color palette with distribution rules
        - Shadow specifications
        - Copy with headlines
        - Amazon-specific optimizations
        """
        # Generate or use cached creative brief
        if context._creative_brief is None:
            # Determine primary color
            primary_color = context.primary_color
            if not primary_color and context.color_palette:
                primary_color = context.color_palette[0]
            elif not primary_color and context.brand_colors:
                primary_color = context.brand_colors[0]
            else:
                primary_color = primary_color or "#2196F3"  # Default blue

            context._creative_brief = generate_listing_brief(
                product_name=context.title,
                features=context.features,
                vibe=context.brand_vibe,
                primary_color=primary_color,
                brand_name=context.brand_name,
                user_colors=context.color_palette or context.brand_colors or None,
            )

        listing_brief = context._creative_brief

        # Get the image-specific brief
        if image_type not in listing_brief.briefs:
            # Fallback for unknown image types
            return self._build_legacy_prompt(image_type, context, None)

        image_brief = listing_brief.briefs[image_type]

        # Convert brief to prompt
        prompt = self.brief_generator.to_prompt(image_brief, listing_brief)

        # Add reference image instructions
        prompt = self._add_reference_instructions(prompt, image_type, context)

        # Add style reference guidance if provided
        if context.has_style_reference:
            prompt += self._build_style_reference_guidance()

        return prompt

    def _add_reference_instructions(
        self,
        prompt: str,
        image_type: str,
        context: ProductContext,
    ) -> str:
        """Add reference image instructions to prompt"""
        instructions = """
[REFERENCE IMAGES PROVIDED]
Use the provided product photo as the source of truth for the product.
Maintain product accuracy while applying the creative direction above.
"""
        if context.has_logo and image_type != 'main':
            instructions += """
LOGO INTEGRATION:
- A logo image is also provided
- Integrate it naturally into the composition
- Position in corner or as design element
- Maintain brand recognition
"""
        return instructions + "\n\n" + prompt

    def _build_legacy_prompt(
        self,
        image_type: str,
        context: ProductContext,
        style_override: Optional[str] = None,
    ) -> str:
        """
        Build prompt using legacy template system.
        Kept for backwards compatibility with existing style_id based workflows.
        """
        # Get base template
        template = self.templates[image_type]

        # Get intent modifiers for this image type
        intent_modifiers = get_intent_modifiers(image_type, context.intents)

        # Infer category and get color guidance (fallback if no brand colors)
        category = infer_category(context.title, context.keywords)
        color_guidance = get_color_guidance(category)

        # Ensure we have at least 3 features
        features = context.features + [''] * (3 - len(context.features))

        # Build the base prompt
        prompt = template.format(
            product_title=context.title,
            key_feature=features[0],
            feature_1=features[0],
            feature_2=features[1],
            feature_3=features[2],
            target_audience=context.target_audience,
            intent_modifiers=intent_modifiers,
            top_keywords=', '.join(context.keywords[:5]) if context.keywords else 'quality, premium'
        )

        # Add style modifier (highest priority - defines the visual language)
        style_id = style_override or context.style_id
        if style_id:
            style = get_style_preset(style_id)
            if style:
                prompt = style.prompt_modifier + "\n\n" + prompt

        # Add brand context (logo only on non-main images)
        brand_context = build_brand_context(
            brand_colors=context.brand_colors,
            brand_name=context.brand_name,
            has_logo=context.has_logo,
            image_type=image_type,
        )
        if brand_context:
            prompt += f"\n\n{brand_context}"

        # Add color palette guidance
        color_palette_guidance = self._build_color_palette_guidance(context)
        if color_palette_guidance:
            prompt += f"\n\n{color_palette_guidance}"
        # Fallback to category-based color guidance if no palette specified
        elif not context.brand_colors and image_type in ['lifestyle', 'infographic_1', 'infographic_2']:
            prompt += f"\n\n{color_guidance}"

        # Add style reference guidance
        if context.has_style_reference:
            prompt += self._build_style_reference_guidance()

        # Add cohesion reminder for all images
        if style_id:
            cohesion = build_cohesion_reminder(style_id, image_type)
            if cohesion:
                prompt += cohesion

        return prompt

    def _build_color_palette_guidance(self, context: ProductContext) -> str:
        """Build color palette guidance for prompts"""
        parts = []

        # User specified exact colors
        if context.color_palette:
            colors_str = ", ".join(context.color_palette)
            parts.append("[COLOR PALETTE - USER SPECIFIED]")
            parts.append(f"Use EXACTLY these colors: {colors_str}")
            parts.append("- Primary color: Use for main elements, backgrounds")
            parts.append("- Secondary color: Use for supporting elements")
            parts.append("- Accent color(s): Use sparingly for emphasis")
            parts.append("- Follow 60-30-10 rule: 60% primary, 30% secondary, 10% accent")
            parts.append("- Maintain consistency across all images in the set")

        # User specified color count only
        elif context.color_count:
            parts.append("[COLOR PALETTE - AI GENERATED]")
            parts.append(f"Generate a cohesive {context.color_count}-color palette:")
            parts.append(f"- Create exactly {context.color_count} harmonious colors")
            parts.append("- Colors should work well together (analogous, complementary, or triadic)")
            parts.append("- Consider the product and target audience when choosing colors")
            parts.append("- Follow 60-30-10 rule for color distribution")
            parts.append("- Ensure sufficient contrast for readability")

        return "\n".join(parts) if parts else ""

    def _build_style_reference_guidance(self) -> str:
        """Build guidance for using style reference image"""
        return """
[STYLE REFERENCE IMAGE - CRITICAL]
A style reference image is provided as one of the reference images.
MATCH THE VISUAL STYLE of this reference:

EXTRACT AND APPLY:
- Color palette and color relationships
- Typography style (if visible)
- Lighting mood and quality
- Composition and layout principles
- Texture and material treatments
- Overall aesthetic and mood

DO NOT:
- Copy the exact content or products from the style reference
- Ignore the actual product photo (first reference image)

The product should be showcased in a style that MATCHES the reference aesthetic.
"""

    def build_style_preview_prompt(
        self,
        context: ProductContext,
        style_id: str,
    ) -> str:
        """
        Build a prompt specifically for style preview (main image only).
        Used to show user different style options before full generation.
        """
        return self.build_prompt('main', context, style_override=style_id)

    def build_all_prompts(
        self,
        context: ProductContext,
    ) -> Dict[str, str]:
        """
        Build prompts for all 5 image types with consistent style.

        Args:
            context: Product information with style_id set

        Returns:
            Dict mapping image_type to prompt string
        """
        return {
            image_type: self.build_prompt(image_type, context)
            for image_type in self.templates.keys()
        }


# Singleton instance
_engine: Optional[PromptEngine] = None


def get_prompt_engine() -> PromptEngine:
    """Get or create the prompt engine singleton"""
    global _engine
    if _engine is None:
        _engine = PromptEngine()
    return _engine
