#!/usr/bin/env python3
"""Download HTMX and Alpine.js into static/js/vendor/ (no CDN at runtime)."""

from pathlib import Path
import urllib.request

VENDORS = {
    "htmx.min.js": "https://unpkg.com/htmx.org@2.0.4/dist/htmx.min.js",
    "alpine.min.js": "https://cdn.jsdelivr.net/npm/alpinejs@3.14.9/dist/cdn.min.js",
}

TARGET_DIR = Path(__file__).resolve().parent / "static" / "js" / "vendor"


def download(url: str, dest: Path) -> None:
    print(f"Downloading {url} -> {dest}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, dest)


def main() -> None:
    for filename, url in VENDORS.items():
        download(url, TARGET_DIR / filename)
    print("Done.")


if __name__ == "__main__":
    main()
