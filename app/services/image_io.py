from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageOps


def load_oriented_image(path: str | Path) -> Image.Image:
    """Load an image with camera/phone EXIF orientation applied."""
    image = Image.open(path)
    return ImageOps.exif_transpose(image).convert("RGBA")
