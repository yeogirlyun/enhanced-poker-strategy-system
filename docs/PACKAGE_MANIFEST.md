# Hand Model Project Package Manifest
Generated: 2025-08-15T01:16:48.912012
Package: hand_model_project_20250815_011648.zip

## Included Files (21)
- HAND_MODEL_PROJECT_REPORT.md
- backend/core/bot_session_state_machine.py
- backend/core/decision_engine_v2.py
- backend/core/flexible_poker_state_machine.py
- backend/core/gto_to_hand_converter.py
- backend/core/hand_model.py
- backend/core/hand_model_decision_engine.py
- backend/core/poker_types.py
- backend/ui/components/hands_review_panel_unified.py
- cycle_test_gto_log.txt
- cycle_test_hand.json
- cycle_test_hand_hand_model.json
- cycle_test_replay_log.txt
- example_hand.json
- gto_hand_for_verification.json
- gto_hand_for_verification_hand_model.json
- hands_review_replay_log.txt
- hands_review_replay_report.json
- test_gto_to_hands_review_complete_cycle.py
- test_hand_model.py
- test_hand_model_integration.py

## Package Contents

### Core Implementation
- hand_model.py: Complete poker hand data structure
- gto_to_hand_converter.py: Converts GTO format to Hand model  
- hand_model_decision_engine.py: Robust action replay engine

### Test Suite
- test_hand_model.py: Comprehensive fuzz testing (24 test scenarios)
- test_hand_model_integration.py: End-to-end integration testing

### Supporting Files
- bot_session_state_machine.py: Session management for hands review
- flexible_poker_state_machine.py: Core poker game logic
- decision_engine_v2.py: Abstract decision engine interface
- poker_types.py: Core data type definitions

### Data Examples
- cycle_test_hand*.json: GTO session data (original and converted)
- gto_hand_for_verification*.json: Verification test data
- example_hand.json: Hand model example output

### Documentation
- HAND_MODEL_PROJECT_REPORT.md: Complete project analysis and status

## Key Issues Identified
1. Player index/name mapping inconsistency between GTO converter and session
2. Integration test infinite loop due to player mismatch
3. Need to preserve original player identities from GTO data

## Next Steps
1. Fix player naming convention in gto_to_hand_converter.py
2. Debug original GTO data format for actual player names
3. Update HandModelDecisionEngine to handle name variations
4. Complete integration testing and production deployment
