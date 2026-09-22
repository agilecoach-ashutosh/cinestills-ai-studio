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

    def select_sdxl_model(self) -> dict:
        models = self.list_models()
        compatible = [
            model
            for model in models
            if str(model.get("base", "")).lower() == "sdxl"
            and str(model.get("type", "")).lower() == "main"
        ]
        if not compatible:
            raise InvokeError(
                "No SDXL main model was found in InvokeAI. Install the SDXL starter bundle first."
            )

        preferred = next(
            (
                model
                for model in compatible
                if "juggernaut" in str(model.get("name", "")).lower()
            ),
            compatible[0],
        )

        required = ("key", "hash", "name", "base", "type")
        missing = [field for field in required if not preferred.get(field)]
        if missing:
            raise InvokeError(
                "InvokeAI returned an incomplete model record: " + ", ".join(missing)
            )

        return {
            "key": preferred["key"],
            "hash": preferred["hash"],
            "name": preferred["name"],
            "base": preferred["base"],
            "type": preferred["type"],
            "submodel_type": None,
        }

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

    def _build_sdxl_img2img_graph(
        self,
        image_name: str,
        prompt: str,
        model: dict,
        width: int,
        height: int,
        strength: float,
        steps: int,
        cfg_scale: float,
    ) -> dict:
        prefix = uuid.uuid4().hex[:10]

        def node_id(name: str) -> str:
            return f"cinestills-{prefix}-{name}"

        loader = node_id("model")
        pos = node_id("positive")
        neg = node_id("negative")
        noise = node_id("noise")
        i2l = node_id("i2l")
        denoise = node_id("denoise")
        l2i = node_id("l2i")

        negative_prompt = (
            "different person, changed identity, altered face, extra person, duplicate person, "
            "deformed face, distorted anatomy, low quality, blurry"
        )

        nodes = {
            loader: {
                "id": loader,
                "type": "sdxl_model_loader",
                "model": model,
                "is_intermediate": True,
                "use_cache": True,
            },
            pos: {
                "id": pos,
                "type": "sdxl_compel_prompt",
                "prompt": prompt,
                "style": prompt,
                "original_width": width,
                "original_height": height,
                "target_width": width,
                "target_height": height,
                "crop_top": 0,
                "crop_left": 0,
                "is_intermediate": True,
                "use_cache": True,
            },
            neg: {
                "id": neg,
                "type": "sdxl_compel_prompt",
                "prompt": negative_prompt,
                "style": negative_prompt,
                "original_width": width,
                "original_height": height,
                "target_width": width,
                "target_height": height,
                "crop_top": 0,
                "crop_left": 0,
                "is_intermediate": True,
                "use_cache": True,
            },
            noise: {
                "id": noise,
                "type": "noise",
                "seed": random.randint(0, 2_147_483_647),
                "width": width,
                "height": height,
                "use_cpu": True,
                "is_intermediate": True,
                "use_cache": False,
            },
            i2l: {
                "id": i2l,
                "type": "i2l",
                "image": {"image_name": image_name},
                "fp32": False,
                "tiled": False,
                "tile_size": 0,
                "color_compensation": "SDXL",
                "is_intermediate": True,
                "use_cache": True,
            },
            denoise: {
                "id": denoise,
                "type": "denoise_latents",
                "steps": steps,
                "cfg_scale": cfg_scale,
                "cfg_rescale_multiplier": 0,
                "denoising_start": max(0.0, min(1.0, 1.0 - strength)),
                "denoising_end": 1.0,
                "scheduler": "dpmpp_2m_sde_k",
                "is_intermediate": True,
                "use_cache": True,
            },
            l2i: {
                "id": l2i,
                "type": "l2i",
                "fp32": False,
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
            edge(loader, "clip", pos, "clip"),
            edge(loader, "clip2", pos, "clip2"),
            edge(loader, "clip", neg, "clip"),
            edge(loader, "clip2", neg, "clip2"),
            edge(loader, "unet", denoise, "unet"),
            edge(pos, "conditioning", denoise, "positive_conditioning"),
            edge(neg, "conditioning", denoise, "negative_conditioning"),
            edge(noise, "noise", denoise, "noise"),
            edge(loader, "vae", i2l, "vae"),
            edge(i2l, "latents", denoise, "latents"),
            edge(denoise, "latents", l2i, "latents"),
            edge(loader, "vae", l2i, "vae"),
        ]

        return {
            "id": f"cinestills-{prefix}-graph",
            "nodes": nodes,
            "edges": edges,
        }

    @staticmethod
    def _find_value(value, key: str):
        if isinstance(value, dict):
            if key in value and value[key]:
                return value[key]
            for child in value.values():
                found = InvokeClient._find_value(child, key)
                if found:
                    return found
        elif isinstance(value, list):
            for child in value:
                found = InvokeClient._find_value(child, key)
                if found:
                    return found
        return None

    @staticmethod
    def _raise_for_status(response: requests.Response, context: str) -> None:
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            detail = response.text.strip()
            if len(detail) > 1200:
                detail = detail[:1200] + "..."
            raise InvokeError(f"{context}.\n\n{detail or exc}") from exc
