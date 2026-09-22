import unittest

from app.presets import PRESETS, StudioPreset, presets_for
from app.prompt_engine import LookSettings, SubjectLocks, build_prompt


class PromptEngineTests(unittest.TestCase):
    def test_preset_ids_are_unique(self):
        ids = [preset.id for preset in PRESETS]
        self.assertEqual(len(ids), len(set(ids)))

    def test_subject_locks_and_look_are_composed(self):
        preset = StudioPreset(
            id="test",
            name="Test",
            mode="Retouch",
            category="Test",
            prompt="Clean the selected area.",
            strict_composite=False,
        )
        prompt = build_prompt(
            preset,
            custom_instruction="keep the result subtle",
            locks=SubjectLocks(face=True, hair=False, body=True, pose=True, clothing=False, skin_tone=True),
            look=LookSettings(lens="85mm", lighting="Golden Hour", depth="Shallow depth of field"),
        )
        self.assertIn("facial identity", prompt)
        self.assertIn("85mm lens look", prompt)
        self.assertIn("Golden Hour", prompt)
        self.assertIn("keep the result subtle", prompt)

    def test_expanded_catalog_contains_magic_brush_friendly_modes(self):
        self.assertTrue(presets_for("Dress & Fabric"))
        self.assertTrue(presets_for("Retouch"))
        self.assertTrue(presets_for("Interior"))


if __name__ == "__main__":
    unittest.main()
