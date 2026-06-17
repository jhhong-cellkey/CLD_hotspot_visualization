#!/usr/bin/env python3
"""Static file server with HTTP Range support for IGV.js."""

from __future__ import annotations

import argparse
import io
import os
import shutil
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path


class RangeHTTPRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self) -> None:
        self.send_header("Accept-Ranges", "bytes")
        super().end_headers()

    def do_GET(self) -> None:
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            super().do_GET()
            return

        try:
            file_size = os.path.getsize(path)
        except OSError:
            self.send_error(404, "File not found")
            return

        range_header = self.headers.get("Range")
        with open(path, "rb") as handle:
            if range_header:
                start, end = self._parse_range(range_header, file_size)
                if start is None:
                    self.send_error(416, "Requested Range Not Satisfiable")
                    return

                handle.seek(start)
                chunk = handle.read(end - start + 1)
                self.send_response(206)
                self.send_header("Content-Type", self.guess_type(path))
                self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
                self.send_header("Content-Length", str(len(chunk)))
                self.end_headers()
                self.wfile.write(chunk)
                return

            self.send_response(200)
            self.send_header("Content-Type", self.guess_type(path))
            self.send_header("Content-Length", str(file_size))
            self.end_headers()
            shutil.copyfileobj(handle, self.wfile)

    def _parse_range(self, range_header: str, file_size: int) -> tuple[int | None, int | None]:
        units, _, range_spec = range_header.partition("=")
        if units.strip().lower() != "bytes" or "," in range_spec:
            return None, None

        start_text, _, end_text = range_spec.partition("-")
        if not start_text and not end_text:
            return None, None

        if start_text:
            start = int(start_text)
            end = int(end_text) if end_text else file_size - 1
        else:
            suffix = int(end_text)
            start = max(file_size - suffix, 0)
            end = file_size - 1

        if start >= file_size or start > end:
            return None, None

        return start, min(end, file_size - 1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve IGV static files with Range support.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8020)
    parser.add_argument(
        "--directory",
        default=str(Path(__file__).resolve().parent),
        help="Directory to serve",
    )
    args = parser.parse_args()

    os.chdir(args.directory)
    server = ThreadingHTTPServer((args.host, args.port), RangeHTTPRequestHandler)
    print(f"Serving {args.directory} on http://{args.host}:{args.port}/")
    server.serve_forever()


if __name__ == "__main__":
    main()
