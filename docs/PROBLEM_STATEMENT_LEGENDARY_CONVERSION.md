## Problem Statement — Legendary Hands → Unified Hand Model

We maintain a curated collection of 130 “legendary” poker hands in a JSON
format optimized for display: per-hand `players`, a `board` object, and an
`actions` dictionary keyed by street. This structure is not compatible with the
app’s single source of truth for deterministic replay: the `Hand` model
(`backend/core/hand_model.py`). As a result, the Hands Review tab cannot load
these hands, and attempts to treat them as GTO or Hand-model data raise
conversion errors.

### Purpose

Create a lossless, deterministic representation of all 130 legendary hands in
the standardized `Hand` model so they can be:
- Replayed precisely in Hands Review using `HandModelDecisionEngine`
- Serialized/deserialized with round‑trip integrity (read/write JSON)
- Extended with future analytics (pots, showdown, stats) without changing UI

### Constraints & Approach

- Preserve player identities using canonical IDs ("Player{n}") while keeping
  human‑readable `display_name`.
- Infer blind postings and insert `POST_BLIND` actions for clean preflop state.
- Normalize street actions into ordered `Action` objects with incremental `amount`.
- Map common legendary strings (e.g., "all-in", "3bet") to `ActionType`.
- Carry hole cards into `metadata.hole_cards` for consistent visibility rules.

### Deliverables

- Converter: `core/legendary_to_hand_converter.py` (pure, deterministic)
- CLI: `tools/convert_legendary_cli.py` to convert the full set into a folder
  of per‑hand JSON files plus an index.

### Usage

```bash
python3 backend/tools/convert_legendary_cli.py \
  --input backend/data/legendary_hands_complete_130_fixed.json \
  --outdir backend/data/legendary_converted
```

This writes Hand‑model JSON files and an index to `backend/data/legendary_converted/`.


