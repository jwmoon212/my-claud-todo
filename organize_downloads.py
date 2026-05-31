#!/usr/bin/env python3
"""
organize_downloads.py
Organizes ~/Downloads: images → Pictures, PDFs → Documents, old files → Archive
Runs a dry-run first, then prompts before moving anything.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

# ── config ─────────────────────────────────────────────────────────────────────

SOURCE    = Path.home() / "Downloads"
PICTURES  = SOURCE / "Pictures"
DOCUMENTS = SOURCE / "Documents"
ARCHIVE   = SOURCE / "Archive"

IMAGE_EXTS  = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".svg", ".ico"}
CUTOFF_DAYS = 30

# ── helpers ────────────────────────────────────────────────────────────────────

def unique_target(path: Path) -> Path:
    """Return path unchanged if free, otherwise append _1, _2, … until free."""
    if not path.exists():
        return path
    stem, suffix, parent = path.stem, path.suffix, path.parent
    n = 1
    while (candidate := parent / f"{stem}_{n}{suffix}").exists():
        n += 1
    return candidate

# ── collect moves ──────────────────────────────────────────────────────────────

Move = dict  # keys: file, from_path, to_path, dest, reason

cutoff = datetime.now() - timedelta(days=CUTOFF_DAYS)
moves: list[Move] = []

for entry in SOURCE.iterdir():
    if not entry.is_file():
        continue

    ext = entry.suffix.lower()
    dest = reason = None

    if ext in IMAGE_EXTS:
        dest, reason = PICTURES, "image"
    elif ext == ".pdf":
        dest, reason = DOCUMENTS, "PDF"
    else:
        mtime = datetime.fromtimestamp(entry.stat().st_mtime)
        if mtime < cutoff:
            dest, reason = ARCHIVE, f"older than {CUTOFF_DAYS} days"

    if dest:
        moves.append({
            "file":      entry.name,
            "from_path": entry,
            "to_path":   dest / entry.name,
            "dest":      dest,
            "reason":    reason,
        })

# ── dry-run report ─────────────────────────────────────────────────────────────

CYAN   = "\033[0;36m"
YELLOW = "\033[0;33m"
GREEN  = "\033[0;32m"
RED    = "\033[0;31m"
RESET  = "\033[0m"

if not moves:
    print("Nothing to move.")
    raise SystemExit(0)

print(f"\n{CYAN}=== DRY RUN — nothing has been moved yet ==={RESET}\n")

groups: dict[Path, list[Move]] = defaultdict(list)
for m in moves:
    groups[m["dest"]].append(m)

for dest in (PICTURES, DOCUMENTS, ARCHIVE):
    group = groups.get(dest)
    if not group:
        continue
    label = dest.name
    print(f"{YELLOW}[{label}]  ({len(group)} file(s)){RESET}")
    for m in group:
        print(f"  {m['file']}  [{m['reason']}]")
    print()

print(f"{CYAN}Total: {len(moves)} file(s) will be moved.{RESET}\n")

# ── confirm ────────────────────────────────────────────────────────────────────

answer = input("Proceed? (yes/no) ").strip().lower()
if answer not in ("yes", "y"):
    print(f"{RED}Aborted. No files were moved.{RESET}")
    raise SystemExit(0)

# ── move ───────────────────────────────────────────────────────────────────────

for d in (PICTURES, DOCUMENTS, ARCHIVE):
    d.mkdir(parents=True, exist_ok=True)

moved = errors = 0

for m in moves:
    target = unique_target(m["to_path"])
    try:
        shutil.move(str(m["from_path"]), target)
        print(f"{GREEN}Moved: {m['file']} → {m['dest'].name}{RESET}")
        moved += 1
    except Exception as e:
        print(f"{RED}ERROR moving {m['file']}: {e}{RESET}")
        errors += 1

print(f"\n{CYAN}Done. {moved} moved, {errors} error(s).{RESET}")
