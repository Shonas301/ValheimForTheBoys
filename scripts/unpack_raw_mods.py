#!/usr/bin/env python3
"""Unpack archives found in ./raw_mods into per-archive subdirectories.

This script will iterate files in the raw_mods directory and attempt to
unpack them using shutil.unpack_archive (supports zip, tar, gztar, bztar, xztar).
Each archive is extracted into `raw_mods/<archive-basename>/`.
"""

from __future__ import annotations

import argparse
import logging
import shutil
from pathlib import Path

from term import action, meta, note, warn


def unpack_all(raw_dir: Path, remove_archive: bool = False) -> int:
    if not raw_dir.exists():
        logging.error("raw_mods directory does not exist: %s", raw_dir)
        return 2

    extracted = []
    skipped = []

    for p in sorted(raw_dir.iterdir()):
        if p.is_dir():
            continue
        name = p.stem
        target = raw_dir / name
        try:
            logging.info(action("Attempting to unpack") + f" {p.name} -> {target}")
            target.mkdir(parents=True, exist_ok=True)
            # shutil.unpack_archive will raise if format unsupported
            shutil.unpack_archive(str(p), str(target))
            extracted.append((p.name, target))
            if remove_archive:
                p.unlink()
        except shutil.ReadError:
            logging.warning(warn(f"Skipping unsupported archive: {p.name}"))
            skipped.append(p.name)
        except Exception:
            logging.exception(warn(f"Failed to unpack {p.name}"))
            skipped.append(p.name)

    logging.info(
        meta(
            f"Extraction complete. Extracted: {len(extracted)}, Skipped: {len(skipped)}"
        )
    )
    if extracted:
        for a, t in extracted:
            logging.info(note(f" - {a} -> {t}"))
    if skipped:
        logging.info(warn(f"Skipped archives: {', '.join(skipped)}"))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Unpack archives in raw_mods/")
    parser.add_argument(
        "--remove",
        action="store_true",
        help="Remove archive files after successful extraction",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    repo_root = Path(__file__).resolve().parents[1]
    raw_dir = repo_root / "raw_mods"
    return unpack_all(raw_dir, remove_archive=args.remove)


if __name__ == "__main__":
    raise SystemExit(main())
