"""
Canvas Compositor for A+ Content Module Continuity

Creates green-screen canvases from previous modules and crops results
from Gemini generation to produce seamless inter-module transitions.

Technique: Paste module N on top of a taller canvas, fill the bottom
with solid bright green (#00FF00) as an obvious "fill this" marker.
Gemini sees the green and knows exactly what area to complete.
"""
from PIL import Image as PILImage
from typing import Tuple
import logging

logger = logging.getLogger(__name__)

# Canvas dimensions: 1464 wide, 4:3 ratio = 1464 x 1098
CANVAS_WIDTH = 1464
CANVAS_HEIGHT = 1098  # 1464 * 3/4 = 1098
MODULE_HEIGHT = 600

# Bright green marker color — unmistakable "fill this" signal
GREEN_SCREEN = (0, 255, 0)


class CanvasCompositor:
    """Creates green-screen canvases and splits completed results for seamless A+ modules."""

    def create_canvas(
        self,
        previous_module: PILImage.Image,
    ) -> PILImage.Image:
        """
        Build a tall canvas with the previous module on top and bright green below.

        Input:  1464x600 (previous module)
        Output: 1464x1098 (4:3 ratio canvas for Gemini)

        Layout:
          y=0   to y=599:  Previous module (unchanged, hard cut)
          y=600 to y=1097: Solid bright green (#00FF00)
        """
        # Ensure previous module is the right size
        if previous_module.size != (CANVAS_WIDTH, MODULE_HEIGHT):
            previous_module = previous_module.resize(
                (CANVAS_WIDTH, MODULE_HEIGHT), PILImage.Resampling.LANCZOS
            )

        # Create canvas filled with bright green
        canvas = PILImage.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), GREEN_SCREEN)

        # Paste previous module at the top — hard cut, no gradient
        canvas.paste(previous_module, (0, 0))

        logger.info(
            f"Green-screen canvas created: {canvas.size} "
            f"(module={CANVAS_WIDTH}x{MODULE_HEIGHT} on top, "
            f"green fill below y={MODULE_HEIGHT})"
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

    def split_hero_image(
        self,
        image: PILImage.Image,
    ) -> Tuple[PILImage.Image, PILImage.Image]:
        """
        Split a tall hero image exactly in half to create two seamless A+ modules.

        Both halves come from the SAME image — guaranteed perfect alignment, zero seam.
        Each half is resized to CANVAS_WIDTH × MODULE_HEIGHT (1464×600).

        Input:  Single tall image (any size, ideally ~4:3 ratio)
        Output: (top_module, bottom_module) both at CANVAS_WIDTH × MODULE_HEIGHT
        """
        width, height = image.size

        logger.info(
            f"split_hero_image: input={image.size}"
        )

        # Resize full image to exactly CANVAS_WIDTH × (MODULE_HEIGHT * 2).
        # Then split at the midpoint — zero content loss, pixel-perfect seam.
        # Slight aspect ratio adjustment is invisible on AI-generated images
        # and far better than cropping off 39% of the composition.
        target_w = CANVAS_WIDTH
        target_h = MODULE_HEIGHT * 2
        full = image.resize((target_w, target_h), PILImage.Resampling.LANCZOS)

        # Split at exact midpoint
        top_module = full.crop((0, 0, target_w, MODULE_HEIGHT))
        bottom_module = full.crop((0, MODULE_HEIGHT, target_w, target_h))

        logger.info(
            f"Hero split: input={image.size}, resized={full.size}, "
            f"top={top_module.size}, bottom={bottom_module.size}"
        )
        return top_module, bottom_module
