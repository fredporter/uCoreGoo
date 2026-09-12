"""Contracts for Google bridge readiness."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Tuple


@dataclass(frozen=True)
class GoogleBridgeContract:
    """Canonical contract for the Wave G Google bridge."""

    capability_key: str = "google_ai_bridge"
    token_ownership: str = "server_vault_only"
    oauth_scopes: Tuple[str, ...] = (
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/drive.file",
    )
    oauth_required_secrets: Tuple[str, ...] = (
        "GOOGLE_CLIENT_ID",
        "GOOGLE_CLIENT_SECRET",
        "GOOGLE_REFRESH_TOKEN",
    )
    oauth_endpoints: Tuple[str, ...] = (
        "https://accounts.google.com/o/oauth2/v2/auth",
        "https://oauth2.googleapis.com/token",
    )
    oauth_pkce_required: bool = True
    chat_targets: Tuple[str, ...] = ("gemini", "gems")
    drive_sync_mode: str = "thin_mirror"
    supported_models: Tuple[str, ...] = (
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "imagen-3.0-generate-002",
    )
    api_key_secrets: Tuple[str, ...] = (
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
    )
    image_presets: Tuple[str, ...] = (
        "mono_teletext",
        "mono_blueprint",
        "mono_botanical",
        "mono_chrome",
        "mono_editorial",
    )

    def as_dict(self) -> Dict[str, Any]:
        """Serialize contract to a dictionary."""

        return asdict(self)


def default_google_contract() -> GoogleBridgeContract:
    """Return the default Google bridge contract."""

    return GoogleBridgeContract()
