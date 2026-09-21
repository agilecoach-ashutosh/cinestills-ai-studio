from dataclasses import dataclass


@dataclass(frozen=True)
class EditRecipe:
    name: str
    prompt: str
    identity_mode: str = "STRICT"


RECIPES = [
    EditRecipe(
        "Executive Office",
        "Replace only the background with a premium modern executive office, floor-to-ceiling windows, natural daylight, photorealistic. Keep the person unchanged.",
    ),
    EditRecipe(
        "Theatre Stage",
        "Replace only the background with a professional theatre stage, subtle dramatic lighting, realistic depth and shadows. Keep the person unchanged.",
    ),
    EditRecipe(
        "Natural Outdoor",
        "Replace only the background with a natural outdoor setting, soft daylight, realistic depth of field. Keep the person unchanged.",
    ),
    EditRecipe(
        "Neutral Studio",
        "Replace only the background with a clean neutral professional studio backdrop, soft balanced light. Keep the person unchanged.",
    ),
]
