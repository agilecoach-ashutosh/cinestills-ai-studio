from __future__ import annotations

from dataclasses import dataclass

from app.presets import StudioPreset


@dataclass(frozen=True)
class SubjectLocks:
    face: bool = True
    hair: bool = True
    body: bool = True
    pose: bool = True
    clothing: bool = True
    skin_tone: bool = True


@dataclass(frozen=True)
class LookSettings:
    lens: str = "Natural"
    lighting: str = "Match Source"
    depth: str = "Natural"
    color_grade: str = "Natural"
    texture: str = "Clean"
    intensity: str = "Natural"


def _keyword_instruction(preset: StudioPreset, keyword: str) -> str:
    keyword = keyword.strip()
    if not keyword:
        return ""

    if preset.mode == "Background":
        return (
            f"Use {keyword} as the new environment. Interpret the idea as a believable "
            "professional portrait background. Match the source camera height, perspective, "
            "focal length, light direction, colour temperature, depth of field, contact shadows "
            "and atmospheric depth so the subject belongs naturally in the scene."
        )
    if preset.mode == "Complete Redesign":
        return (
            f"Use {keyword} as the creative direction and translate it into a coherent wardrobe, "
            "setting, props, lighting and photographic era."
        )
    if preset.mode == "Change Outfit":
        return (
            f"Use {keyword} as the wardrobe direction. Make the garment photorealistic with "
            "believable fabric, light and shadows."
        )
    return f"Use {keyword} as the creative direction while keeping the result photographic and coherent."


def build_prompt(
    preset: StudioPreset,
    custom_instruction: str = "",
    locks: SubjectLocks | None = None,
    look: LookSettings | None = None,
    keyword: str = "",
) -> str:
    look = look or LookSettings()

    sections = ["Photorealistic professional portrait edit.", preset.prompt]
    keyword_text = _keyword_instruction(preset, keyword)
    if keyword_text:
        sections.append(keyword_text)

    look_bits: list[str] = []
    if look.lens != "Natural":
        look_bits.append(f"{look.lens} lens look")
    if look.lighting != "Match Source":
        look_bits.append(look.lighting)
    if look.depth != "Natural":
        look_bits.append(look.depth)
    if look.color_grade != "Natural":
        look_bits.append(f"{look.color_grade} color grading")
    if look.texture != "Clean":
        look_bits.append(look.texture)
    if look.intensity != "Natural":
        look_bits.append(f"{look.intensity.lower()} transformation strength")
    if look_bits:
        sections.append("Photographic look: " + ", ".join(look_bits) + ".")

    custom_instruction = custom_instruction.strip()
    if custom_instruction:
        sections.append("Additional direction: " + custom_instruction)

    return "\n\n".join(sections)


def finalize_prompt(
    edited_prompt: str,
    preset: StudioPreset,
    locks: SubjectLocks | None = None,
) -> str:
    """Return exactly the visible prompt; generation adds no hidden instructions."""
    return edited_prompt.strip()
