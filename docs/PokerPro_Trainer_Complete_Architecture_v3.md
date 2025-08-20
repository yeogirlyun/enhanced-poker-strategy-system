# PokerPro Trainer - Complete Architecture Reference v3

**Status**: Production Ready  
**Last Updated**: January 2024  
**Purpose**: Comprehensive reference for complete codebase reconstruction if needed  

---

## 🏗️ **SYSTEM OVERVIEW**

The PokerPro Trainer uses a **single-threaded, event-driven architecture** centered around four core pillars:

1. **PurePokerStateMachine (PPSM)** - Deterministic poker engine with hand replay capabilities
2. **GTO Engine Integration** - Game Theory Optimal decision making with deterministic hand generation
3. **Modern UI Architecture** - Component-based UI with clean separation of concerns  
4. **Session Management System** - Pluggable session types (GTO, Practice, Hands Review, Live)

### **Core Design Principles**

- **Single Source of Truth**: PPSM is the authoritative game state
- **Deterministic Behavior**: All game logic is reproducible and testable
- **Clean Separation**: UI renders state, never controls game logic
- **Event-Driven**: All interactions flow through well-defined interfaces
- **Pluggable Components**: DecisionEngines and Sessions are swappable

---

## 🧠 **GTO ENGINE INTEGRATION**

### **Architecture Overview**

The GTO (Game Theory Optimal) Engine Integration provides **deterministic, strategic poker decision making** with complete round trip integrity testing. The system creates a closed loop: HandModel → PPSM → GTO → HandModel → HandsReviewSession replay.

### **Core Components**

#### **1. IndustryGTOEngine**
```python
class IndustryGTOEngine(UnifiedDecisionEngineProtocol):
    """
    Strategic poker decision engine with:
    - Preflop/postflop strategy implementation
    - Position-based decision making
    - Stack depth and aggression factor configuration
    - Deterministic action selection
    """
```

#### **2. GTODecisionEngineAdapter**
```python
class GTODecisionEngineAdapter(DecisionEngineProtocol):
    """
    Bridge between GTO engine and PPSM:
    - Converts PPSM GameState to GTO StandardGameState
    - Handles action_player=None edge cases gracefully
    - Provides legal actions validation
    - Maintains interface compatibility
    """
```

#### **3. GTOHandsGenerator**
```python
class GTOHandsGenerator:
    """
    Automated hand generation using GTO decisions:
    - Multi-player support (2-9 players)
    - Deterministic hand outcomes
    - JSON export for persistence
    - Performance benchmarking
    """
```

### **Data Flow Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Hand Model   │───▶│      PPSM       │───▶│   GTO Engine    │
│   (JSON DB)    │    │  (Game Logic)   │    │ (Decisions)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                       │                       │
         │                       ▼                       ▼
         │              ┌─────────────────┐    ┌─────────────────┐
         │              │ GTO Hands       │    │ Round Trip      │
         │              │ Generator       │    │ Integrity       │
         │              └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Hands Review    │    │ JSON Export     │    │ 100% Test       │
│ Session         │    │ (data/)         │    │ Success Rate    │
│ (Deterministic) │    └─────────────────┘    └─────────────────┘
└─────────────────┘
```

### **Key Features**

#### **1. Deterministic Hand Generation**
- **Consistent Outcomes**: Same input always produces same result
- **Multi-Player Support**: 2-9 player configurations
- **Strategic Play**: Realistic poker scenarios using GTO principles
- **Performance**: Sub-second hand generation

#### **2. Round Trip Integrity**
- **Complete Pipeline**: HandModel → PPSM → GTO → HandModel → HandsReviewSession
- **Data Validation**: Pot amounts, player counts, action sequences
- **Deterministic Replay**: HandsReviewSession with deterministic deck
- **100% Success Rate**: All integration tests passing

#### **3. Hands Review Integration**
- **Deterministic Deck**: Card sequences from GTO hand data
- **HandModelDecisionEngine**: Replays exact GTO-generated actions
- **Session Management**: Proper initialization and cleanup
- **Performance Monitoring**: Action execution timing and validation

### **Data Storage Architecture**

```
data/
├── gto_hands_2_players.json      # 2-player GTO hands
├── gto_hands_4_players.json      # 4-player GTO hands  
├── gto_hands_6_players.json      # 6-player GTO hands
├── gto_hands_8_players.json      # 8-player GTO hands
└── gto_hands_9_players.json      # 9-player GTO hands

