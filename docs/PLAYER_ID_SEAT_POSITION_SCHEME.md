## Player Identity, Seat, and Position — Unified Scheme

Problem
- We have recurring bugs from mixing three identities for the same participant:
  - "player_id" strings (e.g., "Player1", human names, or legacy names)
  - `seat_no` (physical chair around the table, 1..N)
  - `position` labels (BTN, SB, BB, UTG, etc.), which change per hand
- Historical formats (legendary/GTO) and Hand model disagree on actor references and the FPSM/renderer expect slightly different identifiers. This causes:
  - Mismatched actors during replay (engine expects PlayerX; action is recorded for PlayerY)
  - Hole cards not revealed (metadata keyed by different names than UI/FPSM use)
  - Wrong first-to-act and blind alignment; stalled replays and missing animations

Design Goals
1. Deterministic actor identity across all layers (loading → engine → FPSM → UI).
2. Separate concerns: identity (stable), seating (physical order), position (derived per hand), display name (UI-only).
3. Backward compatibility with legacy data while avoiding ambiguity going forward.

Core Scheme (Single Source of Truth)
1) Canonical Player UID (stable):
   - Define `player_uid := f"Seat{seat_no}"` (e.g., Seat1..SeatN) as the stable identity used in code and serialized actions.
   - Store a human-friendly `display_name` independently (e.g., "Chris Moneymaker").

2) Hand Model (read/write)
   - `seats: List[Seat]` with fields: `seat_no` (1..N), `player_id` = `player_uid` (SeatX), `display_name`, `starting_stack`.
   - `metadata.hole_cards: Dict[player_uid, [c1,c2]]` — keys are canonical `player_uid`.
   - `streets[STREET].actions[].actor_id` MUST be `player_uid` (SeatX), never display names or index-based aliases.
   - `dealer_position` is implicit via actions: infer from preflop `POST_BLIND(SB/BB)`:
     - Multi-way: `dealer = (sb_seat - 1) % num_players`
     - Heads-up: `dealer = sb_seat`
   - `position` labels (BTN, SB, BB, UTG...) are derived from `dealer` and `num_players` at runtime for display; not used as identity in actions.

3) Converters (legendary/GTO → Hand Model)
   - Normalize names/indices to `player_uid` using `seat_no` from source data. If missing, construct seat map once and persist.
   - Emit explicit `POST_BLIND` actions with `posting_meta.blind_type` in PREFLOP for SB and BB.
   - Sort actions within each street by a global `order`. All action `actor_id` use `player_uid`.
   - Preserve human names as `display_name` only.

4) FPSM (engine + state machine)
   - FPSM `Player.name` MUST equal `player_uid` to round-trip with actions and engine.
   - `get_valid_actions_for_player` and action execution are indexed by seat order; a `uid→index` map is kept internally.
   - For review sessions, align `action_player_index` to the decision engine’s next `actor_uid` before each step.
   - Street transitions/animations are driven by events (`action_executed`, `round_complete`, `state_change`) emitted after each execution.

5) UI (reusable poker game widget)
   - Render using `display_state` that includes for each seat: `player_uid`, `display_name`, `stack`, `current_bet`, and `position` (derived, read-only).
   - Hole cards show logic: resolve from `metadata.hole_cards[player_uid]` when in review mode or at showdown.
   - No business logic; only observe FPSM events and state.

Backward Compatibility
- When loading legacy `player_id` forms ("Player1", real names):
  - Build a one-time normalization map to `player_uid = Seat{seat_no}`.
  - Rewrite actor references during conversion to Hand model.

Validation & Invariants
1. On load, assert:
   - `len(seats) == num_players`
   - `all(SeatX exists for seat_no in 1..N)`
   - For each action, `actor_id in {Seat1..SeatN}`
   - If blinds present: exactly one SB and one BB in PREFLOP
2. During replay:
   - Before executing, sync FPSM next actor to engine’s next `actor_uid`.
   - On street change, emit `round_complete` with the last per-player bet snapshot for correct bet→pot animation.

Migration Plan (incremental)
1. Converters: ensure legendary/GTO importers output `player_uid=Seat{seat_no}` in seats/actions and fill `display_name`.
2. Decision engine: treat `actor_id` as canonical; remove index-based assumptions, but keep a fallback that tolerates Seat→PlayerX aliasing.
3. Hands Review session:
   - Always call `set_preloaded_hand_data({'hand_model': Hand})`.
   - Sync `action_player_index` from engine’s upcoming action before each step.
4. UI: consume `player_uid` and `display_name` distinctly; never infer identity from display strings.

Expected Outcomes
- Deterministic replays with correct first-to-act, street timings, and animations.
- No more name/seat drift between datasets, FPSM, and UI.
- Robust read/write of Hand model JSON with round-trip integrity and clear semantics.


