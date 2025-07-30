# Python Poker Library Research

## Top Python Poker Libraries

### 1. **PyPokerEngine** ⭐⭐⭐⭐⭐
- **GitHub**: https://github.com/ishikota/PyPokerEngine
- **Features**: 
  - Complete Texas Hold'em implementation
  - Hand evaluation, game state management
  - AI player support
  - Tournament and cash game modes
  - Well-documented API
- **Pros**: Most comprehensive, actively maintained
- **Cons**: Complex setup, requires specific environment

### 2. **PokerKit** ⭐⭐⭐⭐
- **GitHub**: https://github.com/uoftcprg/pokerkit
- **Features**:
  - Modern Python poker library
  - Hand evaluation, game rules
  - Multiple poker variants
  - Clean API design
- **Pros**: Modern, well-structured, good documentation
- **Cons**: Newer library, smaller community

### 3. **treys** ⭐⭐⭐⭐
- **GitHub**: https://github.com/worldveil/deuces
- **Features**:
  - Fast hand evaluation
  - C++ backend for performance
  - Simple API
- **Pros**: Very fast, battle-tested
- **Cons**: Limited to hand evaluation, no game engine

### 4. **PyPoker** ⭐⭐⭐
- **PyPI**: https://pypi.org/project/pypoker/
- **Features**:
  - Basic poker game implementation
  - Hand evaluation
  - Simple game flow
- **Pros**: Easy to use, lightweight
- **Cons**: Limited features, basic implementation

### 5. **poker** ⭐⭐⭐
- **PyPI**: https://pypi.org/project/poker/
- **Features**:
  - Hand evaluation and comparison
  - Card representation
- **Pros**: Simple, focused on hand evaluation
- **Cons**: No game engine, just evaluation

## Recommended Integration Approach

### **Option 1: PyPokerEngine (Recommended)**
```python
# Example integration
from pypokerengine.api.game import setup_config, start_poker
from pypokerengine.players import BasePokerPlayer

class StrategyBasedPlayer(BasePokerPlayer):
    def declare_action(self, valid_actions, hole_card, round_state):
        # Use our strategy system here
        action = self.get_strategy_action(hole_card, round_state)
        return action
```

### **Option 2: PokerKit (Modern Alternative)**
```python
# Example integration
from pokerkit import Game, Player, Action

class StrategyGame:
    def __init__(self, strategy_data):
        self.strategy = strategy_data
        self.game = Game()
    
    def play_hand(self):
        # Integrate with our strategy system
        pass
```

### **Option 3: Hybrid Approach**
- Use **treys** for fast hand evaluation
- Build custom game engine with our strategy system
- Integrate with existing GUI

## Integration Strategy

### **Phase 1: Library Selection**
1. Test PyPokerEngine and PokerKit
2. Evaluate performance and compatibility
3. Choose best fit for our needs

### **Phase 2: Strategy Integration**
1. Create strategy adapter layer
2. Map our strategy data to library actions
3. Implement deviation tracking

### **Phase 3: GUI Integration**
1. Replace custom poker engine
2. Maintain visual interface
3. Add advanced features

## Testing Plan

### **Library Testing**
```bash
# Test PyPokerEngine
pip install PyPokerEngine
python -c "from pypokerengine.api.game import setup_config; print('PyPokerEngine works')"

# Test PokerKit
pip install pokerkit
python -c "from pokerkit import Game; print('PokerKit works')"

# Test treys
pip install treys
python -c "from treys import Card, Evaluator; print('treys works')"
```

### **Performance Comparison**
- Hand evaluation speed
- Memory usage
- Game state management
- API complexity

## Next Steps

1. **Install and test** PyPokerEngine and PokerKit
2. **Create integration prototypes**
3. **Evaluate performance** and ease of integration
4. **Choose best library** for our needs
5. **Implement strategy adapter**
6. **Replace custom engine** with library
7. **Maintain visual interface**

## Benefits of Using Existing Libraries

### **Advantages:**
- **Battle-tested code**: Proven implementations
- **Performance**: Optimized algorithms
- **Features**: Advanced poker features
- **Maintenance**: Community support
- **Standards**: Industry-standard implementations

### **Our Focus:**
- **Strategy integration**: Map our strategies to library actions
- **GUI development**: Visual interface and feedback
- **Learning features**: Deviation tracking and analysis
- **Custom features**: Strategy optimization and practice modes 