bug_reports/                       # Bug analysis and reports
├── GTO_INTEGRATION_BUG_REPORT_COMPLETE.md
└── GTO_BUG_REPORT_SUMMARY.md

req_requests/                      # Requirements and specifications
└── GTO_ENGINE_INTEGRATION_COMPLETE_REQUIREMENT.md
```

---

## 🎮 **PURE POKER STATE MACHINE (PPSM)**

### **Architecture Overview**

The PPSM is a **deterministic, single-threaded poker engine** that serves as the single source of truth for all poker game state and logic.

```python
class PurePokerStateMachine:
    """
    Core poker engine with:
    - Deterministic game state management
    - Hand replay capabilities via DecisionEngineProtocol
    - Clean to-amount semantics for all actions
    - Comprehensive validation and error handling
    """
```

### **Key Features**

#### **1. Deterministic Deck System**
```python
# Uses predetermined card sequences for reproducible hands
deck = ["Kh", "Kd", "Ad", "2c", "4h", "4s", "Qh", "2h", "2d"]
```

#### **2. To-Amount Semantics (Authoritative)**
- **BET**: `to_amount` = total amount to reach (not delta)
- **RAISE**: `to_amount` = total amount to raise to (not additional)
- **CALL/CHECK**: `to_amount` ignored (engine computes)

#### **3. DecisionEngineProtocol Integration**
```python
class DecisionEngineProtocol:
    def get_decision(self, player_name: str, game_state) -> tuple[ActionType, Optional[float]]:
        """Return (ActionType, to_amount) for player to act"""
        pass
    
    def has_decision_for_player(self, player_name: str) -> bool:
        """Check if engine has decision for player"""
        pass
```

#### **4. Hand Model Replay**
```python
def replay_hand_model(self, hand_model) -> dict:
    """
    Replay a Hand object using HandModelDecisionEngineAdapter
    Returns comprehensive results with pot validation
    """
```

### **State Management**

#### **Game States**
- `START_HAND` → `PREFLOP_BETTING` → `FLOP_BETTING` → `TURN_BETTING` → `RIVER_BETTING` → `SHOWDOWN`

#### **Player State Tracking**
- `current_bet`: Amount player has wagered this street
- `stack`: Remaining chips
- `is_active`: Can still act in hand
- `has_folded`: Eliminated from hand

#### **Round State Management**
- `current_bet`: Current bet to match
- `last_full_raise_size`: For minimum raise validation  
- `need_action_from`: Set of player indices who need to act
- `reopen_available`: Whether betting can be reopened

### **Validation System**

#### **Action Validation**
```python
def _is_valid_action(self, player: Player, action_type: ActionType, to_amount: Optional[float]) -> bool:
    """
    Comprehensive validation including:
    - Player can act (not folded, has chips)
    - Action is legal for current street
    - Bet amounts are valid (within limits, proper increments)
    - Raise amounts meet minimum requirements
    """
```

#### **Pot Validation**
```python
def _validate_pot_integrity(self) -> bool:
    """
    Ensures total chips in play equals:
    - All player stacks + current bets + pot
    - No chips created or destroyed
    """
```

---

## 🎨 **UI ARCHITECTURE**

### **Component Hierarchy**

```
AppShell
├── ServiceContainer
│   ├── ThemeManager
│   ├── SoundManager
│   ├── EventBus
│   └── Store
├── TabContainer
│   ├── HandsReviewTab
│   ├── PracticeSessionTab
│   └── GTOSessionTab
└── PokerTableRenderer (Unified Poker Table — Pure Renderer)
    ├── CanvasManager
    ├── LayerManager (felt → seats → stacks → community → bets → pot → action → status → overlay)
    ├── RendererPipeline
    └── Table Components
        ├── TableFelt
        ├── Seats
        ├── Community
        ├── PotDisplay
        ├── BetDisplay
        ├── DealerButton
        └── ActionIndicator
