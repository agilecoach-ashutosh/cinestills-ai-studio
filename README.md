# CineStills AI Studio

**Change the scene. Keep the person.**

CineStills AI Studio is a local-first desktop photo editing application for prompt-driven edits without Photoshop.

## V0.1

The first working path is background transformation with strict subject preservation:

1. Load a local photograph.
2. Choose a background preset.
3. CineStills sends a resized working copy to your **local** InvokeAI instance.
4. InvokeAI / SDXL generates the new scene.
5. A local segmentation model isolates the person.
6. CineStills composites the **original subject pixels** over the generated background.
7. Preview and save the result.

This is intentionally different from relying only on a "do not change the face" prompt. In Strict mode, the visible subject comes from the original photograph.

## Architecture

```text
CineStills PySide6 App
      |
      +--> Prompt Recipe Engine
      |
      +--> InvokeAI local HTTP API
      |        |
      |        +--> SDXL / Juggernaut XL
      |
      +--> Local Subject Segmentation
      |
      +--> Strict Original-Subject Composite
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
4. Choose a photo, select a preset and click **Generate Locally**.

If dependencies change, `start.cmd` automatically sends you through `setup.cmd` once.

### First generation note

The subject-segmentation component may download its free model weights on first use. After they are cached, subject masking runs locally.

## Privacy

CineStills does not require an OpenAI or Gemini API key for local mode. The source image, generated image and segmentation work remain on your machine when using local InvokeAI.

## Project philosophy

Local-first by default. Cloud providers may be added later as optional adapters, but the core product should remain useful without paid API usage.
