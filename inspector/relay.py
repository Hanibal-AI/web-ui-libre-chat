"""
Locker inspector — a transparent logging relay.

THIS IS A TEMPORARY, TEST-ONLY TOOL. It is not part of the product, not
meant to be run in anything resembling production, and exists purely to
make Locker's masking observable during local testing/demos (see
Docs/roadmap.md Phase 2.1).

Why it exists: Locker itself never logs request/response bodies, by
design (../locker/SECURITY.md) — `docker compose logs locker` shows
nothing about what it masked. To actually see the masked payload Locker
sends upstream, something has to sit between Locker and the real LLM
provider and log what passes through. That's all this does: relay
byte-for-byte, print what it saw.

What it sees is already masked by the time it gets here (Locker forwards
it after masking, this just observes the outbound side) — so raw PII a
user typed is not what shows up in these logs, the placeholder is. What
IS sensitive here: the real provider API key (forwarded through
unmodified in the Authorization header) and full prompt/response content
(masked, but still your conversation data) both pass through this
process in plaintext and land in its stdout logs. Do not leave this
running against real traffic longer than a test session, and never wire
it into anything but a local dev/demo setup.

Usage: set Locker's OPENAI_BASE_URL to this relay's address; it forwards
everything to INSPECTOR_UPSTREAM (the real provider) and prints both
sides. See `make dev-inspect` in the Makefile.
"""

import http.client
import http.server
import json
import os
from urllib.parse import urlparse

UPSTREAM = os.environ.get("INSPECTOR_UPSTREAM", "https://api.openai.com")
PORT = int(os.environ.get("INSPECTOR_PORT", "9091"))
_upstream = urlparse(UPSTREAM)

# Headers that describe *this specific hop's* connection/framing and must
# never be blindly copied from one leg (upstream response) to the other
# (our response to Locker) — each leg sets its own.
_HOP_BY_HOP = {
    "host", "connection", "keep-alive", "transfer-encoding",
    "content-length", "content-encoding",
}


def _pretty(body: bytes) -> str:
    try:
        return json.dumps(json.loads(body), indent=2, ensure_ascii=False)
    except Exception:
        return body.decode(errors="replace")


def _open_upstream(method: str, path: str, body: bytes, src_headers):
    conn_cls = (
        http.client.HTTPSConnection if _upstream.scheme == "https" else http.client.HTTPConnection
    )
    port = _upstream.port or (443 if _upstream.scheme == "https" else 80)
    conn = conn_cls(_upstream.hostname, port, timeout=120)

    headers = {k: v for k, v in src_headers.items() if k.lower() not in _HOP_BY_HOP}
    headers["Host"] = _upstream.hostname
    headers["Content-Length"] = str(len(body))
    # Never ask the upstream to gzip: relaying compressed bytes onward
    # without decompressing would corrupt the client-facing response
    # once Content-Encoding is stripped below.
    headers["Accept-Encoding"] = "identity"

    # INSPECTOR_UPSTREAM's own path (e.g. "/v1") must prefix the incoming
    # path: Locker's provider adapter already strips that prefix before
    # forwarding here, on the assumption the configured base URL restores
    # it — same convention this relay has to honor.
    full_path = _upstream.path.rstrip("/") + path
    conn.request(method, full_path, body=body, headers=headers)
    return conn, conn.getresponse()


class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        print(f"\n=== >>> REQUEST {self.path} (Locker -> {UPSTREAM}) ===", flush=True)
        print(_pretty(body), flush=True)

        conn, resp = _open_upstream("POST", self.path, body, self.headers)
        content_type = resp.getheader("Content-Type", "")
        is_stream = "text/event-stream" in content_type

        if is_stream:
            self._relay_streaming(resp, content_type)
        else:
            self._relay_buffered(resp, content_type)
        conn.close()

    def _relay_buffered(self, resp, content_type):
        # Read the full body first so we can send a correct, self-computed
        # Content-Length — the one bug-for-bug reason to avoid streaming
        # this path: relaying the framing header from one HTTP connection
        # onto a different one (with Content-Encoding stripped) is not
        # generally valid, and left the client hanging when tried.
        data = resp.read()

        self.send_response(resp.status)
        self.send_header("Content-Type", content_type or "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

        print(f"\n=== <<< RESPONSE {self.path} ({UPSTREAM} -> Locker) ===", flush=True)
        print(_pretty(data), flush=True)

    def _relay_streaming(self, resp, content_type):
        self.send_response(resp.status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-cache")
        # No Content-Length for a stream; signal end-of-body by closing
        # the connection once done, instead of chunked-encoding it
        # ourselves (simplest correct framing for a one-shot relay).
        self.send_header("Connection", "close")
        self.close_connection = True
        self.end_headers()

        print(f"\n=== <<< RESPONSE {self.path} ({UPSTREAM} -> Locker) [stream] ===", flush=True)
        collected = bytearray()
        while True:
            chunk = resp.read(1024)
            if not chunk:
                break
            self.wfile.write(chunk)
            self.wfile.flush()
            collected += chunk
        print(collected.decode(errors="replace"), flush=True)

    def log_message(self, fmt, *args):
        pass  # silence the default per-request access log line; the request/response dumps above are the point


if __name__ == "__main__":
    print(f"Locker inspector: relaying http://0.0.0.0:{PORT} -> {UPSTREAM}", flush=True)
    print("TEMPORARY TEST-ONLY TOOL — see the module docstring in relay.py before using this against real traffic.", flush=True)
    http.server.HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
