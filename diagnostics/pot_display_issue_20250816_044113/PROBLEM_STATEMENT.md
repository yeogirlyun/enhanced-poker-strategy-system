Title: Pot display not rendering in Hands Review widget (canvas readiness & z-order)

Context
- App: Poker Strategy Practice System (Hands Review tab)
- Widget: backend/ui/components/reusable_poker_game_widget.py
- Symptom: Center pot graphics often does not appear during replay. Board and seats render; bet chips animate; pot remains missing.

Observed logs (system_* log excerpts)
- Repeated lines: "Deferring pot display creation - canvas too small: 1x1" during initial rendering.
- After previous fixes, still no visible pot, suggesting either 1) creation continues to happen before canvas sizes, or 2) it’s created but obscured.

What we attempted
1) Deterministic board replay and review-mode deck (unrelated to pot, but ensured table flow was correct).
2) Pot creation improvements in _draw_pot_display():
   - Calculate pot position below board with seat-aware spacing
   - Size pot via metrics; store window id
   - Raise pot window to top
3) Update-path hardening in update_pot_amount():
   - If pot exists: set amount + raise; else draw then set
   - Added diagnostics: coords, viewable flags, community coords
4) Defer-create when canvas not yet sized:
   - Earlier version: naive after(100–180ms) retry
   - New version: readiness helpers `_is_canvas_ready()` + `_wait_then()` to retry until width/height≥200, then create and set amount
5) Seat/board layout fixes to avoid overlap with pot (HU left/right seats, board lowered a bit).

Why it still failed
- Latest logs still showed frequent 1x1 size deferrals originally; after readiness code landed, pot still not visible. Two remaining hypotheses:
  A) The readiness guard lives in update_pot_amount(), but the first few calls happen before widget binding / event loop settles; no subsequent pot updates are invoked after readiness, so create never fires.
  B) The pot window is created but ends under another canvas item (z-order race) or outside visible region. We raise the tag, but if the id wasn't created due to readiness short-circuit, there is nothing to raise.

Next steps proposed
- Emit a forced pot update upon first successful canvas draw (_draw_table end) using the last known pot amount, guarded by readiness → guarantees one creation pass after the table is fully drawn.
- If no amount is known, create pot widget at $0.00 just to establish window id, then let subsequent updates set amount.
- Add a one-off z-order audit: after creation, dump canvas stack order and ids for pot + community; if pot not top, force tag_raise.

Files of interest (included below)
- backend/ui/components/reusable_poker_game_widget.py (pot creation + update)
- backend/ui/components/modern_poker_widgets.py (ChipStackDisplay)
- backend/core/flexible_poker_state_machine.py (get_game_info + emit events; board/seat states)
- Latest system log snippets.

