"""
World Engine Local Server.
==========================
Lightweight HTTP server providing writer dashboard hosting and REST API endpoints.
Uses Python standard library (http.server) with zero external server dependencies.
"""

from __future__ import annotations

import json
import logging
import mimetypes
import os
import sys
import threading
import urllib.parse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, Optional

from world_engine.dashboard.builder import build_dashboard_html
from world_engine.law_catalog.recommender import DomainLawRecommender

logger = logging.getLogger("world_engine.serve")


class WorldEngineHTTPHandler(BaseHTTPRequestHandler):
    """Custom request handler serving the dashboard and REST API."""

    def log_message(self, format: str, *args: Any) -> None:
        # Suppress noisy logging during standard operation
        pass

    def _send_json(self, data: Any, status: int = HTTPStatus.OK) -> None:
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # REST API endpoints
        if path == "/api/status":
            self._send_json({
                "engine_version": "2.5.0",
                "status": "deterministic_green",
                "subsystems_passed": 30,
                "laws_count": 41,
                "benchmark": "قطار الرمل",
            })
            return

        if path == "/api/health":
            self._send_json({"status": "healthy"})
            return

        # Serve static dashboard files
        root_dir = Path(__file__).resolve().parent.parent
        docs_dir = root_dir / "docs"

        if path in ("/", "/index.html", "/dashboard"):
            target_file = docs_dir / "writer_dashboard.html"
            if not target_file.exists():
                build_dashboard_html(output_path=target_file)
        else:
            # Strip leading slash and normalize
            rel = path.lstrip("/")
            target_file = docs_dir / rel

        if target_file.exists() and target_file.is_file():
            content_type, _ = mimetypes.guess_type(str(target_file))
            content_type = content_type or "application/octet-stream"
            with open(target_file, "rb") as f:
                content = f.read()

            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", f"{content_type}; charset=utf-8" if "text" in content_type else content_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length > 0 else ""

        try:
            req_data = json.loads(body) if body else {}
        except Exception:
            req_data = {"text": body}

        text = req_data.get("text", "")

        if path == "/api/recommend-rules":
            recommender = DomainLawRecommender()
            rec = recommender.recommend_for_text(text)
            self._send_json({
                "recommended_pack": rec.recommended_pack_id,
                "confidence": rec.confidence_score,
                "matched_keywords": rec.matched_keywords,
                "suggested_rules_count": len(rec.suggested_rules),
                "suggested_rules": rec.suggested_rules,
            })
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Endpoint not found")


class DashboardServer:
    """Server runner with thread-safe startup and shutdown."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8080):
        self.host = host
        self.port = port
        self.httpd: Optional[HTTPServer] = None
        self._thread: Optional[threading.Thread] = None

    def start(self, background: bool = False) -> None:
        """Start the HTTP server."""
        self.httpd = HTTPServer((self.host, self.port), WorldEngineHTTPHandler)
        if background:
            self._thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
            self._thread.start()
        else:
            print(f"[*] World Engine Writer Dashboard running at http://{self.host}:{self.port}")
            print("[*] Press Ctrl+C to terminate.")
            try:
                self.httpd.serve_forever()
            except KeyboardInterrupt:
                self.stop()

    def stop(self) -> None:
        """Stop the HTTP server."""
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
            self.httpd = None


def run_server(host: str = "127.0.0.1", port: int = 8080, open_browser: bool = False) -> None:
    """CLI entry point for running the dashboard server."""
    # Ensure writer_dashboard.html is built
    root_dir = Path(__file__).resolve().parent.parent
    dash_file = root_dir / "docs" / "writer_dashboard.html"
    if not dash_file.exists():
        build_dashboard_html(output_path=dash_file)

    if open_browser:
        import webbrowser
        webbrowser.open(f"http://{host}:{port}")

    server = DashboardServer(host=host, port=port)
    server.start(background=False)
