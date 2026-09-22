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
    summary: str = ""
    changes: tuple[str, ...] = ()
    requires_mask: bool = False
    accent: str = "#D7FF00"


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

    # Expanded studio / portrait presets from the working prompt library.
    StudioPreset(
        "paper-pink-reflective",
        "Pink Reflective Floor",
        "Background",
        "Studio Paper",
        "Replace the background with a smooth plain pink studio backdrop and a clean reflective fiberglass floor, subtle realistic reflection beneath the subject, soft studio lighting and premium portrait finish.",
        True,
        ("pink", "reflection", "studio"),
    ),
    StudioPreset(
        "paper-pink-clouds",
        "Pink Clouds + Smoke",
        "Background",
        "Studio Creative",
        "Replace the background with a smooth plain pink portrait backdrop with restrained soft clouds and atmospheric smoke, clean studio depth and realistic light integration.",
        True,
        ("pink", "clouds", "smoke"),
    ),
    StudioPreset(
        "paper-pink-silk",
        "Pink Flowing Silk",
        "Background",
        "Studio Creative",
        "Replace the background with a smooth pink portrait studio filled with elegant flowing silk curtains, soft layered fabric depth and clean diffused photography lighting.",
        True,
        ("pink", "silk", "fabric"),
    ),
    StudioPreset(
        "canvas-neutral",
        "Neutral Canvas Fabric",
        "Background",
        "Studio Paper",
        "Replace the background with a premium neutral canvas-fabric portrait backdrop, subtle woven texture, soft directional studio light and natural floor shadow.",
        True,
        ("canvas", "neutral", "studio"),
    ),
    StudioPreset(
        "gray-moon-light",
        "Gray Studio + Moon Light",
        "Background",
        "Studio Creative",
        "Replace the background with a clean gray studio backdrop in a premium editorial setup, adding a large perfectly round warm-white illuminated circle behind the subject and a subtle reflective floor.",
        True,
        ("gray", "moon", "editorial"),
    ),
    StudioPreset(
        "christmas-bokeh",
        "Christmas Bokeh Lights",
        "Background",
        "Low Key",
        "Replace the background with a dark portrait scene using warm Christmas-tree lights rendered as elegant soft bokeh, realistic depth and flattering low-key illumination.",
        True,
        ("christmas", "bokeh", "lights"),
    ),
    StudioPreset(
        "boho-flower-arch",
        "Boho Flower Arch",
        "Background",
        "Indoor",
        "Replace the background with an indoor boho maternity-style setup featuring an elegant flower arch, cane and woven accents, pampas elements and warm soft studio light.",
        True,
        ("boho", "flower-arch", "maternity"),
    ),
    StudioPreset(
        "boho-cane-chairs",
        "Boho Cane Chair Studio",
        "Background",
        "Indoor",
        "Replace the background with a warm boho studio containing a tasteful golden cage chair and a natural cane chair, woven textures, neutral styling and soft portrait light.",
        True,
        ("boho", "cane", "chair"),
    ),

    # Expanded outdoor scene library.
    StudioPreset(
        "garden-swing",
        "Garden Swing",
        "Background",
        "Outdoor",
        "Replace the background with a lush garden and an aesthetic wooden swing hanging from a large tree branch, decorated with pastel flowers and flowing fabric, warm sunlight and dreamy natural bokeh.",
        True,
        ("garden", "swing", "flowers"),
    ),
    StudioPreset(
        "flower-field-bicycle",
        "Flower Field + Vintage Bicycle",
        "Background",
        "Outdoor",
        "Replace the background with a wide field of colorful flowers including lavender, daisies and sunflowers, with a vintage bicycle and flower basket placed naturally in the scene, warm sunlight and cinematic depth.",
        True,
        ("flowers", "bicycle", "field"),
    ),
    StudioPreset(
        "tropical-garden",
        "Tropical Garden",
        "Background",
        "Outdoor",
        "Replace the background with a lush tropical garden, large palm leaves, exotic red and orange flowers, layered greenery, slight atmospheric mist and rich photorealistic texture.",
        True,
        ("tropical", "garden", "greenery"),
    ),
    StudioPreset(
        "rain-kissed-garden",
        "Rain-Kissed Garden",
        "Background",
        "Outdoor",
        "Replace the background with a fresh garden just after rainfall, wet leaves with droplets, subtly reflective ground, soft cloudy light and muted green cinematic tones.",
        True,
        ("rain", "garden", "wet"),
    ),
    StudioPreset(
        "rustic-countryside",
        "Rustic Countryside",
        "Background",
        "Outdoor",
        "Replace the background with open countryside, tall dry grass, a rustic wooden fence and a small flower cart, warm sunset tones and natural cinematic texture.",
        True,
        ("countryside", "rustic", "sunset"),
    ),
    StudioPreset(
        "rose-garden",
        "Rose Garden Depth",
        "Background",
        "Outdoor",
        "Replace the background with a dense rose garden using red, pink and white roses, softly blurred foreground flowers, clear subject space and deep natural bokeh.",
        True,
        ("rose", "garden", "bokeh"),
    ),
    StudioPreset(
        "garden-picnic",
        "Garden Picnic Setup",
        "Background",
        "Outdoor",
        "Replace the background with a green park picnic setup using a blanket, basket, fruits, flowers and books arranged tastefully, soft sunlight and relaxed lifestyle-photography depth.",
        True,
        ("picnic", "garden", "lifestyle"),
    ),
    StudioPreset(
        "forest-stream",
        "Forest Stream + Stones",
        "Background",
        "Outdoor",
        "Replace the background with a photorealistic forest scene containing a gentle water stream, natural stones, moss, soft fog, flowering shrubs and filtered sunshine.",
        True,
        ("forest", "stream", "moss"),
    ),

    # Kids / birthday scene extensions.
    StudioPreset(
        "kids-balloon-tent",
        "Boho Tent + Balloons",
        "Background",
        "Kids & Birthday",
        "Replace the background with an outdoor scenic kids setup featuring a boho tent, tasteful toy props, balloons floating naturally and warm soft sunlight.",
        True,
        ("kids", "tent", "balloons"),
    ),
    StudioPreset(
        "kids-heart-balloons",
        "Heart Balloon Garden",
        "Background",
        "Kids & Birthday",
        "Replace the background with an outdoor scenic garden, tasteful toy props and red heart-shaped foil balloons floating and resting naturally on the ground, with soft realistic light.",
        True,
        ("kids", "heart", "balloons"),
    ),
    StudioPreset(
        "kids-sprinkler",
        "Garden Water Sprinkler",
        "Background",
        "Kids & Birthday",
        "Replace the background with a softly blurred outdoor garden scene with a water sprinkler in the distance, fresh greenery, natural summer light and playful photographic atmosphere.",
        True,
        ("kids", "sprinkler", "garden"),
    ),

    # Stage / traditional scene extensions.
    StudioPreset(
        "stage-guitar",
        "Live Guitar Stage",
        "Background",
        "Stage",
        "Replace the background with a professional live-performance stage for a guitarist, realistic stage depth, controlled spotlights, subtle haze and concert lighting that matches the subject.",
        True,
        ("stage", "guitar", "concert"),
    ),
    StudioPreset(
        "stage-drums",
        "Live Drum Stage",
        "Background",
        "Stage",
        "Replace the background with a professional live-performance stage suitable for a drummer, realistic stage depth, controlled spotlights, subtle haze and concert lighting.",
        True,
        ("stage", "drums", "concert"),
    ),
    StudioPreset(
        "traditional-night",
        "Traditional Night Scene",
        "Background",
        "Traditional",
        "Replace the background with a tasteful night-time traditional setting that matches the existing scene, using warm practical lights, realistic depth and restrained festive atmosphere.",
        True,
        ("traditional", "night", "warm"),
    ),

    # Localized wardrobe / fabric recipes.
    StudioPreset(
        "tossing-fabric",
        "Tossing Dress Fabric",
        "Dress & Fabric",
        "Fabric Motion",
        "Extend the selected dress fabric into a graceful tossed motion, matching the existing material, color, texture, folds, light direction and perspective while preserving the person's identity and anatomy.",
        False,
        ("dress", "fabric", "motion"),
    ),
    StudioPreset(
        "flowing-fabric",
        "Flowing Fabric",
        "Dress & Fabric",
        "Fabric Motion",
        "Create elegant flowing fabric from the selected garment area, matching the original cloth exactly and integrating realistic movement, folds, highlights and shadows without altering the face or body.",
        False,
        ("dress", "flowing", "fabric"),
    ),

    # Add / remove and atmospheric elements.
    StudioPreset(
        "add-marigold-diya",
        "Marigold + Diya",
        "Add / Remove",
        "Props",
        "Add tasteful marigold flowers and traditional diyas in the selected puja-thali or ceremonial area, matching the existing perspective, warm light and photographic realism.",
        False,
        ("marigold", "diya", "traditional"),
    ),
    StudioPreset(
        "add-fairy-bulbs",
        "Series Bulbs",
        "Add / Remove",
        "Atmosphere",
        "Add a tasteful series of warm decorative bulbs in the selected background area, with realistic bokeh, light spill and depth that matches the source photograph.",
        True,
        ("bulbs", "lights", "bokeh"),
    ),

    # Product-styling recipes.
    StudioPreset(
        "product-fruit-smoke",
        "White Studio + Fruit Smoke",
        "Product",
        "Product Studio",
        "Place the product on a seamless white paper backdrop with tastefully arranged fruits and subtle dreamy smoke in the foreground, premium commercial lighting and clean realistic shadows.",
        False,
        ("product", "fruit", "smoke"),
    ),
    StudioPreset(
        "product-vegetable-bowls",
        "Vegetable Bowl Styling",
        "Product",
        "Product Styling",
        "Style the selected product on a smooth plain paper backdrop with colorful vegetables arranged neatly in small white bowls, balanced commercial composition and realistic contact shadows.",
        False,
        ("product", "vegetables", "styling"),
    ),
    StudioPreset(
        "product-knife-peppers",
        "Knife + Bell Pepper Styling",
        "Product",
        "Product Styling",
        "Style the selected chopping-board product on a smooth plain paper backdrop with knives and bell peppers arranged cleanly around it, premium top-down commercial photography lighting.",
        False,
        ("product", "knife", "pepper"),
    ),
    StudioPreset(
        "product-cloth-topdown",
        "Top-Down Cloth Studio",
        "Product",
        "Product Styling",
        "Place the selected product on a smooth cloth backdrop in a top-down composition with tasteful green leaves, controlled dramatic lighting and premium commercial styling.",
        False,
        ("product", "top-down", "cloth"),
    ),

    # Interior / real-estate prop recipes.
    StudioPreset(
        "interior-tea-table",
        "Style Tea Table",
        "Interior",
        "Real Estate Props",
        "Add tasteful realistic accessories to the selected tea-table area, keeping the furniture, architecture, camera perspective and existing room lighting unchanged.",
        False,
        ("interior", "tea-table", "decor"),
    ),
    StudioPreset(
        "interior-bedroom-shelf",
        "Style Bedroom Shelf",
        "Interior",
        "Real Estate Props",
        "Add tasteful realistic accessories and decor to the selected bedroom-shelf area, matching the room style, scale, light direction and perspective.",
        False,
        ("interior", "bedroom", "shelf"),
    ),
    StudioPreset(
        "interior-kitchen-shelf",
        "Style Kitchen Shelf",
        "Interior",
        "Real Estate Props",
        "Add tasteful kitchen accessories and decor to the selected shelf area, keeping the kitchen architecture unchanged and matching existing light, scale and perspective.",
        False,
        ("interior", "kitchen", "shelf"),
    ),
    StudioPreset(
        "interior-workstation",
        "Style Workstation",
        "Interior",
        "Real Estate Props",
        "Add a realistic computer screen, keyboard and tasteful desk accessories to the selected workstation area, matching room perspective, reflections and existing lighting.",
        False,
        ("interior", "computer", "workstation"),
    ),

    # Complete portrait redesigns. These intentionally change scene and styling.
    StudioPreset(
        "redesign-vintage-motorsport", "Vintage Motorsport", "Complete Redesign", "Retro & Vintage",
        "Restyle the portrait as a polished mid-century motorsport editorial with a classic motorcycle, period-inspired wardrobe, warm neutral daylight, restrained pin-up influence and premium magazine composition.",
        False, ("retro", "motorcycle", "editorial"), "Mid-century fashion and classic motorcycle editorial.",
        ("outfit", "background", "props", "lighting"), False, "#E4B46A",
    ),
    StudioPreset(
        "redesign-80s-bollywood", "80s Bollywood", "Complete Redesign", "Retro & Vintage",
        "Reimagine the portrait as a glamorous 1980s Bollywood film still with era-appropriate Indian fashion, expressive cinematic lighting, rich film colour and an authentic period set.",
        False, ("80s", "bollywood", "film"), "Colourful 1980s Indian cinema styling.",
        ("outfit", "background", "hair", "lighting"), False, "#FF6F61",
    ),
    StudioPreset(
        "redesign-royal-heritage", "Royal Heritage", "Complete Redesign", "Indian Heritage",
        "Create a refined Indian royal portrait with heritage architecture, intricately styled traditional clothing, elegant jewellery, warm lamp light and dignified fine-art composition.",
        False, ("royal", "heritage", "india"), "Regal Indian fine-art portrait.",
        ("outfit", "background", "accessories", "lighting"), False, "#C9993A",
    ),
    StudioPreset(
        "redesign-future-fashion", "Future Fashion", "Complete Redesign", "Modern & Futuristic",
        "Create a sophisticated near-future fashion editorial with sculptural wardrobe, clean architectural forms, controlled cyan and amber accents and realistic high-end campaign lighting.",
        False, ("future", "fashion", "editorial"), "Premium futuristic fashion campaign.",
        ("outfit", "background", "lighting"), False, "#55D6E6",
    ),
    StudioPreset(
        "redesign-dark-academia", "Dark Academia", "Complete Redesign", "Cinematic",
        "Restyle the portrait in a dark-academia library with tailored vintage clothing, old books, dark wood, window light, subtle dust atmosphere and moody cinematic grading.",
        False, ("library", "vintage", "moody"), "Moody literary portrait with vintage tailoring.",
        ("outfit", "background", "props", "lighting"), False, "#8B6B4A",
    ),
    StudioPreset(
        "redesign-hollywood", "Hollywood Editorial", "Complete Redesign", "Cinematic",
        "Create a luxury Hollywood editorial portrait with immaculate styling, dramatic key light, subtle rim light, premium set design and restrained filmic colour.",
        False, ("hollywood", "luxury", "editorial"), "Luxury celebrity-magazine treatment.",
        ("outfit", "background", "lighting"), False, "#E5D7B8",
    ),
    StudioPreset(
        "redesign-fantasy-warrior", "Fantasy Warrior", "Complete Redesign", "Fantasy",
        "Transform the portrait into a photorealistic fantasy-warrior character with detailed practical costume, atmospheric landscape, cinematic rim light and believable materials rather than illustration.",
        False, ("fantasy", "warrior", "cinematic"), "Photorealistic cinematic character portrait.",
        ("outfit", "background", "props", "lighting"), False, "#7BA69A",
    ),
    StudioPreset(
        "redesign-festive-lights", "Festive Lights", "Complete Redesign", "Festival",
        "Create an elegant Indian festive portrait with refined traditional styling, marigold details, diyas, warm string-light bokeh and realistic celebratory ambience.",
        False, ("festival", "diya", "indian"), "Warm, elegant Indian festive transformation.",
        ("outfit", "background", "accessories", "lighting"), False, "#FF9F43",
    ),

    # Outfit transformations.
    StudioPreset(
        "outfit-executive-suit", "Executive Suit", "Change Outfit", "Professional",
        "Replace only the clothing with a perfectly fitted premium executive suit, realistic fabric, seams, folds and source-matched light. Keep face, hair, body, hands, pose and background unchanged.",
        False, ("suit", "executive", "formal"), "Premium business wardrobe.", ("outfit",), True, "#577590",
    ),
    StudioPreset(
        "outfit-elegant-saree", "Elegant Saree", "Change Outfit", "Indian Traditional",
        "Replace only the clothing with an elegant Indian saree draped naturally for the existing pose, realistic textile detail, folds and source-matched lighting. Preserve identity and anatomy.",
        False, ("saree", "traditional", "india"), "Graceful saree with realistic draping.", ("outfit",), True, "#D66D75",
    ),
    StudioPreset(
        "outfit-designer-lehenga", "Designer Lehenga", "Change Outfit", "Indian Traditional",
        "Replace only the clothing with a refined designer lehenga, tasteful embroidery, realistic weight and folds, fitted to the existing body and pose with matching light and shadows.",
        False, ("lehenga", "designer", "traditional"), "Detailed contemporary Indian occasion wear.", ("outfit",), True, "#B565A7",
    ),
    StudioPreset(
        "outfit-evening-gown", "Evening Gown", "Change Outfit", "Fashion",
        "Replace only the clothing with a sophisticated evening gown, realistic tailoring and flowing fabric, respecting the existing body, pose, hands, perspective and scene lighting.",
        False, ("gown", "fashion", "evening"), "Sophisticated full-length fashion styling.", ("outfit",), True, "#6C5B7B",
    ),
    StudioPreset(
        "outfit-smart-casual", "Smart Casual", "Change Outfit", "Everyday",
        "Replace only the clothing with polished smart-casual styling, natural fit, realistic fabric texture and source-matched light while retaining all other image content.",
        False, ("casual", "modern", "lifestyle"), "Modern, approachable everyday styling.", ("outfit",), True, "#4D908E",
    ),
    StudioPreset(
        "outfit-streetwear", "Editorial Streetwear", "Change Outfit", "Fashion",
        "Replace only the clothing with premium contemporary streetwear, layered styling, realistic fabric and fit, while preserving identity, pose, body shape, hands and background.",
        False, ("streetwear", "editorial", "fashion"), "Bold contemporary fashion layers.", ("outfit",), True, "#F9844A",
    ),

    # Lighting and mood.
    StudioPreset(
        "light-golden-hour", "Golden Hour", "Lighting & Mood", "Natural Light",
        "Relight the photograph with warm low golden-hour sunlight, soft directional highlights, believable shadow direction and subtle atmospheric warmth without changing identity or scene content.",
        False, ("golden-hour", "warm", "natural"), "Warm sunset-quality portrait light.", ("lighting", "colour"), False, "#F9C74F",
    ),
    StudioPreset(
        "light-soft-window", "Soft Window Light", "Lighting & Mood", "Natural Light",
        "Relight the portrait with large soft window light, gentle facial modelling, controlled highlights and natural shadow falloff while preserving all features and image content.",
        False, ("window", "soft", "portrait"), "Flattering natural window illumination.", ("lighting",), False, "#BDE0FE",
    ),
    StudioPreset(
        "light-low-key", "Low-Key Drama", "Lighting & Mood", "Studio Light",
        "Create a professional low-key portrait treatment with controlled dramatic key light, deep clean shadows and a subtle rim highlight while keeping facial identity and texture natural.",
        False, ("low-key", "dramatic", "studio"), "Dark, sculpted professional lighting.", ("lighting", "colour"), False, "#6D6875",
    ),
    StudioPreset(
        "light-neon", "Cinematic Neon", "Lighting & Mood", "Creative Light",
        "Relight the portrait with restrained cinematic cyan and magenta practical light, realistic colour spill and dimensional shadows without changing the person's features.",
        False, ("neon", "cinematic", "colour"), "Controlled cyan-magenta cinematic mood.", ("lighting", "colour"), False, "#B5179E",
    ),
    StudioPreset(
        "light-dreamy", "Dreamy Pastel", "Lighting & Mood", "Creative Light",
        "Create soft dreamy portrait lighting with delicate pastel highlights, airy contrast, natural skin and subtle glow while maintaining realistic detail and identity.",
        False, ("dreamy", "pastel", "soft"), "Airy pastel light with natural skin.", ("lighting", "colour"), False, "#F7CAD0",
    ),

    # Professional portrait outcomes.
    StudioPreset(
        "portrait-linkedin", "LinkedIn Headshot", "Professional Portrait", "Business",
        "Create a credible modern LinkedIn headshot with clean neutral background, flattering soft studio light, professional framing and authentic natural expression. Preserve identity exactly.",
        False, ("linkedin", "headshot", "business"), "Clean and approachable professional headshot.", ("background", "lighting", "crop"), False, "#4EA8DE",
    ),
    StudioPreset(
        "portrait-executive", "Executive Portrait", "Professional Portrait", "Business",
        "Create a premium executive portrait with confident composition, sophisticated dark-neutral environment, tailored professional styling and controlled editorial lighting.",
        False, ("executive", "leadership", "portrait"), "Leadership portrait with premium gravitas.", ("outfit", "background", "lighting"), False, "#4361EE",
    ),
    StudioPreset(
        "portrait-actor", "Actor Portfolio", "Professional Portrait", "Creative Portfolio",
        "Create a natural actor portfolio portrait with expressive eyes, authentic skin texture, simple wardrobe, uncluttered background and cinematic yet believable light.",
        False, ("actor", "portfolio", "natural"), "Expressive casting-style portfolio portrait.", ("background", "lighting", "crop"), False, "#90BE6D",
    ),
    StudioPreset(
        "portrait-fashion", "Fashion Editorial", "Professional Portrait", "Creative Portfolio",
        "Create a high-end fashion editorial portrait with refined styling, intentional composition, premium studio lighting, natural skin texture and magazine-quality colour.",
        False, ("fashion", "editorial", "magazine"), "High-fashion magazine finish.", ("outfit", "background", "lighting"), False, "#F94144",
    ),
    StudioPreset(
        "portrait-studio-classic", "Classic Studio", "Professional Portrait", "Studio",
        "Create a timeless studio portrait with a seamless neutral backdrop, soft key and fill light, subtle separation light and clean professional colour.",
        False, ("classic", "studio", "timeless"), "Timeless neutral studio portrait.", ("background", "lighting"), False, "#ADB5BD",
    ),

    # Professional skin retouching. These are intentionally conservative.
    StudioPreset(
        "retouch-natural", "Natural Cleanup", "Professional Skin Retouching", "Skin Finish",
        "Perform subtle professional skin cleanup: remove only temporary blemishes and minor distractions, gently balance uneven tone, control shine and preserve pores, fine texture, permanent features and natural complexion.",
        False, ("skin", "natural", "retouch"), "Invisible cleanup with real skin texture.", ("skin",), True, "#F6BD60",
    ),
    StudioPreset(
        "retouch-polished", "Polished Portrait", "Professional Skin Retouching", "Skin Finish",
        "Apply polished professional portrait retouching with restrained blemish cleanup, balanced tone, softened temporary under-eye darkness and controlled highlights while retaining pores and facial structure.",
        False, ("skin", "polished", "portrait"), "Refined finish without plastic smoothing.", ("skin",), True, "#F5CAC3",
    ),
    StudioPreset(
        "retouch-editorial", "Editorial Beauty", "Professional Skin Retouching", "Skin Finish",
        "Apply high-end editorial beauty retouching using realistic frequency-separation aesthetics, even tonal transitions and precise highlight control while preserving pores, complexion and distinctive permanent features.",
        False, ("beauty", "editorial", "skin"), "High-end beauty finish with authentic texture.", ("skin",), True, "#E8A598",
    ),
    StudioPreset(
        "retouch-under-eye", "Under-Eye Balance", "Professional Skin Retouching", "Targeted",
        "Reduce only temporary under-eye darkness and puffiness with natural tonal blending. Preserve eye shape, expression, eyelashes, fine lines and facial identity.",
        False, ("under-eye", "targeted", "natural"), "Gentle, targeted under-eye correction.", ("skin",), True, "#DDBEA9",
    ),
    StudioPreset(
        "retouch-shine", "Reduce Shine", "Professional Skin Retouching", "Targeted",
        "Reduce distracting facial shine while retaining healthy natural highlights, skin texture, pores, complexion and the original lighting direction.",
        False, ("shine", "skin", "targeted"), "Controlled highlights without flattening skin.", ("skin",), True, "#FFE5D9",
    ),

    # Enhancement and restoration.
    StudioPreset(
        "enhance-detail", "Improve Clarity", "Enhance & Restore", "Enhance",
        "Improve photographic clarity, fine detail, micro-contrast and exposure balance conservatively. Do not change identity, expression, facial features or introduce invented details.",
        False, ("clarity", "detail", "enhance"), "Natural clarity and exposure improvement.", ("detail", "exposure"), False, "#43AA8B",
    ),
    StudioPreset(
        "enhance-low-light", "Low-Light Rescue", "Enhance & Restore", "Enhance",
        "Recover a low-light portrait by reducing noise, restoring natural colour, balancing exposure and improving usable detail without over-sharpening or changing the person.",
        False, ("low-light", "noise", "restore"), "Cleaner, naturally exposed night photo.", ("detail", "exposure", "colour"), False, "#277DA1",
    ),
    StudioPreset(
        "restore-old-photo", "Restore Old Photo", "Enhance & Restore", "Restore",
        "Restore the damaged photograph by repairing scratches, dust, fading and small missing areas while preserving every person's identity, age, expression and authentic photographic character.",
        False, ("old-photo", "repair", "restore"), "Repair age damage without rewriting history.", ("damage", "detail", "exposure"), False, "#9C755F",
    ),
    StudioPreset(
        "restore-colourise", "Natural Colourisation", "Enhance & Restore", "Restore",
        "Colourise the black-and-white photograph with historically plausible, restrained natural colours, believable skin tones and fabric colours while preserving original contrast and identity.",
        False, ("colourise", "restore", "old-photo"), "Historically restrained natural colour.", ("colour",), False, "#84A59D",
    ),
)


PRIMARY_MODES: tuple[str, ...] = (
    "Change Background",
    "Complete Redesign",
    "Change Outfit",
    "Lighting & Mood",
    "Professional Portrait",
    "Professional Skin Retouching",
    "Enhance & Restore",
)


def _internal_mode(mode: str) -> str:
    return "Background" if mode == "Change Background" else mode


def modes() -> list[str]:
    return list(PRIMARY_MODES)


def categories_for_mode(mode: str) -> list[str]:
    internal = _internal_mode(mode)
    return list(dict.fromkeys(p.category for p in PRESETS if p.mode == internal))


def presets_for(mode: str, category: str | None = None) -> list[StudioPreset]:
    internal = _internal_mode(mode)
    return [
        p for p in PRESETS
        if p.mode == internal and (category is None or p.category == category)
    ]
