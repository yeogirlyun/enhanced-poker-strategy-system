from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Tuple


class HandsRepository:
    """
    Simple repository that enumerates available hands from known data folders
    and loads them into a list of display-state snapshots usable by the UI.
    """

    SEARCH_DIRS = [
        os.path.join(
            "backend",
            "data",
            "legendary_hands_valid_nlhe_canonical",
            "per_hand",
        ),
        os.path.join(
            "backend",
            "data",
            "legendary_hands_canonical_uid_handmodel",
            "per_hand",
        ),
        os.path.join("backend", "data"),
    ]

    def list_sources(self) -> List[Tuple[str, str]]:
        """Return existing (display_name, base_path) sources."""
        sources: List[Tuple[str, str]] = []
        for base in self.SEARCH_DIRS:
            if os.path.isdir(base):
                name = os.path.basename(base)
                sources.append((name, base))
        return sources

    def list_hands(
        self,
        base_path: str | None = None,
        search_text: str | None = None,
    ) -> List[Tuple[str, str]]:
        """Return list of (display_name, path), optionally filtered."""
        result: List[Tuple[str, str]] = []
        bases = [base_path] if base_path else self.SEARCH_DIRS
        for base in bases:
            if not os.path.isdir(base):
                continue
            for name in sorted(os.listdir(base)):
                if name.lower().endswith(".json"):
                    path = os.path.join(base, name)
                    display = os.path.splitext(name)[0]
                    if (
                        search_text
                        and search_text.lower() not in display.lower()
                    ):
                        continue
                    result.append((display, path))
        return result

    def load_snapshots(self, path: str) -> List[Dict[str, Any]]:
        """
        Load a hand file and return a list of display-state-like snapshots.
        Heuristic parsing to accommodate multiple file shapes.
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return []

        # Common shapes
        candidates: List[List[Dict[str, Any]]] = []
        for key in [
            "display_states",
            "timeline",
            "frames",
            "states",
            "steps",
        ]:
            seq = data.get(key)
            if isinstance(seq, list):
                candidates.append(seq)

        # Nested shapes
        for key in ["hand", "content", "data"]:
            inner: Any = data.get(key)
            if isinstance(inner, dict):
                for sub in [
                    "display_states",
                    "timeline",
                    "frames",
                    "states",
                    "steps",
                ]:
                    seq = inner.get(sub)
                    if isinstance(seq, list):
                        candidates.append(seq)

        if not candidates:
            # Single snapshot fallback
            if any(k in data for k in ("pot", "board", "players")):
                return [data]
            return []

        # Normalize to expected dict: pot/board/players/dealer_position
        out: List[Dict[str, Any]] = []
        for seq in candidates:
            for entry in seq:
                if not isinstance(entry, dict):
                    continue
                snap = self._coerce_snapshot(entry)
                if snap:
                    out.append(snap)
        return out

    def _coerce_snapshot(self, entry: Dict[str, Any]) -> Dict[str, Any] | None:
        # Some datasets may nest display_state
        base = entry.get("display_state")
        ds: Dict[str, Any]
        if isinstance(base, dict):
            ds = base
        else:
            ds = entry
        pot = ds.get("pot", entry.get("pot", 0))
        board = ds.get("board", entry.get("board", []))
        players = ds.get("players", entry.get("players", []))
        dealer = ds.get(
            "dealer_position",
            ds.get(
                "dealer_index",
                entry.get("dealer_index", 0),
            ),
        )
        try:
            return {
                "pot": int(pot or 0),
                "board": list(board or []),
                "players": list(players or []),
                "dealer_position": int(dealer or 0),
            }
        except Exception:
            return None
