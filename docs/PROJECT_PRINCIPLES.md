## Poker Project Principles — Identity, Seating, Positions, and Determinism

This document is the reference for AI/code review enforcement. All code, data, and UI must conform to these principles.

### 1) Identities vs Seating vs Positions
- **player_uid (canonical, stable within a hand)**: use `Seat{seat_no}` or `P{seat_no}` (e.g., `Seat3`).
- **seat_no (physical chair)**: integer 1..N (clockwise order).
- **display_name (UI-only)**: arbitrary human-friendly string; never used for identity.
- **position (BTN/SB/BB/UTG… derived)**: computed per hand/street; never stored in actions, never used for identity.

### 2) Hand Model Requirements (read/write)
- `seats[].player_uid` is the authoritative identity. Mirror to legacy `player_id` for I/O as needed.
- `metadata.hole_cards` is keyed by `player_uid`.
- Actions use `actor_uid` (canonical). A temporary `actor_id` alias is allowed only for backward compatibility.
- Preflop forced wagers are explicit actions: `POST_ANTE`, `POST_BLIND` (`posting_meta.blind_type ∈ {SB, BB, Dead}`), `STRADDLE`, `POST_DEAD`.
- Global `order` across all actions is strictly increasing.
- Add `metadata.button_seat_no` (single source of truth for BTN); derive positions from it.

### 3) Converters (Legendary/GTO → Hand Model)
- Normalize all legacy names to `player_uid` using seat numbers; preserve `display_name`.
- Emit `POST_*` and `STRADDLE` explicitly, then convert betting actions.
- Guarantee monotone `to_amount` per actor, add `RETURN_UNCALLED` when a street ends by folds vs last aggressor.
- Validate invariants (see §6) and repair trivial issues or fail with precise errors.

### 4) FPSM + Decision Engine
- FPSM `Player.name == player_uid`. Maintain `uid↔index` maps; do not rely on display names.
- Review mode: before each step, sync `action_player_index` to the engine's next `actor_uid`.
- Street timing & animations depend on events: emit `action_executed`, `round_complete`, `state_change` deterministically.
- Heads-up rules are codified: BTN posts SB, BB acts last preflop; postflop BTN acts first.

### 5) UI (Reusable Poker Game Widget & subclasses)
- Render-only; no logic. Read `display_state` fields, including derived `position` and `display_name`.
- Hole cards shown in review mode or showdown via `metadata.hole_cards[player_uid]`.
- Never infer identity from strings displayed on screen.

### 6) Validation & Determinism Invariants
- `order` strictly increasing; FLOP/TURN/RIVER board sizes 3/4/5 with continuity.
- If `pots[]` present: `sum(shares) == amount`. If `final_stacks` present: chip conservation `sum(starting) == sum(final) + rake`.
- Preflop has at most one SB and BB; straddle chain labeled in order.
- Every action's `actor_uid` ∈ `{Seat1..SeatN}`; no display names in actions.

### 7) Backward Compatibility
- Accept legacy `player_id`/`actor_id`; normalize once at ingress to `player_uid/actor_uid` and store canonical values.
- For external write-outs, mirror canonical fields to legacy fields if required.

### 8) Prohibited / Anti-patterns
- Using display names as identity in engine/FPSM/serialization.
- Storing positions in actions or using positions for identity.
- Implicit blinds/antes/straddles; all must be explicit actions.
- UI-side timing or business logic.

### 9) Enforcement
- AI assistants and CI must:
  - Reject PRs that introduce identity drift (e.g., actor names not equal to `Seat*`).
  - Fail builds when invariants in §6 are violated.
  - Ensure converters output canonicalized Hand model per §2.
  - Verify FPSM/engine synchronize next actor per review mode requirements.

### 10) Future-proofing
- Support `metadata.run_count > 1` by allowing `streets[STREET].board_runs` while keeping `board` for single-run hands.
- Keep `seat_uid` optional for debug-rich builds where seat numbering semantics differ across sources.

### 11) DUPLICATE CODE PREVENTION — CRITICAL ENFORCEMENT
**MANDATORY: All AI models and developers MUST follow these rules to prevent debugging nightmares.**

#### 11.1 Pre-Development Duplicate Audit
- **BEFORE writing any new code**, run `python3 py_duplicate_def_auditor.py --root .` to ensure 0 duplicates
- **NEVER proceed** if duplicates are found - fix them first
- **REJECT any PR** that introduces new duplicates

#### 11.2 Strict Naming Conventions
- **Class names**: Must be unique across the entire project
- **Method names**: Must be unique within each class (inheritance overrides are legitimate)
- **Function names**: Must be unique at module level (local functions are legitimate)
- **Variable names**: Must be unique within their scope

#### 11.3 Inheritance and Composition Rules
- **Prefer composition over inheritance** to reduce method name conflicts
- **When inheritance is necessary**: Use method overriding, not method redefinition
- **Nested classes**: Must have unique names from outer classes
- **Mixins**: Must not conflict with existing method names

#### 11.4 Code Organization Requirements
- **Single Responsibility**: Each class/function should have one clear purpose
- **DRY Principle**: Never duplicate logic - extract to shared utilities
- **Module Separation**: Related functionality should be in separate modules
- **Interface Contracts**: Use abstract base classes to define clear contracts

#### 11.5 AI Model Requirements
- **ALWAYS check existing codebase** before proposing new implementations
- **NEVER suggest duplicate class/method names** without checking conflicts
- **ALWAYS propose refactoring** if similar functionality exists elsewhere
- **ALWAYS run duplicate audit** after any code changes

#### 11.6 Debugging Prevention
- **Duplicate code creates debugging nightmares** because:
  - Changes in one place don't propagate to duplicates
  - Bug fixes become inconsistent across duplicates
  - Code reviews miss duplicate-related issues
  - Testing becomes unreliable with duplicate logic

#### 11.7 Enforcement Actions
- **Immediate rejection** of any code that introduces duplicates
- **Mandatory refactoring** before code review approval
- **Duplicate audit integration** in CI/CD pipeline
- **Developer education** on duplicate prevention techniques

#### 11.8 Legacy Duplicate Cleanup
- **Existing duplicates** must be identified and documented
- **Refactoring plan** required for any duplicate removal
- **No new features** until critical duplicates are resolved
- **Regular audits** to prevent duplicate accumulation

**VIOLATION CONSEQUENCES**: Code with duplicates will be rejected, and developers must complete duplicate prevention training before continuing.

**📖 DETAILED RULES**: See [DUPLICATE_PREVENTION_RULES.md](DUPLICATE_PREVENTION_RULES.md) for comprehensive guidelines.


