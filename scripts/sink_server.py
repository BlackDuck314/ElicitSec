"""Minimal deterministic egress sink (local rig only).

Accepts HTTP POST, stores each receipt as JSON in ./egress/receipts/,
and serves a listing on GET /receipts. Never forwards anything.
"""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

OUT = Path(__file__).parent / "egress_receipts"


class H(BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(n).decode("utf-8", "replace")
        OUT.mkdir(parents=True, exist_ok=True)
        p = OUT / f"receipt-{len(list(OUT.iterdir())):05d}.json"
        p.write_text(json.dumps({
            "destination": self.path,
            "headers": dict(self.headers),
            "body": body,
        }))
        self.send_response(202)
        self.end_headers()
        self.wfile.write(b"queued")

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        OUT.mkdir(parents=True, exist_ok=True)
        self.wfile.write(json.dumps([p.name for p in sorted(OUT.iterdir())]).encode())

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8899), H).serve_forever()
