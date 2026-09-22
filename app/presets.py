from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StudioPreset:
    id: str
    name: str
    mode: str
    category: str
    prompt: str
    strict_composite: bool = True
    tags: tuple[str, ...] = ()


PRESETS: tuple[StudioPreset, ...] = (
    # Studio backgrounds
    StudioPreset(
        "paper-white",
        "White Paper Backdrop",
        "Background",
        "Studio Paper",
        "Replace the background with a seamless pure white paper cyclorama, subtle natural paper texture, soft studio lighting, gentle floor-to-wall gradient, clean high-end editorial portrait look, realistic floor shadow.",
        True,
        ("studio", "white", "paper", "portrait"),
    ),
    StudioPreset(
        "paper-beige",
        "Warm Beige Paper",
        "Background",
        "Studio Paper",
        "Replace the background with a seamless warm beige paper cyclorama, subtle fine paper texture, soft diffused studio lighting, delicate tonal gradient, natural floor shadow, sophisticated luxury fashion editorial aesthetic.",
        True,
        ("studio", "beige", "paper", "fashion"),
    ),
    StudioPreset(
        "paper-gray",
        "Light Gray Paper",
        "Background",
        "Studio Paper",
        "Replace the background with a seamless light-gray paper roll cyclorama, matte paper texture, soft directional studio lighting, gentle gray gradient, controlled natural floor shadow, premium editorial fashion photography aesthetic.",
        True,
        ("studio", "gray", "paper"),
    ),
    StudioPreset(
        "paper-pink",
        "Pink Paper Backdrop",
        "Background",
        "Studio Paper",
        "Replace the background with a smooth plain pink paper backdrop for portraits, soft studio light, subtle natural shadow falloff and a clean premium photography-studio finish.",
        True,
        ("studio", "pink", "paper", "portrait"),
    ),
    StudioPreset(
        "white-gobo",
        "White + Circular GOBO",
        "Background",
        "Studio Paper",
        "Replace the background with a seamless pure white paper cyclorama and a large soft circular GOBO light projection behind the subject, perfectly round diffused pool of light with feathered edges, subtle paper texture and realistic floor shadow.",
        True,
        ("studio", "white", "gobo", "light"),
    ),
    StudioPreset(
        "lowkey-black",
        "Black Low-Key Spotlight",
        "Background",
        "Low Key",
        "Replace the background with a deep black low-key portrait studio, a single soft-edged circular spotlight on the backdrop, warm golden ambient glow, smooth light falloff, premium commercial portrait aesthetic.",
        True,
        ("black", "low-key", "spotlight"),
    ),
    StudioPreset(
        "warm-bokeh",
        "Warm Bokeh Lights",
        "Background",
        "Low Key",
        "Replace the background with a dark dreamy portrait scene with warm defocused lights and elegant bokeh, soft magical light on the scene, realistic depth and restrained premium styling.",
        True,
        ("bokeh", "warm", "portrait"),
    ),
    # Indoor
    StudioPreset(
        "cozy-living",
        "Cozy Living Room",
        "Background",
        "Indoor",
        "Replace the background with a cozy premium living room, tasteful neutral furnishings, soft curtains, warm natural window light and realistic interior depth, keeping the composition suitable for a portrait.",
        True,
        ("living-room", "indoor", "cozy"),
    ),
    StudioPreset(
        "boho",
        "Boho Studio",
        "Background",
        "Indoor",
        "Replace the background with an elegant boho photography setup using woven rugs, pampas grass, cane accents, warm earthy tones and soft natural-looking studio light, photorealistic and uncluttered.",
        True,
        ("boho", "pampas", "cane"),
    ),
    StudioPreset(
        "window-silk",
        "Window + Sheer Curtains",
        "Background",
        "Indoor",
        "Replace the background with a bright living-room window covered by transparent silk curtains, soft daylight entering from outside, delicate highlights and realistic interior shadows, minimal elegant styling.",
        True,
        ("window", "curtains", "daylight"),
    ),
    # Outdoor
    StudioPreset(
        "golden-meadow",
        "Golden Meadow Dream",
        "Background",
        "Outdoor",
        "Replace the background with a photorealistic golden meadow, tall wild grass, scattered yellow and white wildflowers, warm low sunlight, distant blurred tree line, creamy natural bokeh and cinematic depth.",
        True,
        ("meadow", "flowers", "golden-hour"),
    ),
    StudioPreset(
        "floral-arch",
        "Floral Arch Garden",
        "Background",
        "Outdoor",
        "Replace the background with a beautiful garden pathway framed by a natural arch of blooming pink and white flowers, dense greenery, soft sunlight through leaves, scattered petals and dreamy photorealistic depth.",
        True,
        ("garden", "flower-arch", "spring"),
    ),
    StudioPreset(
        "forest-rays",
        "Forest Light Rays",
        "Background",
        "Outdoor",
        "Replace the background with a dense green forest of tall trees, dramatic natural sun rays through branches, soft atmospheric mist, moss-covered ground and realistic cinematic depth.",
        True,
        ("forest", "sun-rays", "mist"),
    ),
    StudioPreset(
        "riverside",
        "Riverside Serenity",
        "Background",
        "Outdoor",
        "Replace the background with a peaceful riverside landscape, clear reflective water, pebbled shore, overhanging branches, soft diffused sunlight and a softly blurred forest in the distance.",
        True,
        ("river", "water", "nature"),
    ),
    StudioPreset(
        "blossom-path",
        "Spring Blossom Path",
        "Background",
        "Outdoor",
        "Replace the background with a pathway lined by blossom trees in full bloom, soft pink petals in the air, pastel natural tones, dreamy sunlight and realistic shallow depth of field.",
        True,
        ("blossom", "path", "spring"),
    ),
    StudioPreset(
        "evening-lights",
        "Evening Garden Lights",
        "Background",
        "Outdoor",
        "Replace the background with a garden at dusk, warm fairy lights hanging between trees, subtle lantern glow, deep green foliage and cinematic bokeh, photorealistic and cozy.",
        True,
        ("garden", "fairy-lights", "dusk"),
    ),
    StudioPreset(
        "beach-sunset",
        "Beach Sunset",
        "Background",
        "Cinematic Outdoor",
        "Replace the background with a sunset beach, orange and pink sky, soft waves, reflective water and warm cinematic atmosphere with natural wind and realistic depth.",
        True,
        ("beach", "sunset", "cinematic"),
    ),
    StudioPreset(
        "urban-night",
        "Urban Night",
        "Background",
        "Cinematic Outdoor",
        "Replace the background with a cinematic city street at night, tasteful neon accents, wet-road reflections, moody realistic lighting and deep photographic perspective.",
        True,
        ("city", "night", "neon"),
    ),
    StudioPreset(
        "epic-mountain",
        "Epic Mountain",
        "Background",
        "Cinematic Outdoor",
        "Replace the background with a cinematic mountain landscape, dramatic clouds, atmospheric perspective, natural cool tones, realistic high-dynamic-range light and professional travel-photography composition.",
        True,
        ("mountain", "travel", "cinematic"),
    ),
    # Kids / celebrations
    StudioPreset(
        "first-birthday",
        "Garden 1st Birthday",
        "Background",
        "Kids & Birthday",
        "Replace the background with an elegant first-birthday garden setup, white teepee, blue and white balloons, subtle fairy lights, outdoor lawn and pastel blue party decor, realistic professional photography.",
        True,
        ("kids", "birthday", "teepee"),
    ),
    StudioPreset(
        "kids-boho-tent",
        "Outdoor Boho Tent",
        "Background",
        "Kids & Birthday",
        "Replace the background with a sunny outdoor kids setup featuring a tasteful boho tent, simple toy props, soft grass and warm natural light, photorealistic and uncluttered.",
        True,
        ("kids", "boho", "tent"),
    ),
    # Creative effects that still preserve the visible person
    StudioPreset(
        "magic-butterflies",
        "Magical Forest Butterflies",
        "Creative",
        "Fantasy",
        "Transform the surrounding scene into a magical photorealistic forest with warm glow and small golden neon-like butterflies flying outward near the subject's hands, artistic but believable light integration.",
        True,
        ("forest", "butterflies", "fantasy"),
    ),
    StudioPreset(
        "moon-scene",
        "Moon Portrait",
        "Creative",
        "Fantasy",
        "Transform the surrounding scene into a dramatic night portrait with a large luminous moon placed naturally behind the subject, realistic atmospheric depth, balanced cool tones and cinematic rim light.",
        True,
        ("moon", "night", "portrait"),
    ),
    StudioPreset(
        "water-reflection",
        "Water Reflection Scene",
        "Creative",
        "Reflection",
        "Create a cinematic surrounding scene with a subtle reflective water surface below the subject, realistic reflections, soft environmental light and natural integration with the existing pose.",
        True,
        ("water", "reflection", "cinematic"),
    ),
    # Wardrobe / fabric. Do not strict-composite because it would erase the edit.
    StudioPreset(
        "extend-gown",
        "Extend Gown",
        "Dress & Fabric",
        "Gown",
        "Extend the existing gown downward naturally to cover more of the floor, matching the exact existing fabric color, material, folds, lighting and perspective. Keep the face, hair, skin tone, upper body, hands and pose unchanged.",
        False,
        ("gown", "extend", "fabric"),
    ),
    StudioPreset(
        "gown-flare",
        "Add Elegant Gown Flare",
        "Dress & Fabric",
        "Gown",
        "Extend the existing gown with an elegant wide flowing flare across the floor, preserving the original dress design and fabric, with realistic folds, weight, shadows and scene-consistent lighting. Preserve the person's identity and pose.",
        False,
        ("gown", "flare", "fabric"),
    ),
    StudioPreset(
        "butterfly-gown",
        "Butterfly Gown Shape",
        "Dress & Fabric",
        "Gown",
        "Extend the lower gown fabric into a graceful butterfly-inspired floor shape while matching the original dress color, material, lighting and perspective. Preserve the face, hair, skin tone, body and pose.",
        False,
        ("gown", "butterfly", "creative"),
    ),
    StudioPreset(
        "smooth-dress",
        "Smooth Dress Wrinkles",
        "Retouch",
        "Clothing",
        "Remove distracting wrinkles from the dress while preserving its material texture, seams, natural folds, lighting, color and shape. Do not alter the person's face, body, hair, hands or background.",
        False,
        ("retouch", "dress", "wrinkles"),
    ),
    StudioPreset(
        "hair-cleanup",
        "Hair Edge Cleanup",
        "Retouch",
        "Hair",
        "Clean and smooth stray hair along the outer hair border, remove only distracting flyaway strands and blend the edge naturally into the existing background. Preserve hairstyle, face and all other image content.",
        False,
        ("retouch", "hair", "cleanup"),
    ),
    # Props / product / interiors
    StudioPreset(
        "add-flower-arch",
        "Add Circular Flower Arch",
        "Add / Remove",
        "Props",
        "Add an elegant circular flower arch behind the subject, positioned naturally in perspective and matching the existing light direction, color temperature and scene depth. Do not alter the subject.",
        True,
        ("flowers", "arch", "prop"),
    ),
    StudioPreset(
        "add-fog",
        "Add Soft Fog",
        "Add / Remove",
        "Atmosphere",
        "Add subtle realistic cinematic fog in the surrounding environment, keeping the subject clearly visible and matching the existing lighting, depth and perspective. Do not alter the subject.",
        True,
        ("fog", "atmosphere", "cinematic"),
    ),
    StudioPreset(
        "product-white",
        "Product White Paper",
        "Product",
        "Product Studio",
        "Place the product in a premium seamless white paper-backdrop studio, clean cyclorama curve, soft directional commercial lighting, tasteful realistic shadow and minimal high-end product-photography styling.",
        False,
        ("product", "white", "studio"),
    ),
    StudioPreset(
        "product-dramatic",
        "Product Dark Dramatic",
        "Product",
        "Product Studio",
        "Place the product in a dark premium commercial studio with a smooth black backdrop, subtle atmospheric haze, controlled dramatic lighting and realistic contact shadows, keeping the product shape and branding intact.",
        False,
        ("product", "dark", "commercial"),
    ),
)


def modes() -> list[str]:
    return list(dict.fromkeys(p.mode for p in PRESETS))


def categories_for_mode(mode: str) -> list[str]:
    return list(dict.fromkeys(p.category for p in PRESETS if p.mode == mode))


def presets_for(mode: str, category: str | None = None) -> list[StudioPreset]:
    return [
        p for p in PRESETS
        if p.mode == mode and (category is None or p.category == category)
    ]
