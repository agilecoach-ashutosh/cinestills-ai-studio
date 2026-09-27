import unittest

import numpy as np
from PIL import Image

from app.services.face_lock import FaceRegion, create_face_lock_mask, preserve_original_face


class FaceLockTests(unittest.TestCase):
    def test_face_center_is_restored_and_background_remains_generated(self):
        original = Image.new("RGB", (200, 200), "red")
        generated = Image.new("RGB", (200, 200), "blue")
        region = FaceRegion(70, 55, 60, 75)

        result = preserve_original_face(original, generated, region)

        self.assertEqual(result.getpixel((100, 90)), (255, 0, 0))
        self.assertEqual(result.getpixel((10, 10)), (0, 0, 255))

    def test_mask_is_soft_and_localized(self):
        image = Image.new("RGB", (200, 200), "white")
        mask = create_face_lock_mask(image, FaceRegion(70, 55, 60, 75))

        self.assertEqual(mask.getpixel((100, 90)), 255)
        self.assertEqual(mask.getpixel((10, 10)), 0)
        edge_values = np.asarray(mask.crop((60, 40, 140, 150)))
        self.assertTrue(np.any((edge_values > 0) & (edge_values < 255)))


if __name__ == "__main__":
    unittest.main()