```

### **Design Principles**

#### **1. Pure Rendering Components**
- UI components are **stateless renderers**
- All business logic resides in PPSM or services
- Components subscribe to state via selectors
- No direct state mutation from UI

#### **2. State-Driven Architecture**
- Single source of truth: Store
- UI renders based on state changes
- Actions flow: UI → Store → Reducer → State → UI
- No imperative UI updates

#### **3. Event-Driven Integration**
- EventBus for cross-service communication
- Services handle side effects (sounds, animations)
- UI dispatches actions, never calls services directly
- Clean separation of concerns

#### **4. Reusable Poker Table Renderer**
- `backend/ui/renderers/poker_table_renderer.py` is a **pure** renderer reused by every session.
- Input is a single `PokerTableState` (immutable dataclass).
- Emits renderer intents (e.g., `REQUEST_ANIMATION`) that the shell adapts to `EffectBus`.
- No business logic, no session awareness, no PPSM calls.

### **State / Effects Flow (MVU)**

```
UI Intent → SessionManager.handle_* → PPSM → Store.replace(table_state, effects)
      ↓                                    ↓
PokerTableRenderer.render(state)     EffectBus.run(effects) → Director gating
```

### **Theme System Integration**

- **Design System v2**: Token-based color system
- **Hot-swappable themes**: Runtime theme switching
- **Responsive design**: Dynamic sizing based on container
- **Accessibility**: WCAG 2.1 AA compliance

---

## 🎯 **SESSION IMPLEMENTATION ARCHITECTURE**

### **Hands Review Session**

#### **Purpose**
- Load and replay GTO/Legendary hands
- Step-by-step action progression
- Auto-play with configurable timing
- Theme switching and responsive layout

#### **Core Components**
- **Enhanced RPGW**: Unified poker table display
- **Hand Loader**: JSON parsing and validation
- **Action Controller**: Step-by-step progression
- **Theme Manager**: Dynamic theme switching

#### **Implementation Flow**
```python
# 1. Hand Loading
hand_data = load_hand_from_json(file_path)
display_state = create_display_state(hand_data)

# 2. Action Execution
action = get_next_action(hand_data, current_index)
store.dispatch({"type": "ENHANCED_RPGW_EXECUTE_ACTION", "action": action})

# 3. State Update
new_state = reducer(current_state, action)
renderer_pipeline.render_once(new_state)

# 4. Side Effects
event_bus.publish("enhanced_rpgw:feedback", {"type": "sound", "action": action})
```

### **Practice Session**

#### **Purpose**
- Interactive poker practice with AI opponents
- Configurable starting conditions
- Real-time decision making
- Performance tracking and analysis

#### **Core Components**
- **PPSM Integration**: Live game state management
- **AI Decision Engine**: Opponent behavior simulation
- **Session Controller**: Game flow coordination
- **Progress Tracker**: Performance metrics

#### **Implementation Flow**
```python
# 1. Session Initialization
ppsm = PurePokerStateMachine()
session_controller = PracticeSessionController(ppsm, event_bus)

# 2. Game Loop
while session_active:
    current_player = ppsm.get_current_player()
    if current_player.is_ai:
        decision = ai_engine.get_decision(current_player, ppsm.game_state)
        ppsm.execute_action(decision)
    else:
        # Wait for human input via UI
        pass

# 3. State Synchronization
display_state = ppsm_to_display_state(ppsm.game_state)
store.dispatch({"type": "UPDATE_PRACTICE_SESSION", "state": display_state})
```

### **GTO Session**

#### **Purpose**
- Live GTO strategy implementation
- Real-time hand analysis
- Decision tree visualization
- Performance benchmarking

#### **Core Components**
- **GTO Engine**: Strategy calculation and validation
- **Hand Analyzer**: Real-time equity calculations
- **Decision Tree**: Visual strategy representation
- **Benchmark System**: Performance metrics

#### **Implementation Flow**
```python
# 1. Strategy Loading
gto_strategy = load_gto_strategy(strategy_file)
gto_engine = GTOEngine(gto_strategy)

