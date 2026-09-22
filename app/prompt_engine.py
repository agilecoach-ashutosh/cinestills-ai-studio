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


def build_prompt(
    preset: StudioPreset,
    custom_instruction: str = "",
    locks: SubjectLocks | None = None,
    look: LookSettings | None = None,
) -> str:
    locks = locks or SubjectLocks()
    look = look or LookSettings()

    preserve: list[str] = []
    if locks.face:
        preserve.append("facial identity and facial geometry")
    if locks.hair:
        preserve.append("hairstyle unless the selected edit explicitly targets hair")
    if locks.body:
        preserve.append("body proportions and visible anatomy")
    if locks.pose:
        preserve.append("pose, camera angle and subject position")
    if locks.clothing:
        preserve.append("existing clothing unless the selected edit explicitly targets clothing")
    if locks.skin_tone:
        preserve.append("natural skin tone")

    sections = [
        "Photorealistic professional photography edit.",
        preset.prompt,
    ]

    if preserve:
        sections.append("Preserve " + ", ".join(preserve) + ".")

    sections.append(
        "Do not create duplicate people, extra limbs, extra fingers, text, watermarks, "
        "unrequested accessories or unrelated objects."
    )

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

    if look_bits:
        sections.append("Photographic look: " + ", ".join(look_bits) + ".")

    custom_instruction = custom_instruction.strip()
    if custom_instruction:
        sections.append("Additional instruction: " + custom_instruction)

    return "\n\n".join(sections)
