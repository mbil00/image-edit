"""Built-in templates for common image editing operations."""

from .registry import Template

BUILTIN_TEMPLATES = [
    Template(
        name="remove-bg",
        prompt=(
            "Remove the background from this image completely. "
            "Make the background fully transparent while preserving the main subject "
            "with clean, precise edges. Keep only the primary subject visible."
        ),
        description="Remove background, make transparent",
        aliases=["removebg", "nobg", "background-remove"],
    ),
    Template(
        name="enhance",
        prompt=(
            "Enhance this image to improve overall quality. "
            "Increase clarity and sharpness, optimize lighting and exposure, "
            "reduce noise, and improve color balance. "
            "Make the image look more professional and polished."
        ),
        description="Improve quality, clarity, and lighting",
        aliases=["improve", "fix", "auto-enhance"],
    ),
    Template(
        name="upscale",
        prompt=(
            "Upscale and enhance this image to a higher resolution. "
            "Increase the detail and sharpness while maintaining natural appearance. "
            "Fill in fine details intelligently and reduce any pixelation or blur."
        ),
        description="Increase resolution intelligently",
        aliases=["resize", "enlarge", "hd"],
    ),
    Template(
        name="vintage",
        prompt=(
            "Apply a vintage film photography effect to this image. "
            "Add subtle film grain, slightly faded colors, warm tones, "
            "and a nostalgic aesthetic reminiscent of photos from the 1970s-80s."
        ),
        description="Apply vintage/retro film effect",
        aliases=["retro", "film", "old-photo"],
    ),
    Template(
        name="sepia",
        prompt=(
            "Convert this image to sepia tone. "
            "Apply a warm brownish tint throughout, "
            "creating a classic, antique photograph appearance."
        ),
        description="Apply sepia tone effect",
        aliases=["brown", "antique"],
    ),
    Template(
        name="sharpen",
        prompt=(
            "Sharpen this image to increase clarity and detail. "
            "Enhance edges and fine details while avoiding artifacts. "
            "Make the image appear crisper and more defined."
        ),
        description="Sharpen and increase clarity",
        aliases=["crisp", "clarity"],
    ),
    Template(
        name="bw",
        prompt=(
            "Convert this image to black and white. "
            "Create a high-quality monochrome version with good tonal range, "
            "proper contrast, and artistic appeal."
        ),
        description="Convert to black and white",
        aliases=["blackwhite", "grayscale", "mono", "monochrome"],
    ),
    Template(
        name="blur-bg",
        prompt=(
            "Apply a professional depth-of-field blur to the background. "
            "Keep the main subject in sharp focus while creating a smooth, "
            "pleasing bokeh effect on the background. "
            "Make it look like a professional portrait photo."
        ),
        description="Blur background, keep subject sharp",
        aliases=["bokeh", "portrait-mode", "depth"],
    ),
    Template(
        name="cartoon",
        prompt=(
            "Transform this image into a cartoon or illustrated style. "
            "Simplify details, add bold outlines, and use vibrant, "
            "flat colors to create an animated/comic book appearance."
        ),
        description="Convert to cartoon/illustration style",
        aliases=["animate", "comic", "illustrated"],
    ),
    Template(
        name="watercolor",
        prompt=(
            "Transform this image into a watercolor painting style. "
            "Add soft, flowing brush strokes, subtle color bleeding, "
            "and the characteristic translucent quality of watercolor art."
        ),
        description="Apply watercolor painting effect",
        aliases=["painting", "artistic"],
    ),
]
