# Prompt Engineering System
from .engine import PromptEngine, ProductContext, get_prompt_engine
from .intent_modifiers import get_intent_modifiers
from .color_psychology import get_color_guidance, infer_category
from .styles import get_style_preset, get_all_styles, build_brand_context, build_cohesion_reminder, StylePreset
from .design_framework import (
    DesignFramework,
    generate_random_framework,
    get_design_preset,
    get_all_presets,
)
# AI Designer prompts (MASTER level)
from .ai_designer import (
    PRINCIPAL_DESIGNER_VISION_PROMPT,
    GENERATE_IMAGE_PROMPTS_PROMPT,
    ENHANCE_PROMPT_WITH_FEEDBACK_PROMPT,
    GLOBAL_NOTE_INSTRUCTIONS,
)

__all__ = [
    'PromptEngine',
    'ProductContext',
    'get_prompt_engine',
    'get_intent_modifiers',
    'get_color_guidance',
    'infer_category',
    'get_style_preset',
    'get_all_styles',
    'build_brand_context',
    'build_cohesion_reminder',
    'StylePreset',
    'DesignFramework',
    'generate_random_framework',
    'get_design_preset',
    'get_all_presets',
    # AI Designer prompts
    'PRINCIPAL_DESIGNER_VISION_PROMPT',
    'GENERATE_IMAGE_PROMPTS_PROMPT',
    'ENHANCE_PROMPT_WITH_FEEDBACK_PROMPT',
    'GLOBAL_NOTE_INSTRUCTIONS',
]
