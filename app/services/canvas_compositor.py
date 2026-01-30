"""
Canvas Compositor for A+ Content Module Continuity

Creates gradient-faded canvases from previous modules and crops results
from Gemini inpainting to produce seamless inter-module transitions.

Technique documented in: docs/gemini-image-continuity-technique.md
"""
from PIL import Image as PILImage
from typing import Tuple
import logging

logger = logging.getLogger(__name__)

# Canvas dimensions: 1464 wide, 4:3 ratio = 1464 x 1098
# 4:3 is the proven ratio from the continuity technique doc
CANVAS_WIDTH = 1464
CANVAS_HEIGHT = 1098  # 1464 * 3/4 = 1098
MODULE_HEIGHT = 600
BLEND_ZONE = 80  # pixels of gradient fade


class CanvasCompositor:
    """Creates gradient canvases and crops inpainted results for seamless A+ modules."""

    def create_gradient_canvas(
        self,
        previous_module: PILImage.Image,
        blend_zone: int = BLEND_ZONE,
    ) -> PILImage.Image:
        """
        Build a tall canvas with the previous module on top, gradient-fading
        into a solid color fill below.

        Input:  1464x600 (previous module)
        Output: 1464x1171 (5:4 ratio canvas for Gemini)

        Layout:
          y=0   to y=(MODULE_HEIGHT - blend_zone - 1): Previous module unchanged
          y=(MODULE_HEIGHT - blend_zone) to y=(MODULE_HEIGHT - 1): Gradient blend zone
          y=MODULE_HEIGHT to y=(CANVAS_HEIGHT - 1): Solid fill (avg bottom-edge color)
        """
        # Ensure previous module is the right size
        if previous_module.size != (CANVAS_WIDTH, MODULE_HEIGHT):
            previous_module = previous_module.resize(
                (CANVAS_WIDTH, MODULE_HEIGHT), PILImage.Resampling.LANCZOS
            )

        # Sample average color from the bottom 5 rows of the previous module
        bottom_color = self._average_bottom_color(previous_module, rows=5)
        logger.info(f"Bottom edge average color: RGB{bottom_color}")

        # Create canvas filled with that solid color
        canvas = PILImage.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), bottom_color)

        # Paste previous module at the top
        canvas.paste(previous_module, (0, 0))

        # Apply gradient blend over the last `blend_zone` pixels of the module
        blend_start_y = MODULE_HEIGHT - blend_zone
        for y_offset in range(blend_zone):
            alpha = y_offset / blend_zone  # 0.0 at top of blend → 1.0 at bottom
            canvas_y = blend_start_y + y_offset
            for x in range(CANVAS_WIDTH):
                orig_r, orig_g, orig_b = previous_module.getpixel((x, canvas_y))
                blended = (
                    int(orig_r * (1 - alpha) + bottom_color[0] * alpha),
                    int(orig_g * (1 - alpha) + bottom_color[1] * alpha),
                    int(orig_b * (1 - alpha) + bottom_color[2] * alpha),
                )
                canvas.putpixel((x, canvas_y), blended)

        logger.info(
            f"Gradient canvas created: {canvas.size} "
            f"(blend_zone={blend_zone}px, fill=RGB{bottom_color})"
        )
        return canvas

    def split_canvas_output(
        self,
        completed_canvas: PILImage.Image,
    ) -> Tuple[PILImage.Image, PILImage.Image]:
        """
        Split Gemini's completed canvas into two seamless A+ modules.

        Both halves come from the SAME image so the seam is invisible.
        The top half replaces the previous module (refined by Gemini),
        the bottom half becomes the new module.

        Split point is proportional: MODULE_HEIGHT / CANVAS_HEIGHT of the
        output height, matching where the original module ended in the canvas.

        Input:  Gemini output (any size at ~4:3 ratio)
        Output: (top_module, bottom_module) both at CANVAS_WIDTH x MODULE_HEIGHT
        """
        width, height = completed_canvas.size
        split_ratio = MODULE_HEIGHT / CANVAS_HEIGHT  # 600/1098 ≈ 0.546
        split_y = int(height * split_ratio)

        logger.info(
            f"split_canvas_output: input={completed_canvas.size}, "
            f"split_y={split_y} (ratio={split_ratio:.3f})"
        )

        # Top half → refined previous module
        top_half = completed_canvas.crop((0, 0, width, split_y))
        top_module = top_half.resize(
            (CANVAS_WIDTH, MODULE_HEIGHT), PILImage.Resampling.LANCZOS
        )

        # Bottom half → new module
        bottom_half = completed_canvas.crop((0, split_y, width, height))
        bottom_module = bottom_half.resize(
            (CANVAS_WIDTH, MODULE_HEIGHT), PILImage.Resampling.LANCZOS
        )

        logger.info(
            f"Split result: top={top_half.size}→{top_module.size}, "
            f"bottom={bottom_half.size}→{bottom_module.size}"
        )
        return top_module, bottom_module

    @staticmethod
    def _average_bottom_color(
        image: PILImage.Image, rows: int = 5
    ) -> Tuple[int, int, int]:
        """Average RGB color of the bottom N rows of an image."""
        width, height = image.size
        r_total, g_total, b_total = 0, 0, 0
        pixel_count = width * rows

        for y in range(height - rows, height):
            for x in range(width):
                r, g, b = image.getpixel((x, y))[:3]
                r_total += r
                g_total += g
                b_total += b

        return (
            r_total // pixel_count,
            g_total // pixel_count,
            b_total // pixel_count,
        )
