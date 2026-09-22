from __future__ import annotations

from io import BytesIO
from pathlib import Path
import time

from PIL import Image, ImageOps
from PySide6.QtCore import QThread, Signal

from app.services.identity_guard import create_subject_mask, prepare_working_image
from app.services.invoke_client import InvokeClient
from app.services.mask_ops import apply_edit_mask


class GenerationWorker(QThread):
    status = Signal(str)
    succeeded = Signal(str)
    failed = Signal(str)

    def __init__(
        self,
        source_path: str,
        prompt: str,
        base_url: str,
        strict_composite: bool = True,
        edit_mask_path: str | None = None,
    ) -> None:
        super().__init__()
        self.source_path = source_path
        self.prompt = prompt
        self.base_url = base_url
        self.strict_composite = strict_composite
        self.edit_mask_path = edit_mask_path

    def run(self) -> None:
        try:
            root = Path.cwd()
            temp_dir = root / "temp"
            output_dir = root / "output"
            temp_dir.mkdir(parents=True, exist_ok=True)
            output_dir.mkdir(parents=True, exist_ok=True)

            stamp = str(int(time.time() * 1000))
            working_path = temp_dir / f"cinestills-input-{stamp}.png"
            output_path = output_dir / f"cinestills-{stamp}.png"

            self.status.emit("Preparing image...")
            width, height = prepare_working_image(self.source_path, working_path)

            self.status.emit("Generating locally with InvokeAI...")
            client = InvokeClient(base_url=self.base_url)
            generated_bytes = client.edit_image(
                source_path=working_path,
                prompt=self.prompt,
                width=width,
                height=height,
            )

            original = ImageOps.exif_transpose(Image.open(self.source_path)).convert("RGB")

            if self.edit_mask_path:
                self.status.emit("Applying Magic Brush selection...")
                edited = apply_edit_mask(
                    source_path=self.source_path,
                    generated_bytes=generated_bytes,
                    mask_path=self.edit_mask_path,
                )
            else:
                edited = Image.open(BytesIO(generated_bytes)).convert("RGB")
                edited = edited.resize(original.size, Image.Resampling.LANCZOS)

            if self.strict_composite:
                self.status.emit("Applying strict subject preservation...")
                subject_mask = create_subject_mask(original)
                edited = Image.composite(original, edited, subject_mask)

            output_path.parent.mkdir(parents=True, exist_ok=True)
            edited.save(output_path, "PNG")
            self.succeeded.emit(str(output_path))
        except Exception as exc:
            self.failed.emit(str(exc))
