"""
Image utility functions for resizing and processing generated images.
"""
from PIL import Image as PILImage
from typing import Tuple
import logging

logger = logging.getLogger(__name__)

# A+ Content module dimensions
APLUS_DIMENSIONS = {
    "full_image": (1464, 600),           # Premium Full Image Module
    "full_image_mobile": (600, 450),     # Mobile version
    "dual_image": (650, 350),            # Premium Dual Images
    "four_image": (300, 225),            # Premium Four Images
    "comparison": (200, 225),            # Premium Comparison Table
}

# Standard listing image dimensions
LISTING_DIMENSIONS = {
    "main": (2000, 2000),                # 1:1 square
    "infographic": (2000, 2000),
    "lifestyle": (2000, 2000),
    "comparison": (2000, 2000),
}


def resize_to_dimensions(
    image: PILImage.Image,
    target_width: int,
    target_height: int,
    method: str = "cover"
) -> PILImage.Image:
    """
    Resize an image to exact target dimensions.

    Args:
        image: PIL Image to resize
        target_width: Target width in pixels
        target_height: Target height in pixels
        method: Resize method
            - "cover": Crop to fill (no letterboxing, may lose edges)
            - "contain": Fit inside (may add letterboxing)
            - "stretch": Stretch to fit (may distort)

    Returns:
        Resized PIL Image
    """
    orig_width, orig_height = image.size
    target_ratio = target_width / target_height
    orig_ratio = orig_width / orig_height

    logger.info(f"Resizing image from {orig_width}x{orig_height} to {target_width}x{target_height} (method={method})")

    if method == "cover":
        # Scale to cover the target, then crop center
        if orig_ratio > target_ratio:
            # Image is wider - scale by height, crop width
            new_height = target_height
            new_width = int(orig_width * (target_height / orig_height))
        else:
            # Image is taller - scale by width, crop height
            new_width = target_width
            new_height = int(orig_height * (target_width / orig_width))

        # Resize
        resized = image.resize((new_width, new_height), PILImage.Resampling.LANCZOS)

        # Crop center
        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
        right = left + target_width
        bottom = top + target_height

        return resized.crop((left, top, right, bottom))

    elif method == "contain":
        # Scale to fit inside, add padding if needed
        if orig_ratio > target_ratio:
            # Image is wider - scale by width
            new_width = target_width
            new_height = int(orig_height * (target_width / orig_width))
        else:
            # Image is taller - scale by height
            new_height = target_height
            new_width = int(orig_width * (target_height / orig_height))

        # Resize
        resized = image.resize((new_width, new_height), PILImage.Resampling.LANCZOS)

        # Create white background and paste centered
        result = PILImage.new("RGB", (target_width, target_height), (255, 255, 255))
        paste_x = (target_width - new_width) // 2
        paste_y = (target_height - new_height) // 2
        result.paste(resized, (paste_x, paste_y))

        return result

    elif method == "stretch":
        # Direct resize (may distort)
        return image.resize((target_width, target_height), PILImage.Resampling.LANCZOS)

    else:
        raise ValueError(f"Unknown resize method: {method}")


def resize_for_aplus_module(
    image: PILImage.Image,
    module_type: str,
    mobile: bool = False
) -> PILImage.Image:
    """
    Resize an image for a specific A+ Content module type.

    Args:
        image: PIL Image to resize
        module_type: A+ module type (e.g., "full_image", "dual_image")
        mobile: If True, use mobile dimensions

    Returns:
        Resized PIL Image at exact module dimensions
    """
    key = f"{module_type}_mobile" if mobile and f"{module_type}_mobile" in APLUS_DIMENSIONS else module_type

    if key not in APLUS_DIMENSIONS:
        raise ValueError(f"Unknown A+ module type: {module_type}")

    width, height = APLUS_DIMENSIONS[key]
    return resize_to_dimensions(image, width, height, method="cover")


def get_aspect_ratio_for_module(module_type: str) -> str:
    """
    Get the Gemini aspect ratio string for a module type.

    Args:
        module_type: A+ module type

    Returns:
        Aspect ratio string for Gemini API (e.g., "21:9", "16:9")
    """
    if module_type == "full_image":
        # 1464/600 = 2.44:1, closest is 21:9 (2.33:1)
        return "21:9"
    elif module_type == "dual_image":
        # 650/350 = 1.86:1, closest is 16:9 (1.78:1)
        return "16:9"
    elif module_type == "four_image":
        # 300/225 = 1.33:1, closest is 4:3 (1.33:1)
        return "4:3"
    elif module_type == "comparison":
        # 200/225 = 0.89:1, closest is 9:16 rotated... actually 4:5 (0.8:1)
        return "4:5"
    else:
        return "1:1"  # Default square
