import unittest

from udos_google.src.contracts import default_google_contract
from udos_google.src.routes import GoogleBridgeRoutes
from udos_google.src.service import GoogleBridgeService


class TestGoogleBridge(unittest.TestCase):
    def test_contract_and_health(self):
        contract = default_google_contract()
        self.assertEqual(contract.capability_key, "google_ai_bridge")
        self.assertEqual(contract.token_ownership, "server_vault_only")
        self.assertIn("gemini", contract.chat_targets)

        routes = GoogleBridgeRoutes(GoogleBridgeService(contract))
        self.assertEqual(routes.health()["status"], "ok")
        self.assertEqual(routes.get_contract()["contract"]["capability_key"], "google_ai_bridge")
        self.assertFalse(routes.health()["oauth_ready"])

    def test_oauth_readiness(self):
        routes = GoogleBridgeRoutes(GoogleBridgeService())

        blocked = routes.oauth_readiness({"GOOGLE_CLIENT_ID": "x"})
        self.assertEqual(blocked["status"], "blocked")
        self.assertIn("GOOGLE_CLIENT_SECRET", blocked["missing_secrets"])

        ready = routes.oauth_readiness(
            {
                "GOOGLE_CLIENT_ID": "x",
                "GOOGLE_CLIENT_SECRET": "y",
                "GOOGLE_REFRESH_TOKEN": "z",
            }
        )
        self.assertEqual(ready["status"], "success")
        self.assertTrue(ready["ready"])
        self.assertEqual(ready["token_ownership"], "server_vault_only")

        oauth_contract = routes.oauth_contract()
        self.assertTrue(oauth_contract["pkce_required"])
        self.assertIn("https://oauth2.googleapis.com/token", oauth_contract["oauth_endpoints"])

    def test_chat_and_sync_thin_slice(self):
        routes = GoogleBridgeRoutes(GoogleBridgeService())
        chat_one = routes.chat("gemini", "hello", session_id="s1")
        chat_two = routes.chat("gems", "next", session_id="s1")
        sync_one = routes.sync_drive("doc-1", "first", vault_path="vault://docs/doc-1.md")
        sync_two = routes.sync_drive("doc-1", "second", vault_path="vault://docs/doc-1.md")

        self.assertEqual(chat_one["status"], "success")
        self.assertEqual(chat_one["provider"], "gemini")
        self.assertEqual(chat_one["session_id"], "s1")
        self.assertEqual(chat_one["turns"], 2)

        self.assertEqual(chat_two["status"], "success")
        self.assertEqual(chat_two["provider"], "gems")
        self.assertEqual(chat_two["session_id"], "s1")
        self.assertEqual(chat_two["turns"], 4)

        self.assertEqual(sync_one["status"], "locally_recorded")
        self.assertEqual(sync_one["remote_upload"], "pending")
        self.assertEqual(sync_one["record"]["mode"], "thin_mirror")
        self.assertEqual(sync_one["record"]["revision"], 1)

        self.assertEqual(sync_two["status"], "locally_recorded")
        self.assertEqual(sync_two["remote_upload"], "pending")
        self.assertEqual(sync_two["record"]["revision"], 2)
        self.assertNotEqual(sync_one["record"]["checksum"], sync_two["record"]["checksum"])

        listed = routes.list_drive_records()
        self.assertEqual(listed["status"], "success")
        self.assertEqual(listed["count"], 1)

        fetched = routes.get_drive_record("doc-1")
        self.assertEqual(fetched["status"], "success")
        self.assertEqual(fetched["record"]["revision"], 2)

        missing = routes.get_drive_record("missing")
        self.assertEqual(missing["status"], "missing")

    def test_api_key_and_advanced_routes(self):
        routes = GoogleBridgeRoutes(GoogleBridgeService())

        # Test API key readiness
        api_ready = routes.service.api_key_readiness({"GEMINI_API_KEY": "fake-key"})
        self.assertTrue(api_ready["ready"])
        self.assertEqual(api_ready["key_source"], "provided")

        # Test Grounded Search
        search_res = routes.grounded_search("WebAssembly in Rust", session_id="s_grounded")
        self.assertEqual(search_res["status"], "success")
        self.assertEqual(search_res["model"], "gemini-2.0-flash")
        self.assertGreater(len(search_res["citations"]), 0)
        self.assertIn("WebAssembly", search_res["summary"])

        # Test Image Generation (Nano Banana / Imagen 3)
        img_res = routes.generate_image("A retro teletext city", style_preset="mono_teletext")
        self.assertEqual(img_res["status"], "success")
        self.assertEqual(img_res["model"], "imagen-3.0-generate-002")
        self.assertEqual(img_res["style_preset"], "mono_teletext")
        self.assertIn("nano_banana", img_res["asset_id"])

    def test_vault_scan_and_sync(self):
        import tempfile
        import os
        routes = GoogleBridgeRoutes(GoogleBridgeService())

        with tempfile.TemporaryDirectory() as tmp_vault:
            # Create sample files (.md and .yaml)
            doc1 = os.path.join(tmp_vault, "note1.md")
            with open(doc1, "w") as f:
                f.write("# Hello World\nTesting local vault mirror.")
            doc2 = os.path.join(tmp_vault, "config.yaml")
            with open(doc2, "w") as f:
                f.write("theme: mono\nmode: teletext")

            scan_res = routes.scan_vault(tmp_vault)
            self.assertEqual(scan_res["status"], "success")
            self.assertEqual(scan_res["scanned"], 2)
            self.assertEqual(scan_res["updated"], 2)

            # Check that ledger contains them
            records = routes.list_drive_records()["records"]
            paths = [r["vault_path"] for r in records]
            self.assertIn("vault://note1.md", paths)
            self.assertIn("vault://config.yaml", paths)

            # Test vault sync status
            status_res = routes.get_vault_status(tmp_vault)
            self.assertEqual(status_res["status"], "success")
            self.assertEqual(status_res["mirrored_count"], 2)
            self.assertEqual(status_res["modified_count"], 0)
            self.assertEqual(status_res["unmirrored_count"], 0)

    def test_notebook_code_execution(self):
        routes = GoogleBridgeRoutes(GoogleBridgeService())
        res = routes.execute_code("print(1 + 1)", language="python")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["language"], "python")
        self.assertEqual(res["outcome"], "OUTCOME_OK")
        self.assertIn("print(1 + 1)", res["output"])

    def test_gdoc_markdown_roundtrip(self):
        service = GoogleBridgeService()
        sample_md = (
            "---\n"
            "title: Neural Research Notebook\n"
            "type: notebook\n"
            "runtime: gemini\n"
            "---\n\n"
            "# Neural Research Notebook\n"
            "Testing bidirectional offline conversion.\n\n"
            "```python\n"
            "import math\n"
            "print(math.pi)\n"
            "```\n"
        )
        gdoc_payload = service.convert_markdown_to_gdoc(sample_md)
        self.assertEqual(gdoc_payload["title"], "Neural Research Notebook")
        self.assertEqual(gdoc_payload["metadata"]["type"], "notebook")
        self.assertEqual(len(gdoc_payload["body"]["content"]), 3)

        converted_md = service.convert_gdoc_to_markdown(gdoc_payload)
        self.assertIn("title: Neural Research Notebook", converted_md)
        self.assertIn("type: notebook", converted_md)
        self.assertIn("import math", converted_md)

    def test_aiohttp_route_registration(self):
        from aiohttp import web
        from udos_google.routes import register_routes

        app = web.Application()
        register_routes(app)

        registered_paths = [route.resource.canonical for route in app.router.routes()]
        self.assertIn("/api/google/health", registered_paths)
        self.assertIn("/api/google/chat", registered_paths)
        self.assertIn("/api/google/grounded-search", registered_paths)
        self.assertIn("/api/google/image/generate", registered_paths)
        self.assertIn("/api/google/code/execute", registered_paths)
        self.assertIn("/api/google/drive/sync", registered_paths)
        self.assertIn("/api/google/drive/scan", registered_paths)
        self.assertIn("/api/google/drive/status", registered_paths)


if __name__ == "__main__":
    unittest.main()



