#!/usr/bin/env python3
"""
SafeGuard AI — Frontend Test Dashboard Server
Serves the `testing_ui` static directory on http://127.0.0.1:8080 and opens browser automatically.
"""

import functools
import http.server
import os
import socket
import socketserver
import sys
import urllib.request
import webbrowser
from pathlib import Path

DEFAULT_PORT = 8080
BACKEND_HEALTH_URL = "http://127.0.0.1:8000/api/v1/health/"


def is_port_in_use(port: int) -> bool:
    """Check whether a port is already occupied."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def find_available_port(start_port: int, max_attempts: int = 20) -> int:
    """Find first available port starting from start_port."""
    for p in range(start_port, start_port + max_attempts):
        if not is_port_in_use(p):
            return p
    return start_port


def check_backend_status() -> bool:
    """Checks if the SafeGuard Django backend is responding on port 8000."""
    try:
        req = urllib.request.Request(
            BACKEND_HEALTH_URL,
            headers={"User-Agent": "SafeGuard-UI-Launcher/1.0"},
        )
        with urllib.request.urlopen(req, timeout=1.5) as response:
            return response.status == 200
    except Exception:
        return False


def main():
    # Set current working directory to this script's directory
    ui_dir = Path(__file__).resolve().parent
    os.chdir(ui_dir)

    port = find_available_port(DEFAULT_PORT)
    ui_url = f"http://127.0.0.1:{port}/"

    print("=" * 65)
    print("   🛡️   SafeGuard AI — API Interactive Testing Suite")
    print("=" * 65)
    print(f"📁 Serving Directory: {ui_dir}")
    print(f"🚀 Dashboard URL:     {ui_url}")
    print("-" * 65)

    backend_alive = check_backend_status()
    if backend_alive:
        print("✅ Backend Status:    CONNECTED to SafeGuard Django API (127.0.0.1:8000)")
    else:
        print("⚠️  Backend Status:    OFFLINE or NOT DETECTED at 127.0.0.1:8000")
        print("   Tip: Run `python manage.py runserver` in the backend folder")
    print("-" * 65)
    print("⌨️  Press Ctrl+C to stop the dashboard server.")
    print("=" * 65)

    # Automatically launch default browser
    try:
        webbrowser.open(ui_url)
    except Exception as e:
        print(f"Note: Could not automatically open browser ({e}).")
        print(f"Please open manually: {ui_url}")

    # Set up HTTP Request Handler
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ui_dir))

    # Enable socket address reuse to prevent "Address already in use" on restarts
    socketserver.TCPServer.allow_reuse_address = True

    try:
        with socketserver.TCPServer(("127.0.0.1", port), handler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down SafeGuard Testing Suite server. Goodbye!")
        try:
            sys.exit(0)
        except SystemExit:
            pass


if __name__ == "__main__":
    main()
