# Tests Directory

This directory contains all test files for the Poker Strategy System.

## Test Files

### `test_enhanced_evaluator.py`
Tests the enhanced hand evaluation system with various poker hands.
- Tests hand ranking (Royal Flush, Four of a Kind, etc.)
- Tests preflop hand strength calculations
- Validates equity calculations

### `test_poker_table.py`
Tests the professional poker table GUI with animations and sound effects.
- Tests table rendering and player positioning
- Tests dealer button movement
- Tests player action animations
- Tests sound effects system

### `comprehensive_test_suite.py`
Comprehensive test suite for the poker state machine and game logic.
- Tests complete hand flow from preflop to showdown
- Tests bot decision making
- Tests strategy integration
- Tests position management

## Running Tests

### Run All Tests
```bash
cd tests
python3 run_all_tests.py
```

### Run Specific Test
```bash
cd tests
python3 run_all_tests.py test_enhanced_evaluator.py
```

### Run Individual Tests
```bash
cd tests
python3 test_enhanced_evaluator.py
python3 test_poker_table.py
python3 comprehensive_test_suite.py
```

## Test Structure

All test files are designed to be run independently and include:
- Comprehensive test cases
- Clear pass/fail reporting
- Detailed error messages
- Performance timing

## Test Coverage

The test suite covers:
- ✅ Hand evaluation and ranking
- ✅ Preflop hand strength calculations
- ✅ Poker table GUI functionality
- ✅ State machine logic
- ✅ Bot decision making
- ✅ Strategy integration
- ✅ Position management
- ✅ Sound effects system
- ✅ Animation system

## Adding New Tests

To add a new test file:

1. Create the test file in this directory
2. Add the file name to `run_all_tests.py` in the `test_files` list
3. Ensure the test file has proper import paths for backend modules
4. Include a main test function that can be called by the test runner

## Test Environment

Tests run with the backend directory added to the Python path, allowing direct imports of backend modules. This ensures tests can access all the necessary components of the poker strategy system. 