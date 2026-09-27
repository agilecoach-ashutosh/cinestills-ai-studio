from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter


class FaceLockError(RuntimeError):
    """Raised when Exact Face Lock cannot safely locate a face."""


@dataclass(frozen=True)
class FaceRegion:
    x: int
    y: int
    width: int
    height: int


def detect_primary_face(image: Image.Image) -> FaceRegion:
    """Detect the largest visible frontal face using OpenCV's local cascade."""
    rgb = np.asarray(image.convert("RGB"))
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    faces = cascade.detectMultiScale(
        gray,
        scaleFactor=1.08,
        minNeighbors=5,
        minSize=(max(32, image.width // 20), max(32, image.height // 20)),
    )
    if len(faces) == 0:
        raise FaceLockError(
            "Exact Face Lock could not find a clear frontal face. Use a sharper, front-facing "
            "portrait; CineStills stopped rather than risk changing the person's identity."
        )
    x, y, width, height = max(faces, key=lambda item: int(item[2]) * int(item[3]))
    return FaceRegion(int(x), int(y), int(width), int(height))


def create_face_lock_mask(image: Image.Image, region: FaceRegion | None = None) -> Image.Image:
    """Create a feathered oval that preserves the identity-bearing face interior."""
    region = region or detect_primary_face(image)
    side = int(region.width * 0.08)
    top = int(region.height * 0.16)
    bottom = int(region.height * 0.10)
    bounds = (
        max(0, region.x - side),
        max(0, region.y - top),
        min(image.width, region.x + region.width + side),
        min(image.height, region.y + region.height + bottom),
    )
    mask = Image.new("L", image.size, 0)
    ImageDraw.Draw(mask).ellipse(bounds, fill=255)
    feather = max(3.0, min(region.width, region.height) * 0.055)
    return mask.filter(ImageFilter.GaussianBlur(radius=feather))


def preserve_original_face(
    original: Image.Image,
    generated: Image.Image,
    region: FaceRegion | None = None,
) -> Image.Image:
    """Restore source face pixels after generation while softly blending the edge."""
    original = original.convert("RGB")
    generated = generated.convert("RGB").resize(original.size, Image.Resampling.LANCZOS)
    return Image.composite(original, generated, create_face_lock_mask(original, region))
