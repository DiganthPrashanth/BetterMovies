import re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parent
MOVIE_PATH = "/Movies/Spider-Man (2002) Open Matte 35Mm 1440P Scan.mkv"
MOVIE = ROOT / unquote(MOVIE_PATH.lstrip("/"))


class MovieHandler(SimpleHTTPRequestHandler):
    def _serve_movie(self, send_body):
        size = MOVIE.stat().st_size
        range_header = self.headers.get("Range")
        start, end = 0, size - 1

        if range_header:
            match = re.fullmatch(r"bytes=(\d*)-(\d*)", range_header.strip())
            if not match or (not match.group(1) and not match.group(2)):
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{size}")
                self.end_headers()
                return

            first, last = match.groups()
            if first:
                start = int(first)
                end = min(int(last), size - 1) if last else size - 1
            else:
                suffix_length = int(last)
                start = max(size - suffix_length, 0)

            if start >= size or end < start:
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{size}")
                self.end_headers()
                return

        partial = range_header is not None
        self.send_response(206 if partial else 200)
        self.send_header("Content-Type", "video/x-matroska")
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(end - start + 1))
        if partial:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.end_headers()

        if send_body:
            with MOVIE.open("rb") as movie:
                movie.seek(start)
                remaining = end - start + 1
                while remaining:
                    chunk = movie.read(min(256 * 1024, remaining))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    remaining -= len(chunk)

    def do_GET(self):
        if unquote(urlsplit(self.path).path) == MOVIE_PATH:
            self._serve_movie(send_body=True)
            return
        super().do_GET()

    def do_HEAD(self):
        if unquote(urlsplit(self.path).path) == MOVIE_PATH:
            self._serve_movie(send_body=False)
            return
        super().do_HEAD()


if __name__ == "__main__":
    if not MOVIE.is_file():
        raise FileNotFoundError(f"Movie file not found: {MOVIE}")

    server = ThreadingHTTPServer(("127.0.0.1", 8000), MovieHandler)
    print("Serving BetterMovies at http://127.0.0.1:8000/Spider-Man_(2002).html")
    print("The browser reads the original MKV directly; no media copies are created.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping BetterMovies server.")
    finally:
        server.server_close()
