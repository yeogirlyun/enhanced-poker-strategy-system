# 🚨 UI Bug Report: Initial Small Poker Table Remnants

## Summary
On first render of Hands Review, a smaller poker table appears briefly and leaves visual remnants under the full‑size table. This suggests an early draw using a fallback canvas size before the layout is resolved. The stale drawing is not fully cleared when the correct size arrives.

## Environment
- OS: macOS 14 (Sonoma) – darwin 24.6.0
- Python: system python3
- App area: `backend/ui/tabs/hands_review_tab.py` and `backend/ui/tableview/*`

## Steps to Reproduce
1. Launch the new UI and open the Hands Review tab.
2. Observe the table area on the right pane on initial load.

## Expected
- The poker table should render once at the final layout size and occupy the pane without artifacts.

## Actual
- A small table appears (roughly default 800×600) and portions of that first draw remain visible after the full‑size render. Artifacts look like a smaller oval felt under the large table.

## Evidence / Clues
- Renderer prints indicate a fallback size may be used:
  - `🎨 Rendered poker table: 800x600 ...` (first paint)
  - then resized paints with correct dimensions.
- `RendererPipeline.render_once` uses a fallback size if canvas width/height ≤ 1 and draws immediately.
- Layer cleanup deletes a fixed set of tags but stale shapes may have been drawn with unexpected tags from first render.

## Suspected Root Cause
1. Canvas renders before the parent layout has established a real size, so defaults (800×600) are used for the first frame.
2. The first render creates oval felt and accents that are not fully removed when the second, correctly sized render runs.

## Recent Attempts/Mitigations Present Now
- `CanvasManager.__init__` sets the canvas size to the parent’s width/height on init and binds `<Configure>` to manage overlay order.
- `TableFelt.render` clears many felt‑related tags at the start of each render.

Despite these, the initial small render still occurs on the reporter’s machine.

## Candidate Fixes
- Defer the first render until we observe a meaningful parent size (e.g., via a one‑shot `<Configure>` handler or by scheduling after `update_idletasks()` and checking width/height > threshold).
- Add an initial “full clear” on the very first render, including any generic tags that could be left by the fallback draw, and avoid drawing with fallback 800×600 unless absolutely necessary.
- Ensure that all shapes in `TableFelt` are consistently tagged with `layer:felt` (and sub‑tags) so a single `delete('layer:felt')` removes all remnants.

## Impact
- Cosmetic but persistent; undermines professional look and can confuse users about the table size.

## Files of Interest
- `backend/ui/tableview/renderer_pipeline.py`
- `backend/ui/tableview/canvas_manager.py`
- `backend/ui/tableview/components/table_felt.py`
- `backend/ui/tabs/hands_review_tab.py`

## Minimal Repro State
- Open app to Hands Review with any theme; no hand needs to be loaded to observe artifact.

## Proposed Acceptance Criteria
- No visual remnants from any pre‑layout draw.
- First visible table matches the final pane size.
- Subsequent resizes remain clean without ghosting.


