#!/usr/bin/env python3
"""Static file server for local preview with no-cache headers.

python -m http.server sends no Cache-Control, so browsers heuristically
cache its responses — stale pages (and stale redirects) survive rebuilds.
This serves the same directory but marks every response no-store.

Usage: python serve_local.py  (serves site/_build/html on port 8000)
"""

import http.server

DIRECTORY = "site/_build/html"
PORT = 8000


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


if __name__ == "__main__":
    http.server.ThreadingHTTPServer(("", PORT), NoCacheHandler).serve_forever()
