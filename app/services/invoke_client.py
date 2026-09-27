from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import random
import time
import uuid

import requests

from app.config import CONFIG


@dataclass
class InvokeHealth:
    ok: bool
    detail: str


class InvokeError(RuntimeError):
    pass


class InvokeClient:
    """Small client for a locally running InvokeAI Community Edition instance."""

    def __init__(self, base_url: str | None = None, timeout: float = 5.0) -> None:
        self.base_url = (base_url or CONFIG.invoke_base_url).rstrip("/")
        self.timeout = timeout

    def health(self) -> InvokeHealth:
        candidates = (
            "/api/v1/app/version",
            "/api/v1/app/config",
            "/docs",
        )
        last_error = "InvokeAI not reachable"
        for path in candidates:
            try:
                response = requests.get(
                    f"{self.base_url}{path}",
                    timeout=self.timeout,
                )
                if response.status_code < 500:
                    return InvokeHealth(True, f"Connected to {self.base_url}")
                last_error = f"HTTP {response.status_code} from {path}"
            except requests.RequestException as exc:
                last_error = str(exc)

        return InvokeHealth(False, last_error)

    def health_quick(self, timeout: float = 0.8) -> InvokeHealth:
        """Fast UI heartbeat that avoids freezing the desktop when InvokeAI is down."""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/app/version",
                timeout=timeout,
            )
            if response.status_code < 500:
                return InvokeHealth(True, f"Connected to {self.base_url}")
            return InvokeHealth(False, f"HTTP {response.status_code} from /api/v1/app/version")
        except requests.RequestException as exc:
            return InvokeHealth(False, str(exc))

    def list_models(self) -> list[dict]:
        response = requests.get(
            f"{self.base_url}/api/v2/models/",
            timeout=max(self.timeout, 15),
        )
        self._raise_for_status(response, "Could not read InvokeAI models")
        payload = response.json()
        if isinstance(payload, dict):
            models = payload.get("models", [])
        else:
            models = payload
        return models if isinstance(models, list) else []

    @staticmethod
    def _model_identifier(model: dict) -> dict:
        required = ("key", "hash", "name", "base", "type")
        missing = [field for field in required if not model.get(field)]
        if missing:
            raise InvokeError(
                "InvokeAI returned an incomplete model record: " + ", ".join(missing)
            )
        return {
            "key": model["key"],
            "hash": model["hash"],
            "name": model["name"],
            "base": model["base"],
            "type": model["type"],
            "submodel_type": None,
        }

    def select_qwen_edit_components(self) -> tuple[dict, dict, dict]:
        """Select the installed Qwen Image Edit transformer and its standalone components."""
        models = self.list_models()

        main_models = [
            model
            for model in models
            if str(model.get("base", "")).lower() == "qwen-image"
            and str(model.get("type", "")).lower() == "main"
            and "qwen image edit 2511" in str(model.get("name", "")).lower()
        ]
        if not main_models:
            raise InvokeError(
                "Qwen Image Edit 2511 was not found in InvokeAI. Install the Qwen Image bundle first."
            )

        # Prefer the quality-first Q8_0 build used by CineStills, with any installed
        # 2511 edit build as a fallback.
        edit_model = next(
            (
                model
                for model in main_models
                if "q8_0" in str(model.get("name", "")).lower()
            ),
            main_models[0],
        )

        vae = next(
            (
                model
                for model in models
                if str(model.get("type", "")).lower() == "vae"
                and "qwen image vae" in str(model.get("name", "")).lower()
            ),
            None,
        )
        encoder = next(
            (
                model
                for model in models
                if "qwen2.5-vl encoder" in str(model.get("name", "")).lower()
            ),
            None,
        )
        if vae is None:
            raise InvokeError("Qwen Image VAE was not found in InvokeAI.")
        if encoder is None:
            raise InvokeError("Qwen2.5-VL Encoder was not found in InvokeAI.")

        return (
            self._model_identifier(edit_model),
            self._model_identifier(vae),
            self._model_identifier(encoder),
        )

    def upload_image(self, path: str | Path) -> str:
        image_path = Path(path)
        with image_path.open("rb") as handle:
            response = requests.post(
                f"{self.base_url}/api/v1/images/upload",
                params={
                    "image_category": "general",
                    "is_intermediate": "true",
                },
                files={"file": (image_path.name, handle, "image/png")},
                timeout=max(self.timeout, 60),
            )
        self._raise_for_status(response, "InvokeAI could not receive the source image")
        payload = response.json()
        image_name = self._find_value(payload, "image_name")
        if not image_name:
            raise InvokeError("InvokeAI uploaded the image but did not return an image name.")
        return str(image_name)

    def edit_image(
        self,
        source_path: str | Path,
        prompt: str,
        width: int,
        height: int,
        strength: float = 0.72,
        steps: int = 28,
        cfg_scale: float = 5.5,
        poll_interval: float = 0.75,
        timeout_seconds: int = 600,
    ) -> bytes:
        model = self.select_sdxl_model()
        image_name = self.upload_image(source_path)
        graph = self._build_sdxl_img2img_graph(
            image_name=image_name,
            prompt=prompt,
            model=model,
            width=width,
            height=height,
            strength=strength,
            steps=steps,
            cfg_scale=cfg_scale,
        )

        response = requests.post(
            f"{self.base_url}/api/v1/queue/default/enqueue_batch",
            json={
                "batch": {
                    "graph": graph,
                    "runs": 1,
                    "origin": "cinestills-ai-studio",
                }
            },
            timeout=max(self.timeout, 30),
        )
        self._raise_for_status(response, "InvokeAI rejected the generation request")
        payload = response.json()
        item_ids = payload.get("item_ids") or payload.get("queue_item_ids") or []
        if not item_ids:
            raise InvokeError("InvokeAI accepted the request but returned no queue item.")

        item_id = item_ids[0]
        deadline = time.monotonic() + timeout_seconds

        while time.monotonic() < deadline:
            item_response = requests.get(
                f"{self.base_url}/api/v1/queue/default/i/{item_id}",
                timeout=max(self.timeout, 15),
            )
            self._raise_for_status(item_response, "Could not read InvokeAI queue status")
            item = item_response.json()
            status = str(item.get("status", "")).lower()

            if status == "completed":
                image_name = self._find_value(item.get("session", {}).get("results", {}), "image_name")
                if not image_name:
                    image_name = self._find_value(item, "image_name")
                if not image_name:
                    raise InvokeError("Generation completed, but InvokeAI returned no output image.")
                return self.download_image(str(image_name))

            if status in {"failed", "canceled", "cancelled"}:
                message = (
                    item.get("error_message")
                    or self._find_value(item, "error")
                    or f"InvokeAI generation {status}."
                )
                raise InvokeError(str(message))

            time.sleep(poll_interval)

        raise InvokeError("InvokeAI generation timed out after 10 minutes.")

    def download_image(self, image_name: str) -> bytes:
        response = requests.get(
            f"{self.base_url}/api/v1/images/i/{image_name}/full",
            timeout=max(self.timeout, 60),
        )
        self._raise_for_status(response, "Could not download the generated image")
        return response.content

    def _build_qwen_image_edit_graph(
        self,
        image_name: str,
        prompt: str,
        model: dict,
        vae_model: dict,
        encoder_model: dict,
        width: int,
        height: int,
        strength: float,
        steps: int,
        cfg_scale: float,
    ) -> dict:
        """Build the native InvokeAI Qwen Image Edit graph.

        The source photo is used twice, matching InvokeAI's own Qwen graph:
        as a VL reference image for instruction-aware editing and as reference
        latents for the edit transformer.
        """
        prefix = uuid.uuid4().hex[:10]

        def node_id(name: str) -> str:
            return f"cinestills-{prefix}-{name}"

        loader = node_id("model")
        image = node_id("reference-image")
        collect = node_id("reference-collect")
        pos = node_id("positive")
        ref_i2l = node_id("reference-i2l")
        denoise = node_id("denoise")
        l2i = node_id("l2i")

        # InvokeAI trains/conditions Qwen Image Edit references around a 1024^2
        # pixel area. Preserve aspect ratio and snap to the required 32px grid.
        ratio = max(width, 1) / max(height, 1)
        ref_width = max(32, round(((1024 * 1024 * ratio) ** 0.5) / 32) * 32)
        ref_height = max(32, round((ref_width / ratio) / 32) * 32)

        nodes = {
            loader: {
                "id": loader,
                "type": "qwen_image_model_loader",
                "model": model,
                "vae_model": vae_model,
                "qwen_vl_encoder_model": encoder_model,
                "is_intermediate": True,
                "use_cache": True,
            },
            image: {
                "id": image,
                "type": "image",
                "image": {"image_name": image_name},
                "is_intermediate": True,
                "use_cache": True,
            },
            collect: {
                "id": collect,
                "type": "collect",
                "is_intermediate": True,
                "use_cache": True,
            },
            pos: {
                "id": pos,
                "type": "qwen_image_text_encoder",
                "prompt": prompt,
                "quantization": "none",
                "is_intermediate": True,
                "use_cache": True,
            },
            ref_i2l: {
                "id": ref_i2l,
                "type": "qwen_image_i2l",
                "image": {"image_name": image_name},
                "width": ref_width,
                "height": ref_height,
                "tiled": False,
                "tile_size": 0,
                "is_intermediate": True,
                "use_cache": True,
            },
            denoise: {
                "id": denoise,
                "type": "qwen_image_denoise",
                "steps": max(1, steps),
                "cfg_scale": max(1.0, cfg_scale),
                "denoising_start": max(0.0, min(1.0, 1.0 - strength)),
                "denoising_end": 1.0,
                "seed": random.randint(0, 2_147_483_647),
                "width": max(16, round(width / 16) * 16),
                "height": max(16, round(height / 16) * 16),
                "is_intermediate": True,
                "use_cache": False,
            },
            l2i: {
                "id": l2i,
                "type": "qwen_image_l2i",
                "tiled": False,
                "tile_size": 0,
                "is_intermediate": False,
                "use_cache": False,
            },
        }

        def edge(source_node: str, source_field: str, destination_node: str, destination_field: str) -> dict:
            return {
                "source": {"node_id": source_node, "field": source_field},
                "destination": {"node_id": destination_node, "field": destination_field},
            }

        edges = [
            edge(loader, "qwen_vl_encoder", pos, "qwen_vl_encoder"),
            edge(image, "image", collect, "item"),
            edge(collect, "collection", pos, "reference_images"),
            edge(loader, "vae", ref_i2l, "vae"),
            edge(ref_i2l, "latents", denoise, "reference_latents"),
            edge(loader, "transformer", denoise, "transformer"),
            edge(pos, "conditioning", denoise, "positive_conditioning"),
            edge(denoise, "latents", l2i, "latents"),
            edge(loader, "vae", l2i, "vae"),
        ]

        return {
            "id": f"cinestills-{prefix}-qwen-edit-graph",
            "nodes": nodes,
            "edges": edges,
        }


