import unittest

from app.presets import PRESETS, StudioPreset, modes, presets_for
from app.prompt_engine import (
    LookSettings,
    PROTECTED_START,
    SubjectLocks,
    build_prompt,
    finalize_prompt,
)


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

    def test_public_catalog_is_portrait_focused(self):
        self.assertEqual(
            modes(),
            [
                "Change Background",
                "Complete Redesign",
                "Change Outfit",
                "Lighting & Mood",
                "Professional Portrait",
                "Professional Skin Retouching",
                "Enhance & Restore",
            ],
        )
        self.assertTrue(presets_for("Complete Redesign"))
        self.assertTrue(presets_for("Professional Skin Retouching"))

    def test_keyword_becomes_context_aware_background_direction(self):
        preset = presets_for("Change Background")[0]
        prompt = build_prompt(preset, keyword="Kashmir")
        self.assertIn("Kashmir", prompt)
        self.assertIn("light direction", prompt)
        self.assertIn("depth of field", prompt)

    def test_user_edits_survive_while_identity_guard_is_rebuilt(self):
        preset = presets_for("Complete Redesign")[0]
        edited = "My own final creative direction without the generated guard."
        final = finalize_prompt(edited, preset)
        self.assertIn(edited, final)
        self.assertIn(PROTECTED_START, final)
        self.assertIn("same recognisable person", final)


if __name__ == "__main__":
    unittest.main()
