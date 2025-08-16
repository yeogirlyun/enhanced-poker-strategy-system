# Hands Review Patch
- Adds a real `core/` package so `from core.*` imports resolve.
- Rewrites relative imports to absolute `core.*`.
- Enhances tester to accept `--data` and `DATA_FILE`.
- Includes stubs for optional deps.
Run:
  PYTHONPATH=. python HANDS_REVIEW_SOURCE_CODE/hands_review_validation_tester.py --data data/legendary_hands.json --limit 100