# 2. Live Analysis
current_hand = ppsm.get_current_hand_state()
gto_decision = gto_engine.analyze_hand(current_hand)
equity = gto_engine.calculate_equity(current_hand)

# 3. Decision Support
store.dispatch({
    "type": "UPDATE_GTO_ANALYSIS",
    "decision": gto_decision,
    "equity": equity,
    "confidence": gto_engine.get_confidence()
})
```

---

## 🔧 **ENHANCED RPGW ARCHITECTURE**

### **Component Integration**

The Enhanced RPGW serves as the unified poker table component across all session types, providing consistent rendering, theming, and interaction patterns.

#### **Core Architecture**
```python
class EnhancedRPGW:
    def __init__(self, parent_frame, theme_manager):
        self.canvas_manager = CanvasManager(parent_frame)
        self.layer_manager = LayerManager()
        self.renderer_pipeline = RendererPipeline()
        self.table_components = self._setup_table_components()
    
    def _setup_table_components(self):
        return {
            'table': TableFelt(),
            'seats': Seats(),
            'community': Community(),
            'pot': PotDisplay(),
            'bet': BetDisplay(),
            'dealer': DealerButton(),
            'action': ActionIndicator()
        }
```

#### **State-Driven Rendering**
```python
def render_table(self, display_state):
    """
    Renders poker table based on display state
    - No business logic, pure rendering
    - Responsive sizing and positioning
    - Theme-aware styling
    """
    self.renderer_pipeline.render_once(display_state)
```

#### **Display State Structure**
```python
display_state = {
    'table': {
        'width': 800,
        'height': 600,
        'theme': 'luxury_noir'
    },
    'pot': {
        'amount': 150,
        'position': (400, 300)
    },
    'seats': [
        {
            'player_uid': 'seat1',
            'name': 'Player1',
            'stack': 1000,
            'current_bet': 50,
            'cards': ['Ah', 'Kd'],
            'position': (300, 400),
            'acting': True
        }
    ],
    'board': ['2s', 'Jd', '6c'],
    'dealer': {'position': 0},
    'action': {'type': 'BET', 'player': 'seat1', 'amount': 50},
    'replay': {'current_step': 5, 'total_steps': 16}
}
```

---

## 🎭 **EVENT HANDLER INTEGRATION**

### **Store Reducer Pattern**

The UI architecture uses a Redux-like store with reducers to manage state updates and trigger side effects.

#### **Action Types**
```python
# Enhanced RPGW Actions
ENHANCED_RPGW_EXECUTE_ACTION = "ENHANCED_RPGW_EXECUTE_ACTION"
UPDATE_ENHANCED_RPGW_STATE = "UPDATE_ENHANCED_RPGW_STATE"
ENHANCED_RPGW_ANIMATION_EVENT = "ENHANCED_RPGW_ANIMATION_EVENT"

# Session Actions
UPDATE_PRACTICE_SESSION = "UPDATE_PRACTICE_SESSION"
UPDATE_GTO_ANALYSIS = "UPDATE_GTO_ANALYSIS"
```

#### **Reducer Implementation**
```python
def enhanced_rpgw_reducer(state, action):
    if action['type'] == 'ENHANCED_RPGW_EXECUTE_ACTION':
        # Triggers event for service layer
        new_state = {
            **state,
            'enhanced_rpgw': {
                **state.get('enhanced_rpgw', {}),
                'current_action': action['action'],
                'action_index': action['action_index'],
                'execution_status': 'pending'
            }
        }
        
        # Trigger service layer event
        if 'event_bus' in state:
            state['event_bus'].publish(
                "enhanced_rpgw:action_executed",
                {
                    "action": action['action'],
                    "action_index": action['action_index'],
                    "state": new_state
                }
            )
        return new_state
    
    elif action['type'] == 'UPDATE_ENHANCED_RPGW_STATE':
        # Updates state from PPSM execution results
        return {
            **state,
            'enhanced_rpgw': {
                **state.get('enhanced_rpgw', {}),
                **action['updates'],
                'execution_status': 'completed'
            }
        }
    
    elif action['type'] == 'ENHANCED_RPGW_ANIMATION_EVENT':
        # Handles animation events
        return {
            **state,
            'enhanced_rpgw': {
                **state.get('enhanced_rpgw', {}),
                'animation_event': action['animation_data']
            }
        }
    
    return state
