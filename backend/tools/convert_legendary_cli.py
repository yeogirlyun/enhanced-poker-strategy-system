#!/usr/bin/env python3
"""
CLI: Convert legendary JSON → Hand model JSONL or folder of hands

Usage:
  python3 backend/tools/convert_legendary_cli.py \
      --input backend/data/legendary_hands_complete_130_fixed.json \
      --outdir backend/data/legendary_converted

Output:
  - Writes one Hand-model JSON per legendary hand to --outdir, named by hand id
  - Also writes an index file `hands_index.json` listing created files
"""

from __future__ import annotations

import argparse
import json
import os
from typing import List

# Run-from-backend imports
from core.hand_model import Hand
from core.legendary_to_hand_converter import convert_legendary_collection


def ensure_dir(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def save_hand(outdir: str, hand: Hand) -> str:
    hand_id = hand.metadata.hand_id or "LEG-UNKNOWN"
    # Sanitize filename
    safe_id = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in hand_id)
    outpath = os.path.join(outdir, f"{safe_id}.json")
    hand.save_json(outpath)
    return outpath


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert legendary JSON to Hand model files")
    parser.add_argument("--input", required=True, help="Path to legendary JSON file")
    parser.add_argument("--outdir", required=True, help="Directory to write Hand model JSON files")
    args = parser.parse_args()

    ensure_dir(args.outdir)

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    hands: List[Hand] = convert_legendary_collection(data)
    index = []
    for h in hands:
        path = save_hand(args.outdir, h)
        index.append({"hand_id": h.metadata.hand_id, "path": path})

    with open(os.path.join(args.outdir, "hands_index.json"), "w", encoding="utf-8") as f:
        json.dump({"count": len(index), "hands": index}, f, ensure_ascii=False, indent=2)

    print(f"Converted {len(index)} hands → {args.outdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


