"""Minimal, dependency-free client for Odoo's external JSON-2 API."""

from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]


def load_env_file(path: Path = ROOT / ".env") -> None:
    """Load simple KEY=value entries without overriding shell environment."""
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if key and key not in os.environ:
            os.environ[key] = value


class OdooAPIError(RuntimeError):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status
        self.message = message


class OdooJSON2Client:
    def __init__(self) -> None:
        load_env_file()
        self.base_url = os.environ.get("ODOO_URL", "").strip().rstrip("/")
        self.api_key = os.environ.get("ODOO_API_KEY", "").strip()
        self.database = os.environ.get("ODOO_DATABASE", "").strip()
        self.timeout = float(os.environ.get("ODOO_TIMEOUT_SECONDS", "25"))
        self._field_cache: dict[str, dict] = {}

    @property
    def configured(self) -> bool:
        return bool(self.base_url and self.api_key)

    def call(self, model: str, method: str, **params):
        if not self.configured:
            raise OdooAPIError(503, "Odoo connection is not configured. Set ODOO_URL and ODOO_API_KEY in .env.")
        if not self.base_url.startswith("https://"):
            raise OdooAPIError(500, "ODOO_URL must use HTTPS.")

        body = json.dumps(params, separators=(",", ":")).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json",
            "User-Agent": "BrightloopSubscriptionAPI/1.0",
        }
        if self.database:
            headers["X-Odoo-Database"] = self.database
        url = f"{self.base_url}/json/2/{quote(model, safe='')}/{quote(method, safe='')}"
        request = Request(url, data=body, headers=headers, method="POST")
        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload = response.read()
        except HTTPError as error:
            error_body = error.read().decode("utf-8", errors="replace")
            try:
                details = json.loads(error_body)
                message = details.get("message") or details.get("name") or "Odoo rejected the request."
            except (json.JSONDecodeError, AttributeError):
                message = "Odoo rejected the request."
            if error.code == 401:
                message = "Odoo rejected the API key. Check the key, user access, and Custom plan availability."
            elif error.code == 403:
                message = "The Odoo user behind this API key does not have permission for this operation."
            elif error.code >= 500:
                message = "Odoo could not complete the request. Check the Odoo model, fields, and server logs."
            raise OdooAPIError(error.code, str(message)) from None
        except (URLError, TimeoutError, OSError) as error:
            raise OdooAPIError(502, f"Could not reach Odoo: {error.reason if isinstance(error, URLError) else error}") from None

        if not payload:
            return None
        try:
            return json.loads(payload.decode("utf-8"))
        except json.JSONDecodeError:
            raise OdooAPIError(502, "Odoo returned an invalid JSON response.") from None

    def fields(self, model: str) -> dict:
        if model not in self._field_cache:
            fields = self.call(model, "fields_get")
            if not isinstance(fields, dict):
                raise OdooAPIError(502, f"Odoo did not return field metadata for {model}.")
            self._field_cache[model] = fields
        return self._field_cache[model]

    def supported(self, model: str, candidates: list[str]) -> list[str]:
        metadata = self.fields(model)
        return [field for field in candidates if field == "id" or field in metadata]

    def search_read(self, model: str, domain: list, fields: list[str], limit: int = 20, offset: int = 0, order: str | None = None):
        params = {
            "domain": domain,
            "fields": self.supported(model, fields),
            "limit": limit,
            "offset": offset,
        }
        if order:
            params["order"] = order
        return self.call(model, "search_read", **params)

