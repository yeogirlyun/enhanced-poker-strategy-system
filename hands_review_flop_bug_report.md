Hands Review – Flop Failure Bug Report

Summary
- Symptom: During Hands Review validation, preflop actions succeed but the first flop BET does not advance pot/current_bet. The subsequent CALL becomes invalid (call_amount=0), causing replay divergence from original hand(s).
- Scope: Affects review mode using composition-based `HandsReviewBotSession` with deterministic deck seeding. FPSM must remain unchanged per constraint.

Reproduction
1) From backend directory:
   - Run: `python3 tools/hands_review_validation_tester.py`
2) Observe the first hand:
   - Preflop: RAISE (seat1) and CALL (seat2) succeed
   - Flop: BET (seat1) logs as successful, but FPSM `current_bet` remains 0 and `pot` unchanged; next CALL (seat2) fails.

Observed Logs (abridged)
```
... Preflop OK ...
🔍 HAND_MODEL_ENGINE: Action 3/8
   Action player: seat1
   Action: BET, Amount: 60
🔥 BOT_ACTION_DEBUG: Executing action:
   Player: seat2
   Action: ActionType.BET
   Amount: $60.0
   ...
✅ BOT_ACTION_DEBUG: Action executed successfully
   FPSM current_bet: $0.0
   FPSM pot: $15.0
... next action ...
❌ Invalid action: seat2 cannot CALL $60.00. Valid: { ... 'call_amount': 0.0, ... }
```

Impact
- 100% of reviewed hands fail due to first flop action not altering betting state, making all subsequent call/raise validation incorrect.

Context and Recent Changes
- Composition architecture verified by `test_composition_architecture.py` (PASS)
- Deterministic deck seeding added in `HandsReviewBotSession.start_hand` to account for FPSM skipping deck setup in review mode
- First-to-act logic fixed for preflop vs. postflop
- `HandModelDecisionEngine` now emits `actor_index` to align the acting seat with recorded actions
- Validator updated to derive `dealer_position` and initialize blinds (pot/current_bet) correctly from preflop only

Diagnosis (Root Cause Hypothesis)
- The flop BET path in FPSM does not update `game_state.current_bet`/`pot` under the current review-mode setup. Given the constraint not to modify FPSM, the observed state reset/missed update makes the next CALL compute `call_amount=0.0`.
- Secondary signal: After BET, round-completion or bet-reset logic may be triggering early in the FPSM, or BET path is a no-op for state in this configuration.

Constraints
- Do not modify `FlexiblePokerStateMachine` (FPSM)
- Maintain composition architecture; review session must work deterministically

Proposed Fix (Non-invasive Shim)
- In `BotSessionStateMachine.execute_next_bot_action` (review session only), mirror chip deltas for BET/CALL/RAISE on the FPSM `game_state` before delegating the action to FPSM:
  - BET x: set acting player's `current_bet += x`; set `game_state.current_bet = max(current_bet)`; increase `pot` accordingly
  - CALL x: bring player's `current_bet` up to `game_state.current_bet`; add delta to `pot`
  - RAISE to T: compute delta vs current, update `current_bet` to T and `pot`
- This preserves FPSM code while ensuring subsequent validations (e.g., CALL) see correct `call_amount`.

Next Validation Steps
1) Implement review-only state shim (as above) in `BotSessionStateMachine` prior to calling `fpsm.execute_action(...)`
2) Re-run `python3 tools/hands_review_validation_tester.py`
3) If failures persist:
   - Inspect `_is_round_complete` vs. `players_acted_this_round` behavior around flop transitions
   - Verify postflop first-to-act consistency (already corrected via dealer-derived ordering)

Files Included in Bundle
- `backend/core/bot_session_state_machine.py` (composition session, deterministic deck seeding)
- `backend/core/hand_model_decision_engine.py` (strict actor mapping; emits `actor_index`)
- `backend/core/flexible_poker_state_machine.py` (reference)
- `backend/core/hand_model.py` (Hand, Street structures)
- `backend/providers/deck_provider.py`, `preloaded_deck.py`, `random_deck.py`
- `backend/tools/hands_review_validation_tester.py`
- `backend/tools/hands_review_validation_results.json` (latest run)

Environment
- OS: macOS 14 (Darwin 24.6.0)
- Python: 3.13.x
- Pygame present (for sound stubs)

Owner Decision Needed
- Approve review-only state shim in `BotSessionStateMachine` to proceed without altering FPSM