```

### **Service Layer Event Handling**

Services subscribe to events and handle business logic, side effects, and PPSM interactions.

#### **Enhanced RPGW Controller**
```python
class EnhancedRPGWController:
    def __init__(self, event_bus, store, ppsm):
        self.event_bus = event_bus
        self.store = store
        self.ppsm = ppsm
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        self.event_bus.subscribe(
            "enhanced_rpgw:action_executed",
            self._handle_action_execution
        )
        self.event_bus.subscribe(
            "enhanced_rpgw:trigger_animation",
            self._handle_animation_trigger
        )
    
    def _handle_action_execution(self, event_data):
        # Execute action in PPSM (business logic)
        ppsm_result = self._execute_ppsm_action(event_data['action'])
        
        # Update store with PPSM results
        self.store.dispatch({
            "type": "UPDATE_ENHANCED_RPGW_STATE",
            "updates": {
                "ppsm_result": ppsm_result,
                "last_executed_action": event_data['action'],
                "execution_timestamp": time.time()
            }
        })
        
        # Trigger appropriate animations/sounds
        self._trigger_action_feedback(event_data['action'], ppsm_result)
    
    def _execute_ppsm_action(self, action):
        # Placeholder for actual PPSM execution logic
        # This method will contain the core game state updates
        pass  # (Detailed logic for DEAL_HOLE, DEAL_BOARD, POST_BLIND, BET, RAISE, CALL, CHECK, FOLD, END_HAND)
    
    def _trigger_action_feedback(self, action, ppsm_result):
        # Publishes feedback events (sounds, animations)
        feedback_mapping = {
            'DEAL_HOLE': 'card_deal',
            'DEAL_BOARD': 'card_deal',
            'POST_BLIND': 'chip_bet',
            'BET': 'player_bet',
            'RAISE': 'player_bet',
            'CALL': 'player_call',
            'CHECK': 'player_check',
            'FOLD': 'player_fold',
            'END_HAND': 'hand_end'
        }
        feedback_type = feedback_mapping.get(action['type'], 'default')
        self.event_bus.publish(
            "enhanced_rpgw:feedback",
            {
                "type": feedback_type,
                "action": action,
                "ppsm_result": ppsm_result
            }
        )
    
    def _handle_animation_trigger(self, event_data):
        # Publishes animation events to the store for UI to pick up
        if event_data.get('type') == 'player_highlight':
            self.event_bus.publish(
                "enhanced_rpgw:animation_event",
                {
                    "type": "SCHEDULE_HIGHLIGHT_CLEAR",
                    "delay_ms": 200,
                    "action": "clear_highlight"
                }
            )
```

---

## 🎨 **THEME SYSTEM INTEGRATION**

### **Design System v2**

The theme system provides a comprehensive, token-based approach to styling and theming across all UI components.

#### **Token Categories**
- **Colors**: Semantic color tokens (primary, secondary, accent)
- **Typography**: Font families, sizes, weights, and line heights
- **Spacing**: Consistent spacing scale (xs, sm, md, lg, xl)
- **Elevation**: Shadow and depth tokens
- **Border Radius**: Corner rounding values
- **Animation**: Duration and easing curves

#### **Integration Points**
```python
# Theme Manager
theme_manager = ThemeManager()
theme_manager.load_theme('luxury_noir')

# Component Usage
button.configure(
    bg=theme_manager.get_token('btn.primary.bg'),
    fg=theme_manager.get_token('btn.primary.fg'),
    font=theme_manager.get_token('font.button')
)
```

#### **Theme Change Handling**
```python
def on_theme_change(self, new_theme):
    # Update theme manager
    self.theme_manager.load_theme(new_theme)
    
    # Re-render Enhanced RPGW with new theme
    self._render_enhanced_rpgw_table()
    
    # Refresh widget sizing for new theme
    self._refresh_enhanced_rpgw_widget()
