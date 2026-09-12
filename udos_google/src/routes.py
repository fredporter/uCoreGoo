"""Route handlers for Google bridge scaffolding."""

from __future__ import annotations

from typing import Any, Dict

from .service import GoogleBridgeService


class GoogleBridgeRoutes:
    """Container for Wave G route handlers."""

    def __init__(self, service: GoogleBridgeService):
        self.service = service

    def get_contract(self) -> Dict[str, Any]:
        """Handle GET /api/google/contract."""

        return {
            "status": "success",
            "contract": self.service.get_contract(),
        }

    def health(self) -> Dict[str, Any]:
        """Handle GET /api/google/health."""

        return self.service.health()

    def oauth_contract(self) -> Dict[str, Any]:
        """Handle GET /api/google/oauth/contract."""

        contract = self.service.get_contract()
        return {
            "status": "success",
            "token_ownership": contract["token_ownership"],
            "required_secrets": list(contract["oauth_required_secrets"]),
            "pkce_required": contract["oauth_pkce_required"],
            "oauth_endpoints": list(contract["oauth_endpoints"]),
            "oauth_scopes": list(contract["oauth_scopes"]),
        }

    def oauth_readiness(self, provided_secrets: Dict[str, str] | None = None) -> Dict[str, Any]:
        """Handle POST /api/google/oauth/readiness."""

        readiness = self.service.oauth_readiness(provided_secrets)
        return {
            "status": "success" if readiness["ready"] else "blocked",
            **readiness,
        }

    def chat(self, provider: str, prompt: str, session_id: str = "default") -> Dict[str, Any]:
        """Handle POST /api/google/chat."""

        return self.service.chat_message(provider, prompt, session_id=session_id)

    def sync_drive(
        self,
        document_id: str,
        content: str,
        vault_path: str | None = None,
    ) -> Dict[str, Any]:
        """Handle POST /api/google/drive/sync."""

        return self.service.drive_sync(document_id, content, vault_path=vault_path)

    def grounded_search(self, query: str, session_id: str = "default") -> Dict[str, Any]:
        """Handle POST /api/google/grounded-search."""

        return self.service.grounded_search(query, session_id=session_id)

    def generate_image(
        self,
        prompt: str,
        style_preset: str = "mono_teletext",
        aspect_ratio: str = "1:1",
    ) -> Dict[str, Any]:
        """Handle POST /api/google/image/generate."""

        return self.service.generate_image(
            prompt, style_preset=style_preset, aspect_ratio=aspect_ratio
        )

    def scan_vault(self, vault_path: str | None = None) -> Dict[str, Any]:
        """Handle POST /api/google/drive/scan."""

        return self.service.sync_vault_directory(vault_path)

    def get_drive_record(self, document_id: str) -> Dict[str, Any]:
        """Handle GET /api/google/drive/sync/{id}."""

        record = self.service.get_drive_record(document_id)
        if record is None:
            return {
                "status": "missing",
                "document_id": document_id,
            }
        return {
            "status": "success",
            "record": record,
        }

    def list_drive_records(self) -> Dict[str, Any]:
        """Handle GET /api/google/drive/sync."""

        records = self.service.list_drive_records()
        return {
            "status": "success",
            "count": len(records),
            "records": records,
        }

    def execute_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Handle POST /api/google/code/execute."""
        return self.service.execute_notebook_cell(code, language=language)

    def get_vault_status(self, vault_path: str | None = None) -> Dict[str, Any]:
        """Handle GET /api/google/drive/status."""
        return self.service.get_vault_sync_status(vault_path)


# ── Global default instance and aiohttp registration ────────────────

_default_routes: GoogleBridgeRoutes | None = None



def get_routes() -> GoogleBridgeRoutes:
    """Return singleton GoogleBridgeRoutes instance."""
    global _default_routes
    if _default_routes is None:
        _default_routes = GoogleBridgeRoutes(GoogleBridgeService())
    return _default_routes


async def handle_google_health(_request: Any) -> Any:
    """GET /api/google/health."""
    from aiohttp import web
    return web.json_response(get_routes().health())


async def handle_google_contract(_request: Any) -> Any:
    """GET /api/google/contract."""
    from aiohttp import web
    return web.json_response(get_routes().get_contract())


async def handle_google_oauth_contract(_request: Any) -> Any:
    """GET /api/google/oauth/contract."""
    from aiohttp import web
    return web.json_response(get_routes().oauth_contract())


async def handle_google_oauth_readiness(request: Any) -> Any:
    """POST /api/google/oauth/readiness."""
    from aiohttp import web
    try:
        body = await request.json()
    except Exception:
        body = {}
    return web.json_response(get_routes().oauth_readiness(body))


async def handle_google_chat(request: Any) -> Any:
    """POST /api/google/chat."""
    from aiohttp import web
    try:
        body = await request.json()
    except Exception:
        return web.json_response({"error": "Invalid JSON body"}, status=400)
    provider = body.get("provider", "gemini")
    prompt = body.get("prompt", "")
    session_id = body.get("session_id", "default")
    res = await get_routes().service.async_chat(provider, prompt, session_id)
    return web.json_response(res)


async def handle_google_grounded_search(request: Any) -> Any:
    """POST /api/google/grounded-search."""
    from aiohttp import web
    try:
        body = await request.json()
    except Exception:
        return web.json_response({"error": "Invalid JSON body"}, status=400)
    query = body.get("query", "")
    session_id = body.get("session_id", "default")
    res = await get_routes().service.async_grounded_search(query, session_id)
    return web.json_response(res)


async def handle_google_image_generate(request: Any) -> Any:
    """POST /api/google/image/generate."""
    from aiohttp import web
    try:
        body = await request.json()
    except Exception:
        return web.json_response({"error": "Invalid JSON body"}, status=400)
    prompt = body.get("prompt", "")
    style_preset = body.get("style_preset", "mono_teletext")
    aspect_ratio = body.get("aspect_ratio", "1:1")
    res = await get_routes().service.async_generate_image(prompt, style_preset, aspect_ratio)
    return web.json_response(res)


async def handle_google_drive_sync(request: Any) -> Any:
    """POST /api/google/drive/sync."""
    from aiohttp import web
    try:
        body = await request.json()
    except Exception:
        return web.json_response({"error": "Invalid JSON body"}, status=400)
    doc_id = body.get("document_id", "")
    content = body.get("content", "")
    vault_path = body.get("vault_path")
    return web.json_response(get_routes().sync_drive(doc_id, content, vault_path))


async def handle_google_drive_list(_request: Any) -> Any:
    """GET /api/google/drive/sync."""
    from aiohttp import web
    return web.json_response(get_routes().list_drive_records())


async def handle_google_drive_get(request: Any) -> Any:
    """GET /api/google/drive/sync/{id}."""
    from aiohttp import web
    doc_id = request.match_info.get("id", "")
    return web.json_response(get_routes().get_drive_record(doc_id))


async def handle_google_drive_scan(request: Any) -> Any:
    """POST /api/google/drive/scan."""
    from aiohttp import web
    try:
        body = await request.json()
    except Exception:
        body = {}
    vault_path = body.get("vault_path")
    return web.json_response(get_routes().scan_vault(vault_path))


async def handle_google_drive_status(request: Any) -> Any:
    """GET /api/google/drive/status."""
    from aiohttp import web
    vault_path = request.query.get("vault_path")
    return web.json_response(get_routes().get_vault_status(vault_path))


async def handle_google_code_execute(request: Any) -> Any:
    """POST /api/google/code/execute."""
    from aiohttp import web
    try:
        body = await request.json()
    except Exception:
        return web.json_response({"error": "Invalid JSON body"}, status=400)
    code = body.get("code", "")
    language = body.get("language", "python")
    res = await get_routes().service.async_execute_notebook_cell(code, language=language)
    return web.json_response(res)


async def handle_dreambeans_briefing(request: Any) -> Any:
    """GET /api/google/dreambeans/briefing."""
    from aiohttp import web
    return web.json_response(get_routes().service.generate_dreambean_briefing())


def register_routes(app: Any) -> None:
    """Register Google bridge plugin routes on a uCore application."""
    app.router.add_get("/api/google/health", handle_google_health)
    app.router.add_get("/api/google/contract", handle_google_contract)
    app.router.add_get("/api/google/oauth/contract", handle_google_oauth_contract)
    app.router.add_post("/api/google/oauth/readiness", handle_google_oauth_readiness)
    app.router.add_post("/api/google/chat", handle_google_chat)
    app.router.add_post("/api/google/grounded-search", handle_google_grounded_search)
    app.router.add_post("/api/google/image/generate", handle_google_image_generate)
    app.router.add_post("/api/google/code/execute", handle_google_code_execute)
    app.router.add_post("/api/google/drive/sync", handle_google_drive_sync)
    app.router.add_post("/api/google/drive/scan", handle_google_drive_scan)
    app.router.add_get("/api/google/drive/sync", handle_google_drive_list)
    app.router.add_get("/api/google/drive/sync/{id}", handle_google_drive_get)
    app.router.add_get("/api/google/drive/status", handle_google_drive_status)
    app.router.add_get("/api/google/dreambeans/briefing", handle_dreambeans_briefing)


