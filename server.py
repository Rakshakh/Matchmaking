"""Production-ready minimal server for the Matchmaking app.

Serves static assets and exposes:
- GET /api/health
- GET /api/match?age=29&intent=long-term&interests=hiking,music
"""

from __future__ import annotations

import json
import os
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from matchmaking import Preferences, find_best_match

ROOT_DIR = Path(__file__).parent
PROFILE_PATH = ROOT_DIR / "data" / "profiles.json"


with PROFILE_PATH.open("r", encoding="utf-8") as handle:
    PROFILES = json.load(handle)


def _json(handler: SimpleHTTPRequestHandler, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class MatchmakingHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT_DIR), **kwargs)

    def log_message(self, format: str, *args):
        return super().log_message("[matchmaking] " + format, *args)

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/health":
            return _json(self, {"status": "ok", "profiles": len(PROFILES)})

        if parsed.path == "/api/match":
            return self._handle_match(parsed.query)

        return super().do_GET()

    def _handle_match(self, raw_query: str):
        query = parse_qs(raw_query)

        try:
            age = int(query.get("age", [""])[0])
            intent = query.get("intent", [""])[0].strip().lower()
            interests_csv = query.get("interests", [""])[0]

            if age < 18 or age > 80:
                raise ValueError("age must be between 18 and 80")
            if intent not in {"long-term", "casual", "friendship"}:
                raise ValueError("intent must be one of: long-term, casual, friendship")

            interests = {
                value.strip().lower()
                for value in interests_csv.split(",")
                if value.strip()
            }

            preferences = Preferences(age=age, intent=intent, interests=interests)
            best = find_best_match(preferences, PROFILES)

            return _json(
                self,
                {
                    "match": {
                        "name": best["name"],
                        "age": best["age"],
                        "city": best["city"],
                        "intent": best["intent"],
                        "interests": best["interests"],
                        "score": best["score"],
                    }
                },
            )
        except (ValueError, KeyError) as error:
            return _json(self, {"error": str(error)}, status=HTTPStatus.BAD_REQUEST)


def main() -> None:
    port = int(os.getenv("PORT", "4173"))
    server = ThreadingHTTPServer(("0.0.0.0", port), MatchmakingHandler)
    print(f"Matchmaking server listening on http://0.0.0.0:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
