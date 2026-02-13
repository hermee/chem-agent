#!/usr/bin/env python3
"""Serve the standalone AI-LNP Agent Dioxus app."""
import http.server
import socketserver
import os

PORT = 8001
DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")

class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".wasm": "application/wasm",
        ".js": "application/javascript",
        ".css": "text/css",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def do_GET(self):
        # SPA fallback: serve index.html for paths that don't match a file
        path = os.path.join(DIR, self.path.lstrip("/"))
        if not os.path.exists(path) and not self.path.startswith("/api"):
            self.path = "/"
        super().do_GET()

socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"🤖 AI-LNP Agent standalone → http://localhost:{PORT}")
    httpd.serve_forever()
