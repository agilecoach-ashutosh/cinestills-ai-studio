from __future__ import annotations

from dataclasses import dataclass
import re

from app.presets import StudioPreset


PROTECTED_START = "[IDENTITY LOCK - PROTECTED]"
PROTECTED_END = "[/IDENTITY LOCK]"


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
            "setting, props, lighting and photographic era while retaining the same person."
        )
    if preset.mode == "Change Outfit":
        return (
            f"Use {keyword} as the wardrobe direction. Make the garment photorealistic, correctly "
            "fitted to the existing body and pose, with source-matched fabric light and shadows."
        )
    return f"Use {keyword} as the creative direction while keeping the result photographic and coherent."


def identity_guard_text(preset: StudioPreset, locks: SubjectLocks | None = None) -> str:
    locks = locks or SubjectLocks()
    preserve: list[str] = []
    if locks.face:
        preserve.append("the same recognisable person, facial identity and facial geometry")
    if locks.hair:
        preserve.append("hairstyle unless this selected transformation explicitly changes hair")
    if locks.body:
        preserve.append("body proportions and anatomically correct visible features")
    if locks.pose:
        preserve.append("pose, camera angle and subject position")
    if locks.clothing:
        preserve.append("existing clothing unless this selected transformation changes clothing")
    if locks.skin_tone:
        preserve.append("natural complexion and skin tone without whitening")

    strategy = (
        "Keep the original subject pixels unchanged and composite them over the new scene."
        if preset.strict_composite
        else "Use the source face as the primary identity reference and do not invent a different face."
    )
    details = "Preserve " + ", ".join(preserve) + "." if preserve else ""
    return " ".join(
        part for part in (
            strategy,
            details,
            "Keep both eyes, nose, lips, jawline and distinctive permanent features consistent.",
            "Do not create duplicate people, extra limbs, extra fingers, distorted anatomy, text or watermarks.",
        ) if part
    )


def build_prompt(
    preset: StudioPreset,
    custom_instruction: str = "",
    locks: SubjectLocks | None = None,
    look: LookSettings | None = None,
    keyword: str = "",
) -> str:
    locks = locks or SubjectLocks()
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

    creative = "\n\n".join(sections)
    return f"{creative}\n\n{PROTECTED_START}\n{identity_guard_text(preset, locks)}\n{PROTECTED_END}"


def strip_identity_block(prompt: str) -> str:
    pattern = re.compile(
        re.escape(PROTECTED_START) + r".*?" + re.escape(PROTECTED_END),
        flags=re.DOTALL,
    )
    return pattern.sub("", prompt).strip()


def finalize_prompt(
    edited_prompt: str,
    preset: StudioPreset,
    locks: SubjectLocks | None = None,
) -> str:
    """Respect user edits while always rebuilding the protected identity block."""
    creative = strip_identity_block(edited_prompt)
    return f"{creative}\n\n{PROTECTED_START}\n{identity_guard_text(preset, locks)}\n{PROTECTED_END}"
