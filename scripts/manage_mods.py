#!/usr/bin/env python3
"""Replicates `install_mods.sh` behavior in Python.

Supported commands: copy, install, remove, fetch

This script performs filesystem operations; use with care. It keeps the same
default paths as the original script but expands ~ and supports dry-run.
"""

from __future__ import annotations

import argparse
import logging
import shutil
import sys
from pathlib import Path

from fetch_mods import fetch_and_unpack
from term import action, note

INSTALL_LOC = Path("/mnt/c/Program Files (x86)/Steam/steamapps/common/Valheim/")
MODDIR = INSTALL_LOC / "BepInEx" / "plugins"
COPYDIR = Path.home() / "val" / "plugins"
BEPINEX = [
    "BepInEx",
    "doorstop_libs",
    "doorstop_config.ini",
    "winhttp.dll",
]
BEPINCOPY = Path.home() / "val" / "bepin"


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def copy_bepinex(dry_run: bool = False) -> None:
    if not BEPINCOPY.exists():
        logging.info("creating copy of BepInEx")
        if not dry_run:
            ensure_dir(BEPINCOPY)

    for f in BEPINEX:
        src = INSTALL_LOC / f
        dest = BEPINCOPY / f
        logging.info("Copying %s -> %s", src, dest)
        if dry_run:
            continue
        if src.exists():
            if src.is_dir():
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(src, dest)
            else:
                ensure_dir(dest.parent)
                shutil.copy2(src, dest)
        else:
            logging.warning("Source %s does not exist, skipping", src)


def print_mods() -> None:
    # Print top-level dlls
    for f in (COPYDIR).glob("*.dll"):
        print("> %s" % f.stem)
    # Print recursive dlls
    for f in (COPYDIR).rglob("*.dll"):
        print("> %s" % f.stem)


def copy_plugin_mods(dry_run: bool = False) -> None:
    if not MODDIR.exists():
        logging.error("Failure: MODDIR %s does not exist", MODDIR)
        sys.exit(1)

    if not COPYDIR.exists():
        logging.info("Creating copy of mods in %s", COPYDIR)
        if not dry_run:
            ensure_dir(COPYDIR)

    logging.info("Copying plugins from %s to %s", MODDIR, COPYDIR)
    if not dry_run:
        # copy contents of MODDIR into COPYDIR
        for item in MODDIR.iterdir():
            dest = COPYDIR / item.name
            if item.is_dir():
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)

    logging.info("Moved Mods:")
    print_mods()


def copy_mods(dry_run: bool = False) -> None:
    copy_plugin_mods(dry_run=dry_run)
    copy_bepinex(dry_run=dry_run)


def remove_mods(dry_run: bool = False) -> None:
    copy_mods(dry_run=dry_run)
    for f in BEPINEX:
        target = INSTALL_LOC / f
        logging.info(action(f"Removing {target}"))
        if dry_run:
            continue
        if target.exists():
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()


def reinstall(dry_run: bool = False) -> None:
    src_dir = Path.home() / "val" / "bepin"
    if not src_dir.exists():
        logging.error("Source directory %s does not exist", src_dir)
        sys.exit(1)
    for f in src_dir.iterdir():
        dest = INSTALL_LOC / f.name
        logging.info(action(f"Installing {f} -> {dest}"))
        if dry_run:
            continue
        if f.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(f, dest)
        else:
            shutil.copy2(f, dest)


def install_cmd(dry_run: bool = False) -> None:
    fetch_and_unpack(dry_run=dry_run)
    move_extracted_raw_mods(dry_run=dry_run)


def move_extracted_raw_mods(dry_run: bool = False) -> None:
    """Move contents of each extracted directory in raw_mods into MODDIR.

    For each directory under project/raw_mods, move its child files/dirs into
    the game's plugin directory `MODDIR`. If an item already exists at the
    destination, it will be removed and replaced.
    """
    repo_root = Path(__file__).resolve().parents[1]
    raw_dir = repo_root / "raw_mods"
    if not raw_dir.exists():
        logging.info("No raw_mods directory found at %s, skipping move", raw_dir)
        return

    for item in sorted(raw_dir.iterdir()):
        if not item.is_dir():
            # skip top-level files (archives) — prefer extracted dirs
            continue
        logging.info(action(f"Moving contents of {item} into {MODDIR}"))
        for child in item.iterdir():
            dest = MODDIR / child.name
            logging.info(note(f" - {child} -> {dest}"))
            if dry_run:
                continue
            # Ensure MODDIR exists
            ensure_dir(MODDIR)
            # If destination exists, remove it
            if dest.exists():
                if dest.is_dir():
                    shutil.rmtree(dest)
                else:
                    dest.unlink()
            # Move (rename) where possible, copy otherwise
            try:
                child.replace(dest)
            except Exception:
                # fallback to copy
                if child.is_dir():
                    shutil.copytree(child, dest)
                else:
                    shutil.copy2(child, dest)


def fetch() -> None:
    logging.info("Not Implemented")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Install/copy/remove Valheim mods")
    parser.add_argument(
        "cmd", choices=["remove", "install", "fetch", "copy"], help="command to run"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="show actions without applying them"
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    if args.cmd == "remove":
        remove_mods(dry_run=args.dry_run)
    elif args.cmd == "install":
        install_cmd(dry_run=args.dry_run)
    elif args.cmd == "fetch":
        fetch()
    elif args.cmd == "copy":
        copy_mods(dry_run=args.dry_run)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
