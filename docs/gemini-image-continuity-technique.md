# Gemini Image Continuity Technique

## Purpose

Generate seamless image extensions (outpainting) using Gemini's image editing capabilities to create multi-section visuals that look like one continuous photograph.

## The Problem

Gemini (and most image generation models) don't natively support outpainting. When given a reference image and asked to "continue" it, they **re-interpret the entire scene** as a style reference rather than extending the canvas. This results in duplicated scenes with visible seams when merged.

## What Doesn't Work

| Approach | Result |
|----------|--------|
| "Continue this image downward" | Model recreates the full scene instead of extending it |
| Generate separately + stitch | Visible seam, misaligned objects, color mismatch |
| Paste original on top of generated | Objects shift at the join line |
| Hard blank canvas (solid color below original) | Model treats it as two separate zones, creates a shelf/edge/line between them |

## What Works: Gradient Canvas + Inpainting Language

### Step 1: Create a Gradient-Faded Canvas

Instead of a hard cutoff between the original image and blank space, create a **gradient blend zone** at the boundary. This prevents the model from seeing a hard line to separate "two sections."

```python
from PIL import Image
import numpy as np

orig = Image.open('original.jpg')
arr = np.array(orig)

# Sample average color from the bottom edge
bottom_avg = arr[-5:, :, :].mean(axis=(0, 1)).astype(np.uint8)

# Create extended canvas (2x height) filled with bottom-edge color
extended = Image.new('RGB', (orig.width, orig.height * 2), tuple(bottom_avg))
extended.paste(orig, (0, 0))

# Gradient blend over the last 80px of the original into the solid fill
blend_zone = 80
for y in range(blend_zone):
    alpha = y / blend_zone
    for x in range(orig.width):
        orig_pixel = arr[orig.height - blend_zone + y, x]
        blended = (orig_pixel * (1 - alpha) + bottom_avg * alpha).astype(np.uint8)
        extended.putpixel((x, orig.height - blend_zone + y), tuple(blended))

extended.save('canvas_to_fill.png')
```

### Step 2: Prompt as Inpainting (Not Outpainting)

Frame the task as **editing/completing a single image**, not extending one. Key vocabulary:

**Use:**
- "Edit this image to complete it"
- "Fill the blank portion"
- "ONE single continuous photograph"
- "Camera pulled back to show a wider view"
- "Same single flat table extending further toward the viewer"
- "Single continuous perspective, single light source, one unified scene"
- "NO edge, NO shelf, NO line, NO break"

**Avoid:**
- "Continue this image"
- "Extend downward"
- "Generate a matching image"
- "Seamless continuation" (model ignores this)

### Step 3: Describe the Scene Holistically

Don't describe the new section in isolation. Describe the **entire scene as one photograph** and tell the model what the viewer sees in the filled area as part of that single shot.

### Example Prompt (A+ Result)

```
Edit this image to complete it as ONE single continuous photograph.
The top portion shows [describe existing scene]. The bottom portion
is blank and needs to be filled.

IMPORTANT: This must look like ONE single photograph taken with a
camera pulled back to show a wider view. The table surface continues
seamlessly - NO edge, NO shelf, NO line, NO break. Same single flat
table extending further toward the viewer with [describe new content]
displayed in the foreground of the SAME table. [Describe connecting
elements like scattered items, draped fabric]. The [background]
continues in the background. Single continuous perspective, single
light source, one unified scene.
```

## Aspect Ratios & Amazon A+ Module Sizing

### The Math

Amazon A+ Content modules use wide banner images, typically around **~2.34:1 ratio** (e.g., 1464x625px).

Gemini's closest available aspect ratio for generating a **two-module vertical image** is **4:3 (1.33:1)**. Here's how the ratios work out:

| What | Dimensions | Ratio |
|------|-----------|-------|
| Original A+ module image | 1464 x 625 | ~2.34:1 |
| Gemini output at 4:3 | 1200 x 896 | 1.33:1 |
| Each half when split | 1200 x 448 | ~2.68:1 |

### Why 4:3 Works

When you generate at **4:3**, splitting the output in half gives you two images at roughly **2.68:1** - close enough to the Amazon A+ banner ratio (~2.34:1) that resizing works without significant distortion.

The pipeline:
```
4:3 generated image (1200x896)
        |
        v
  Split in half horizontally
        |
        v
  Top half:    1200 x 448  (~2.68:1)  -->  Resize to 1464 x 625  =  Module 1
  Bottom half: 1200 x 448  (~2.68:1)  -->  Resize to 1464 x 625  =  Module 2
```

### Splitting & Resizing for A+ Upload

```python
from PIL import Image

generated = Image.open('gemini_output.png')
mid = generated.height // 2

# Split into two modules
module_1 = generated.crop((0, 0, generated.width, mid))
module_2 = generated.crop((0, mid, generated.width, generated.height))

# Resize both to Amazon A+ module dimensions
target_size = (1464, 625)
module_1 = module_1.resize(target_size, Image.LANCZOS)
module_2 = module_2.resize(target_size, Image.LANCZOS)

module_1.save('module_1.png')
module_2.save('module_2.png')
```

### Result

When uploaded to Amazon A+ as two consecutive modules, they appear as **one seamless image** because:
1. They were generated as a single photograph by Gemini
2. The split point is invisible - no seam, no color shift
3. Both halves share the same lighting, perspective, and color palette

### Other Ratios

| Gemini Ratio | Each Half Ratio | Best For |
|-------------|----------------|----------|
| 4:3 | ~2.68:1 | Amazon A+ banners (close to 2.34:1) |
| 16:9 | ~3.56:1 | Ultra-wide banners, website heroes |
| 1:1 | ~2:1 | Wider module formats |
| 9:16 | ~0.56:1 | Vertical/portrait splits (side-by-side modules) |

## Key Findings

1. **Gemini treats reference images as style guides, not canvases** - you must feed it the canvas WITH the blank space as the reference image itself.
2. **Gradient fade > hard cutoff** - a blended boundary prevents the model from creating a visual "shelf" or dividing line.
3. **"Camera pulled back" framing** - this single phrase dramatically improved results by reframing the task as perspective, not stitching.
4. **Connecting elements matter** - asking for items that span both zones (draped ribbon, scattered sprigs) helps unify the composition.
5. **Describe what NOT to do** - explicitly saying "NO edge, NO shelf, NO line" steers the model away from its default behavior of creating visual separation.
6. **OpenAI gpt-image-1 comparison** - produced higher fidelity object details but same fundamental limitation (recreates rather than extends). Gemini responded better to the canvas inpainting technique.

## Workflow Summary

```
Original Image
      |
      v
[Create gradient canvas - 2x height, faded bottom]
      |
      v
[Feed canvas as reference to Gemini with inpainting prompt]
      |
      v
[Gemini returns ONE unified image - use as-is, no merging needed]
```
