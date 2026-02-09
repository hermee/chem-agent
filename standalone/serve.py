#!/usr/bin/env python3
"""Serve the standalone AI-LNP Agent Dioxus app."""
import http.server
import socketserver
import os

PORT = 4300
DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"🤖 AI-LNP Agent standalone → http://localhost:{PORT}")
    httpd.serve_forever()
