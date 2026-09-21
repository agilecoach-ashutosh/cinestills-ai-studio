from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps
from rembg import remove


def prepare_working_image(
    source_path: str | Path,
    destination: str | Path,
    max_side: int = 1024,
) -> tuple[int, int]:
    """Create an Invoke-friendly PNG while preserving the source aspect ratio."""
    image = ImageOps.exif_transpose(Image.open(source_path)).convert("RGB")
    working = image.copy()
    working.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)

    width = max(64, (working.width // 8) * 8)
    height = max(64, (working.height // 8) * 8)
    if (width, height) != working.size:
        working = working.resize((width, height), Image.Resampling.LANCZOS)

    Path(destination).parent.mkdir(parents=True, exist_ok=True)
    working.save(destination, "PNG")
    return working.size


def create_subject_mask(image: Image.Image) -> Image.Image:
    """Return a soft white-subject/black-background mask generated locally."""
    mask = remove(image, only_mask=True)

    if isinstance(mask, bytes):
        mask = Image.open(BytesIO(mask))
    if not isinstance(mask, Image.Image):
        raise RuntimeError("Local subject segmentation did not return an image mask.")

    mask = mask.convert("L")
    # Protect a few pixels around hair/clothing edges, then feather the transition.
    mask = mask.filter(ImageFilter.MaxFilter(7))
    mask = mask.filter(ImageFilter.GaussianBlur(radius=2.0))
    return mask


def preserve_original_subject(
    source_path: str | Path,
    generated_bytes: bytes,
    destination: str | Path,
) -> str:
    """Composite original subject pixels over the AI-generated scene.

    The face and body come from the source photograph, not regenerated pixels.
    """
    original = ImageOps.exif_transpose(Image.open(source_path)).convert("RGB")
    generated = Image.open(BytesIO(generated_bytes)).convert("RGB")
    generated = generated.resize(original.size, Image.Resampling.LANCZOS)

    subject_mask = create_subject_mask(original)
    final = Image.composite(original, generated, subject_mask)

    output_path = Path(destination)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    final.save(output_path, "PNG")
    return str(output_path)
