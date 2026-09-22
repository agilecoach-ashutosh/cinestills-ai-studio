import tempfile
import unittest
from io import BytesIO
from pathlib import Path

from PIL import Image

from app.services.mask_ops import apply_edit_mask


class MaskOpsTests(unittest.TestCase):
    def test_only_masked_area_uses_generated_pixels(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_path = root / "source.png"
            mask_path = root / "mask.png"

            Image.new("RGB", (100, 100), "white").save(source_path)
            generated = Image.new("RGB", (100, 100), "black")
            buffer = BytesIO()
            generated.save(buffer, "PNG")

            mask = Image.new("L", (100, 100), 0)
            for y in range(25, 75):
                for x in range(25, 75):
                    mask.putpixel((x, y), 255)
            mask.save(mask_path)

            result = apply_edit_mask(
                source_path=source_path,
                generated_bytes=buffer.getvalue(),
                mask_path=mask_path,
                feather_radius=0,
            )

            self.assertEqual(result.getpixel((5, 5)), (255, 255, 255))
            self.assertEqual(result.getpixel((50, 50)), (0, 0, 0))


if __name__ == "__main__":
    unittest.main()
