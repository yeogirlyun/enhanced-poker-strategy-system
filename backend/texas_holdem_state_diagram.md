# Texas Hold'em Poker Action State Diagram Research

## Standard Texas Hold'em Action Flow

### 1. Hand Initialization State
```
START_HAND
├── Deal hole cards (2 per player)
├── Post blinds (SB, BB)
├── Set action to UTG (first to act after BB)
└── TRANSITION: PREFLOP_BETTING
```

### 2. Preflop Betting Round
```
PREFLOP_BETTING
├── Current bet = BB amount
├── Action order: UTG → MP → CO → BTN → SB → BB
├── Actions: FOLD, CALL, RAISE
├── Round complete when: All active players have equal bets
└── TRANSITION: DEAL_FLOP (if >1 player active)
```

### 3. Flop Betting Round
```
DEAL_FLOP
├── Deal 3 community cards
├── Reset current bet = 0
├── Set action to first active player after BTN
├── TRANSITION: FLOP_BETTING
```

```
FLOP_BETTING
├── Current bet = 0 (Pot First Action)
├── Action order: First active after BTN → clockwise
├── Actions: CHECK, BET, FOLD, CALL, RAISE
├── Round complete when: All active players have equal bets
└── TRANSITION: DEAL_TURN (if >1 player active)
```

### 4. Turn Betting Round
```
DEAL_TURN
├── Deal 1 community card (4th card)
├── Reset current bet = 0
├── Set action to first active player after BTN
├── TRANSITION: TURN_BETTING
```

```
TURN_BETTING
├── Current bet = 0 (Pot First Action)
├── Action order: First active after BTN → clockwise
├── Actions: CHECK, BET, FOLD, CALL, RAISE
├── Round complete when: All active players have equal bets
└── TRANSITION: DEAL_RIVER (if >1 player active)
```

### 5. River Betting Round
```
DEAL_RIVER
├── Deal 1 community card (5th card)
├── Reset current bet = 0
├── Set action to first active player after BTN
├── TRANSITION: RIVER_BETTING
```

```
RIVER_BETTING
├── Current bet = 0 (Pot First Action)
├── Action order: First active after BTN → clockwise
├── Actions: CHECK, BET, FOLD, CALL, RAISE
├── Round complete when: All active players have equal bets
└── TRANSITION: SHOWDOWN (if >1 player active)
```

### 6. Showdown State
```
SHOWDOWN
├── Reveal all active players' hole cards
├── Determine winner(s)
├── Award pot to winner(s)
└── TRANSITION: END_HAND
```

## State Machine Implementation Requirements

### State Enum
```python
class PokerState(Enum):
    START_HAND = "start_hand"
    PREFLOP_BETTING = "preflop_betting"
    DEAL_FLOP = "deal_flop"
    FLOP_BETTING = "flop_betting"
    DEAL_TURN = "deal_turn"
    TURN_BETTING = "turn_betting"
    DEAL_RIVER = "deal_river"
    RIVER_BETTING = "river_betting"
    SHOWDOWN = "showdown"
    END_HAND = "end_hand"
```

### Action Types
```python
class ActionType(Enum):
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"
```

### State Transitions
```python
STATE_TRANSITIONS = {
    PokerState.START_HAND: [PokerState.PREFLOP_BETTING],
    PokerState.PREFLOP_BETTING: [PokerState.DEAL_FLOP, PokerState.END_HAND],
    PokerState.DEAL_FLOP: [PokerState.FLOP_BETTING],
    PokerState.FLOP_BETTING: [PokerState.DEAL_TURN, PokerState.END_HAND],
    PokerState.DEAL_TURN: [PokerState.TURN_BETTING],
    PokerState.TURN_BETTING: [PokerState.DEAL_RIVER, PokerState.END_HAND],
    PokerState.DEAL_RIVER: [PokerState.RIVER_BETTING],
    PokerState.RIVER_BETTING: [PokerState.SHOWDOWN, PokerState.END_HAND],
    PokerState.SHOWDOWN: [PokerState.END_HAND],
    PokerState.END_HAND: [PokerState.START_HAND],
}
```

## Key Rules for Each State

### Preflop Rules
- **Starting bet**: BB amount (e.g., $1)
- **Action order**: UTG → MP → CO → BTN → SB → BB
- **Valid actions**: FOLD, CALL, RAISE
- **Round completion**: All active players have equal bets

### Postflop Rules (Flop, Turn, River)
- **Starting bet**: $0 (Pot First Action)
- **Action order**: First active player after BTN → clockwise
- **Valid actions**: CHECK, BET, FOLD, CALL, RAISE
- **Round completion**: All active players have equal bets

### All-In Situations
- **Definition**: Player bets entire stack
- **Action**: Other players can only FOLD or CALL (no RAISE)
- **Round completion**: When all active players have acted

### All-Fold Situations
- **Definition**: All players fold except one
- **Action**: Last remaining player wins pot immediately
- **Transition**: END_HAND (no showdown needed)

## Implementation Guidelines

### 1. State Machine Class
```python
class PokerStateMachine:
    def __init__(self):
        self.current_state = PokerState.START_HAND
        self.game_state = GameState()
        self.action_player_index = 0
        self.current_bet = 0
        self.pot = 0
    
    def transition_to(self, new_state):
        # Validate transition
        if new_state in STATE_TRANSITIONS[self.current_state]:
            self.current_state = new_state
            self.handle_state_entry()
        else:
            raise InvalidStateTransitionError()
    
    def handle_state_entry(self):
        # Handle specific logic for each state
        pass
```

### 2. Action Validation
```python
def is_valid_action(self, player, action, amount):
    if self.current_state in [PokerState.PREFLOP_BETTING]:
        return action in [ActionType.FOLD, ActionType.CALL, ActionType.RAISE]
    elif self.current_state in [PokerState.FLOP_BETTING, PokerState.TURN_BETTING, PokerState.RIVER_BETTING]:
        if self.current_bet == 0:
            return action in [ActionType.CHECK, ActionType.BET]
        else:
            return action in [ActionType.FOLD, ActionType.CALL, ActionType.RAISE]
    return False
```

### 3. Round Completion Check
```python
def is_round_complete(self):
    active_players = [p for p in self.game_state.players if p.is_active]
    if len(active_players) <= 1:
        return True
    
    target_bet = self.current_bet
    for player in active_players:
        if player.current_bet != target_bet:
            return False
    return True
```

### 4. Next Action Player
```python
def get_next_action_player(self):
    if self.current_state == PokerState.PREFLOP_BETTING:
        # UTG starts after BB
        return (self.bb_position + 1) % len(self.game_state.players)
    else:
        # First active player after BTN
        start_pos = (self.btn_position + 1) % len(self.game_state.players)
        while not self.game_state.players[start_pos].is_active:
            start_pos = (start_pos + 1) % len(self.game_state.players)
        return start_pos
```

## Benefits of State Machine Approach

### 1. Predictable Flow
- Clear state transitions
- No ad-hoc logic
- Easy to debug and test

### 2. Rule Compliance
- Enforces proper poker rules
- Prevents invalid actions
- Maintains game integrity

### 3. Extensibility
- Easy to add new states
- Simple to modify rules
- Clean separation of concerns

### 4. Debugging
- Clear state logging
- Easy to track issues
- Predictable behavior

## Implementation Priority

1. **Replace current ad-hoc logic** with state machine
2. **Implement proper state transitions**
3. **Add action validation**
4. **Fix round completion logic**
5. **Add comprehensive logging**
6. **Test all scenarios**

This approach will eliminate the current issues and provide a robust, maintainable poker game engine. 