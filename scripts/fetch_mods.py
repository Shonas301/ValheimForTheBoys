#!/usr/bin/env python3
"""Download mod artifacts into ./raw_mods, replicating scripts/install.sh behavior.

This script uses `env.py` for the URL list and saves files into the project's
`raw_mods` directory. It supports a --dry-run flag to print actions without
performing downloads.
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import List
from urllib.parse import urlsplit

from unpack_raw_mods import unpack_all
from term import action, note, warn, meta

try:
    import requests  # type: ignore

    _HAS_REQUESTS = True
except Exception:
    _HAS_REQUESTS = False


def basename_from_url(url: str) -> str:
    return Path(urlsplit(url).path).name or url


def download_requests(url: str, dest: Path) -> None:
    dest_path = dest / basename_from_url(url)
    logging.info(action("Fetching") + f" {url}")
    logging.info(meta(f"-> {dest_path.name}"))
    resp = requests.get(url, stream=True)
    resp.raise_for_status()
    with open(dest_path, "wb") as out:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                out.write(chunk)


def download_urllib(url: str, dest: Path) -> None:
    import urllib.request

    dest_path = dest / basename_from_url(url)
    logging.info(action("Fetching") + f" {url}")
    logging.info(meta(f"-> {dest_path.name}"))
    with urllib.request.urlopen(url) as resp, open(dest_path, "wb") as out:
        out.write(resp.read())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Download mod zips into raw_mods/")
    parser.add_argument(
        "--dry-run", action="store_true", help="Print actions without downloading"
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    # Load env.yaml next to this script
    fetch_and_unpack(dry_run=args.dry_run)


def fetch_and_unpack(dry_run: bool = False) -> None:
    env_yaml = Path(__file__).resolve().parent / "env.yaml"
    urls: List[str] = []
    if env_yaml.exists():
        try:
            import yaml  # type: ignore

            with env_yaml.open("r", encoding="utf-8") as fh:
                docs = yaml.safe_load(fh)
                if isinstance(docs, list):
                    for item in docs:
                        if isinstance(item, dict) and "url" in item:
                            urls.append(str(item["url"]))
        except Exception:
            # Fallback simple parser for this specific YAML shape
            for line in env_yaml.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("url:"):
                    _, v = line.split("url:", 1)
                    urls.append(v.strip())
    else:
        logging.error("env.yaml not found at %s", env_yaml)
        return 2

    dest = Path(__file__).resolve().parents[1] / "raw_mods"
    dest.mkdir(parents=True, exist_ok=True)

    for url in urls:
        if dry_run:
            logging.info(note("Would fetch") + f" {url} -> {basename_from_url(url)}")
            continue
        try:
            if _HAS_REQUESTS:
                download_requests(url, dest)
            else:
                download_urllib(url, dest)
        except Exception:
            logging.exception(warn(f"Failed to download {url}"))

    unpack_all(dest, remove_archive=False)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
