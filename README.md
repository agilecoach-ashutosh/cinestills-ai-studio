# CineStills AI Studio

**Change the scene. Keep the person.**

CineStills AI Studio is a local-first desktop photo editing application for prompt-driven edits without Photoshop. The first milestone focuses on background replacement while preserving the subject as much as possible.

## V0.1 goal

- Load a local photo
- Choose a background preset
- Add an optional custom instruction
- Generate locally through InvokeAI
- Compare original vs result
- Save the edited image

## Architecture

```text
PySide6 Desktop App
      |
      +--> Prompt Recipe Engine
      |
      +--> Identity Guard / Masking
      |
      +--> InvokeAI local service
                 |
                 +--> SDXL / Juggernaut XL
                 |
                 +--> future local models
```

## Current status

UI scaffold and local InvokeAI connectivity layer are in place. The next implementation step is wiring an Invoke workflow endpoint for image generation/editing and adding automatic subject masking.

## Requirements

- Windows 10/11
- Python 3.12 recommended
- InvokeAI Community Edition installed and running locally
- NVIDIA GPU recommended

## Windows setup

No terminal commands are required.

1. Run **`setup.cmd`** once. It creates the private Python environment, installs the required components, and starts CineStills.
2. After the first setup, run **`start.cmd`** whenever you want to open CineStills AI Studio.
3. Keep InvokeAI running while using local AI generation.

If the environment is ever deleted, running `setup.cmd` recreates it automatically.

## Project philosophy

Local-first by default. Cloud providers may be added later as optional adapters, but the core product should remain useful without paid API usage.
