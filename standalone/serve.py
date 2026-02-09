#!/usr/bin/env python3
"""Serve the standalone AI-LNP Agent Dioxus app."""
import http.server
import os

PORT = 4300
DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")

os.chdir(DIR)
handler = http.server.SimpleHTTPRequestHandler
with http.server.HTTPServer(("0.0.0.0", PORT), handler) as httpd:
    print(f"🤖 AI-LNP Agent standalone → http://localhost:{PORT}")
    httpd.serve_forever()
