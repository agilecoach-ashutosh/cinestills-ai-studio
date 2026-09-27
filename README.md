# CineStills AI Studio

**Upload. Describe. Generate.**

CineStills AI Studio is a local-first portrait transformation application for photographers and everyday users. Its default Quick Generate workspace needs only a photo and a plain-language prompt. The complete theme-based workflow remains available under **Workspace → Portrait Studio**.

## V0.5 Quick Generate

The default screen is intentionally minimal:

1. Upload a photo.
2. Write what you want in ordinary language.
3. Choose Natural, Creative or Dramatic strength.
4. Select Generate.
5. Compare and save the result.

Quick Generate sends the visible prompt exactly as written. It does not silently add identity, pose, camera-angle or composition constraints. Use **Workspace → Portrait Studio** (or `Ctrl+2`) for the full theme gallery, masks and photographic controls. Return to Quick Generate with `Ctrl+1`.

## V0.4 Portrait Studio

V0.4 replaces the earlier tool-heavy workflow with an action-first portrait studio.

### Main transformations

1. **Change Background** — studio, indoor, outdoor, cinematic, celebrations and more
2. **Complete Redesign** — retro, Indian heritage, cinematic, festival, fashion and fantasy looks
3. **Change Outfit** — professional, traditional, fashion and everyday wardrobe
4. **Lighting & Mood** — natural, studio and creative relighting
5. **Professional Portrait** — LinkedIn, executive, actor, studio and fashion outcomes
6. **Professional Skin Retouching** — natural, polished, editorial and targeted corrections
7. **Enhance & Restore** — clarity, low-light rescue, old-photo repair and colourisation

The V0.4 catalogue contains 76 visible themes arranged into clear collections. Older product and interior recipes remain in the source catalogue but no longer compete for attention in the main portrait workflow.

## User workflow

1. Upload a portrait.
2. Choose what to change.
3. Browse or search the theme gallery.
4. Add an optional idea such as `Kashmir`, `Diwali` or `Paris café`.
5. Adjust transformation strength, light or colour.
6. Review and optionally edit the generated final prompt.
7. Generate locally through InvokeAI.
8. Compare and save the result.

## No-prompt and editable-prompt modes

CineStills creates a full photography instruction from the selected theme and simple controls. A single keyword is expanded with scene integration guidance for perspective, light direction, colour temperature, depth of field and contact shadows.

The generated prompt remains editable. Users can:

- rewrite any creative direction
- regenerate from the selected controls
- return to the previous prompt
- copy the final prompt
- save the prompt as a personal preset

At generation time, CineStills sends the visible editable prompt without appending a protected or hidden instruction block.

## Identity-preservation strategies

CineStills uses different protection strategies because different edits affect different pixels.

### Strict Identity Lock

Background transformations generate the new scene and then composite the original subject pixels over it. The original face and person are not regenerated.

### Reference Identity Lock

Complete redesign, outfit, lighting and professional portrait modes add **Exact Face Lock** on top of the source image-to-image reference. CineStills detects the primary frontal face locally, generates the redesign, and then restores the identity-bearing source face pixels through a soft oval blend. If no clear face is detected, generation stops instead of silently risking a different identity.

### Painted edit area

Outfit and professional skin-retouching themes recommend painting the exact area allowed to change. Pixels outside that area are restored locally after generation. This is the safest current workflow for clothing and targeted skin corrections.

Professional retouching is intentionally conservative: it protects pores, natural complexion, permanent features and facial structure while addressing temporary blemishes, shine or under-eye darkness.

## Privacy and processing

- Local InvokeAI processing by default
- No OpenAI or Gemini API key required
- Local segmentation and mask compositing
- Source and output photographs remain on the user's computer in local mode
- Personal prompt presets are stored locally in `.cinestills/personal-presets.json`

## Windows setup

No terminal commands are required.

1. Run **`setup.cmd`** once.
2. Keep InvokeAI running locally.
3. Run **`start.cmd`**.
4. Upload a portrait and choose a look.

If dependencies change, `start.cmd` routes back through setup automatically.

## Requirements

- Windows 10/11
- Python 3.12 recommended
- InvokeAI Community Edition running locally
- An SDXL main model installed in InvokeAI
- NVIDIA GPU recommended

## Current quality boundary

Strict background replacement retains the original person pixel-for-pixel. Full redesigns now retain the central facial pixels with Exact Face Lock while allowing hair, clothing, lighting and surroundings to change. This works best with a clear frontal or near-frontal portrait and the original pose; it deliberately stops when a face cannot be detected. Large pose changes and profile faces still require a dedicated face-reference adapter plus similarity validation in a later model-layer upgrade.

## Architecture

```text
Portrait upload
      |
      +--> Transformation category
      |        |
      |        +--> Searchable theme catalogue
      |        +--> Keyword expansion
      |        +--> Simple photographic controls
      |
      +--> Editable prompt
      |        |
      |        +--> Protected Identity Lock
      |
      +--> InvokeAI / SDXL local generation
      |        |
      |        +--> Optional painted-area composite
      |        +--> Strict subject composite for backgrounds
      |
      +--> Compare and save
```

## Next quality milestones

- Original photographic preview artwork for every theme card
- Native InvokeAI inpainting instead of output-only mask compositing
- Face-reference conditioning for major restyles
- Automated identity-similarity checks and retry
- Four-result contact sheet and before/after slider
- Favourites and full personal-preset gallery

## Project philosophy

Prompting should be optional. Creative control should not be.
