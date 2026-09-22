from __future__ import annotations

from io import BytesIO
from pathlib import Path
import time

from PIL import Image, ImageOps
from PySide6.QtCore import QThread, Signal

from app.services.identity_guard import prepare_working_image, preserve_original_subject
from app.services.invoke_client import InvokeClient


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
    ) -> None:
        super().__init__()
        self.source_path = source_path
        self.prompt = prompt
        self.base_url = base_url
        self.strict_composite = strict_composite

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

            if self.strict_composite:
                self.status.emit("Applying strict subject preservation...")
                final_path = preserve_original_subject(
                    source_path=self.source_path,
                    generated_bytes=generated_bytes,
                    destination=output_path,
                )
            else:
                self.status.emit("Finalizing generative edit...")
                original = ImageOps.exif_transpose(Image.open(self.source_path)).convert("RGB")
                generated = Image.open(BytesIO(generated_bytes)).convert("RGB")
                generated = generated.resize(original.size, Image.Resampling.LANCZOS)
                generated.save(output_path, "PNG")
                final_path = str(output_path)

            self.succeeded.emit(final_path)
        except Exception as exc:
            self.failed.emit(str(exc))
