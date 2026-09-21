from __future__ import annotations

from dataclasses import dataclass
import requests

from app.config import CONFIG


@dataclass
class InvokeHealth:
    ok: bool
    detail: str


class InvokeClient:
    """Thin client around a locally running InvokeAI instance.

    V0.1 intentionally keeps this adapter small. Once we lock the exact
    Invoke workflow/API shape, generation and image-edit calls will live here.
    """

    def __init__(self, base_url: str | None = None, timeout: float = 3.0) -> None:
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
