# GTO Poker Engine Tester

A comprehensive testing framework for Game Theory Optimal (GTO) poker decision engines.

## Project Structure

```
backend/gto/
├── __init__.py
├── unified_types.py           # Common data structures and protocols
├── industry_gto_engine.py     # Sample GTO engine implementation
├── gto_decision_engine_adapter.py  # Adapter for PPSM integration
├── gto_hands_generator.py     # Hand generation and batch processing
└── test_gto_integration.py    # Testing harness and benchmarks
```

## Features

- **Unified Types**: Standardized data structures for game state representation
- **GTO Engine**: Industry-standard poker decision engine with preflop/postflop strategies
- **PPSM Integration**: Adapter to bridge with existing Pure Poker State Machine
- **Hand Generation**: Automated generation of realistic poker hands using GTO decisions
- **Testing Framework**: Comprehensive integration tests and performance benchmarks

## Usage

### Generate Test Hands

```bash
cd poker_gto_project
python -m backend.gto.test_gto_integration --generate --players 2-6 --hands-per-count 10
```

### Run Performance Benchmarks

```bash
python -m backend.gto.test_gto_integration --benchmark --players 6 --iterations 50
```

### Options

- `--generate`: Generate and test GTO hands
- `--players`: Player counts to test (e.g., '6' or '2-9')
- `--hands-per-count`: Number of hands to generate per player count
- `--benchmark`: Run performance benchmarks  
- `--iterations`: Number of iterations for benchmarks

## Integration

The GTO engine can be integrated with existing poker systems through the `GTODecisionEngineAdapter`, which provides a bridge between the unified GTO types and your existing poker state machine.

## Output

Generated hands are saved as JSON files with naming pattern:
- `gto_hands_2_players.json`
- `gto_hands_3_players.json`
- etc.

Each hand contains comprehensive game state information including final pot, board cards, and player actions.
