"""Serve the product page with the price read from the shop database (DATABASE_URL, a SQLite or Postgres URL)."""

import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

PAGE = Path(__file__).with_name("index.html")


def price_cents(url: str) -> int:
    parsed = urlparse(url)
    if parsed.scheme == "sqlite":
        import sqlite3
        connection = sqlite3.connect(parsed.path)
    else:
        import psycopg  # the shop runs on Postgres in every shared environment
        connection = psycopg.connect(url)
    row = connection.execute("select price_cents from products where slug = 'zaino-trekking-30l'").fetchone()
    return row[0]


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        cents = price_cents(os.environ["DATABASE_URL"])
        body = PAGE.read_text().replace("{{ price }}", f"€ {cents // 100},{cents % 100:02d}").encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    if not os.environ.get("DATABASE_URL"):
        sys.exit("DATABASE_URL is not set: the page reads its prices from the shop database")
    ThreadingHTTPServer(("127.0.0.1", int(sys.argv[1])), Handler).serve_forever()