```

---

## 🚀 **PERFORMANCE AND SCALABILITY**

### **Rendering Optimization**

- **Lazy Rendering**: Only re-render components when state changes
- **Layer Management**: Efficient z-order management via LayerManager
- **Canvas Optimization**: Minimize canvas redraws and object creation
- **Memory Management**: Proper cleanup of canvas objects and event handlers

### **State Management Efficiency**

- **Immutable Updates**: Use spread operators for state updates
- **Selective Subscriptions**: Components only subscribe to relevant state slices
- **Event Debouncing**: Prevent excessive event processing during rapid state changes
- **Batch Updates**: Group multiple state changes into single render cycles

### **Resource Management**

- **Sound Caching**: Pre-load and cache sound files
- **Image Optimization**: Use appropriate image formats and sizes
- **Memory Monitoring**: Track memory usage and implement cleanup strategies
- **Performance Profiling**: Monitor render times and optimize bottlenecks

---

## 🧪 **TESTING AND QUALITY ASSURANCE**

### **Testing Strategy**

#### **Unit Testing**
- **Reducers**: Test state transformations and side effects
- **Selectors**: Validate state derivation logic
- **Services**: Test business logic and PPSM interactions
- **Components**: Test rendering and event handling

#### **Integration Testing**
- **Session Flows**: End-to-end session execution
- **Theme Switching**: Theme change behavior and consistency
- **Hand Replay**: Complete hand replay functionality
- **Performance**: Render performance and memory usage

#### **GTO Integration Testing**
- **Round Trip Integrity**: HandModel → PPSM → GTO → HandModel → HandsReviewSession
- **Deterministic Replay**: Verify identical outcomes using deterministic deck
- **Multi-Player Scenarios**: Test 2-9 player configurations
- **Performance Benchmarks**: Measure GTO decision making speed

#### **Accessibility Testing**
- **WCAG Compliance**: Automated and manual accessibility testing
- **Keyboard Navigation**: Full keyboard accessibility
- **Screen Reader**: Screen reader compatibility
- **Color Contrast**: Visual accessibility validation

### **Quality Metrics**

- **Code Coverage**: Minimum 80% test coverage
- **Performance Benchmarks**: Render time < 16ms per frame
- **Memory Usage**: Stable memory footprint during extended use
- **Error Handling**: Graceful degradation and user feedback
- **Accessibility Score**: WCAG 2.1 AA compliance

---

## 📚 **IMPLEMENTATION GUIDELINES**

### **Development Workflow**

1. **Feature Planning**: Define requirements and acceptance criteria
2. **Architecture Review**: Ensure compliance with architectural principles
3. **Implementation**: Follow established patterns and conventions
4. **Testing**: Comprehensive unit and integration testing
5. **Code Review**: Architecture and quality review
6. **Integration**: Merge and deploy with monitoring

### **Code Standards**

- **Python**: PEP 8 compliance with project-specific overrides
- **Type Hints**: Comprehensive type annotations
- **Documentation**: Clear docstrings and inline comments
- **Error Handling**: Graceful error handling with user feedback
- **Logging**: Structured logging for debugging and monitoring

### **Architecture Compliance**

- **Single Source of Truth**: All state managed through Store
- **Event-Driven**: UI actions flow through Store → Reducer → Services
- **Pure Components**: UI components are stateless renderers
- **Service Separation**: Business logic isolated in service layer
- **Theme Integration**: All styling via theme tokens

---

## 🔮 **FUTURE ROADMAP**

### **Phase 1: Core Implementation** ✅ **COMPLETED**
- ✅ Complete Enhanced RPGW integration
- ✅ Implement all three session types
- ✅ Establish testing framework
- ✅ Performance optimization
- ✅ **GTO Engine Integration with 100% test success rate**

### **Phase 2: Advanced Features**
- Advanced animation system
- Enhanced sound integration
- Performance analytics
- Accessibility improvements
- **GTO Strategy Expansion**: Advanced preflop/postflop strategies
- **Hand Database Management**: Large-scale GTO hand storage and retrieval

### **Phase 3: Scalability**
- Multi-table support
- Advanced session management
- Plugin architecture
- Cloud integration
- **GTO Cloud Services**: Distributed GTO computation and storage

---

*This document serves as the authoritative reference for the PokerPro Trainer architecture. All implementations must comply with these principles and patterns.*
