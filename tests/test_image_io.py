import tempfile
import unittest
from pathlib import Path

from PIL import Image

from app.services.image_io import load_oriented_image


class ImageIoTests(unittest.TestCase):
    def test_exif_orientation_is_applied(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rotated.jpg"
            source = Image.new("RGB", (40, 20), "white")
            exif = Image.Exif()
            exif[274] = 6  # Rotate 90 degrees clockwise for display.
            source.save(path, "JPEG", exif=exif)

            loaded = load_oriented_image(path)

            self.assertEqual(loaded.size, (20, 40))


if __name__ == "__main__":
    unittest.main()
