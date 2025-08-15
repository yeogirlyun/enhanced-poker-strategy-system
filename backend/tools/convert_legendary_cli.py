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
from typing import Any, Dict, List

# Local imports
from core.legendary_to_hand_converter import convert_legendary_collection, is_legendary_hand_obj, LegendaryToHandConverter


def load_json(path: str) -> Any:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(path: str, data: Any) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert legendary JSON to Hand-model JSONs with canonical Seat* UIDs")
    parser.add_argument('--input', '-i', required=True, help='Path to legendary JSON (dict with hands:[...]) or list of hand dicts')
    parser.add_argument('--out_dir', '-o', required=True, help='Directory to write per-hand JSON files')
    parser.add_argument('--combined', '-c', help='Optional combined JSON (array of Hand objects)')
    args = parser.parse_args()

    raw = load_json(args.input)

    # Normalize to collection dict for the converter
    if isinstance(raw, dict) and 'hands' in raw:
        collection = raw
    elif isinstance(raw, list):
        collection = {'hands': raw}
    else:
        raise SystemExit('Input must be list of hands or dict with hands key')

    hands = convert_legendary_collection(collection)
    print(f"Converted {len(hands)} hands")

    # Save individual files
    count = 0
    for hand in hands:
        hand_id = hand.metadata.hand_id or f"LEG-{count+1:04d}"
        out_path = os.path.join(args.out_dir, f"{hand_id}.json")
        save_json(out_path, hand.to_dict())
        count += 1

    print(f"Wrote {count} hand-model JSONs to {args.out_dir}")

    # Save combined if requested
    if args.combined:
        combined_data = [h.to_dict() for h in hands]
        save_json(args.combined, combined_data)
        print(f"Wrote combined file to {args.combined}")


if __name__ == '__main__':
    main()


