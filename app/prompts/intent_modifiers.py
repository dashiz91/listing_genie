"""
Keyword Intent Modifiers for Visual Proof
Based on Creative Blueprint Section 5 - Chris Rawlings' PPC Loop
"""
from typing import Dict, List

# Visual proof statements for each intent type
INTENT_VISUAL_PROOF = {
    'durability': [
        "Show rugged, premium materials and construction quality",
        "Emphasize durability through visual texture and build quality",
        "Include visual cues suggesting long-lasting performance",
    ],
    'use_case': [
        "Show product in the exact context implied by search terms",
        "Visualize the specific use case scenario",
        "Environment should match intended usage",
    ],
    'style': [
        "Match visual aesthetic to style-related keywords",
        "Color palette and composition should reflect style intent",
        "Design elements should resonate with aesthetic preferences",
    ],
    'problem_solution': [
        "Visualize the solved state / positive outcome",
        "Show relief, satisfaction, or resolution",
        "Before/after or transformation visual if appropriate",
    ],
    'comparison': [
        "Emphasize superiority and premium positioning",
        "Clear winner hierarchy in visual presentation",
        "Quality differentiation should be obvious",
    ],
}

# Which intents matter most for each image type
IMAGE_TYPE_INTENT_PRIORITY = {
    'main': ['durability', 'style'],
    'infographic_1': ['problem_solution', 'durability'],
    'infographic_2': ['problem_solution', 'use_case'],
    'lifestyle': ['use_case', 'style'],
    'comparison': ['comparison', 'durability'],
}


def get_intent_modifiers(
    image_type: str,
    keyword_intents: Dict[str, List[str]]
) -> str:
    """
    Generate intent-specific prompt modifiers for an image type.

    Args:
        image_type: The type of image being generated
        keyword_intents: Mapping of keywords to their classified intents

    Returns:
        String of intent modifiers to inject into the prompt
    """
    # Collect all unique intents from keywords
    all_intents = set()
    for intents in keyword_intents.values():
        all_intents.update(intents)

    # Get priority intents for this image type
    priority_intents = IMAGE_TYPE_INTENT_PRIORITY.get(image_type, [])

    # Build modifier string
    modifiers = []
    for intent in priority_intents:
        if intent in all_intents:
            proof_statements = INTENT_VISUAL_PROOF.get(intent, [])
            if proof_statements:
                modifiers.append(f"[{intent.upper()} INTENT]")
                modifiers.extend(f"- {stmt}" for stmt in proof_statements)

    if not modifiers:
        return "Focus on professional product presentation and visual appeal."

    return '\n'.join(modifiers)
