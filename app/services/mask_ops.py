from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps


def apply_edit_mask(
    source_path: str | Path,
    generated_bytes: bytes,
    mask_path: str | Path,
    feather_radius: float = 5.0,
) -> Image.Image:
    """Return source pixels everywhere except the user-painted edit area."""
    source = ImageOps.exif_transpose(Image.open(source_path)).convert("RGB")
    generated = Image.open(BytesIO(generated_bytes)).convert("RGB")
    generated = generated.resize(source.size, Image.Resampling.LANCZOS)

    mask = Image.open(mask_path).convert("L")
    mask = mask.resize(source.size, Image.Resampling.LANCZOS)
    if feather_radius > 0:
        mask = mask.filter(ImageFilter.GaussianBlur(radius=feather_radius))

    return Image.composite(generated, source, mask)
