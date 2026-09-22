# CineStills AI Studio

**Change the scene. Keep the person.**

CineStills AI Studio is a local-first desktop photo editing application for photographers and creators who want practical AI-assisted edits without depending on paid cloud APIs.

## V0.2 Studio

V0.2 turns the original single-preset prototype into a structured editing studio.

### Edit modes

- **Background** — studio paper, low-key, indoor, outdoor, cinematic, kids and birthday scenes
- **Creative** — moon scenes, magical forests, reflections and atmospheric transformations
- **Dress & Fabric** — gown extension, flare and fabric-shape edits
- **Retouch** — targeted prompt recipes such as hair-edge cleanup and dress wrinkle cleanup
- **Add / Remove** — props and atmosphere such as flower arches and fog
- **Product** — clean and dramatic product-studio recipes

### Subject Lock

CineStills now exposes reusable preservation controls for:

- face / identity
- hair
- body proportions
- pose and subject position
- clothing
- skin tone

The generated prompt is visible in the app so photographers can see exactly what will be sent to the local engine.

### Cinematic Look

Reusable photographic controls can be layered over any preset:

- 35mm / 50mm / 85mm lens look
- golden hour, diffused, backlit and low-key lighting
- shallow or deep focus
- warm film, muted editorial, teal-orange and cool grading
- fine film grain or high-dynamic-range treatment

## Preservation modes

CineStills intentionally uses two different preservation strategies.

### Strict subject preservation

Background and scene presets use the original V0.1 pipeline:

1. Load the source photograph.
2. Generate a new scene locally with InvokeAI / SDXL.
3. Segment the original subject locally.
4. Composite the **original subject pixels** over the generated scene.
5. Preview and save.

This is stronger than merely prompting the model not to change the face.

### Generative identity preservation

Dress, hair, product and other edits that must change subject pixels cannot use strict compositing because doing so would paste the old pixels back over the requested edit.

Those recipes therefore use prompt-based identity constraints while allowing the requested area to change.

> Current limitation: V0.2 does not yet provide a brush/mask editor. Generative retouch and wardrobe edits operate through the local image-to-image workflow and may affect more of the image than a future masked workflow will.

## Architecture

```text
CineStills PySide6 App
      |
      +--> Structured Preset Library
      |
      +--> Prompt Composer
      |        |
      |        +--> Subject Locks
      |        +--> Cinematic Look
      |
      +--> InvokeAI local HTTP API
      |        |
      |        +--> SDXL / Juggernaut XL
      |
      +--> Local Subject Segmentation
      |
      +--> Strict Composite when the edit allows it
      |
      +--> Preview / Save
```

## Requirements

- Windows 10/11
- Python 3.12 recommended
- InvokeAI Community Edition installed and running locally
- An SDXL main model installed in InvokeAI
- NVIDIA GPU recommended

## Windows setup

No terminal commands are required.

1. Run **`setup.cmd`** once.
2. Keep InvokeAI running.
3. Run **`start.cmd`** to open CineStills AI Studio.
4. Choose a photo.
5. Select **Mode → Category → Preset**.
6. Adjust Subject Lock and Cinematic Look controls if needed.
7. Click **Generate Locally**.
8. Save the result.

If dependencies change, `start.cmd` automatically sends you through `setup.cmd` once.

### First generation note

The subject-segmentation component may download its free model weights on first use. After they are cached, subject masking runs locally.

## Prompt-library design

Presets are stored as structured recipes rather than one giant collection of pasted prompts. Each recipe contains:

- editing mode
- category
- scene/edit instruction
- preservation strategy
- searchable tags

This makes the studio library easier to expand with additional maternity, pre-wedding, kids, portrait, product and commercial packs.

## Privacy

CineStills does not require an OpenAI or Gemini API key for local mode. The source image, generated image and segmentation work remain on your machine when using local InvokeAI.

## Roadmap

The next high-value editing layer is a local **Magic Brush / mask editor** so users can paint the exact region for hair cleanup, garment extension, prop insertion or object removal before generation.

## Project philosophy

Local-first by default. Cloud providers may be added later as optional adapters, but the core product should remain useful without paid API usage.
