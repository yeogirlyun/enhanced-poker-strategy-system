# 🃏 **HANDS REVIEW TAB - COMPREHENSIVE MEGA DOCUMENT**

## 📋 **DOCUMENT OVERVIEW**

This mega document contains the complete specification, architecture, design, and implementation details for the Poker Hands Review Tab using MVU architecture.

**Purpose**: Complete development reference for industry-strength hands review functionality

**Architecture**: MVU (Model-View-Update) Pattern with infinite loop prevention

**Features**: Step-by-step hand playback, auto-play, professional animations, audio-visual feedback

**Integration**: Reusable across Practice, GTO, and Review session managers

**Generated**: 2025-08-20 11:59:45

**Source Directory**: `/Users/yeogirlyun/Python/Poker`

---

## REQUIREMENTS SPECIFICATION

### HANDS_REVIEW_TAB_REQUIREMENTS_v1.md

**Path**: `HANDS_REVIEW_TAB_REQUIREMENTS_v1.md`

```markdown
# 🃏 **HANDS REVIEW TAB - COMPREHENSIVE REQUIREMENTS DOCUMENT v1.0**

**Status**: Industry-Strength Requirements  
**Target Architecture**: MVU (Model-View-Update) Pattern  
**Last Updated**: January 2025  
**Purpose**: Complete specifications for poker hands review functionality  

---

## 📋 **EXECUTIVE SUMMARY**

The Hands Review Tab is a critical training component that allows poker players to analyze and review previously played hands through an interactive, visual poker table interface. The system must support step-by-step hand playback, automated replay, and comprehensive visual feedback using the MVU architecture for maximum reliability and maintainability.

---

## 🎯 **CORE OBJECTIVES**

### **Primary Goals**
- **Educational Excellence**: Provide clear, step-by-step hand analysis for skill improvement
- **Visual Clarity**: Industry-standard poker table rendering with professional animations
- **User Experience**: Intuitive controls for both manual and automated hand review
- **Architecture Compliance**: Full MVU pattern implementation preventing infinite loops
- **Performance**: Smooth 60 FPS animations with responsive UI interactions

### **Key Success Metrics**
- **Zero Infinite Loops**: Stable MVU implementation with proper immutable state
- **Sub-100ms Response**: Button clicks to visual feedback under 100ms
- **Universal Compatibility**: Works with Practice, GTO, and Review session types
- **Audio-Visual Sync**: Perfect synchronization between sounds and visual actions
- **Memory Efficiency**: Stable memory usage during extended review sessions

---

## 🏗️ **SYSTEM ARCHITECTURE**

### **MVU Architecture Implementation**

```
┌─────────────────────────────────────┐
│           VIEW LAYER                │
│  ┌─────────────────────────────┐   │
│  │    Hands Review Tab         │   │
│  │  - Hand selector dropdown   │   │
│  │  - Control buttons          │   │
│  │  - Progress slider          │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │    Poker Table Renderer     │   │
│  │  - Canvas-based rendering   │   │
│  │  - Player seats (2-9)       │   │
│  │  - Community cards          │   │
│  │  - Pot graphics             │   │
│  │  - Animation layers         │   │
│  └─────────────────────────────┘   │
└─────────────┬───────────────────────┘
              │ TableRendererProps (immutable)
┌─────────────▼───────────────────────┐
│           MODEL LAYER               │
│  ┌─────────────────────────────┐   │
│  │    Immutable Model State    │   │
│  │  - seats: Mapping[int, SeatState] │
│  │  - board: tuple[str, ...]   │   │
│  │  - pot: int                 │   │
│  │  - legal_actions: frozenset │   │
│  │  - review_cursor: int       │   │
│  │  - waiting_for: str         │   │
│  └─────────────────────────────┘   │
└─────────────┬───────────────────────┘
              │ Commands (effects)
┌─────────────▼───────────────────────┐
│         EFFECTS LAYER               │
│  - Audio: PlaySound, Speak         │
│  - Visual: Animate, UpdateCanvas   │
│  - Data: LoadHand, SaveState       │
│  - Timing: ScheduleTimer           │
└─────────────────────────────────────┘
```

### **Session Manager Integration**

```python
# Reusable across session types
class UniversalPokerTableRenderer:
    """Reusable poker table for all session types"""
    
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager  # Practice/GTO/Review
        
    def render(self, props: TableRendererProps):
        # Universal rendering logic
        pass

# Session-specific drivers
ReviewSessionManager   → ReviewDriver   → MVU Store
PracticeSessionManager → PracticeDriver → MVU Store  
GTOSessionManager      → GTODriver      → MVU Store
```

---

## 📊 **FUNCTIONAL REQUIREMENTS**

### **FR-001: Hand Data Management**

#### **FR-001.1: Multi-Source Hand Loading**
- **Requirement**: Support multiple hand data sources
- **Sources**: 
  - `legendary_hands.json` (100 legendary hands)
  - `gto_hands.json` (GTO-analyzed hands)
  - Live session exports
  - User-imported hand histories
- **Format**: Standardized JSON format with metadata, seats, streets, actions
- **Performance**: Load 1000+ hands in <2 seconds

#### **FR-001.2: Hand Metadata Display**
- **Hand ID**: Unique identifier (e.g., "BB001", "HU047")
- **Table Info**: Stakes, max players, ante/blinds
- **Player Info**: Starting stacks, position, hole cards
- **Session Type**: Review/Practice/GTO classification
- **Analysis Tags**: Bluff, Value bet, All-in, etc.

#### **FR-001.3: Data Validation**
- **Schema Validation**: Ensure all required fields present
- **Action Sequence**: Validate logical action progression
- **Stack Conservation**: Verify chip accounting accuracy
- **Error Handling**: Graceful fallback for corrupted hands

### **FR-002: Visual Poker Table Rendering**

#### **FR-002.1: Table Layout Specifications**
- **Seat Configuration**: Dynamic 2-9 player support
- **Seat Positioning**: Circular arrangement with proper spacing
- **Table Dimensions**: Responsive sizing (600x400 minimum)
- **Visual Hierarchy**: Felt < Seats < Community < Pot < Overlays

#### **FR-002.2: Player Seat Rendering**
```python
class SeatVisualRequirements:
    """Visual requirements for each player seat"""
    
    # Seat State Indicators
    position_indicator: bool      # Dealer button, blinds
    stack_display: str           # "$1,247" format with commas
    name_display: str            # Player name or "Seat X"
    action_indicator: str        # Current action status
    
    # Visual Highlighting
    acting_highlight: bool       # Yellow/gold border when acting
    winner_highlight: bool       # Green celebration when wins
    folded_dimming: bool        # 50% opacity when folded
    all_in_indicator: bool      # Special "ALL IN" badge
    
    # Card Display
    hole_cards: List[str]       # ["As", "Kd"] or card backs
    card_visibility: str        # "hidden", "visible", "winner_reveal"
    
    # Chip Graphics
    bet_chips: ChipStack        # Current bet amount visualization
    stack_chips: ChipStack      # Remaining stack visualization
    chip_animation: bool        # Chips moving to/from pot
```

#### **FR-002.3: Community Cards Rendering**
- **Initial State**: 5 card backs in flop/turn/river positions
- **Flop Reveal**: 3 cards flip simultaneously with sound
- **Turn Reveal**: 4th card flips with distinct sound
- **River Reveal**: 5th card flips with distinct sound
- **Card Quality**: High-resolution card graphics (SVG preferred)
- **Animation**: Smooth card flip transition (200ms duration)

#### **FR-002.4: Pot Graphics System**
```python
class PotVisualRequirements:
    """Comprehensive pot rendering specifications"""
    
    # Pot Display
    pot_amount: str             # "$0", "$47", "$1,247" formatting
    pot_position: Point         # Center of table
    chip_visualization: bool    # 3D chip stack representation
    
    # Chip Animations
    bet_to_pot: Animation      # Chips move from player to pot
    pot_to_winner: Animation   # Pot chips move to winner
    side_pots: List[PotStack]  # Multiple pot visualization
    
    # Animation Timing
    bet_collection_delay: int = 1000    # 1 second after street ends
    winner_payout_delay: int = 2000     # 2 seconds after showdown
    animation_duration: int = 800       # 800ms smooth movement
```

### **FR-003: Audio-Visual Feedback System**

#### **FR-003.1: Human Voice Announcements**
- **Action Calls**: "Player 1 calls", "Player 2 raises to forty-seven"
- **Street Transitions**: "The flop", "The turn", "The river"
- **Showdown**: "Player 1 wins with pair of kings"
- **Voice Quality**: Professional, clear female announcer
- **Language**: English with potential multi-language support

#### **FR-003.2: Mechanical Sound Effects**
```python
class SoundEffectRequirements:
    """Complete audio feedback specifications"""
    
    # Action Sounds
    chip_bet: str = "poker_chips1.wav"        # Betting chips
    chip_call: str = "poker_chips2.wav"       # Calling chips  
    chip_fold: str = "card_fold.wav"          # Folding cards
    chip_check: str = "table_tap.wav"         # Checking action
    chip_all_in: str = "allin_push.wav"       # All-in push
    
    # Card Sounds
    card_deal: str = "card_deal.wav"          # Hole cards dealt
    flop_sound: str = "flop_cards.wav"        # 3 cards flip
    turn_sound: str = "turn_card.wav"         # Turn card flip
    river_sound: str = "river_card.wav"       # River card flip
    
    # Winner Sounds
    pot_collect: str = "pot_collect.wav"      # Chips to winner
    winner_fanfare: str = "winner_chime.wav"  # Victory sound
    
    # UI Sounds  
    button_click: str = "ui_click.wav"        # Button feedback
    slider_move: str = "slider_tick.wav"      # Review slider
```

#### **FR-003.3: Audio-Visual Synchronization**
- **Perfect Timing**: Audio plays exactly when visual action occurs
- **No Overlap**: Prevent multiple sounds from conflicting
- **Volume Control**: Respect system/app volume settings
- **Fallback**: Graceful degradation if audio fails

### **FR-004: User Interface Controls**

#### **FR-004.1: Hand Selection Interface**
```python
class HandSelectionRequirements:
    """Hand selection dropdown specifications"""
    
    # Dropdown Content
    hand_format: str = "{hand_id} - {description} ({players}P)"
    # Example: "BB001 - Big Bluff vs Calling Station (2P)"
    
    # Sorting Options
    sort_by_id: bool = True          # Alphabetical by hand ID
    sort_by_type: bool = True        # Group by session type
    filter_by_players: bool = True   # Filter 2P, 3P, etc.
    
    # Performance
    lazy_loading: bool = True        # Load hands on-demand
    search_function: bool = True     # Type-to-search functionality
```

#### **FR-004.2: Playback Controls**
```python
class PlaybackControlRequirements:
    """Comprehensive playback control specifications"""
    
    # Primary Controls
    next_button: Button             # Advance one action
    prev_button: Button             # Go back one action  
    play_pause_button: Button       # Auto-play toggle
    reset_button: Button            # Return to hand start
    
    # Speed Controls
    speed_slider: Scale             # 0.5x to 4x speed
    speed_presets: List[float] = [0.5, 1.0, 2.0, 4.0]
    
    # Review Slider
    review_slider: Scale            # Scrub through actions
    position_display: str = "5/23"  # Current/total actions
    
    # Auto-play Behavior
    auto_play_delay: int = 1000     # 1 second between actions
    pause_on_decision: bool = True  # Pause for hero decisions
    loop_hand: bool = False         # Restart when finished
```

#### **FR-004.3: Progress Visualization**
- **Action Counter**: "Action 5 of 23" display
- **Street Indicator**: Preflop/Flop/Turn/River/Showdown
- **Progress Bar**: Visual timeline of hand progression
- **Action History**: Scrollable list of previous actions

### **FR-005: Animation System**

#### **FR-005.1: Chip Movement Animations**
```python
class ChipAnimationRequirements:
    """Detailed chip animation specifications"""
    
    # Bet to Pot Animation
    def animate_bet_to_pot(self, seat: int, amount: int):
        """
        Animate chips moving from player seat to pot
        Duration: 300ms
        Easing: ease-out cubic bezier
        Visual: 3-5 chip sprites moving in arc
        """
        
    # Pot to Winner Animation  
    def animate_pot_to_winner(self, winner_seat: int, amount: int):
        """
        Animate pot chips moving to winner
        Duration: 500ms  
        Easing: ease-in-out
        Visual: Chip stream with sparkle effect
        """
        
    # Side Pot Handling
    side_pots: List[SidePot]        # Multiple pot visualization
    all_in_protection: bool = True  # Correct side pot math
```

#### **FR-005.2: Card Reveal Animations**
- **Hole Cards**: Instant reveal (review mode) or delayed (practice)
- **Flop**: Simultaneous 3-card flip (200ms each, 100ms stagger)
- **Turn/River**: Single card flip (200ms duration)
- **Showdown**: Winner cards highlighted, losers dimmed
- **Card Backs**: Professional card back design

#### **FR-005.3: Player Highlighting System**
```python
class PlayerHighlightRequirements:
    """Player visual state specifications"""
    
    # Action States
    acting_player: HighlightStyle = {
        'border_color': '#FFD700',     # Gold border
        'border_width': 3,             # 3px thick
        'glow_effect': True,           # Subtle glow
        'animation': 'pulse_slow'      # Gentle pulsing
    }
    
    # Winner Celebration
    winner_player: HighlightStyle = {
        'border_color': '#00FF00',     # Green celebration
        'background_tint': '#90EE90',  # Light green background
        'sparkle_effect': True,        # Particle animation
        'duration': 3000               # 3 seconds
    }
    
    # Folded Players
    folded_player: HighlightStyle = {
        'opacity': 0.5,                # 50% transparency
        'grayscale': True,             # Desaturated colors
        'cards_hidden': True           # Cards face down
    }
```

---

## 🔄 **USER WORKFLOW SPECIFICATIONS**

### **UW-001: Standard Hand Review Workflow**

#### **Step 1: Hand Selection**
1. User opens Hands Review tab
2. System loads available hands from data sources
3. User selects hand from dropdown (e.g., "BB001 - Big Bluff vs Station")
4. System loads hand data and initializes MVU model
5. Poker table displays initial state (preflop, hole cards visible)

#### **Step 2: Manual Step-Through**
1. User clicks "Next" button
2. System dispatches `NextPressed` message to MVU store
3. Store updates model with next action
4. View renders new table state with animations
5. Audio plays appropriate sound (chips/voice)
6. Process repeats until hand completion

#### **Step 3: Auto-Play Mode**
1. User clicks "Auto-Play" button
2. System enters automated playback mode
3. Actions advance automatically every 1 second (configurable)
4. User can pause/resume or adjust speed
5. System pauses on critical decisions (optional)

#### **Step 4: Review Navigation**
1. User drags review slider to specific action
2. System dispatches `ReviewSeek` message
3. Model instantly updates to target state
4. Table renders final state (no intermediate animations)
5. User can fine-tune position with next/prev buttons

### **UW-002: Educational Analysis Workflow**

#### **Study Mode Features**
- **Pause on Hero**: Automatically pause when hero has decision
- **Decision Analysis**: Show GTO recommendations vs actual play
- **Equity Display**: Show hand strength percentages (optional)
- **Action Notes**: Display analysis comments for specific actions
- **Mistake Highlighting**: Visual indicators for suboptimal plays

### **UW-003: Session Manager Integration**

#### **Review Session Manager**
```python
class ReviewSessionManager:
    """Manages review-specific functionality"""
    
    def load_hand(self, hand_id: str) -> HandData:
        """Load hand data for review"""
        
    def get_action_analysis(self, action_index: int) -> Analysis:
        """Get educational analysis for specific action"""
        
    def mark_favorite(self, hand_id: str) -> None:
        """Mark hand as favorite for quick access"""
```

#### **Practice Session Integration**
- **Same Table Renderer**: Reuse exact visual components
- **Different Driver**: Practice decisions vs review playback
- **Seamless Transition**: Switch between modes without UI reload

#### **GTO Session Integration** 
- **GTO Recommendations**: Overlay optimal plays during review
- **Mistake Detection**: Highlight deviations from GTO strategy
- **Learning Mode**: Show correct play before revealing actual action

---

## 🎨 **VISUAL DESIGN SPECIFICATIONS**

### **Theme Integration**
- **Full Theme Support**: Respect all theme tokens from theme system
- **Felt Colors**: Use theme-specific table felt colors
- **Card Designs**: Match theme aesthetic (classic/modern/neon)
- **Chip Colors**: Theme-appropriate chip denominations
- **Hot-Swappable**: Change themes without restarting review

### **Responsive Design**
- **Minimum Size**: 800x600 pixels
- **Maximum Size**: 1920x1080 pixels
- **Aspect Ratio**: Maintain 16:10 poker table proportions
- **Scaling**: All elements scale proportionally
- **Font Sizes**: Readable at all supported resolutions

### **Accessibility**
- **Color Contrast**: 4.5:1 ratio for all text
- **Keyboard Navigation**: Full tab-through support
- **Screen Reader**: ARIA labels for all interactive elements
- **Motion Reduction**: Respect prefers-reduced-motion setting
- **Focus Indicators**: Clear visual focus for keyboard users

---

## ⚡ **PERFORMANCE REQUIREMENTS**

### **Response Time Specifications**
- **Hand Loading**: <500ms for any hand size
- **Next/Previous Action**: <100ms button response
- **Animation Smoothness**: 60 FPS for all animations  
- **Memory Usage**: <100MB for 1000+ hand dataset
- **CPU Usage**: <10% during normal playback

### **Scalability Requirements**
- **Hand Count**: Support 10,000+ hands without performance degradation
- **Session Length**: 8+ hour review sessions without memory leaks
- **Multiple Instances**: Multiple hands review tabs simultaneously
- **Background Loading**: Preload next/previous hands for instant switching

---

## 🔒 **TECHNICAL CONSTRAINTS**

### **MVU Architecture Compliance**
- **Immutable State**: All model data uses immutable collections
- **Pure Reducers**: No side effects in update functions
- **Command Pattern**: All effects as commands to effects layer
- **Single Source of Truth**: One model state per review session

### **Integration Requirements**
- **Service Container**: Full integration with existing DI system
- **Game Director**: Timing via existing scheduling system
- **Event Bus**: Publish events for external monitoring
- **Theme Manager**: Hot-swappable theme support

### **Browser/Platform Compatibility**
- **Tkinter Canvas**: Full Canvas API utilization for rendering
- **Python 3.9+**: Modern Python language features
- **Cross-Platform**: Windows, macOS, Linux support
- **Memory Efficiency**: Garbage collection friendly patterns

---

## 🧪 **TESTING REQUIREMENTS**

### **Unit Testing**
- **Model Tests**: Verify immutable state transitions
- **Reducer Tests**: Test all message types and edge cases
- **Component Tests**: Isolated UI component testing
- **Animation Tests**: Verify timing and visual states

### **Integration Testing**
- **MVU Flow Tests**: Complete user interactions end-to-end
- **Session Manager Tests**: Verify reusability across session types
- **Audio-Visual Sync**: Timing validation for all effects
- **Performance Tests**: Memory and CPU usage validation

### **User Acceptance Testing**
- **Usability Tests**: Real poker players testing interface
- **Educational Effectiveness**: Learning outcome measurements
- **Accessibility Tests**: Screen reader and keyboard navigation
- **Stress Tests**: Extended session and large dataset handling

---

## 📈 **SUCCESS CRITERIA**

### **Primary Success Metrics**
1. **Zero Infinite Loops**: MVU implementation prevents all rendering loops
2. **Sub-100ms Responsiveness**: All user interactions feel instantaneous
3. **Perfect Audio-Visual Sync**: No timing discrepancies between effects
4. **Universal Reusability**: Same renderer works for Practice/GTO/Review
5. **Educational Value**: Users report improved poker understanding

### **Secondary Success Metrics**
1. **Memory Stability**: No memory growth during extended sessions
2. **Animation Quality**: Smooth 60 FPS animations on target hardware
3. **Theme Compatibility**: Works flawlessly with all 16 themes
4. **Accessibility Compliance**: Passes all WCAG 2.1 AA requirements
5. **Performance Scalability**: Handles 10,000+ hands without degradation

---

## 🚀 **IMPLEMENTATION ROADMAP**

### **Phase 1: Core MVU Infrastructure (Week 1-2)**
- ✅ Immutable model types with proper equality
- ✅ Store with state reset protection
- ✅ Basic table renderer with props caching
- ✅ Review driver for hand playback

### **Phase 2: Visual Polish (Week 3-4)**
- 🔲 Professional card graphics and animations
- 🔲 Chip movement and pot animations
- 🔲 Player highlighting and state indicators
- 🔲 Theme integration and responsive design

### **Phase 3: Audio Integration (Week 5)**
- 🔲 Human voice announcements
- 🔲 Mechanical sound effects
- 🔲 Audio-visual synchronization
- 🔲 Volume controls and fallbacks

### **Phase 4: Advanced Features (Week 6-7)**
- 🔲 Auto-play with configurable timing
- 🔲 Educational analysis overlays
- 🔲 Session manager integration
- 🔲 Performance optimization

### **Phase 5: Testing & Polish (Week 8)**
- 🔲 Comprehensive testing suite
- 🔲 Accessibility compliance
- 🔲 Performance benchmarking
- 🔲 User acceptance testing

---

*This requirements document serves as the authoritative specification for hands review tab development. All implementation must adhere to these requirements to ensure industry-strength quality and reliability.*

```

---

## ARCHITECTURE DOCUMENTATION

### MVU_ARCHITECTURE_GUIDE.md

**Path**: `docs/PokerPro_MVU_Architecture_Guide_v2.md`

```markdown
# PokerPro MVU Architecture Guide v2.0
**Status**: Critical Reference - Prevents Infinite Loop Bugs  
**Last Updated**: January 2025  
**Purpose**: Authoritative guide for MVU implementation with explicit anti-patterns  

---

## 🚨 **CRITICAL: PREVENTING INFINITE LOOPS**

### **The Infinite Loop Problem**
The MVU architecture is susceptible to infinite rendering loops when:
1. **Equality checks fail** between identical data structures
2. **State oscillates** between empty and populated states  
3. **UI callbacks trigger** during programmatic updates
4. **Props are recreated** on every render cycle

### **Mandatory Prevention Patterns**

#### **1. ALWAYS Use Immutable Collections in Models**

```python
# ❌ NEVER DO THIS - Causes equality check failures
@dataclass(frozen=True)
class Model:
    seats: Dict[int, SeatState]  # WRONG - mutable Dict
    legal_actions: Set[str]      # WRONG - mutable Set
    banners: List[Banner]        # WRONG - mutable List

# ✅ ALWAYS DO THIS - Enables proper equality
from typing import Mapping, FrozenSet

@dataclass(frozen=True)
class Model:
    seats: Mapping[int, SeatState]  # CORRECT - immutable Mapping
    legal_actions: frozenset[str]   # CORRECT - immutable frozenset
    banners: tuple[Banner, ...]     # CORRECT - immutable tuple
```

#### **2. ALWAYS Implement Explicit Equality Methods**

```python
# ❌ NEVER RELY ON AUTO-GENERATED EQUALITY
@dataclass(frozen=True, eq=True)  # Auto eq=True FAILS with nested objects
class TableRendererProps:
    seats: Dict[int, SeatState]

# ✅ ALWAYS IMPLEMENT CUSTOM EQUALITY
@dataclass(frozen=True, eq=False)  # Disable auto-equality
class TableRendererProps:
    seats: Mapping[int, SeatState]
    
    def __eq__(self, other):
        """Deep equality that actually works"""
        if not isinstance(other, TableRendererProps):
            return False
        # Compare dictionaries by converting to dict
        return dict(self.seats) == dict(other.seats)
```

#### **3. ALWAYS Guard Against State Resets**

```python
# ✅ MANDATORY STORE PROTECTION
def dispatch(self, msg: Msg) -> None:
    old_model = self.model
    new_model, commands = update(self.model, msg)
    
    # CRITICAL: Prevent unexpected state resets
    if (len(old_model.seats) > 0 and 
        len(new_model.seats) == 0 and
        type(msg).__name__ not in ['ResetHand', 'ClearTable']):
        print(f"⚠️ Blocking suspicious reset: {type(msg).__name__}")
        return  # Reject the update
    
    # Only notify if model actually changed
    if new_model != old_model:
        self.model = new_model
        for subscriber in self.subscribers[:]:  # Use slice!
            subscriber(new_model)
```

#### **4. ALWAYS Defer Initial Data Loading**

```python
# ❌ NEVER LOAD DATA IN __init__
def __init__(self):
    self._initialize_mvu()
    self._load_hand(0)  # WRONG - Race condition!

# ✅ ALWAYS DEFER INITIAL LOAD
def __init__(self):
    self._initialize_mvu()
    self._mvu_initialized = True
    # Load data AFTER initialization
    
def _load_hands_data(self):
    # Only load if MVU is ready
    if hasattr(self, '_mvu_initialized'):
        self._load_hand(0)
```

#### **5. ALWAYS Disable Callbacks During Programmatic Updates**

```python
# ✅ MANDATORY CALLBACK PROTECTION
def _update_review_controls(self, props):
    if not hasattr(self, '_updating_scale'):
        self._updating_scale = False
    
    if not self._updating_scale:
        self._updating_scale = True
        try:
            # Temporarily disable callback
            self.review_scale.config(command="")
            self.review_scale.set(props.review_cursor)
            # Re-enable after delay
            self.after(10, lambda: self.review_scale.config(
                command=self._on_review_seek))
        finally:
            self._updating_scale = False
```

---

## 📋 **MVU IMPLEMENTATION CHECKLIST**

### **Model Definition Requirements**
- [ ] All collections use immutable types (`tuple`, `frozenset`, `Mapping`)
- [ ] Custom `__eq__` method implemented for all dataclasses
- [ ] Custom `__hash__` method for frozen dataclasses
- [ ] No mutable default values in dataclass fields
- [ ] `frozen=True` on all model dataclasses

### **Store Implementation Requirements**
- [ ] Guard against suspicious state resets
- [ ] Check model equality before notifying subscribers
- [ ] Use slice when iterating subscribers to avoid mutation
- [ ] Log all state transitions for debugging
- [ ] Thread-safe with proper locking

### **View Implementation Requirements**  
- [ ] Props cached and compared before rendering
- [ ] UI callbacks disabled during programmatic updates
- [ ] Initialization order: Create → Initialize → Subscribe → Load
- [ ] First empty render skipped in review mode
- [ ] All renders logged with seat count

### **Testing Requirements**
- [ ] Test equality between identical models returns `True`
- [ ] Test props comparison with nested structures
- [ ] Test store rejects invalid state transitions
- [ ] Test no infinite loops in 5-second render test
- [ ] Test memory usage remains stable

---

## 🏗️ **MVU ARCHITECTURE PATTERNS**

### **The Three-Layer Architecture**

```
┌─────────────────────────────────────┐
│           View Layer                │
│  - Pure rendering functions         │
│  - No business logic                │
│  - Emits intents only              │
└─────────────┬───────────────────────┘
              │ Props (immutable)
┌─────────────▼───────────────────────┐
│           Model Layer               │
│  - Immutable state (Model)         │
│  - Pure update functions           │
│  - Deterministic transitions       │
└─────────────┬───────────────────────┘
              │ Commands (effects)
┌─────────────▼───────────────────────┐
│         Effects Layer               │
│  - Side effects (I/O, timers)      │
│  - Service calls                   │
│  - External integrations           │
└─────────────────────────────────────┘
```

### **Data Flow (Unidirectional)**

```
User Action → Intent → Message → Update → Model' → Props → Render
                           ↓
                        Commands → Effects → New Messages
```

### **Immutable Model Pattern**

```python
from dataclasses import dataclass, replace
from typing import Mapping, FrozenSet

@dataclass(frozen=True, slots=True)
class Model:
    """Immutable model with value semantics"""
    # Primitive immutable types
    hand_id: str
    pot: int
    
    # Immutable collections
    board: tuple[str, ...]
    seats: Mapping[int, SeatState]
    legal_actions: frozenset[str]
    
    def with_seats(self, seats: dict) -> 'Model':
        """Return new model with updated seats"""
        return replace(self, seats=seats)
    
    def __eq__(self, other):
        """Value-based equality"""
        if not isinstance(other, Model):
            return False
        return (
            self.hand_id == other.hand_id and
            self.pot == other.pot and
            self.board == other.board and
            dict(self.seats) == dict(other.seats) and
            self.legal_actions == other.legal_actions
        )
```

### **Props Memoization Pattern**

```python
class TableRenderer:
    def __init__(self):
        self._props_cache = {}
        self._last_model_hash = None
    
    def render(self, model: Model) -> None:
        # Create stable hash of model
        model_hash = self._compute_model_hash(model)
        
        # Check cache
        if model_hash == self._last_model_hash:
            return  # Skip render, nothing changed
        
        # Create props only when needed
        if model_hash not in self._props_cache:
            self._props_cache[model_hash] = TableRendererProps.from_model(model)
            # Limit cache size
            if len(self._props_cache) > 10:
                self._props_cache.pop(next(iter(self._props_cache)))
        
        props = self._props_cache[model_hash]
        self._last_model_hash = model_hash
        self._render_internal(props)
```

---

## 🧪 **TESTING FOR INFINITE LOOPS**

### **Mandatory Test Suite**

```python
import time
import threading

class TestMVUInfiniteLoopPrevention:
    
    def test_model_equality_with_nested_structures(self):
        """Ensure identical models are equal"""
        model1 = Model.initial()
        model2 = Model.initial()
        assert model1 == model2
        
        # With seats
        seats = {0: SeatState(...), 1: SeatState(...)}
        model1 = replace(model1, seats=seats)
        model2 = replace(model2, seats=seats)
        assert model1 == model2
    
    def test_no_infinite_render_loop(self):
        """Ensure no infinite rendering occurs"""
        render_count = [0]
        
        def counting_render(props):
            render_count[0] += 1
            if render_count[0] > 100:
                raise Exception("Infinite loop detected!")
        
        # Set up MVU with counting renderer
        store = MVUStore(Model.initial())
        renderer = MockRenderer(counting_render)
        store.subscribe(lambda m: renderer.render(
            TableRendererProps.from_model(m)))
        
        # Load hand data
        store.dispatch(LoadHand(hand_data={...}))
        
        # Wait for any async operations
        time.sleep(0.5)
        
        # Should have rendered once or twice, not 100+ times
        assert render_count[0] < 10
    
    def test_store_blocks_invalid_resets(self):
        """Ensure store prevents suspicious state resets"""
        store = MVUStore(Model.initial())
        
        # Load populated state
        store.dispatch(LoadHand(hand_data={'seats': {...}}))
        assert len(store.model.seats) > 0
        
        # Try to reset (should be blocked)
        store.dispatch(SomeOtherMessage())
        assert len(store.model.seats) > 0  # Still populated
    
    def test_props_caching_works(self):
        """Ensure props aren't recreated unnecessarily"""
        created_count = [0]
        
        original_from_model = TableRendererProps.from_model
        def counting_from_model(model):
            created_count[0] += 1
            return original_from_model(model)
        
        TableRendererProps.from_model = counting_from_model
        
        # Render same model multiple times
        model = Model.initial()
        renderer = TableRenderer()
        
        for _ in range(10):
            renderer.render(model)  # Same model
        
        # Props should be created once, not 10 times
        assert created_count[0] == 1
```

---

## 📐 **ARCHITECTURAL RULES**

### **Rule 1: Immutability First**
- Models are **always** immutable
- Use `replace()` to create new models
- Collections must be immutable types
- No in-place mutations ever

### **Rule 2: Explicit Over Implicit**
- Custom equality methods over auto-generated
- Explicit type annotations everywhere
- Clear subscription/unsubscription patterns
- Named constants for magic values

### **Rule 3: Defensive Programming**
- Guard against unexpected state transitions
- Validate inputs at boundaries
- Log everything for debugging
- Fail fast with clear error messages

### **Rule 4: Performance Through Design**
- Cache computed values (props, hashes)
- Early-out comparisons before expensive operations
- Batch updates when possible
- Profile and measure, don't guess

---

## 🎯 **QUICK REFERENCE: DO's AND DON'Ts**

### **DO's**
- ✅ Use `frozenset` for sets in models
- ✅ Use `tuple` for lists in models  
- ✅ Use `Mapping` for dicts in models
- ✅ Implement custom `__eq__` methods
- ✅ Cache props between renders
- ✅ Guard against state resets
- ✅ Defer initial data loading
- ✅ Disable UI callbacks during updates
- ✅ Test for infinite loops explicitly

### **DON'Ts**
- ❌ Use `Dict`, `List`, `Set` in frozen dataclasses
- ❌ Rely on auto-generated equality
- ❌ Create new props on every render
- ❌ Load data during initialization
- ❌ Allow callbacks during programmatic updates
- ❌ Skip equality checks before notifying
- ❌ Mutate subscriber lists during iteration
- ❌ Assume dataclass equality works

---

## 🔍 **DEBUGGING INFINITE LOOPS**

### **Symptoms to Watch For**
1. Console shows alternating states (0 seats → 2 seats → 0 seats)
2. CPU usage spikes to 100%
3. UI becomes unresponsive
4. Render count exceeds reasonable limits

### **Debugging Steps**
1. **Add render counting** to detect excessive renders
2. **Log all dispatches** with message types
3. **Log model transitions** with before/after seat counts
4. **Check equality** between supposedly identical models
5. **Trace callbacks** to find circular triggers
6. **Profile memory** to detect object creation loops

### **Common Root Causes**
1. **Mutable collections** in frozen dataclasses
2. **Missing equality methods** for nested structures
3. **Race conditions** during initialization
4. **Callback loops** from UI widgets
5. **Props recreation** on every render

---

## 🎯 **INTEGRATION WITH EXISTING ARCHITECTURE**

### **GameDirector Compatibility**
The MVU architecture works within the existing GameDirector pattern:

```python
# MVU commands trigger GameDirector scheduling
def _execute_schedule_timer(self, cmd: ScheduleTimer) -> None:
    """Execute timer command via GameDirector"""
    if self.game_director:
        self.game_director.schedule(
            cmd.delay_ms / 1000.0,
            lambda: self.dispatch(cmd.msg)
        )
```

### **Event Bus Integration**
MVU stores can publish to the legacy event bus:

```python
def _execute_publish_event(self, cmd: PublishEvent) -> None:
    """Publish event to legacy event bus"""
    if self.event_bus:
        self.event_bus.publish(cmd.event_type, cmd.data)
```

### **Service Container Access**
MVU components get services through dependency injection:

```python
class MVUHandsReviewTab:
    def __init__(self, parent, services: ServiceContainer):
        self.theme_manager = services.get_app("theme")
        self.effect_bus = services.get_app("effect_bus")
        # ... MVU initialization
```

---

## 🔧 **MIGRATION GUIDELINES**

### **From Legacy UI to MVU**

1. **Extract State**: Move all UI state into immutable Model
2. **Pure Renderers**: Convert UI components to pure functions
3. **Event Mapping**: Map UI events to MVU messages
4. **Command Effects**: Convert side effects to commands
5. **Test Thoroughly**: Verify no infinite loops

### **Gradual Migration Strategy**

1. **Start Small**: Convert one tab/component at a time
2. **Bridge Pattern**: Use adapters between MVU and legacy
3. **Shared Services**: Keep using ServiceContainer
4. **Incremental Testing**: Test each migration step
5. **Monitor Performance**: Watch for regressions

---

*This document is **mandatory reading** for all developers and AI agents working on MVU implementations. Violations of these patterns **will** cause infinite loops.*

```

---

### PROJECT_PRINCIPLES.md

**Path**: `docs/PROJECT_PRINCIPLES_v2.md`

```markdown
## Project Principles v2 (Authoritative)

### Architecture
- Single-threaded, event-driven coordinator (GameDirector). All timing via coordinator.
- Single source of truth per session (Store). No duplicate state.
- Event-driven only. UI is pure render from state; no business logic in UI.
- **MVU Pattern**: For complex UI, use Model-View-Update architecture (see `PokerPro_MVU_Architecture_Guide_v2.md`).

### Separation of concerns
- Domain: entities, rules, state machines; pure and deterministic.
- Application/Services: orchestration, schedulers, adapters; no UI.
- Adapters: persistence, audio, estimators, external APIs.
- UI: render-only; reads from Store; raises intents.

### Coding standards
- OO-first; composition/strategies/state machines over conditionals.
- DRY; reuse components; small, stable public APIs.
- Deterministic core; isolate I/O, randomness, timing.
- Explicit dependency injection; avoid globals/singletons.

### UI design
- Canvas layers: felt < seats < community < pot < overlay.
- Theme tokens only; central ThemeManager; hot-swappable profiles.
- Accessibility: ≥4.5:1 contrast; 44×44 targets; keyboard bindings; live regions.

### Testing & logging
- Snapshot tests for UI; unit tests for reducers/selectors and adapters.
- Logs to `logs/` with rotation; ISO timestamps; module:file:line; no secrets/PII.

### Prohibitions
- No threading/timers for game logic; no blocking animations/sounds.
- No duplicate state sources; no component-to-component timing calls.
- **No mutable collections in MVU models** (use `tuple`, `frozenset`, `Mapping`).
- **No auto-generated equality for nested structures** (implement custom `__eq__`).
- **No data loading during UI initialization** (defer until components ready).

### 🚫 CRITICAL AI AGENT COMPLIANCE RULES (NEVER VIOLATE)

#### **🔥 MVU INFINITE LOOP PREVENTION (CRITICAL)**

**❌ NEVER USE MUTABLE COLLECTIONS IN MVU MODELS**
```python
# WRONG - Will cause infinite loops
@dataclass(frozen=True)
class Model:
    seats: Dict[int, SeatState]  # ❌ Mutable Dict
    legal_actions: Set[str]      # ❌ Mutable Set

# CORRECT - Prevents infinite loops  
@dataclass(frozen=True)
class Model:
    seats: Mapping[int, SeatState]  # ✅ Immutable Mapping
    legal_actions: frozenset[str]   # ✅ Immutable frozenset
```

**❌ NEVER RELY ON AUTO-GENERATED EQUALITY**
```python
# WRONG - eq=True fails with nested objects
@dataclass(frozen=True, eq=True)
class Props: ...

# CORRECT - Custom equality works
@dataclass(frozen=True, eq=False)
class Props:
    def __eq__(self, other): ...
```

**❌ NEVER LOAD DATA DURING UI __init__**
```python
# WRONG - Race condition causes loops
def __init__(self):
    self._init_mvu()
    self._load_hand(0)  # ❌ Too early!

# CORRECT - Deferred loading
def __init__(self):
    self._init_mvu()
    self._mvu_initialized = True
def _load_data(self):
    if hasattr(self, '_mvu_initialized'):
        self._load_hand(0)  # ✅ Safe timing
```

**🔍 REFERENCE: See `docs/PokerPro_MVU_Architecture_Guide_v2.md` for complete infinite loop prevention guide.**

#### **🔥 ARCHITECTURE VIOLATIONS THAT MUST BE PREVENTED**

**❌ VIOLATION 1: Business Logic in UI Components**
```python
# ❌ FORBIDDEN - Business logic in UI
def _next_action(self):
    session_state = self.session_manager.execute_action()  # WRONG!
    self._update_ui(session_state)

# ✅ CORRECT - Pure UI dispatch
def _next_action(self):
    self.store.dispatch({"type": "HANDS_REVIEW_NEXT_ACTION"})
```

**❌ VIOLATION 2: Direct Service Calls from UI**
```python
# ❌ FORBIDDEN - Direct service calls
self.session_manager.execute_action()  # WRONG!
self.effect_bus.play_sound("bet")      # WRONG!

# ✅ CORRECT - Event-driven
self.store.dispatch({"type": "NEXT_ACTION"})
self.event_bus.publish("sound:play", {"type": "bet"})
```

**❌ VIOLATION 3: Timing Violations**
```python
# ❌ FORBIDDEN - Direct timing calls
self.after(1000, callback)           # WRONG!
threading.Timer(1.0, callback)      # WRONG!
time.sleep(1)                        # WRONG!

# ✅ CORRECT - GameDirector timing
self.game_director.schedule(1000, {"type": "DELAYED_ACTION", "callback": callback})
```

**❌ VIOLATION 4: State Mutations in UI**
```python
# ❌ FORBIDDEN - Direct state mutation
self.game_state.pot += 100           # WRONG!
self.display_state['acting'] = True  # WRONG!

# ✅ CORRECT - Store dispatch
self.store.dispatch({"type": "UPDATE_POT", "amount": 100})
```

#### **✅ MANDATORY COMPLIANCE RULES**

1. **UI Components MUST be Pure Renderers**
2. **All Communication MUST be Event-Driven**  
3. **All Timing MUST go through GameDirector**
4. **Single Source of Truth MUST be Maintained**
5. **Store/Reducer Pattern MUST be Used**

#### **🛡️ ENFORCEMENT CHECKLIST**
- [ ] No business logic in UI components
- [ ] No direct service calls from UI  
- [ ] No timing violations (after/Timer/sleep)
- [ ] All state changes via Store dispatch
- [ ] Event-driven communication only

### AI Agent Compliance (Do not deviate)
1. Do **not** add new events or fields. If missing, leave TODO and stop.
2. Never compute poker legality in UI; call selectors/PPSM.
3. Use theme tokens only; no literal colors, shadows, or fonts.
4. Do not use timers/threads for game logic; schedule via Director.
5. No cross-component writes; only Store and events.
6. Respect casing rules (events UPPER_SNAKE_CASE; domain snake_case).
7. Keep functions small and pure; side effects only in adapters.
8. If uncertain, generate interface stubs, not implementations.
9. **NEVER put business logic in UI components - they are pure renderers only**
10. **ALWAYS use Store/Reducer pattern - no direct service calls from UI**
11. **ALL timing must go through GameDirector - no self.after() violations**

### PR Acceptance Checklist
- [ ] No business logic in UI; all decisions via PPSM or DecisionEngine.
- [ ] Events are UPPER_SNAKE_CASE; fields snake_case; streets uppercase.
- [ ] Only theme tokens used; contrast checks pass.
- [ ] Components subscribe via selectors; no direct Store writes.
- [ ] Replay tests pass on sample hands; headless run produces stable state hashes.
- [ ] Logs are present, structured, and scrubbed.

```

---

### COMPLETE_ARCHITECTURE.md

**Path**: `docs/PokerPro_Trainer_Complete_Architecture_v3.md`

```markdown
# PokerPro Trainer - Complete Architecture Reference v3

**Status**: Production Ready  
**Last Updated**: January 2024  
**Purpose**: Comprehensive reference for complete codebase reconstruction if needed  

---

## 🏗️ **SYSTEM OVERVIEW**

The PokerPro Trainer uses a **single-threaded, event-driven architecture** centered around three core pillars:

1. **PurePokerStateMachine (PPSM)** - Deterministic poker engine with hand replay capabilities
2. **Modern UI Architecture** - Component-based UI with clean separation of concerns  
3. **Session Management System** - Pluggable session types (GTO, Practice, Hands Review, Live)

### **Core Design Principles**

- **Single Source of Truth**: PPSM is the authoritative game state
- **Deterministic Behavior**: All game logic is reproducible and testable
- **Clean Separation**: UI renders state, never controls game logic
- **Event-Driven**: All interactions flow through well-defined interfaces
- **Pluggable Components**: DecisionEngines and Sessions are swappable

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

### **Phase 1: Core Implementation**
- Complete Enhanced RPGW integration
- Implement all three session types
- Establish testing framework
- Performance optimization

### **Phase 2: Advanced Features**
- Advanced animation system
- Enhanced sound integration
- Performance analytics
- Accessibility improvements

### **Phase 3: Scalability**
- Multi-table support
- Advanced session management
- Plugin architecture
- Cloud integration

---

*This document serves as the authoritative reference for the PokerPro Trainer architecture. All implementations must comply with these principles and patterns.*

```

---

### VIOLATION_PREVENTION_GUIDE.md

**Path**: `docs/ARCHITECTURE_VIOLATION_PREVENTION_GUIDE.md`

```markdown
# 🚫 Architecture Violation Prevention Guide

**Status**: Critical Reference for AI Agents  
**Purpose**: Prevent common architecture violations that compromise system integrity  
**Target Audience**: AI Coding Assistants, Future Development Teams  

---

## 🎯 **EXECUTIVE SUMMARY**

This guide documents **critical architecture violations** discovered during system analysis and provides **mandatory prevention patterns** for future AI agents. These violations were found in production code and **must never be repeated**.

### **🔥 HIGH-SEVERITY VIOLATIONS FOUND**

1. **Business Logic in UI Components** - UI directly executing business operations
2. **Direct Service Calls from UI** - Bypassing Store/Reducer architecture  
3. **Timing Violations** - Using `self.after()` instead of GameDirector
4. **State Mutations in UI** - Direct state changes bypassing Store
5. **Mixed Rendering Patterns** - Multiple rendering approaches instead of unified system

---

## 📋 **VIOLATION CATALOG & FIXES**

### **🚨 VIOLATION 1: Business Logic in UI Components**

#### **❌ FORBIDDEN PATTERN**
```python
class HandsReviewTab(ttk.Frame):
    def _next_action(self):
        # ❌ WRONG: Business logic in UI
        session_state = self.session_manager.execute_action()
        
        if session_state.current_action_index < session_state.total_actions:
            self._update_status(f"Action {session_state.current_action_index}")
            self._render_table_with_state(session_state)
        else:
            self._update_status("Hand complete")
```

#### **✅ CORRECT PATTERN**
```python
class HandsReviewTab(ttk.Frame):
    def _next_action(self):
        # ✅ CORRECT: Pure UI dispatch
        self.store.dispatch({
            "type": "HANDS_REVIEW_NEXT_ACTION",
            "session_id": self.session_id,
            "timestamp": time.time()
        })
```

#### **🛡️ PREVENTION RULES**
- UI components are **pure renderers only**
- All business logic in Services or PPSM
- UI only dispatches actions and renders state
- No direct calls to session managers from UI

---

### **🚨 VIOLATION 2: Direct Service Calls from UI**

#### **❌ FORBIDDEN PATTERN**
```python
# ❌ WRONG: Direct service calls
def _handle_bet(self):
    result = self.session_manager.execute_bet(amount)  # VIOLATION!
    self.effect_bus.play_sound("bet")                  # VIOLATION!
    self._update_display(result)
```

#### **✅ CORRECT PATTERN**
```python
# ✅ CORRECT: Event-driven architecture
def _handle_bet(self):
    self.store.dispatch({
        "type": "PLAYER_BET_ACTION",
        "amount": amount,
        "session_id": self.session_id
    })
    
    # Service controller handles the business logic:
    # 1. Receives event from reducer
    # 2. Calls session_manager.execute_bet()
    # 3. Calls effect_bus.play_sound()
    # 4. Updates store with results
```

#### **🛡️ PREVENTION RULES**
- No direct service method calls from UI
- All communication via Store → Reducer → Service
- Services handle business logic and side effects
- UI never touches session managers directly

---

### **🚨 VIOLATION 3: Timing Violations**

#### **❌ FORBIDDEN PATTERNS**
```python
# ❌ WRONG: Direct timing calls
self.after(1000, self._complete_action)        # VIOLATION!
threading.Timer(1.0, callback).start()        # VIOLATION!
time.sleep(1)                                  # VIOLATION!

# ❌ WRONG: Update loops with self.after
def _update_loop(self):
    self._refresh_display()
    self.after(16, self._update_loop)           # VIOLATION!
```

#### **✅ CORRECT PATTERNS**
```python
# ✅ CORRECT: GameDirector timing
self.game_director.schedule(1000, {
    "type": "DELAYED_ACTION",
    "callback": self._complete_action
})

# ✅ CORRECT: Event-driven updates
self.event_bus.publish("display:refresh_requested", {
    "interval_ms": 16,
    "component": "table_display"
})
```

#### **🛡️ PREVENTION RULES**
- All timing via GameDirector
- No `self.after()`, `threading.Timer`, or `time.sleep()`
- Use `TimingMigrationHelper` for complex timing
- Event-driven updates instead of polling loops

---

### **🚨 VIOLATION 4: State Mutations in UI**

#### **❌ FORBIDDEN PATTERN**
```python
# ❌ WRONG: Direct state mutations
def _update_pot(self, amount):
    self.game_state.pot += amount              # VIOLATION!
    self.display_state['seats'][0]['acting'] = True  # VIOLATION!
    self._refresh_display()
```

#### **✅ CORRECT PATTERN**
```python
# ✅ CORRECT: Store dispatch for state changes
def _update_pot(self, amount):
    self.store.dispatch({
        "type": "UPDATE_POT_AMOUNT",
        "amount": amount
    })
    
    self.store.dispatch({
        "type": "SET_ACTING_PLAYER",
        "seat_index": 0,
        "acting": True
    })
```

#### **🛡️ PREVENTION RULES**
- All state changes via Store dispatch
- UI never directly mutates state objects
- Single source of truth in Store
- Reducers handle all state transformations

---

### **🚨 VIOLATION 5: Mixed Rendering Patterns**

#### **❌ FORBIDDEN PATTERN**
```python
# ❌ WRONG: Multiple rendering approaches
class HandsReviewTab(ttk.Frame):
    def __init__(self):
        self.poker_widget = ReusablePokerGameWidget(...)  # VIOLATION!
        self.table_renderer = PokerTableRenderer(...)    # VIOLATION!
        self.custom_canvas = tk.Canvas(...)               # VIOLATION!
```

#### **✅ CORRECT PATTERN**
```python
# ✅ CORRECT: Single unified renderer
class HandsReviewTab(ttk.Frame):
    def __init__(self):
        # Single renderer for all poker table rendering
        self.table_renderer = PokerTableRenderer(
            self,
            intent_handler=self._handle_renderer_intent,
            theme_manager=self.theme
        )
```

#### **🛡️ PREVENTION RULES**
- Single `PokerTableRenderer` for all poker table rendering
- No custom canvas rendering alongside renderer
- No legacy widget mixing with new architecture
- Unified rendering pipeline for consistency

---

## 🛡️ **MANDATORY ENFORCEMENT CHECKLIST**

### **Pre-Development Checklist**
- [ ] **UI Design Review**: Verify UI components are pure renderers
- [ ] **Architecture Review**: Confirm Store/Reducer/Service pattern
- [ ] **Timing Review**: All delays via GameDirector
- [ ] **State Flow Review**: No direct state mutations in UI

### **Code Review Checklist**
- [ ] No business logic in UI components
- [ ] No direct service calls from UI (session_manager, effect_bus, etc.)
- [ ] No timing violations (`self.after`, `threading.Timer`, `time.sleep`)
- [ ] All state changes via Store dispatch
- [ ] Event-driven communication only
- [ ] Single PokerTableRenderer used
- [ ] Theme tokens only (no hardcoded colors)

### **Testing Checklist**
- [ ] UI components can be tested in isolation (no business logic)
- [ ] Service layer can be tested without UI
- [ ] State changes are deterministic via reducers
- [ ] Timing is controlled via GameDirector

---

## 🚨 **IMMEDIATE REJECTION CRITERIA**

**Reject any code that contains:**

```python
# ❌ IMMEDIATE REJECTION TRIGGERS
session_manager.execute_action()     # Business logic in UI
self.after(                         # Timing violation
threading.Timer                     # Threading violation  
self.game_state.pot =              # Direct state mutation
ReusablePokerGameWidget            # Legacy mixing
```

---

## 📚 **REFERENCE IMPLEMENTATIONS**

### **✅ Compliant HandsReviewTab Structure**
```python
class HandsReviewTab(ttk.Frame):
    def __init__(self, parent, services):
        super().__init__(parent)
        self.services = services
        self.store = services.get_app("store")
        self.event_bus = services.get_app("event_bus")
        
        # Single unified renderer
        self.table_renderer = PokerTableRenderer(...)
        
        # Register with event controller
        self.event_bus.publish("hands_review:session_created", {
            "session_id": self.session_id,
            "session_manager": self.session_manager
        })
    
    def _next_action(self):
        """Pure UI dispatch - no business logic"""
        self.store.dispatch({
            "type": "HANDS_REVIEW_NEXT_ACTION",
            "session_id": self.session_id
        })
    
    def dispose(self):
        """Clean disposal with event notification"""
        self.event_bus.publish("hands_review:session_disposed", {
            "session_id": self.session_id
        })
```

### **✅ Compliant Event Controller Structure**
```python
class HandsReviewEventController:
    def __init__(self, event_bus, store, services):
        self.event_bus = event_bus
        self.store = store
        self.services = services
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        self.event_bus.subscribe(
            "hands_review:next_action_requested",
            self._handle_next_action_request
        )
    
    def _handle_next_action_request(self, event_data):
        """Business logic handling - not in UI"""
        session_id = event_data.get('session_id')
        session_manager = self.session_managers.get(session_id)
        
        # Execute business logic
        session_state = session_manager.execute_action()
        
        # Update store with results
        self.store.dispatch({
            "type": "UPDATE_HANDS_REVIEW_STATE",
            "session_id": session_id,
            "state": session_state
        })
```

---

## 🎯 **SUCCESS METRICS**

### **Architecture Compliance Metrics**
- ✅ **0** business logic methods in UI components
- ✅ **0** direct service calls from UI
- ✅ **0** timing violations (`self.after`, etc.)
- ✅ **0** direct state mutations in UI
- ✅ **1** unified rendering system (PokerTableRenderer)

### **Code Quality Metrics**  
- ✅ **100%** event-driven communication
- ✅ **100%** Store/Reducer pattern compliance
- ✅ **100%** GameDirector timing coordination
- ✅ **100%** theme token usage (no hardcoded colors)

---

## 📞 **SUPPORT & ESCALATION**

### **When to Escalate**
- Architecture violation detected in production
- Uncertainty about Store/Reducer pattern implementation
- Complex timing requirements that may need GameDirector enhancement
- Performance issues related to event-driven architecture

### **Escalation Process**
1. Document the specific violation or concern
2. Reference this guide's violation catalog
3. Propose architecture-compliant alternative
4. Request architecture review before implementation

---

**🔒 This guide is MANDATORY for all AI agents working on this codebase. Violations of these patterns compromise system integrity and MUST be prevented.**

```

---

## DESIGN & THEME SYSTEM

### THEME_COLOR_REFERENCE.md

**Path**: `docs/Complete_Theme_Color_Reference_Table_v2.md`

```markdown
# 🎨 Complete Theme Color Reference Table v2
## Token Normalization (Authoritative)

To prevent drift, **dot.notation** is the preferred naming for all tokens. Keep a compatibility map for legacy underscores.

**Preferred:** `bg.primary`, `bg.secondary`, `a11y.focus`  
**Legacy (compat):** `primary_bg` → `bg.primary`, `secondary_bg` → `bg.secondary`

> Components must **not** hardcode colors. Always use ThemeManager tokens.

### Compatibility Map (initial)
| Legacy token | Preferred token |
|---|---|
| `primary_bg` | `bg.primary` |
| `secondary_bg` | `bg.secondary` |
| `player_name` | `text.playerName` |
| `chip_gold` | `chip.gold` |

> Continue extending this table as you migrate; keep both names active during transition.

## Non-Color Tokens (additive)
Define and centralize non-color tokens used throughout the app:

- **Typography**: `font.body`, `font.caption`, `font.display`  
- **Spacing**: `space.xs`, `space.sm`, `space.md`, `space.lg`, `space.xl`  
- **Elevation**: `elev.0`, `elev.1`, `elev.2`, `elev.3`  
- **Radius**: `radius.sm`, `radius.md`, `radius.lg`, `radius.xl`  

## Accessibility (WCAG)
- Minimum contrast: **≥ 4.5:1** for text; **≥ 3:1** for large text and UI glyphs.
- Focus rings use `a11y.focus` and must be visible at all times.
- Tap targets: **≥ 44×44** px.


## All UI Elements & Color Coding Across 11 Professional Themes

> **Last Updated**: Latest luxury theme integration  
> **Total Themes**: 11 (3 Luxury + 8 Professional Casino)  
> **Total Elements**: 50+ core UI components  

---

## 📊 **LUXURY THEME COLLECTION** (LV Noir Series)

### **💎 LV Noir** - *Deep Mahogany & Antique Gold*
| **Category** | **Element** | **Color Code** | **Description** |
|--------------|-------------|----------------|-----------------|
| **Table Surface** | `table.felt` | `#2A120F` | Deep mahogany felt |
| | `table.rail` | `#1B1612` | Dark leather rail |
| | `table.railHighlight` | `#C3A568` | Antique gold highlight |
| | `table.inlay` | `#6B5B3E` | Aged brass inlay |
| | `table.edgeGlow` | `#3B201A` | Subtle edge glow |
| | `table.center` | `#3B201A` | Center accent |
| **Typography** | `text.primary` | `#F3EAD7` | Warm parchment |
| | `text.secondary` | `#C9BFA9` | Secondary text |
| | `text.muted` | `#948B79` | Muted text |
| | `text_gold` | `#C3A568` | Antique gold text |
| **Gold System** | `gold.base` | `#C3A568` | Antique gold |
| | `gold.bright` | `#E8C87B` | Bright gold |
| | `gold.dim` | `#9E8756` | Dim gold |
| **Burgundy System** | `burgundy.base` | `#7E1D1D` | Burgundy base |
| | `burgundy.deep` | `#4A0F12` | Deep burgundy |
| | `burgundy.bright` | `#A22A2A` | Bright burgundy |
| **Backgrounds** | `primary_bg` | `#141110` | Main background |
| | `secondary_bg` | `#2A2622` | Secondary background |
| | `panel.bg` | `#141110` | Panel background |
| | `panel.fg` | `#F3EAD7` | Panel foreground |
| **Pot & Chips** | `pot.badgeBg` | `#3A2D1E` | Pot badge background |
| | `pot.badgeRing` | `#C3A568` | Pot badge ring |
| | `pot.valueText` | `#F7ECD1` | Pot value text |
| | `chip_gold` | `#C3A568` | Gold chips |
| **Player Seats** | `seat.bg.idle` | `#1B1612` | Idle seat |
| | `seat.bg.active` | `#2A2622` | Active seat |
| | `seat.bg.acting` | `#3A2D1E` | Acting seat |
| | `player.name` | `#C9BFA9` | Player names |
| | `player.stack` | `#C3A568` | Stack amounts |
| **Cards** | `board.cardBack` | `#7E1D1D` | Burgundy card backs |
| | `board.cardFaceFg` | `#F3EAD7` | Card face text |
| | `board.border` | `#6B5B3E` | Card borders |
| **Buttons** | `btn.default.bg` | `#1E1A17` | Default button |
| | `btn.hover.bg` | `#2A2521` | Hover state |
| | `btn.active.bg` | `#3A2F24` | Active state |
| **Dealer Button** | `dealer.buttonBg` | `#F1E3B2` | Antique gold |
| | `dealer.buttonFg` | `#3A2D1E` | Dark text |
| | `dealer.buttonBorder` | `#C3A568` | Gold border |

### **🏆 Crimson Monogram** - *Deep Crimson & Bright Gold*
| **Category** | **Element** | **Color Code** | **Description** |
|--------------|-------------|----------------|-----------------|
| **Table Surface** | `table.felt` | `#3B0E11` | Deep crimson felt |
| | `table.rail` | `#1B1612` | Dark leather rail |
| | `table.railHighlight` | `#E8C87B` | Bright gold highlight |
| | `table.edgeGlow` | `#4A1013` | Crimson edge glow |
| **Typography** | `text_gold` | `#E8C87B` | Bright gold text |
| **Burgundy System** | `burgundy.base` | `#A22A2A` | Brighter burgundy |
| | `burgundy.bright` | `#CC3C52` | Bright burgundy |
| **Backgrounds** | `secondary_bg` | `#4A1013` | Crimson background |
| | `panel.border` | `#4A1013` | Crimson borders |
| **Pot & Chips** | `pot.badgeBg` | `#4A1013` | Crimson pot badge |
| | `pot.badgeRing` | `#E8C87B` | Gold badge ring |

### **🌟 Diamond Elite** - *Deep Navy & Platinum*
| **Category** | **Element** | **Color Code** | **Description** |
|--------------|-------------|----------------|-----------------|
| **Table Surface** | `table.felt` | `#0F1A2E` | Deep navy felt |
| | `table.rail` | `#1B1612` | Dark leather rail |
| | `table.railHighlight` | `#E5E4E2` | Platinum highlight |
| | `table.edgeGlow` | `#1A2B4A` | Navy edge glow |
| **Typography** | `text_platinum` | `#E5E4E2` | Platinum text |
| **Platinum System** | `platinum.base` | `#E5E4E2` | Platinum base |
| | `platinum.bright` | `#F5F5F5` | Bright platinum |
| | `platinum.dim` | `#C0C0C0` | Dim platinum |
| **Navy System** | `navy.base` | `#0F1A2E` | Navy base |
| | `navy.deep` | `#0A0F1A` | Deep navy |
| | `navy.bright` | `#1A2B4A` | Bright navy |
| **Backgrounds** | `primary_bg` | `#0A0F1A` | Main background |
| | `secondary_bg` | `#1A2B4A` | Secondary background |
| | `panel.bg` | `#0A0F1A` | Panel background |
| | `panel.fg` | `#E5E4E2` | Panel foreground |
| **Pot & Chips** | `pot.badgeBg` | `#1A2B4A` | Navy pot badge |
| | `pot.badgeRing` | `#E5E4E2` | Platinum badge ring |
| | `pot.valueText` | `#F5F5F5` | Pot value text |
| | `chip_platinum` | `#E5E4E2` | Platinum chips |
| **Player Seats** | `seat.bg.idle` | `#0F1A2E` | Idle seat |
| | `seat.bg.active` | `#1A2B4A` | Active seat |
| | `seat.bg.acting` | `#2A3B5A` | Acting seat |
| | `player.name` | `#C0C0C0` | Player names |
| | `player.stack` | `#E5E4E2` | Stack amounts |
| **Cards** | `board.cardBack` | `#0F1A2E` | Navy card backs |
| | `board.cardFaceFg` | `#E5E4E2` | Card face text |
| | `board.border` | `#1A2B4A` | Card borders |
| **Buttons** | `btn.default.bg` | `#0F1A2E` | Default button |
| | `btn.hover.bg` | `#1A2B4A` | Hover state |
| | `btn.active.bg` | `#2A3B5A` | Active state |
| **Dealer Button** | `dealer.buttonBg` | `#E5E4E2` | Platinum |
| | `dealer.buttonFg` | `#0F1A2E` | Navy text |
| | `dealer.buttonBorder` | `#1A2B4A` | Navy border |

---

## 🎰 **PROFESSIONAL CASINO THEME COLLECTION**

### **🔵 Classic Blue** - *Traditional Casino Blue*
| **Category** | **Element** | **Color Code** | **Description** |
|--------------|-------------|----------------|-----------------|
| **Table Surface** | `table.felt` | `#1E3A8A` | Classic casino blue |
| | `table.rail` | `#1E40AF` | Darker blue rail |
| | `table.railHighlight` | `#3B82F6` | Bright blue highlight |
| | `table.edgeGlow` | `#1E40AF` | Blue edge glow |
| **Typography** | `text.primary` | `#FFFFFF` | White text |
| | `text.secondary` | `#E5E7EB` | Light gray text |
| | `text.accent` | `#3B82F6` | Blue accent text |
| **Backgrounds** | `primary_bg` | `#111827` | Dark background |
| | `secondary_bg` | `#1F2937` | Secondary background |
| | `panel.bg` | `#374151` | Panel background |
| | `panel.fg` | `#FFFFFF` | Panel foreground |
| **Pot & Chips** | `pot.badgeBg` | `#1E3A8A` | Blue pot badge |
| | `pot.badgeRing` | `#3B82F6` | Blue badge ring |
| | `pot.valueText` | `#FFFFFF` | White pot text |
| | `chip_blue` | `#3B82F6` | Blue chips |
| **Player Seats** | `seat.bg.idle` | `#1F2937` | Idle seat |
| | `seat.bg.active` | `#374151` | Active seat |
| | `seat.bg.acting` | `#4B5563` | Acting seat |
| | `player.name` | `#E5E7EB` | Player names |
| | `player.stack` | `#3B82F6` | Stack amounts |
| **Cards** | `board.cardBack` | `#1E3A8A` | Blue card backs |
| | `board.cardFaceFg` | `#FFFFFF` | White card text |
| | `board.border` | `#3B82F6` | Blue card borders |
| **Buttons** | `btn.default.bg` | `#374151` | Default button |
| | `btn.hover.bg` | `#4B5563` | Hover state |
| | `btn.active.bg` | `#6B7280` | Active state |
| **Dealer Button** | `dealer.buttonBg` | `#3B82F6` | Blue |
| | `dealer.buttonFg` | `#FFFFFF` | White text |
| | `dealer.buttonBorder` | `#1E3A8A` | Dark blue border |

### **🟢 Emerald Green** - *Professional Green*
| **Category** | **Element** | **Color Code** | **Description** |
|--------------|-------------|----------------|-----------------|
| **Table Surface** | `table.felt` | `#065F46` | Professional green |
| | `table.rail` | `#047857` | Darker green rail |
| | `table.railHighlight` | `#10B981` | Bright green highlight |
| | `table.edgeGlow` | `#047857` | Green edge glow |
| **Typography** | `text.primary` | `#FFFFFF` | White text |
| | `text.secondary` | `#E5E7EB` | Light gray text |
| | `text.accent` | `#10B981` | Green accent text |
| **Backgrounds** | `primary_bg` | `#111827` | Dark background |
| | `secondary_bg` | `#1F2937` | Secondary background |
| | `panel.bg` | `#374151` | Panel background |
| | `panel.fg` | `#FFFFFF` | Panel foreground |
| **Pot & Chips** | `pot.badgeBg` | `#065F46` | Green pot badge |
| | `pot.badgeRing` | `#10B981` | Green badge ring |
| | `pot.valueText` | `#FFFFFF` | White pot text |
| | `chip_green` | `#10B981` | Green chips |
| **Player Seats** | `seat.bg.idle` | `#1F2937` | Idle seat |
| | `seat.bg.active` | `#374151` | Active seat |
| | `seat.bg.acting` | `#4B5563` | Acting seat |
| | `player.name` | `#E5E7EB` | Player names |
| | `player.stack` | `#10B981` | Stack amounts |
| **Cards** | `board.cardBack` | `#065F46` | Green card backs |
| | `board.cardFaceFg` | `#FFFFFF` | White card text |
| | `board.border` | `#10B981` | Green card borders |
| **Buttons** | `btn.default.bg` | `#374151` | Default button |
| | `btn.hover.bg` | `#4B5563` | Hover state |
| | `btn.active.bg` | `#6B7280` | Active state |
| **Dealer Button** | `dealer.buttonBg` | `#10B981` | Green |
| | `dealer.buttonFg` | `#FFFFFF` | White text |
| | `dealer.buttonBorder` | `#065F46` | Dark green border |

### **🔴 Ruby Red** - *Bold Casino Red*
| **Category** | **Element** | **Color Code** | **Description** |
|--------------|-------------|----------------|-----------------|
| **Table Surface** | `table.felt` | `#7F1D1D` | Bold casino red |
| | `table.rail` | `#991B1B` | Darker red rail |
| | `table.railHighlight` | `#EF4444` | Bright red highlight |
| | `table.edgeGlow` | `#991B1B` | Red edge glow |
| **Typography** | `text.primary` | `#FFFFFF` | White text |
| | `text.secondary` | `#E5E7EB` | Light gray text |
| | `text.accent` | `#EF4444` | Red accent text |
| **Backgrounds** | `primary_bg` | `#111827` | Dark background |
| | `secondary_bg` | `#1F2937` | Secondary background |
| | `panel.bg` | `#374151` | Panel background |
| | `panel.fg` | `#FFFFFF` | Panel foreground |
| **Pot & Chips** | `pot.badgeBg` | `#7F1D1D` | Red pot badge |
| | `pot.badgeRing` | `#EF4444` | Red badge ring |
| | `pot.valueText` | `#FFFFFF` | White pot text |
| | `chip_red` | `#EF4444` | Red chips |
| **Player Seats** | `seat.bg.idle` | `#1F2937` | Idle seat |
| | `seat.bg.active` | `#374151` | Active seat |
| | `seat.bg.acting` | `#4B5563` | Acting seat |
| | `player.name` | `#E5E7EB` | Player names |
| | `player.stack` | `#EF4444` | Stack amounts |
| **Cards** | `board.cardBack` | `#7F1D1D` | Red card backs |
| | `board.cardFaceFg` | `#FFFFFF` | White card text |
| | `board.border` | `#EF4444` | Red card borders |
| **Buttons** | `btn.default.bg` | `#374151` | Default button |
| | `btn.hover.bg` | `#4B5563` | Hover state |
| | `btn.active.bg` | `#6B7280` | Active state |
| **Dealer Button** | `dealer.buttonBg` | `#EF4444` | Red |
| | `dealer.buttonFg` | `#FFFFFF` | White text |
| | `dealer.buttonBorder` | `#7F1D1D` | Dark red border |

### **🟡 Golden Yellow** - *Warm Casino Gold*
| **Category** | **Element** | **Color Code** | **Description** |
|--------------|-------------|----------------|-----------------|
| **Table Surface** | `table.felt` | `#92400E` | Warm casino gold |
| | `table.rail` | `#B45309` | Darker gold rail |
| | `table.railHighlight` | `#F59E0B` | Bright gold highlight |
| | `table.edgeGlow` | `#B45309` | Gold edge glow |
| **Typography** | `text.primary` | `#FFFFFF` | White text |
| | `text.secondary` | `#E5E7EB` | Light gray text |
| | `text.accent` | `#F59E0B` | Gold accent text |
| **Backgrounds** | `primary_bg` | `#111827` | Dark background |
| | `secondary_bg` | `#1F2937` | Secondary background |
| | `panel.bg` | `#374151` | Panel background |
| | `panel.fg` | `#FFFFFF` | Panel foreground |
| **Pot & Chips** | `pot.badgeBg` | `#92400E` | Gold pot badge |
| | `pot.badgeRing` | `#F59E0B` | Gold badge ring |
| | `pot.valueText` | `#FFFFFF` | White pot text |
| | `chip_gold` | `#F59E0B` | Gold chips |
| **Player Seats** | `seat.bg.idle` | `#1F2937` | Idle seat |
| | `seat.bg.active` | `#374151` | Active seat |
| | `seat.bg.acting` | `#4B5563` | Acting seat |
| | `player.name` | `#E5E7EB` | Player names |
| | `player.stack` | `#F59E0B` | Stack amounts |
| **Cards** | `board.cardBack` | `#92400E` | Gold card backs |
| | `board.cardFaceFg` | `#FFFFFF` | White card text |
| | `board.border` | `#F59E0B` | Gold card borders |
| **Buttons** | `btn.default.bg` | `#374151` | Default button |
| | `btn.hover.bg` | `#4B5563` | Hover state |
| | `btn.active.bg` | `#6B7280` | Active state |
| **Dealer Button** | `dealer.buttonBg` | `#F59E0B` | Gold |
| | `dealer.buttonFg` | `#FFFFFF` | White text |
| | `dealer.buttonBorder` | `#92400E` | Dark gold border |

### **🟣 Royal Purple** - *Elegant Casino Purple*
| **Category** | **Element** | **Color Code** | **Description** |
|--------------|-------------|----------------|-----------------|
| **Table Surface** | `table.felt` | `#581C87` | Elegant casino purple |
| | `table.rail` | `#6B21A8` | Darker purple rail |
| | `table.railHighlight` | `#A855F7` | Bright purple highlight |
| | `table.edgeGlow` | `#6B21A8` | Purple edge glow |
| **Typography** | `text.primary` | `#FFFFFF` | White text |
| | `text.secondary` | `#E5E7EB` | Light gray text |
| | `text.accent` | `#A855F7` | Purple accent text |
| **Backgrounds** | `primary_bg` | `#111827` | Dark background |
| | `secondary_bg` | `#1F2937` | Secondary background |
| | `panel.bg` | `#374151` | Panel background |
| | `panel.fg` | `#FFFFFF` | Panel foreground |
| **Pot & Chips** | `pot.badgeBg` | `#581C87` | Purple pot badge |
| | `pot.badgeRing` | `#A855F7` | Purple badge ring |
| | `pot.valueText` | `#FFFFFF` | White pot text |
| | `chip_purple` | `#A855F7` | Purple chips |
| **Player Seats** | `seat.bg.idle` | `#1F2937` | Idle seat |
| | `seat.bg.active` | `#374151` | Active seat |
| | `seat.bg.acting` | `#4B5563` | Acting seat |
| | `player.name` | `#E5E7EB` | Player names |
| | `player.stack` | `#A855F7` | Stack amounts |
| **Cards** | `board.cardBack` | `#581C87` | Purple card backs |
| | `board.cardFaceFg` | `#FFFFFF` | White card text |
| | `board.border` | `#A855F7` | Purple card borders |
| **Buttons** | `btn.default.bg` | `#374151` | Default button |
| | `btn.hover.bg` | `#4B5563` | Hover state |
| | `btn.active.bg` | `#6B7280` | Active state |
| **Dealer Button** | `dealer.buttonBg` | `#A855F7` | Purple |
| | `dealer.buttonFg` | `#FFFFFF` | White text |
| | `dealer.buttonBorder` | `#581C87` | Dark purple border |

### **🟠 Sunset Orange** - *Warm Casino Orange*
| **Category** | **Element** | **Color Code** | **Description** |
|--------------|-------------|----------------|-----------------|
| **Table Surface** | `table.felt` | `#C2410C` | Warm casino orange |
| | `table.rail` | `#EA580C` | Darker orange rail |
| | `table.railHighlight` | `#FB923C` | Bright orange highlight |
| | `table.edgeGlow` | `#EA580C` | Orange edge glow |
| **Typography** | `text.primary` | `#FFFFFF` | White text |
| | `text.secondary` | `#E5E7EB` | Light gray text |
| | `text.accent` | `#FB923C` | Orange accent text |
| **Backgrounds** | `primary_bg` | `#111827` | Dark background |
| | `secondary_bg` | `#1F2937` | Secondary background |
| | `panel.bg` | `#374151` | Panel background |
| | `panel.fg` | `#FFFFFF` | Panel foreground |
| **Pot & Chips** | `pot.badgeBg` | `#C2410C` | Orange pot badge |
| | `pot.badgeRing` | `#FB923C` | Orange badge ring |
| | `pot.valueText` | `#FFFFFF` | White pot text |
| | `chip_orange` | `#FB923C` | Orange chips |
| **Player Seats** | `seat.bg.idle` | `#1F2937` | Idle seat |
| | `seat.bg.active` | `#374151` | Active seat |
| | `seat.bg.acting` | `#4B5563` | Acting seat |
| | `player.name` | `#E5E7EB` | Player names |
| | `player.stack` | `#FB923C` | Stack amounts |
| **Cards** | `board.cardBack` | `#C2410C` | Orange card backs |
| | `board.cardFaceFg` | `#FFFFFF` | White card text |
| | `board.border` | `#FB923C` | Orange card borders |
| **Buttons** | `btn.default.bg` | `#374151` | Default button |
| | `btn.hover.bg` | `#4B5563` | Hover state |
| | `btn.active.bg` | `#6B7280` | Active state |
| **Dealer Button** | `dealer.buttonBg` | `#FB923C` | Orange |
| | `dealer.buttonFg` | `#FFFFFF` | White text |
| | `dealer.buttonBorder` | `#C2410C` | Dark orange border |

### **🔷 Steel Blue** - *Modern Casino Steel*
| **Category** | **Element** | **Color Code** | **Description** |
|--------------|-------------|----------------|-----------------|
| **Table Surface** | `table.felt` | `#1E40AF` | Modern casino steel |
| | `table.rail` | `#1D4ED8` | Darker steel rail |
| | `table.railHighlight` | `#60A5FA` | Bright steel highlight |
| | `table.edgeGlow` | `#1D4ED8` | Steel edge glow |
| **Typography** | `text.primary` | `#FFFFFF` | White text |
| | `text.secondary` | `#E5E7EB` | Light gray text |
| | `text.accent` | `#60A5FA` | Steel accent text |
| **Backgrounds** | `primary_bg` | `#111827` | Dark background |
| | `secondary_bg` | `#1F2937` | Secondary background |
| | `panel.bg` | `#374151` | Panel background |
| | `panel.fg` | `#FFFFFF` | Panel foreground |
| **Pot & Chips** | `pot.badgeBg` | `#1E40AF` | Steel pot badge |
| | `pot.badgeRing` | `#60A5FA` | Steel badge ring |
| | `pot.valueText` | `#FFFFFF` | White pot text |
| | `chip_steel` | `#60A5FA` | Steel chips |
| **Player Seats** | `seat.bg.idle` | `#1F2937` | Idle seat |
| | `seat.bg.active` | `#374151` | Active seat |
| | `seat.bg.acting` | `#4B5563` | Acting seat |
| | `player.name` | `#E5E7EB` | Player names |
| | `player.stack` | `#60A5FA` | Stack amounts |
| **Cards** | `board.cardBack` | `#1E40AF` | Steel card backs |
| | `board.cardFaceFg` | `#FFFFFF` | White card text |
| | `board.border` | `#60A5FA` | Steel card borders |
| **Buttons** | `btn.default.bg` | `#374151` | Default button |
| | `btn.hover.bg` | `#4B5563` | Hover state |
| | `btn.active.bg` | `#6B7280` | Active state |
| **Dealer Button** | `dealer.buttonBg` | `#60A5FA` | Steel |
| | `dealer.buttonFg` | `#FFFFFF` | White text |
| | `dealer.buttonBorder` | `#1E40AF` | Dark steel border |

---

## 🎨 **TOKEN USAGE GUIDELINES**

### **Component Implementation**
```python
# ✅ Correct: Using theme tokens
button.configure(
    bg=theme_manager.get_token('btn.primary.bg'),
    fg=theme_manager.get_token('btn.primary.fg'),
    font=theme_manager.get_token('font.button')
)

# ❌ Incorrect: Hardcoded colors
button.configure(
    bg='#3B82F6',  # Don't hardcode!
    fg='#FFFFFF',
    font=('Arial', 12)
)
```

### **Theme Switching**
```python
def switch_theme(self, theme_name):
    # Load new theme
    self.theme_manager.load_theme(theme_name)
    
    # Re-render all components with new theme
    self._refresh_all_components()
    
    # Update theme selector
    self.theme_selector.set(theme_name)
```

### **Accessibility Compliance**
```python
def validate_contrast(self, bg_color, fg_color):
    """Ensure WCAG 2.1 AA compliance"""
    contrast_ratio = calculate_contrast_ratio(bg_color, fg_color)
    return contrast_ratio >= 4.5  # Minimum for normal text
```

---

## 📋 **MIGRATION CHECKLIST**

### **Phase 1: Token Standardization**
- [ ] Audit all hardcoded colors in components
- [ ] Create compatibility map for legacy tokens
- [ ] Update component implementations to use theme tokens
- [ ] Test theme switching functionality

### **Phase 2: Component Updates**
- [ ] Update Enhanced RPGW components
- [ ] Update session tab components
- [ ] Update button and control components
- [ ] Update text and label components

### **Phase 3: Testing & Validation**
- [ ] Test all themes for visual consistency
- [ ] Validate accessibility compliance
- [ ] Performance testing with theme switching
- [ ] User acceptance testing

---

*This document serves as the authoritative reference for all theme and color usage in the PokerPro Trainer. All components must use theme tokens and comply with accessibility standards.*

```

---

### poker_themes.json

**Path**: `backend/data/poker_themes.json`

```json
{
  "version": "2.1",
  "defaults": {
    "state": {
      "active": {
        "glow": "$accent",
        "shimmer": "$metal",
        "strength": 1.0,
        "period_ms": 2000
      },
      "folded": {
        "desaturate": 0.8,
        "opacity": 0.4
      },
      "winner": {
        "glow": "$metal",
        "shimmer": "$accent",
        "strength": 1.4,
        "period_ms": 1500,
        "particles": true
      },
      "showdown": {
        "spotlight": "#FFFFFF",
        "spotlight_opacity": 0.18,
        "duration_ms": 1500
      },
      "allin": {
        "glow": "$raise",
        "shimmer": "$metal",
        "strength": 1.2,
        "flash_ms": 400
      }
    },
    "selection": {
      "row_bg": "$highlight",
      "row_fg": "$highlight_text"
    },
    "emphasis_bar": {
      "bg_top": "$felt",
      "bg_bottom": "$rail",
      "text": "$emphasis_text",
      "accent_text": "$raise",
      "divider": "$metal",
      "texture": "velvet_8pct"
    },
    "chips": {
      "stack": {
        "face": "$chip_face",
        "edge": "$chip_edge",
        "rim": "$chip_rim",
        "text": "$chip_text"
      },
      "bet": {
        "face": "$bet_face",
        "edge": "$bet_edge",
        "rim": "$bet_rim",
        "text": "$bet_text",
        "glow": "$bet_glow"
      },
      "pot": {
        "face": "$pot_face",
        "edge": "$pot_edge",
        "rim": "$pot_rim",
        "text": "$pot_text",
        "glow": "$pot_glow"
      }
    }
  },
  "themes": [
    {
      "id": "forest-green-pro",
      "name": "Forest Green Professional 🌿",
      "intro": "Classic casino green with dark wood rails—calm, familiar, relentlessly focused. Built on fundamentals and discipline, echoing Doyle Brunson’s steady command under pressure.",
      "persona": "Doyle Brunson",
      "palette": {
        "felt": "#FF0000",
        "rail": "#4A3428",
        "metal": "#C9A34E",
        "accent": "#1DB954",
        "raise": "#B63D3D",
        "call": "#2AA37A",
        "neutral": "#9AA0A6",
        "text": "#EDECEC",
        "highlight": "#D4AF37",
        "highlight_text": "#0B0B0E",
        "emphasis_text": "#F8F3E2",
        "emphasis_bg_top": "#314F3A",
        "emphasis_bg_bottom": "#1E3A28",
        "emphasis_border": "#A88433",
        "emphasis_accent_text": "#D4AF37",
        "chip_face": "#2D5A3D",
        "chip_edge": "#4A3428",
        "chip_rim": "#C9A34E",
        "chip_text": "#F8F7F4",
        "bet_face": "#1DB954",
        "bet_edge": "#4A3428",
        "bet_rim": "#C9A34E",
        "bet_text": "#FFFFFF",
        "bet_glow": "#74E8A3",
        "pot_face": "#E0C98A",
        "pot_edge": "#3A2A20",
        "pot_rim": "#EAD49A",
        "pot_text": "#0B0B0E",
        "pot_glow": "#F1DFAF"
      }
    },
    {
      "id": "velvet-burgundy",
      "name": "Velvet Burgundy 🍷",
      "intro": "Wine-red felt and brass trim; a private salon after midnight—hushed and opulent. Charisma with calculation, channeling Antonio Esfandiari’s flair without sacrificing precision.",
      "persona": "Antonio Esfandiari",
      "palette": {
        "felt": "#4B1C2B",
        "rail": "#3D0F1F",
        "metal": "#C98B5E",
        "accent": "#8C2233",
        "raise": "#B53A44",
        "call": "#2AA37A",
        "neutral": "#A29A90",
        "text": "#F2E9DF",
        "highlight": "#A31D2B",
        "highlight_text": "#F9E7C9",
        "emphasis_text": "#FFEFE3",
        "chip_face": "#4B1C2B",
        "chip_edge": "#3D0F1F",
        "chip_rim": "#C98B5E",
        "chip_text": "#F8F7F4",
        "bet_face": "#8C2233",
        "bet_edge": "#3D0F1F",
        "bet_rim": "#C98B5E",
        "bet_text": "#FFFFFF",
        "bet_glow": "#E37D8C",
        "pot_face": "#E1B78E",
        "pot_edge": "#2B0B14",
        "pot_rim": "#F0CBA0",
        "pot_text": "#0B0B0E",
        "pot_glow": "#F5D8B7",
        "emphasis_bg_top": "#5A1F2F",
        "emphasis_bg_bottom": "#3A0F1F",
        "emphasis_border": "#B97B54",
        "emphasis_accent_text": "#E5B086"
      }
    },
    {
      "id": "emerald-aurora",
      "name": "Emerald Aurora 🌌",
      "intro": "Emerald felt lit by aurora glow—crisp, modern, quietly electric. Analytical brilliance and composure, reflecting Justin Bonomo’s polished tournament edge.",
      "persona": "Justin Bonomo",
      "palette": {
        "felt": "#046D47",
        "rail": "#0C0C0C",
        "metal": "#C9A86A",
        "accent": "#59FFAD",
        "raise": "#B23B43",
        "call": "#32B37A",
        "neutral": "#9CB1A8",
        "text": "#F1F7F4",
        "highlight": "#59FFAD",
        "highlight_text": "#062318",
        "emphasis_text": "#ECFFF7",
        "chip_face": "#046D47",
        "chip_edge": "#0C0C0C",
        "chip_rim": "#C9A86A",
        "chip_text": "#F8F7F4",
        "bet_face": "#59FFAD",
        "bet_edge": "#0C0C0C",
        "bet_rim": "#C9A86A",
        "bet_text": "#06170F",
        "bet_glow": "#A7FFD4",
        "pot_face": "#E3CFA0",
        "pot_edge": "#0A0A0A",
        "pot_rim": "#F0DBAE",
        "pot_text": "#0B0B0E",
        "pot_glow": "#F5E6BE",
        "emphasis_bg_top": "#0D7A55",
        "emphasis_bg_bottom": "#064B35",
        "emphasis_border": "#BFA066",
        "emphasis_accent_text": "#59FFAD"
      }
    },
    {
      "id": "imperial-jade",
      "name": "Imperial Jade 💎",
      "intro": "Deep emerald with antique gold; stately and serene, breathing confidence. Surgical decisions and posture, echoing Stephen Chidwick’s icy precision.",
      "persona": "Stephen Chidwick",
      "palette": {
        "felt": "#0E8044",
        "rail": "#1B1B1B",
        "metal": "#D5C07E",
        "accent": "#166A3E",
        "raise": "#B23B43",
        "call": "#32B37A",
        "neutral": "#9CB1A8",
        "text": "#F9F3DD",
        "highlight": "#00A86B",
        "highlight_text": "#08110D",
        "emphasis_text": "#FAF4DE",
        "chip_face": "#0E8044",
        "chip_edge": "#1B1B1B",
        "chip_rim": "#D5C07E",
        "chip_text": "#F8F7F4",
        "bet_face": "#166A3E",
        "bet_edge": "#1B1B1B",
        "bet_rim": "#D5C07E",
        "bet_text": "#F0FFF8",
        "bet_glow": "#6BDEB0",
        "pot_face": "#E7D8A7",
        "pot_edge": "#141414",
        "pot_rim": "#F1E5BB",
        "pot_text": "#0B0B0E",
        "pot_glow": "#F6EDC7",
        "emphasis_bg_top": "#156F46",
        "emphasis_bg_bottom": "#0B3E2A",
        "emphasis_border": "#C6B06F",
        "emphasis_accent_text": "#D5C07E"
      }
    },
    {
      "id": "ruby-royale",
      "name": "Ruby Royale ❤️‍🔥",
      "intro": "Lustrous ruby felt in black lacquer with gilded edges—brilliant, precise, unmistakable. Controlled aggression and elite poise, mirroring Jason Koon’s disciplined dominance.",
      "persona": "Jason Koon",
      "palette": {
        "felt": "#9B111E",
        "rail": "#0D0D0D",
        "metal": "#FFD700",
        "accent": "#C72C48",
        "raise": "#A41E34",
        "call": "#2AA37A",
        "neutral": "#B79B9B",
        "text": "#FAFAFA",
        "highlight": "#E0115F",
        "highlight_text": "#19070B",
        "emphasis_text": "#FFF7E6",
        "chip_face": "#9B111E",
        "chip_edge": "#0D0D0D",
        "chip_rim": "#FFD700",
        "chip_text": "#FFFFFF",
        "bet_face": "#C72C48",
        "bet_edge": "#0D0D0D",
        "bet_rim": "#FFD700",
        "bet_text": "#FFFFFF",
        "bet_glow": "#FF7A9B",
        "pot_face": "#FFE07A",
        "pot_edge": "#0A0A0A",
        "pot_rim": "#FFE89A",
        "pot_text": "#0B0B0E",
        "pot_glow": "#FFF0B8",
        "emphasis_bg_top": "#B01523",
        "emphasis_bg_bottom": "#6E0F18",
        "emphasis_border": "#E2C64F",
        "emphasis_accent_text": "#FFD700"
      }
    },
    {
      "id": "coral-royale",
      "name": "Coral Royale 🪸",
      "intro": "Warm coral red under soft gold—lively, magnetic, made for bold moves. Big-game charisma with generosity, channeling Alan Keating’s fearless table energy.",
      "persona": "Alan Keating",
      "palette": {
        "felt": "#E34234",
        "rail": "#0F0F0F",
        "metal": "#E4B564",
        "accent": "#FF7F50",
        "raise": "#D64040",
        "call": "#2AA37A",
        "neutral": "#B59C91",
        "text": "#FFF0E6",
        "highlight": "#FF7F50",
        "highlight_text": "#2B120E",
        "emphasis_text": "#FFF3EB",
        "chip_face": "#E34234",
        "chip_edge": "#0F0F0F",
        "chip_rim": "#E4B564",
        "chip_text": "#FFFFFF",
        "bet_face": "#FF7F50",
        "bet_edge": "#0F0F0F",
        "bet_rim": "#E4B564",
        "bet_text": "#2B120E",
        "bet_glow": "#FFC4AE",
        "pot_face": "#F1D39B",
        "pot_edge": "#0D0D0D",
        "pot_rim": "#F6DDB0",
        "pot_text": "#0B0B0E",
        "pot_glow": "#FAE7C9",
        "emphasis_bg_top": "#F15545",
        "emphasis_bg_bottom": "#A92F25",
        "emphasis_border": "#E4B564",
        "emphasis_accent_text": "#75ECC8"
      }
    },
    {
      "id": "golden-dusk",
      "name": "Golden Dusk 🌇",
      "intro": "Burnished amber over dark leather; cinematic nostalgia that never hurries. Veteran reads and closing instinct, reflecting Jason Mercier’s calm endgame edge.",
      "persona": "Jason Mercier",
      "palette": {
        "felt": "#7A4A1F",
        "rail": "#3A1D0D",
        "metal": "#C18F65",
        "accent": "#A3622B",
        "raise": "#B35A3B",
        "call": "#2AA37A",
        "neutral": "#AF9A8A",
        "text": "#F3E3D3",
        "highlight": "#E4B564",
        "highlight_text": "#23160D",
        "emphasis_text": "#FFF3E3",
        "chip_face": "#7A4A1F",
        "chip_edge": "#3A1D0D",
        "chip_rim": "#C18F65",
        "chip_text": "#F8F7F4",
        "bet_face": "#A3622B",
        "bet_edge": "#3A1D0D",
        "bet_rim": "#C18F65",
        "bet_text": "#FFF1E2",
        "bet_glow": "#E8C49E",
        "pot_face": "#E2C39B",
        "pot_edge": "#2C1409",
        "pot_rim": "#EFD2AD",
        "pot_text": "#0B0B0E",
        "pot_glow": "#F5E2C8",
        "emphasis_bg_top": "#8B572A",
        "emphasis_bg_bottom": "#4B2C14",
        "emphasis_border": "#CFA377",
        "emphasis_accent_text": "#E4B564"
      }
    },
    {
      "id": "klimt-royale",
      "name": "Klimt Royale ✨",
      "intro": "Obsidian field with ornamental gold; decadent patterns that shimmer like a gala. Elegant intellect and creative lines, echoing Liv Boeree’s balance of logic and style.",
      "persona": "Liv Boeree",
      "palette": {
        "felt": "#17130E",
        "rail": "#23211B",
        "metal": "#E4C97D",
        "accent": "#166A3E",
        "raise": "#B23B43",
        "call": "#32B37A",
        "neutral": "#A38E6A",
        "text": "#FFF2D9",
        "highlight": "#B87333",
        "highlight_text": "#0D0A07",
        "emphasis_text": "#FFEED0",
        "chip_face": "#17130E",
        "chip_edge": "#23211B",
        "chip_rim": "#E4C97D",
        "chip_text": "#F8F7F4",
        "bet_face": "#166A3E",
        "bet_edge": "#23211B",
        "bet_rim": "#E4C97D",
        "bet_text": "#EFFFF7",
        "bet_glow": "#82D9AE",
        "pot_face": "#EBD79F",
        "pot_edge": "#1A1812",
        "pot_rim": "#F2E2B5",
        "pot_text": "#0B0B0E",
        "pot_glow": "#F7EDC9",
        "emphasis_bg_top": "#221C12",
        "emphasis_bg_bottom": "#130F09",
        "emphasis_border": "#E4C97D",
        "emphasis_accent_text": "#B87333"
      }
    },
    {
      "id": "deco-luxe",
      "name": "Deco Luxe 🏛️",
      "intro": "Champagne geometry on jet black—sleek Art-Deco lines and effortless poise. Thoughtful innovation and restraint, channeling Phil Galfond’s cerebral mastery.",
      "persona": "Phil Galfond",
      "palette": {
        "felt": "#1B1E2B",
        "rail": "#111111",
        "metal": "#D6C08F",
        "accent": "#1A3E34",
        "raise": "#5B1922",
        "call": "#2AA37A",
        "neutral": "#9B9486",
        "text": "#F8F4EA",
        "highlight": "#E1B382",
        "highlight_text": "#0E0C09",
        "emphasis_text": "#F6EFDF",
        "chip_face": "#1B1E2B",
        "chip_edge": "#111111",
        "chip_rim": "#D6C08F",
        "chip_text": "#F8F7F4",
        "bet_face": "#1A3E34",
        "bet_edge": "#111111",
        "bet_rim": "#D6C08F",
        "bet_text": "#E8FFF6",
        "bet_glow": "#8EC9B6",
        "pot_face": "#E7D7AF",
        "pot_edge": "#0F0F0F",
        "pot_rim": "#F0E2BF",
        "pot_text": "#0B0B0E",
        "pot_glow": "#F6ECCD",
        "emphasis_bg_top": "#222532",
        "emphasis_bg_bottom": "#141720",
        "emphasis_border": "#D6C08F",
        "emphasis_accent_text": "#E1B382"
      }
    },
    {
      "id": "oceanic-aqua",
      "name": "Oceanic Aqua 🌊",
      "intro": "Midnight teal with bright aqua spray—refreshing, steady, quietly modern. Patience and clarity in deep waters, reflecting Erik Seidel’s timeless control.",
      "persona": "Erik Seidel",
      "palette": {
        "felt": "#126E82",
        "rail": "#0D1B2A",
        "metal": "#B7C1C8",
        "accent": "#4EEAFF",
        "raise": "#ABCE00",
        "call": "#57C2B6",
        "neutral": "#9DB3C4",
        "text": "#F5F7FA",
        "highlight": "#4EEAFF",
        "highlight_text": "#071018",
        "emphasis_text": "#00FAB7",
        "chip_face": "#126E82",
        "chip_edge": "#0D1B2A",
        "chip_rim": "#B7C1C8",
        "chip_text": "#F8F7F4",
        "bet_face": "#4EEAFF",
        "bet_edge": "#0D1B2A",
        "bet_rim": "#B7C1C8",
        "bet_text": "#06222A",
        "bet_glow": "#A4F6FF",
        "pot_face": "#D6E2EA",
        "pot_edge": "#0B1723",
        "pot_rim": "#E3EDF3",
        "pot_text": "#0B0B0E",
        "pot_glow": "#EFF6FA",
        "emphasis_bg_top": "#177C93",
        "emphasis_bg_bottom": "#0A4153",
        "emphasis_border": "#B7C1C8",
        "emphasis_accent_text": "#D9B4F9"
      }
    },
    {
      "id": "royal-sapphire",
      "name": "Royal Sapphire 🔷",
      "intro": "Jewel-blue confidence with crisp trim—bright, polished, commanding. Relentless precision and tournament steel, capturing Adrián Mateos’s clinical edge.",
      "persona": "Adrián Mateos",
      "palette": {
        "felt": "#0D3B66",
        "rail": "#161616",
        "metal": "#C7D3E0",
        "accent": "#2656D9",
        "raise": "#6C4AB6",
        "call": "#57C2B6",
        "neutral": "#9AB1CF",
        "text": "#F2F6FC",
        "highlight": "#1E90FF",
        "highlight_text": "#061224",
        "emphasis_text": "#EEF6FF",
        "chip_face": "#0D3B66",
        "chip_edge": "#161616",
        "chip_rim": "#C7D3E0",
        "chip_text": "#F8F7F4",
        "bet_face": "#2656D9",
        "bet_edge": "#161616",
        "bet_rim": "#C7D3E0",
        "bet_text": "#E9EEFF",
        "bet_glow": "#8FB1FF",
        "pot_face": "#DEE7EF",
        "pot_edge": "#131313",
        "pot_rim": "#EAF1F6",
        "pot_text": "#0B0B0E",
        "pot_glow": "#F4F8FB",
        "emphasis_bg_top": "#14467B",
        "emphasis_bg_bottom": "#0B2746",
        "emphasis_border": "#C7D3E0",
        "emphasis_accent_text": "#A8C7FF"
      }
    },
    {
      "id": "monet-twilight",
      "name": "Monet Twilight 🎨",
      "intro": "Navy-violet felt with misted glow—soft reflections, poetic and nocturnal. Grace under variance and stoic poise, echoing Patrik Antonius’s midnight composure.",
      "persona": "Patrik Antonius",
      "palette": {
        "felt": "#2A2D64",
        "rail": "#1F1F1B",
        "metal": "#C8BEDF",
        "accent": "#B7A6D0",
        "raise": "#B63D3D",
        "call": "#2AA37A",
        "neutral": "#8EA6B5",
        "text": "#F5F7FA",
        "highlight": "#B7A6D0",
        "highlight_text": "#0E0E15",
        "emphasis_text": "#F2EEFB",
        "chip_face": "#2A2D64",
        "chip_edge": "#1F1F1B",
        "chip_rim": "#C8BEDF",
        "chip_text": "#F8F7F4",
        "bet_face": "#B7A6D0",
        "bet_edge": "#1F1F1B",
        "bet_rim": "#C8BEDF",
        "bet_text": "#15141B",
        "bet_glow": "#E0D9F0",
        "pot_face": "#E6E1F1",
        "pot_edge": "#191916",
        "pot_rim": "#EEEAF6",
        "pot_text": "#0B0B0E",
        "pot_glow": "#F6F3FA",
        "emphasis_bg_top": "#2F326E",
        "emphasis_bg_bottom": "#1B1E44",
        "emphasis_border": "#C8BEDF",
        "emphasis_accent_text": "#E6EF75"
      }
    },
    {
      "id": "caravaggio-sepia-noir",
      "name": "Caravaggio Sepia Noir 🕯️",
      "intro": "Candlelit sepia over deep shadow—drama, heat, fearless contrasts. Audacious pressure and brinkmanship, mirroring Tom Dwan’s fearless lines.",
      "persona": "Tom Dwan",
      "palette": {
        "felt": "#2A1F1A",
        "rail": "#101010",
        "metal": "#D4A373",
        "accent": "#9E0F28",
        "raise": "#B3122E",
        "call": "#2AA37A",
        "neutral": "#9C8F7A",
        "text": "#FFF7E6",
        "highlight": "#EAD6B7",
        "highlight_text": "#1B130B",
        "emphasis_text": "#FFF6E5",
        "chip_face": "#2A1F1A",
        "chip_edge": "#101010",
        "chip_rim": "#D4A373",
        "chip_text": "#F8F7F4",
        "bet_face": "#9E0F28",
        "bet_edge": "#101010",
        "bet_rim": "#D4A373",
        "bet_text": "#FFEFF2",
        "bet_glow": "#F29BAA",
        "pot_face": "#E9D0AA",
        "pot_edge": "#0E0E0E",
        "pot_rim": "#F2DBB9",
        "pot_text": "#0B0B0E",
        "pot_glow": "#F7E8CD",
        "emphasis_bg_top": "#3A2A22",
        "emphasis_bg_bottom": "#1F1612",
        "emphasis_border": "#D4A373",
        "emphasis_accent_text": "#EEB200"
      }
    },
    {
      "id": "stealth-graphite-steel",
      "name": "Stealth Graphite Steel 🖤",
      "intro": "Matte blacks and brushed steel; silent, aerodynamic focus. Unreadable calm and surgical timing, channeling Phil Ivey’s cold precision.",
      "persona": "Phil Ivey",
      "palette": {
        "felt": "#2E2E2E",
        "rail": "#444444",
        "metal": "#8D8D8D",
        "accent": "#00D4FF",
        "raise": "#9E3B49",
        "call": "#57C2B6",
        "neutral": "#8E9196",
        "text": "#E6E7EA",
        "highlight": "#00D4FF",
        "highlight_text": "#041014",
        "emphasis_text": "#F3F4F6",
        "chip_face": "#2E2E2E",
        "chip_edge": "#444444",
        "chip_rim": "#8D8D8D",
        "chip_text": "#F8F7F4",
        "bet_face": "#00D4FF",
        "bet_edge": "#444444",
        "bet_rim": "#8D8D8D",
        "bet_text": "#031418",
        "bet_glow": "#89F0FF",
        "pot_face": "#D9D9D9",
        "pot_edge": "#3A3A3A",
        "pot_rim": "#E6E6E6",
        "pot_text": "#0B0B0E",
        "pot_glow": "#F2F2F2",
        "emphasis_bg_top": "#3A3A3A",
        "emphasis_bg_bottom": "#242424",
        "emphasis_border": "#8D8D8D",
        "emphasis_accent_text": "#9BE3FF"
      }
    },
    {
      "id": "sunset-mirage",
      "name": "Sunset Mirage 🌅",
      "intro": "Amber to violet across the felt—the warmth of desert dusk under velvet lights. Live-read mastery and table conversation, reflecting Daniel Negreanu’s friendly edge.",
      "persona": "Daniel Negreanu",
      "palette": {
        "felt": "#8C1C13",
        "rail": "#2B1B0E",
        "metal": "#E6B87A",
        "accent": "#FF9E57",
        "raise": "#C85C5C",
        "call": "#2AA37A",
        "neutral": "#A68C7A",
        "text": "#F7E7D6",
        "highlight": "#FF9E57",
        "highlight_text": "#2B160E",
        "emphasis_text": "#FFECDD",
        "chip_face": "#8C1C13",
        "chip_edge": "#2B1B0E",
        "chip_rim": "#E6B87A",
        "chip_text": "#F8F7F4",
        "bet_face": "#FF9E57",
        "bet_edge": "#2B1B0E",
        "bet_rim": "#E6B87A",
        "bet_text": "#2B160E",
        "bet_glow": "#FFD1AE",
        "pot_face": "#F1D7AF",
        "pot_edge": "#24170D",
        "pot_rim": "#F7E2C3",
        "pot_text": "#0B0B0E",
        "pot_glow": "#FBEBD3",
        "emphasis_bg_top": "#9B2A20",
        "emphasis_bg_bottom": "#5A1912",
        "emphasis_border": "#E6B87A",
        "emphasis_accent_text": "#FFC499"
      }
    },
    {
      "id": "cyber-neon",
      "name": "Cyber Neon ⚡",
      "intro": "Electric teals and magentas on charcoal—arcade energy for fast grinders. Hyper-focused volume and fearless optimization, channeling Fedor Holz's modern engine.",
      "persona": "Fedor Holz",
      "palette": {
        "felt": "#0A0D10",
        "rail": "#1A1D23",
        "metal": "#00FFFF",
        "accent": "#FF00FF",
        "raise": "#FF0080",
        "call": "#00FF80",
        "neutral": "#808080",
        "text": "#E0E0E0",
        "highlight": "#00FFFF",
        "highlight_text": "#000000",
        "emphasis_text": "#EAF8FF",
        "emphasis_bg_top": "#141417",
        "emphasis_bg_bottom": "#0B0B0D",
        "emphasis_border": "#9BE3FF",
        "emphasis_accent_text": "#FF79F6"
      }
    }
  ]
}
```

---

### theme_tokens.json

**Path**: `backend/ui/theme_tokens.json`

```json

```

---

## MVU IMPLEMENTATION - CORE

### mvu_types.py

**Path**: `backend/ui/mvu/types.py`

```python
"""
MVU (Model-View-Update) Architecture Types
Based on PokerPro UI Implementation Handbook v2
"""

from dataclasses import dataclass
from typing import Literal, Optional, Dict, List, Set, Any, Protocol, Callable, FrozenSet, Mapping
from abc import ABC, abstractmethod
from functools import cached_property


# ============================================================================
# CORE MODEL - FIXED WITH PROPER IMMUTABILITY
# ============================================================================

# Helper types for immutable collections
ImmutableSeats = Mapping[int, "SeatState"]
ImmutableStacks = Mapping[int, int]

@dataclass(frozen=True, slots=True)
class SeatState:
    """State for a single seat at the poker table - FULLY IMMUTABLE"""
    player_uid: str
    name: str
    stack: int
    chips_in_front: int  # Current bet amount
    folded: bool
    all_in: bool
    cards: tuple[str, ...]  # Hole cards (visibility rules applied) - immutable tuple
    position: int
    acting: bool = False
    
    def __eq__(self, other):
        """Explicit equality for reliability"""
        if not isinstance(other, SeatState):
            return False
        return (
            self.player_uid == other.player_uid and
            self.name == other.name and
            self.stack == other.stack and
            self.chips_in_front == other.chips_in_front and
            self.folded == other.folded and
            self.all_in == other.all_in and
            self.cards == other.cards and
            self.position == other.position and
            self.acting == other.acting
        )
    
    def __hash__(self):
        """Consistent hash for frozen dataclass"""
        return hash((
            self.player_uid,
            self.name, 
            self.stack,
            self.chips_in_front,
            self.folded,
            self.all_in,
            self.cards,  # Already a tuple
            self.position,
            self.acting
        ))


@dataclass(frozen=True)
class Action:
    """Represents a poker action"""
    seat: int
    action: str  # "CHECK", "CALL", "BET", "RAISE", "FOLD"
    amount: Optional[int] = None
    street: str = "PREFLOP"


@dataclass(frozen=True)
class GtoHint:
    """GTO strategy hint"""
    action: str
    frequency: float
    reasoning: str


@dataclass(frozen=True)
class Banner:
    """UI banner/message"""
    text: str
    type: Literal["info", "warning", "error", "success"]
    duration_ms: int = 3000


@dataclass(frozen=True, slots=True)
class Model:
    """
    Canonical Model - FIXED with proper immutability
    Single source of truth that describes the complete state
    """
    # Game State - using immutable types
    hand_id: str
    street: Literal["PREFLOP", "FLOP", "TURN", "RIVER", "SHOWDOWN", "DONE"]
    to_act_seat: Optional[int]
    stacks: ImmutableStacks  # Changed from Dict to Mapping
    pot: int
    board: tuple[str, ...]  # ("As", "Kd", "7h", ...) - immutable tuple
    seats: ImmutableSeats  # Changed from Dict to Mapping
    legal_actions: FrozenSet[str]  # Changed from Set to frozenset
    last_action: Optional[Action]
    
    # Session Configuration
    session_mode: Literal["PRACTICE", "GTO", "REVIEW"]
    autoplay_on: bool
    step_delay_ms: int
    waiting_for: Literal["HUMAN_DECISION", "BOT_DECISION", "ANIMATION", "NONE"]
    
    # Review-specific
    review_cursor: int
    review_len: int
    review_paused: bool
    
    # UI State
    gto_hint: Optional[GtoHint]
    banners: tuple[Banner, ...]
    theme_id: str
    tx_id: int  # Animation token
    
    @classmethod
    def initial(cls, session_mode: Literal["PRACTICE", "GTO", "REVIEW"] = "REVIEW") -> "Model":
        """Create initial model state with immutable collections"""
        return cls(
            hand_id="",
            street="PREFLOP",
            to_act_seat=None,
            stacks={},  # Will be converted to immutable in update
            pot=0,
            board=(),
            seats={},  # Will be converted to immutable in update
            legal_actions=frozenset(),
            last_action=None,
            session_mode=session_mode,
            autoplay_on=False,
            step_delay_ms=1000,
            waiting_for="NONE",
            review_cursor=0,
            review_len=0,
            review_paused=False,
            gto_hint=None,
            banners=(),
            theme_id="forest-green-pro",
            tx_id=0
        )
    
    def __eq__(self, other):
        """Deep equality check for Model"""
        if not isinstance(other, Model):
            return False
        
        # Compare all fields explicitly
        return (
            self.hand_id == other.hand_id and
            self.street == other.street and
            self.to_act_seat == other.to_act_seat and
            dict(self.stacks) == dict(other.stacks) and
            self.pot == other.pot and
            self.board == other.board and
            dict(self.seats) == dict(other.seats) and
            self.legal_actions == other.legal_actions and
            self.last_action == other.last_action and
            self.session_mode == other.session_mode and
            self.autoplay_on == other.autoplay_on and
            self.step_delay_ms == other.step_delay_ms and
            self.waiting_for == other.waiting_for and
            self.review_cursor == other.review_cursor and
            self.review_len == other.review_len and
            self.review_paused == other.review_paused and
            self.gto_hint == other.gto_hint and
            self.banners == other.banners and
            self.theme_id == other.theme_id and
            self.tx_id == other.tx_id
        )


# ============================================================================
# MESSAGES (Facts)
# ============================================================================

class Msg(ABC):
    """Base message type"""
    pass


class NextPressed(Msg):
    """User pressed Next button"""
    pass


@dataclass
class AutoPlayToggled(Msg):
    """User toggled auto-play"""
    on: bool


@dataclass
class TimerTick(Msg):
    """Timer tick event"""
    now_ms: int


@dataclass
class UserChose(Msg):
    """Human user made a decision"""
    action: str
    amount: Optional[int] = None


@dataclass
class DecisionRequested(Msg):
    """System requests decision from a seat"""
    seat: int


@dataclass
class DecisionReady(Msg):
    """Decision is ready (from bot or async process)"""
    seat: int
    action: str
    amount: Optional[int]


@dataclass
class AppliedAction(Msg):
    """Action was applied to PPSM"""
    seat: int
    action: str
    amount: Optional[int]


@dataclass
class StreetAdvanced(Msg):
    """Street changed (PREFLOP -> FLOP, etc.)"""
    street: str


@dataclass
class HandFinished(Msg):
    """Hand completed"""
    winners: List[int]
    payouts: Dict[int, int]


@dataclass
class AnimationFinished(Msg):
    """Animation completed"""
    token: int


@dataclass
class ReviewSeek(Msg):
    """Seek to specific position in review"""
    index: int


class ReviewPlayStep(Msg):
    """Play next step in review"""
    pass


@dataclass
class LoadHand(Msg):
    """Load a new hand for review/practice"""
    hand_data: Dict[str, Any]


@dataclass
class ThemeChanged(Msg):
    """Theme was changed"""
    theme_id: str


# ============================================================================
# COMMANDS (Effects)
# ============================================================================

class Cmd(ABC):
    """Base command type"""
    pass


@dataclass
class PlaySound(Cmd):
    """Play a sound effect"""
    name: str


@dataclass
class Speak(Cmd):
    """Text-to-speech announcement"""
    text: str


@dataclass
class Animate(Cmd):
    """Trigger animation"""
    name: str
    payload: Dict[str, Any]
    token: int


@dataclass
class AskDriverForDecision(Cmd):
    """Ask session driver for decision"""
    seat: int


@dataclass
class ApplyPPSM(Cmd):
    """Apply action to Pure Poker State Machine"""
    seat: int
    action: str
    amount: Optional[int]


@dataclass
class ScheduleTimer(Cmd):
    """Schedule a delayed message"""
    delay_ms: int
    msg: Msg


@dataclass
class PublishEvent(Cmd):
    """Publish event to EventBus"""
    topic: str
    payload: Dict[str, Any]



@dataclass
class GetReviewEvent(Cmd):
    """Get and dispatch review event at index"""
    index: int


# ============================================================================
# SESSION DRIVER PROTOCOL
# ============================================================================

class SessionDriver(Protocol):
    """Protocol for session-specific behavior"""
    
    @abstractmethod
    def decide(self, model: Model, seat: int, callback: Callable[[DecisionReady], None]) -> None:
        """Make decision for given seat (async, calls callback when ready)"""
        pass
    
    @abstractmethod
    def review_event_at(self, index: int) -> Optional[Msg]:
        """Get review event at index (REVIEW mode only)"""
        pass
    
    @abstractmethod
    def review_length(self) -> int:
        """Get total review length (REVIEW mode only)"""
        pass


# ============================================================================
# TABLE RENDERER PROPS
# ============================================================================

@dataclass(frozen=True, slots=True)
class TableRendererProps:
    """Props derived from Model - FIXED with proper immutability"""
    # Table state - using immutable types
    seats: ImmutableSeats
    board: tuple[str, ...]
    pot: int
    to_act_seat: Optional[int]
    legal_actions: FrozenSet[str]
    
    # UI state
    banners: tuple[Banner, ...]
    theme_id: str
    autoplay_on: bool
    waiting_for: str
    
    # Review state
    review_cursor: int
    review_len: int
    review_paused: bool
    session_mode: str
    
    # Hints
    gto_hint: Optional[GtoHint]
    
    def __eq__(self, other):
        """Deep equality check that actually works"""
        if not isinstance(other, TableRendererProps):
            return False
        
        # Compare all fields including nested structures
        return (
            dict(self.seats) == dict(other.seats) and
            self.board == other.board and
            self.pot == other.pot and
            self.to_act_seat == other.to_act_seat and
            self.legal_actions == other.legal_actions and
            self.banners == other.banners and
            self.theme_id == other.theme_id and
            self.autoplay_on == other.autoplay_on and
            self.waiting_for == other.waiting_for and
            self.review_cursor == other.review_cursor and
            self.review_len == other.review_len and
            self.review_paused == other.review_paused and
            self.session_mode == other.session_mode and
            self.gto_hint == other.gto_hint
        )
    
    def __hash__(self):
        """Make props hashable for caching"""
        return hash((
            tuple(sorted(self.seats.items())),
            self.board,
            self.pot,
            self.to_act_seat,
            self.legal_actions,
            self.banners,
            self.theme_id,
            self.autoplay_on,
            self.waiting_for,
            self.review_cursor,
            self.review_len,
            self.review_paused,
            self.session_mode,
            self.gto_hint
        ))
    
    @classmethod
    def from_model(cls, model: Model) -> "TableRendererProps":
        """Derive props from model"""
        return cls(
            seats=model.seats,
            board=model.board,
            pot=model.pot,
            to_act_seat=model.to_act_seat,
            legal_actions=model.legal_actions,
            banners=model.banners,
            theme_id=model.theme_id,
            autoplay_on=model.autoplay_on,
            waiting_for=model.waiting_for,
            review_cursor=model.review_cursor,
            review_len=model.review_len,
            review_paused=model.review_paused,
            session_mode=model.session_mode,
            gto_hint=model.gto_hint
        )


# ============================================================================
# INTENT HANDLER PROTOCOL
# ============================================================================

class IntentHandler(Protocol):
    """Protocol for handling user intents from the UI"""
    
    def on_click_next(self) -> None:
        """Next button clicked"""
        pass
    
    def on_toggle_autoplay(self, on: bool) -> None:
        """Auto-play toggled"""
        pass
    
    def on_action_btn(self, action: str, amount: Optional[int] = None) -> None:
        """Action button clicked"""
        pass
    
    def on_seek(self, index: int) -> None:
        """Review seek"""
        pass
    
    def on_request_hint(self) -> None:
        """GTO hint requested"""
        pass

```

---

### mvu_update.py

**Path**: `backend/ui/mvu/update.py`

```python
"""
MVU Update Function - Pure reducers for poker table state
Based on PokerPro UI Implementation Handbook v2
"""

from typing import Tuple, List, Optional
from dataclasses import replace

from .types import (
    Model, Msg, Cmd, SeatState, Action,
    NextPressed, AutoPlayToggled, TimerTick, UserChose,
    DecisionReady, AppliedAction, StreetAdvanced, HandFinished, AnimationFinished,
    ReviewSeek, ReviewPlayStep, LoadHand, ThemeChanged,
    PlaySound, Speak, Animate, AskDriverForDecision, ApplyPPSM,
    ScheduleTimer, GetReviewEvent
)


def update(model: Model, msg: Msg) -> Tuple[Model, List[Cmd]]:
    """
    Pure update function - computes (Model', Cmds) from (Model, Msg)
    No I/O operations allowed inside reducers.
    """
    if isinstance(msg, NextPressed):
        return next_pressed_reducer(model)
    
    if isinstance(msg, AutoPlayToggled):
        return replace(model, autoplay_on=msg.on), []
    
    if isinstance(msg, TimerTick):
        return on_timer_tick(model, msg)
    
    if isinstance(msg, UserChose):
        return apply_decision(model, model.to_act_seat, msg.action, msg.amount)
    
    if isinstance(msg, DecisionReady):
        return apply_decision(model, msg.seat, msg.action, msg.amount)
    
    if isinstance(msg, AppliedAction):
        return on_applied_action(model, msg)
    
    if isinstance(msg, StreetAdvanced):
        return on_street_advanced(model, msg)
    
    if isinstance(msg, HandFinished):
        return on_hand_finished(model, msg)
    
    if isinstance(msg, AnimationFinished):
        return on_animation_finished(model, msg)
    
    if isinstance(msg, ReviewSeek):
        return rebuild_state_to(model, msg.index)
    
    if isinstance(msg, ReviewPlayStep):
        return play_review_step(model)
    
    if isinstance(msg, LoadHand):
        return load_hand(model, msg)
    
    if isinstance(msg, ThemeChanged):
        return replace(model, theme_id=msg.theme_id), []
    
    # Unknown message - no change
    return model, []


# ============================================================================
# KEY REDUCERS
# ============================================================================

def next_pressed_reducer(model: Model) -> Tuple[Model, List[Cmd]]:
    """Handle Next button press based on current state"""
    
    print(f"🔘 Next pressed - State: waiting_for={model.waiting_for}, to_act_seat={model.to_act_seat}, mode={model.session_mode}, cursor={model.review_cursor}/{model.review_len}")
    
    # If waiting for human decision, Next does nothing
    if model.waiting_for == "HUMAN_DECISION":
        print("⏸️ Next pressed but waiting for human decision")
        return model, []
    
    # If waiting for bot decision, ask driver
    if model.waiting_for == "BOT_DECISION" and model.to_act_seat is not None:
        print(f"🤖 Next pressed - asking driver for decision for seat {model.to_act_seat}")
        new_model = replace(model, waiting_for="NONE")
        return new_model, [AskDriverForDecision(model.to_act_seat)]
    
    # If waiting for animation, Next does nothing
    if model.waiting_for == "ANIMATION":
        print("🎬 Next pressed but waiting for animation")
        return model, []
    
    # If no one to act, continue game flow (or advance review)
    if model.to_act_seat is None:
        if model.session_mode == "REVIEW":
            print("📖 Next pressed - no one to act in REVIEW, advancing review")
            return model, [ScheduleTimer(0, ReviewPlayStep())]
        else:
            print("⏭️ Next pressed - no one to act, continuing game flow")
            return model, [ApplyPPSM(seat=-1, action="CONTINUE", amount=None)]
    
    # Someone needs to act
    if model.session_mode == "REVIEW":
        # In review mode, all actions are pre-recorded, so advance review
        print(f"📖 Next pressed in REVIEW mode with to_act_seat={model.to_act_seat} - advancing review")
        return model, [ScheduleTimer(0, ReviewPlayStep())]
    
    # If autoplay is on and current seat is bot, ask for decision
    if model.autoplay_on and seat_is_bot(model, model.to_act_seat):
        print(f"🤖 Next pressed - autoplay bot decision for seat {model.to_act_seat}")
        new_model = replace(model, waiting_for="BOT_DECISION")
        return new_model, [AskDriverForDecision(model.to_act_seat)]
    
    print("❓ Next pressed - no action taken")
    return model, []


def apply_decision(model: Model, seat: Optional[int], action: str, amount: Optional[int]) -> Tuple[Model, List[Cmd]]:
    """Apply a poker decision (from human or bot)"""
    
    # Validate decision
    if seat is None or seat != model.to_act_seat:
        return model, []
    
    if action not in model.legal_actions:
        return model, []
    
    # Generate new transaction ID for animation
    tx = model.tx_id + 1
    
    # Create commands for effects
    cmds = [
        PlaySound(action.lower()),
        Speak(action.capitalize()),
    ]
    
    # Add appropriate animation
    if action in {"BET", "RAISE", "CALL"}:
        cmds.append(Animate("chips_to_pot", {"seat": seat, "amount": amount or 0}, token=tx))
    else:
        cmds.append(Animate("minor_flash", {"seat": seat}, token=tx))
    
    # Apply to PPSM
    cmds.append(ApplyPPSM(seat, action, amount))
    
    # In REVIEW mode, skip animation waiting
    if model.session_mode == "REVIEW":
        new_model = replace(
            model,
            tx_id=tx,
            waiting_for="NONE",
            last_action=Action(seat=seat, action=action, amount=amount, street=model.street)
        )
        # Auto-complete animation immediately
        cmds.append(ScheduleTimer(0, AnimationFinished(token=tx)))
    else:
        # Update model to wait for animation
        new_model = replace(
            model,
            tx_id=tx,
            waiting_for="ANIMATION",
            last_action=Action(seat=seat, action=action, amount=amount, street=model.street)
        )
    
    return new_model, cmds


def on_applied_action(model: Model, msg: AppliedAction) -> Tuple[Model, List[Cmd]]:
    """Handle action applied to PPSM - update from PPSM snapshot"""
    
    # This would typically get updated state from PPSM
    # For now, we'll simulate the state update
    new_model = apply_ppsm_snapshot(model, msg)
    cmds = []
    
    # In REVIEW mode, all actions are pre-recorded, so never wait for decisions
    if model.session_mode == "REVIEW":
        # Always ready for next review step
        new_model = replace(new_model, waiting_for="NONE")
    else:
        # Determine next action for live play
        if new_model.to_act_seat is not None:
            if seat_is_human(new_model, new_model.to_act_seat):
                new_model = replace(new_model, waiting_for="HUMAN_DECISION")
            else:
                new_model = replace(new_model, waiting_for="BOT_DECISION")
                if new_model.autoplay_on:
                    cmds.append(AskDriverForDecision(new_model.to_act_seat))
        else:
            # No one to act - schedule continuation
            cmds.append(ScheduleTimer(new_model.step_delay_ms, NextPressed()))
    

    return new_model, cmds


def on_street_advanced(model: Model, msg: StreetAdvanced) -> Tuple[Model, List[Cmd]]:
    """Handle street advancement (PREFLOP -> FLOP, etc.)"""
    
    tx = model.tx_id + 1
    cmds = [
        Animate("reveal_board", {"street": msg.street}, token=tx),
        PlaySound("deal")
    ]
    
    # In REVIEW mode, skip animation waiting
    if model.session_mode == "REVIEW":
        new_model = replace(
            model,
            street=msg.street,
            tx_id=tx,
            waiting_for="NONE"
        )
        # Auto-complete animation immediately
        cmds.append(ScheduleTimer(0, AnimationFinished(token=tx)))
    else:
        new_model = replace(
            model,
            street=msg.street,
            tx_id=tx,
            waiting_for="ANIMATION"
        )
    
    return new_model, cmds


def on_hand_finished(model: Model, msg: HandFinished) -> Tuple[Model, List[Cmd]]:
    """Handle hand completion"""
    
    tx = model.tx_id + 1
    cmds = [
        Animate("pot_to_winners", {"payouts": msg.payouts}, token=tx),
        PlaySound("win")
    ]
    
    # In REVIEW mode, skip animation waiting
    if model.session_mode == "REVIEW":
        new_model = replace(
            model,
            waiting_for="NONE",
            tx_id=tx,
            street="DONE"
        )
        # Auto-complete animation and schedule next step
        cmds.append(ScheduleTimer(0, AnimationFinished(token=tx)))
        cmds.append(ScheduleTimer(model.step_delay_ms, ReviewPlayStep()))
    else:
        new_model = replace(
            model,
            waiting_for="ANIMATION",
            tx_id=tx,
            street="DONE"
        )
        # Schedule next action for live play
        cmds.append(ScheduleTimer(model.step_delay_ms, NextPressed()))
    
    return new_model, cmds


def on_animation_finished(model: Model, msg: AnimationFinished) -> Tuple[Model, List[Cmd]]:
    """Handle animation completion"""
    
    # Only process if this is the current animation
    if msg.token != model.tx_id:
        return model, []
    
    # Clear waiting state
    new_model = replace(model, waiting_for="NONE")
    
    # Trigger next action if needed
    cmds = []
    if model.autoplay_on and new_model.to_act_seat is not None:
        if seat_is_bot(new_model, new_model.to_act_seat):
            new_model = replace(new_model, waiting_for="BOT_DECISION")
            cmds.append(AskDriverForDecision(new_model.to_act_seat))
    
    return new_model, cmds


def on_timer_tick(model: Model, msg: TimerTick) -> Tuple[Model, List[Cmd]]:
    """Handle timer tick - can be used for timeouts, etc."""
    
    # Remove expired banners
    current_banners = [
        banner for banner in model.banners
        if msg.now_ms < banner.duration_ms  # Simplified - would need actual timestamps
    ]
    
    if len(current_banners) != len(model.banners):
        return replace(model, banners=current_banners), []
    
    return model, []


# ============================================================================
# REVIEW-SPECIFIC REDUCERS
# ============================================================================

def rebuild_state_to(model: Model, index: int) -> Tuple[Model, List[Cmd]]:
    """Rebuild state to specific review index"""
    
    if model.session_mode != "REVIEW":
        return model, []
    
    # Clamp index
    index = max(0, min(index, model.review_len - 1))
    
    # This would typically replay events up to index
    # For now, just update cursor
    new_model = replace(
        model,
        review_cursor=index,
        waiting_for="NONE"
    )
    
    return new_model, []


def play_review_step(model: Model) -> Tuple[Model, List[Cmd]]:
    """Play next step in review"""
    
    print(f"📖 PlayReviewStep: cursor={model.review_cursor}, len={model.review_len}, mode={model.session_mode}")
    
    if model.session_mode != "REVIEW":
        print("❌ PlayReviewStep: Not in REVIEW mode")
        return model, []
    
    if model.review_cursor >= model.review_len - 1:
        print("🏁 PlayReviewStep: End of review reached")
        return model, []
    
    # Advance cursor
    new_cursor = model.review_cursor + 1
    new_model = replace(model, review_cursor=new_cursor)
    
    print(f"➡️ PlayReviewStep: Advancing to cursor {new_cursor}")
    
    # We need to get the event from session driver and dispatch it
    return new_model, [GetReviewEvent(index=new_cursor)]


def load_hand(model: Model, msg: LoadHand) -> Tuple[Model, List[Cmd]]:
    """Load new hand data - FIXED VERSION"""
    
    hand_data = msg.hand_data
    
    # Extract hand information
    hand_id = hand_data.get("hand_id", "")
    seats_data = hand_data.get("seats", {})
    board = tuple(hand_data.get("board", []))
    pot = hand_data.get("pot", 0)
    
    # Convert seats data to SeatState objects (immutable)
    seats = {}
    stacks = {}
    for seat_num, seat_data in seats_data.items():
        seat_state = SeatState(
            player_uid=seat_data.get("player_uid", f"player_{seat_num}"),
            name=seat_data.get("name", f"Player {seat_num}"),
            stack=seat_data.get("stack", 1000),
            chips_in_front=seat_data.get("chips_in_front", 0),
            folded=seat_data.get("folded", False),
            all_in=seat_data.get("all_in", False),
            cards=tuple(seat_data.get("cards", [])),  # Ensure tuple
            position=int(seat_num)
        )
        seats[int(seat_num)] = seat_state
        stacks[int(seat_num)] = seat_state.stack
    
    # CRITICAL: Use frozenset for legal_actions
    legal_actions = frozenset(hand_data.get("legal_actions", []))
    
    new_model = replace(
        model,
        hand_id=hand_id,
        seats=seats,  # Will be treated as immutable Mapping
        stacks=stacks,  # Will be treated as immutable Mapping
        board=board,
        pot=pot,
        street="PREFLOP",
        to_act_seat=hand_data.get("to_act_seat"),
        legal_actions=legal_actions,  # Now frozenset
        waiting_for="NONE",
        review_cursor=0,
        review_len=hand_data.get("review_len", 0)
    )
    
    return new_model, []


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def seat_is_human(model: Model, seat: int) -> bool:
    """Check if seat is controlled by human player"""
    # For now, assume seat 0 is human in practice/review mode
    if model.session_mode in ["PRACTICE", "REVIEW"]:
        return seat == 0
    return False


def seat_is_bot(model: Model, seat: int) -> bool:
    """Check if seat is controlled by bot"""
    return not seat_is_human(model, seat)


def apply_ppsm_snapshot(model: Model, msg: AppliedAction) -> Model:
    """
    Apply PPSM state snapshot after action
    This would typically get real state from PPSM
    """
    
    # Simulate basic state changes
    new_seats = dict(model.seats)
    new_stacks = dict(model.stacks)
    new_pot = model.pot
    
    print(f"🎯 Applying action: {msg.action} by seat {msg.seat} (amount: {msg.amount})")
    
    # Clear all acting status first
    for seat_num in new_seats:
        new_seats[seat_num] = replace(new_seats[seat_num], acting=False)
    
    # Update acting seat
    if msg.seat in new_seats:
        seat_state = new_seats[msg.seat]
        
        # Simulate stack/bet changes
        if msg.action in ["BET", "RAISE", "CALL"] and msg.amount:
            new_stacks[msg.seat] = max(0, new_stacks[msg.seat] - msg.amount)
            new_pot += msg.amount
            new_seats[msg.seat] = replace(
                new_seats[msg.seat],
                stack=new_stacks[msg.seat],
                chips_in_front=seat_state.chips_in_front + msg.amount
            )
            print(f"💰 Seat {msg.seat} bet ${msg.amount}, stack now ${new_stacks[msg.seat]}, pot now ${new_pot}")
            
        elif msg.action == "FOLD":
            new_seats[msg.seat] = replace(new_seats[msg.seat], folded=True)
            print(f"🃏 Seat {msg.seat} folded")
            
        elif msg.action in ["CHECK", "CALL"]:
            print(f"✅ Seat {msg.seat} {msg.action.lower()}ed")
    
    # Find next acting seat (simplified)
    next_seat = None
    active_seats = [s for s in sorted(new_seats.keys()) if not new_seats[s].folded]
    
    if len(active_seats) > 1:
        # Find next seat after current actor
        current_idx = active_seats.index(msg.seat) if msg.seat in active_seats else -1
        next_idx = (current_idx + 1) % len(active_seats)
        next_seat = active_seats[next_idx]
    
    # Update acting status
    if next_seat is not None:
        new_seats[next_seat] = replace(new_seats[next_seat], acting=True)
        print(f"👉 Next to act: Seat {next_seat}")
    else:
        print("🏁 No more players to act")
    
    return replace(
        model,
        seats=new_seats,
        stacks=new_stacks,
        to_act_seat=next_seat,
        pot=new_pot,
        legal_actions={"CHECK", "CALL", "BET", "RAISE", "FOLD"} if next_seat else set()
    )

```

---

### mvu_store.py

**Path**: `backend/ui/mvu/store.py`

```python
"""
MVU Store - Manages Model state and executes Commands
Based on PokerPro UI Implementation Handbook v2
"""

from typing import List, Callable, Optional, Any, Dict
import time
import threading

from .types import (
    Model, Msg, Cmd, SessionDriver, IntentHandler,
    PlaySound, Speak, Animate, AskDriverForDecision, ApplyPPSM,
    ScheduleTimer, PublishEvent, GetReviewEvent,
    DecisionReady, AppliedAction, StreetAdvanced, HandFinished, AnimationFinished
)
from .update import update


class MVUStore:
    """
    MVU Store - Single source of truth for Model state
    Handles message dispatch and command execution
    """
    
    def __init__(
        self,
        initial_model: Model,
        effect_bus: Any = None,
        game_director: Any = None,
        event_bus: Any = None,
        ppsm: Any = None
    ):
        self.model = initial_model
        self.effect_bus = effect_bus
        self.game_director = game_director
        self.event_bus = event_bus
        self.ppsm = ppsm
        
        # Subscribers to model changes
        self.subscribers: List[Callable[[Model], None]] = []
        
        # Session driver (pluggable)
        self.session_driver: Optional[SessionDriver] = None
        
        # Lock for thread safety
        self._lock = threading.RLock()
        
        # Scheduled timers
        self._timers: Dict[str, Any] = {}
        
        print("🏪 MVUStore: Initialized with model:", self.model.session_mode)
    
    def set_session_driver(self, driver: SessionDriver) -> None:
        """Set the session driver for this store"""
        with self._lock:
            self.session_driver = driver
            print(f"🏪 MVUStore: Session driver set: {type(driver).__name__}")
    
    def subscribe(self, callback: Callable[[Model], None]) -> Callable[[], None]:
        """
        Subscribe to model changes
        Returns unsubscribe function
        """
        with self._lock:
            self.subscribers.append(callback)
            
            # Immediately notify with current model
            callback(self.model)
            
            def unsubscribe():
                with self._lock:
                    if callback in self.subscribers:
                        self.subscribers.remove(callback)
            
            return unsubscribe
    
    def dispatch(self, msg: Msg) -> None:
        """
        Dispatch a message to update the model - FIXED VERSION
        """
        with self._lock:
            print(f"🎬 MVUStore: Dispatching {type(msg).__name__}")
            
            # Debug logging for LoadHand
            if hasattr(msg, 'hand_data'):
                seats_count = len(msg.hand_data.get('seats', {})) if msg.hand_data else 0
                print(f"🎬 MVUStore: LoadHand with {seats_count} seats")
            
            # Store old model for comparison
            old_model = self.model
            
            # Update model using pure reducer
            new_model, commands = update(self.model, msg)
            
            # CRITICAL FIX: Prevent empty model from overwriting populated model
            # This prevents the alternating state issue
            if (len(old_model.seats) > 0 and len(new_model.seats) == 0 and 
                type(msg).__name__ not in ['ResetHand', 'ClearTable']):
                print(f"⚠️ MVUStore: Blocking reset from {len(old_model.seats)} to 0 seats")
                print(f"⚠️ MVUStore: Message type was: {type(msg).__name__}")
                # Keep the old model, but still execute commands
                for cmd in commands:
                    self._execute_command(cmd)
                return
            
            # Debug model changes
            if len(new_model.seats) != len(old_model.seats):
                print(f"🎬 MVUStore: Seats changed from {len(old_model.seats)} to {len(new_model.seats)}")
            
            if new_model.pot != old_model.pot:
                print(f"🎬 MVUStore: Pot changed from {old_model.pot} to {new_model.pot}")
            
            if new_model.board != old_model.board:
                print(f"🎬 MVUStore: Board changed from {old_model.board} to {new_model.board}")
            
            # Check if model actually changed using proper equality
            if new_model == old_model:
                print(f"🎬 MVUStore: Model unchanged, skipping subscriber notification")
                # Still execute commands even if model didn't change
                for cmd in commands:
                    self._execute_command(cmd)
                return
            
            # Update stored model
            self.model = new_model
            print(f"🎬 MVUStore: Model updated, notifying {len(self.subscribers)} subscribers")
            
            # Execute commands first
            for cmd in commands:
                self._execute_command(cmd)
            
            # Then notify subscribers (use slice to avoid mutation during iteration)
            for subscriber in self.subscribers[:]:
                try:
                    subscriber(new_model)
                except Exception as e:
                    print(f"⚠️ MVUStore: Subscriber error: {e}")
                    import traceback
                    traceback.print_exc()
    
    def get_model(self) -> Model:
        """Get current model (thread-safe)"""
        with self._lock:
            return self.model
    
    def _execute_command(self, cmd: Cmd) -> None:
        """
        Execute a command using available services
        All I/O happens here, never in reducers
        """
        try:
            if isinstance(cmd, PlaySound):
                self._execute_play_sound(cmd)
            
            elif isinstance(cmd, Speak):
                self._execute_speak(cmd)
            
            elif isinstance(cmd, Animate):
                self._execute_animate(cmd)
            
            elif isinstance(cmd, AskDriverForDecision):
                self._execute_ask_driver(cmd)
            
            elif isinstance(cmd, ApplyPPSM):
                self._execute_apply_ppsm(cmd)
            
            elif isinstance(cmd, ScheduleTimer):
                self._execute_schedule_timer(cmd)
            
            elif isinstance(cmd, PublishEvent):
                self._execute_publish_event(cmd)
            

            
            elif isinstance(cmd, GetReviewEvent):
                self._execute_get_review_event(cmd)
            
            else:
                print(f"⚠️ MVUStore: Unknown command: {type(cmd).__name__}")
        
        except Exception as e:
            print(f"⚠️ MVUStore: Command execution error: {e}")
    
    def _execute_play_sound(self, cmd: PlaySound) -> None:
        """Execute PlaySound command"""
        if self.effect_bus:
            try:
                self.effect_bus.play_sound(cmd.name)
                print(f"🔊 MVUStore: Played sound: {cmd.name}")
            except Exception as e:
                print(f"⚠️ MVUStore: Sound error: {e}")
    
    def _execute_speak(self, cmd: Speak) -> None:
        """Execute Speak command"""
        if self.effect_bus and hasattr(self.effect_bus, 'voice_manager'):
            try:
                self.effect_bus.voice_manager.speak(cmd.text)
                print(f"🗣️ MVUStore: Spoke: {cmd.text}")
            except Exception as e:
                print(f"⚠️ MVUStore: Speech error: {e}")
    
    def _execute_animate(self, cmd: Animate) -> None:
        """Execute Animate command"""
        if self.effect_bus:
            try:
                # Start animation and set up completion callback
                def on_animation_complete():
                    self.dispatch(AnimationFinished(token=cmd.token))
                
                self.effect_bus.animate(
                    cmd.name,
                    cmd.payload,
                    callback=on_animation_complete
                )
                print(f"🎬 MVUStore: Started animation: {cmd.name} (token: {cmd.token})")
                
            except Exception as e:
                print(f"⚠️ MVUStore: Animation error: {e}")
                # Immediately complete animation on error
                self.dispatch(AnimationFinished(token=cmd.token))
    
    def _execute_ask_driver(self, cmd: AskDriverForDecision) -> None:
        """Execute AskDriverForDecision command"""
        if self.session_driver:
            try:
                def on_decision_ready(decision: DecisionReady):
                    self.dispatch(decision)
                
                self.session_driver.decide(self.model, cmd.seat, on_decision_ready)
                print(f"🤖 MVUStore: Asked driver for decision: seat {cmd.seat}")
                
            except Exception as e:
                print(f"⚠️ MVUStore: Driver decision error: {e}")
    
    def _execute_apply_ppsm(self, cmd: ApplyPPSM) -> None:
        """Execute ApplyPPSM command"""
        if self.ppsm:
            try:
                # Apply action to PPSM
                if cmd.seat == -1 and cmd.action == "CONTINUE":
                    # Continue game flow
                    result = self.ppsm.continue_game()
                else:
                    # Apply player action
                    result = self.ppsm.apply_action(cmd.seat, cmd.action, cmd.amount)
                
                # Process PPSM result and dispatch appropriate messages
                self._process_ppsm_result(result, cmd)
                
                print(f"🃏 MVUStore: Applied PPSM action: {cmd.action} by seat {cmd.seat}")
                
            except Exception as e:
                print(f"⚠️ MVUStore: PPSM error: {e}")
    
    def _execute_schedule_timer(self, cmd: ScheduleTimer) -> None:
        """Execute ScheduleTimer command"""
        try:
            timer_id = f"timer_{time.time()}_{id(cmd.msg)}"
            
            def timer_callback():
                self.dispatch(cmd.msg)
                if timer_id in self._timers:
                    del self._timers[timer_id]
            
            if self.game_director and hasattr(self.game_director, 'schedule'):
                # Use GameDirector for scheduling (architecture compliant)
                self.game_director.schedule(cmd.delay_ms, {
                    "type": "MVU_TIMER",
                    "callback": timer_callback
                })
            else:
                # Fallback to threading.Timer
                timer = threading.Timer(cmd.delay_ms / 1000.0, timer_callback)
                self._timers[timer_id] = timer
                timer.start()
            
            print(f"⏰ MVUStore: Scheduled timer: {cmd.delay_ms}ms -> {type(cmd.msg).__name__}")
            
        except Exception as e:
            print(f"⚠️ MVUStore: Timer error: {e}")
    
    def _execute_publish_event(self, cmd: PublishEvent) -> None:
        """Execute PublishEvent command"""
        if self.event_bus:
            try:
                self.event_bus.publish(cmd.topic, cmd.payload)
                print(f"📡 MVUStore: Published event: {cmd.topic}")
            except Exception as e:
                print(f"⚠️ MVUStore: Event publish error: {e}")
    

    
    def _execute_get_review_event(self, cmd: GetReviewEvent) -> None:
        """Execute GetReviewEvent command - get event from session driver"""
        if self.session_driver:
            try:
                event = self.session_driver.review_event_at(cmd.index)
                if event:
                    print(f"📖 MVUStore: Got review event at {cmd.index}: {type(event).__name__}")
                    # Dispatch the review event
                    self.dispatch(event)
                else:
                    print(f"📖 MVUStore: No review event at index {cmd.index}")
            except Exception as e:
                print(f"⚠️ MVUStore: Error getting review event: {e}")
        else:
            print("⚠️ MVUStore: No session driver for review event")
    
    def _process_ppsm_result(self, result: Any, original_cmd: ApplyPPSM) -> None:
        """
        Process PPSM result and dispatch appropriate messages
        This would be customized based on your PPSM interface
        """
        try:
            # Dispatch AppliedAction to trigger state update
            self.dispatch(AppliedAction(
                seat=original_cmd.seat,
                action=original_cmd.action,
                amount=original_cmd.amount
            ))
            
            # Check for street advancement
            if hasattr(result, 'street_changed') and result.street_changed:
                self.dispatch(StreetAdvanced(street=result.new_street))
            
            # Check for hand completion
            if hasattr(result, 'hand_finished') and result.hand_finished:
                self.dispatch(HandFinished(
                    winners=getattr(result, 'winners', []),
                    payouts=getattr(result, 'payouts', {})
                ))
        
        except Exception as e:
            print(f"⚠️ MVUStore: PPSM result processing error: {e}")
    
    def cleanup(self) -> None:
        """Cleanup resources"""
        with self._lock:
            # Cancel all timers
            for timer in self._timers.values():
                if hasattr(timer, 'cancel'):
                    timer.cancel()
            self._timers.clear()
            
            # Clear subscribers
            self.subscribers.clear()
            
            print("🏪 MVUStore: Cleaned up")


class MVUIntentHandler(IntentHandler):
    """
    Intent handler that dispatches messages to MVU store
    Converts UI events to messages
    """
    
    def __init__(self, store: MVUStore):
        self.store = store
    
    def on_click_next(self) -> None:
        """Next button clicked"""
        from .types import NextPressed
        self.store.dispatch(NextPressed())
    
    def on_toggle_autoplay(self, on: bool) -> None:
        """Auto-play toggled"""
        from .types import AutoPlayToggled
        self.store.dispatch(AutoPlayToggled(on=on))
    
    def on_action_btn(self, action: str, amount: Optional[int] = None) -> None:
        """Action button clicked"""
        from .types import UserChose
        self.store.dispatch(UserChose(action=action, amount=amount))
    
    def on_seek(self, index: int) -> None:
        """Review seek"""
        from .types import ReviewSeek
        self.store.dispatch(ReviewSeek(index=index))
    
    def on_request_hint(self) -> None:
        """GTO hint requested"""
        # This would dispatch a GTO hint request message
        print("🎯 MVUIntentHandler: GTO hint requested")
        pass

```

---

### mvu_view.py

**Path**: `backend/ui/mvu/view.py`

```python
"""
MVU View - Pure rendering components that read from Model
Based on PokerPro UI Implementation Handbook v2
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Dict, Any

from .types import Model, TableRendererProps, IntentHandler


class MVUPokerTableRenderer(ttk.Frame):
    """
    Pure View component for poker table
    Reads only from Model, emits intents via IntentHandler
    """
    
    def __init__(
        self,
        parent: tk.Widget,
        intent_handler: Optional[IntentHandler] = None,
        theme_manager: Any = None
    ):
        super().__init__(parent)
        
        self.intent_handler = intent_handler or DummyIntentHandler()
        self.theme_manager = theme_manager
        
        # Current props (for change detection)
        self.current_props: Optional[TableRendererProps] = None
        
        # UI components
        self.canvas: Optional[tk.Canvas] = None
        self.controls_frame: Optional[ttk.Frame] = None
        self.next_btn: Optional[ttk.Button] = None
        self.autoplay_var: Optional[tk.BooleanVar] = None
        self.action_buttons: Dict[str, ttk.Button] = {}
        self.status_label: Optional[ttk.Label] = None
        self.review_scale: Optional[ttk.Scale] = None
        
        self._setup_ui()
        
        print("🎨 MVUPokerTableRenderer: Initialized as pure View component")
    
    def _setup_ui(self) -> None:
        """Setup the UI components"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Main canvas for table rendering
        self.canvas = tk.Canvas(
            self,
            width=800,
            height=600,
            bg="#0D4F3C"  # Default felt color
        )
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Controls frame
        self.controls_frame = ttk.Frame(self)
        self.controls_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.controls_frame.grid_columnconfigure(1, weight=1)
        
        # Next button
        self.next_btn = ttk.Button(
            self.controls_frame,
            text="Next",
            command=self.intent_handler.on_click_next
        )
        self.next_btn.grid(row=0, column=0, padx=5)
        
        # Auto-play checkbox
        self.autoplay_var = tk.BooleanVar()
        autoplay_cb = ttk.Checkbutton(
            self.controls_frame,
            text="Auto-play",
            variable=self.autoplay_var,
            command=self._on_autoplay_toggle
        )
        autoplay_cb.grid(row=0, column=1, padx=5, sticky="w")
        
        # Status label
        self.status_label = ttk.Label(
            self.controls_frame,
            text="Ready"
        )
        self.status_label.grid(row=0, column=2, padx=5)
        
        # Action buttons frame
        self.actions_frame = ttk.Frame(self.controls_frame)
        self.actions_frame.grid(row=0, column=3, padx=5)
        
        # Create action buttons
        actions = ["FOLD", "CHECK", "CALL", "BET", "RAISE"]
        for i, action in enumerate(actions):
            btn = ttk.Button(
                self.actions_frame,
                text=action,
                command=lambda a=action: self._on_action_btn(a)
            )
            btn.grid(row=0, column=i, padx=2)
            self.action_buttons[action] = btn
        
        # Review controls (shown only in review mode)
        self.review_frame = ttk.Frame(self.controls_frame)
        self.review_frame.grid(row=1, column=0, columnspan=4, sticky="ew", pady=5)
        self.review_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(self.review_frame, text="Review:").grid(row=0, column=0, padx=5)
        
        self.review_scale = ttk.Scale(
            self.review_frame,
            from_=0,
            to=100,
            orient="horizontal",
            command=self._on_review_seek
        )
        self.review_scale.grid(row=0, column=1, sticky="ew", padx=5)
        
        self.review_position_label = ttk.Label(self.review_frame, text="0/0")
        self.review_position_label.grid(row=0, column=2, padx=5)
    
    def render(self, props: TableRendererProps) -> None:
        """
        Render the table based on props
        Pure function - only reads from props, never mutates state
        """
        # Skip if props haven't changed
        if self.current_props == props:
            return
        
        # Log render for debugging (minimal)
        if self.current_props is None:
            print(f"🎨 MVUPokerTableRenderer: Initial render with {len(props.seats)} seats")
        
        self.current_props = props
        
        # Update controls based on props
        self._update_controls(props)
        
        # Render table on canvas
        self._render_table(props)
        
        # Update review controls
        self._update_review_controls(props)
    
    def _update_controls(self, props: TableRendererProps) -> None:
        """Update control buttons and status"""
        
        # Update status
        status_text = f"Waiting for: {props.waiting_for}"
        if props.to_act_seat is not None:
            status_text += f" (Seat {props.to_act_seat})"
        self.status_label.config(text=status_text)
        
        # Update next button
        next_enabled = props.waiting_for != "HUMAN_DECISION"
        self.next_btn.config(state="normal" if next_enabled else "disabled")
        
        # Update autoplay
        self.autoplay_var.set(props.autoplay_on)
        
        # Update action buttons
        human_turn = (
            props.to_act_seat == 0 and  # Assuming seat 0 is human
            props.waiting_for == "HUMAN_DECISION"
        )
        
        for action, btn in self.action_buttons.items():
            enabled = human_turn and action in props.legal_actions
            btn.config(state="normal" if enabled else "disabled")
    
    def _render_table(self, props: TableRendererProps) -> None:
        """Render the poker table on canvas"""
        
        # Clear canvas
        self.canvas.delete("all")
        
        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            # Canvas not ready yet
            self.after(50, lambda: self.render(props))
            return
        
        # Draw felt background
        self.canvas.create_oval(
            50, 50, canvas_width - 50, canvas_height - 50,
            fill="#0D4F3C", outline="#2D5016", width=3,
            tags="felt"
        )
        
        # Draw seats
        self._draw_seats(props, canvas_width, canvas_height)
        
        # Draw community cards
        self._draw_community_cards(props, canvas_width, canvas_height)
        
        # Draw pot
        self._draw_pot(props, canvas_width, canvas_height)
        
        # Draw banners
        self._draw_banners(props, canvas_width, canvas_height)
    
    def _draw_seats(self, props: TableRendererProps, width: int, height: int) -> None:
        """Draw player seats"""
        
        import math
        
        # Calculate seat positions around oval table
        center_x, center_y = width // 2, height // 2
        radius_x, radius_y = (width - 100) // 2, (height - 100) // 2
        
        for seat_num, seat_state in props.seats.items():
            # Calculate position
            angle = (seat_num / max(len(props.seats), 1)) * 2 * math.pi - math.pi / 2
            x = center_x + radius_x * math.cos(angle)
            y = center_y + radius_y * math.sin(angle)
            
            # Draw seat background
            seat_color = "#FFD700" if seat_state.acting else "#8B4513"
            if seat_state.folded:
                seat_color = "#696969"
            
            self.canvas.create_rectangle(
                x - 60, y - 30, x + 60, y + 30,
                fill=seat_color, outline="black", width=2,
                tags=f"seat_{seat_num}"
            )
            
            # Draw player name
            self.canvas.create_text(
                x, y - 15,
                text=seat_state.name,
                font=("Arial", 10, "bold"),
                fill="black",
                tags=f"seat_{seat_num}_name"
            )
            
            # Draw stack
            self.canvas.create_text(
                x, y,
                text=f"${seat_state.stack}",
                font=("Arial", 9),
                fill="black",
                tags=f"seat_{seat_num}_stack"
            )
            
            # Draw bet amount
            if seat_state.chips_in_front > 0:
                self.canvas.create_text(
                    x, y + 15,
                    text=f"Bet: ${seat_state.chips_in_front}",
                    font=("Arial", 8),
                    fill="red",
                    tags=f"seat_{seat_num}_bet"
                )
            
            # Draw hole cards (if visible)
            if seat_state.cards and not seat_state.folded:
                card_x = x - 20
                for i, card in enumerate(seat_state.cards[:2]):  # Max 2 hole cards
                    self._draw_card(card_x + i * 20, y - 45, card, f"hole_{seat_num}_{i}")
    
    def _draw_community_cards(self, props: TableRendererProps, width: int, height: int) -> None:
        """Draw community cards"""
        
        if not props.board:
            return
        
        center_x, center_y = width // 2, height // 2
        card_width, card_height = 40, 60
        total_width = len(props.board) * (card_width + 5) - 5
        start_x = center_x - total_width // 2
        
        for i, card in enumerate(props.board):
            x = start_x + i * (card_width + 5)
            y = center_y - card_height // 2
            self._draw_card(x, y, card, f"board_{i}")
    
    def _draw_pot(self, props: TableRendererProps, width: int, height: int) -> None:
        """Draw pot display"""
        
        center_x, center_y = width // 2, height // 2
        
        # Pot background
        self.canvas.create_oval(
            center_x - 40, center_y + 60, center_x + 40, center_y + 100,
            fill="#DAA520", outline="black", width=2,
            tags="pot_bg"
        )
        
        # Pot amount
        self.canvas.create_text(
            center_x, center_y + 80,
            text=f"${props.pot}",
            font=("Arial", 12, "bold"),
            fill="black",
            tags="pot_amount"
        )
    
    def _draw_card(self, x: int, y: int, card: str, tag: str) -> None:
        """Draw a single card"""
        
        # Card background
        self.canvas.create_rectangle(
            x, y, x + 40, y + 60,
            fill="white", outline="black", width=2,
            tags=tag
        )
        
        # Card text
        self.canvas.create_text(
            x + 20, y + 30,
            text=card,
            font=("Arial", 10, "bold"),
            fill="black",
            tags=f"{tag}_text"
        )
    
    def _draw_banners(self, props: TableRendererProps, width: int, height: int) -> None:
        """Draw UI banners"""
        
        for i, banner in enumerate(props.banners):
            y_pos = 20 + i * 30
            
            # Banner colors
            colors = {
                "info": "#ADD8E6",
                "warning": "#FFD700",
                "error": "#FF6B6B",
                "success": "#90EE90"
            }
            
            bg_color = colors.get(banner.type, "#FFFFFF")
            
            self.canvas.create_rectangle(
                10, y_pos, width - 10, y_pos + 25,
                fill=bg_color, outline="black",
                tags=f"banner_{i}"
            )
            
            self.canvas.create_text(
                width // 2, y_pos + 12,
                text=banner.text,
                font=("Arial", 10),
                fill="black",
                tags=f"banner_{i}_text"
            )
    
    def _update_review_controls(self, props: TableRendererProps) -> None:
        """Update review-specific controls - FIXED VERSION"""
        
        is_review = props.session_mode == "REVIEW"
        
        if is_review:
            self.review_frame.grid()
            
            # CRITICAL FIX: Use flag to prevent callback loops
            if not hasattr(self, '_updating_scale'):
                self._updating_scale = False
            
            if props.review_len > 0 and not self._updating_scale:
                self._updating_scale = True
                try:
                    # Configure scale range
                    self.review_scale.config(to=max(props.review_len - 1, 0))
                    
                    # Update value without triggering callback
                    current_val = self.review_scale.get()
                    if current_val != props.review_cursor:
                        # Temporarily remove command
                        self.review_scale.config(command="")
                        self.review_scale.set(props.review_cursor)
                        # Re-add command after a delay to avoid immediate trigger
                        self.after(10, lambda: self.review_scale.config(command=self._on_review_seek))
                
                finally:
                    self._updating_scale = False
            
            # Update position label
            self.review_position_label.config(
                text=f"{props.review_cursor}/{props.review_len}"
            )
        else:
            self.review_frame.grid_remove()
    
    def _on_autoplay_toggle(self) -> None:
        """Handle autoplay toggle"""
        self.intent_handler.on_toggle_autoplay(self.autoplay_var.get())
    
    def _on_action_btn(self, action: str) -> None:
        """Handle action button click"""
        # For BET/RAISE, we'd need amount input - simplified for now
        amount = None
        if action in ["BET", "RAISE"]:
            amount = 100  # Placeholder amount
        
        self.intent_handler.on_action_btn(action, amount)
    
    def _on_review_seek(self, value: str) -> None:
        """Handle review seek - FIXED VERSION"""
        if hasattr(self, '_updating_scale') and self._updating_scale:
            return  # Ignore if we're updating programmatically
        
        try:
            index = int(float(value))
            self.intent_handler.on_seek(index)
        except ValueError:
            pass


class DummyIntentHandler:
    """Dummy intent handler for testing"""
    
    def on_click_next(self) -> None:
        print("🎯 DummyIntentHandler: Next clicked")
    
    def on_toggle_autoplay(self, on: bool) -> None:
        print(f"🎯 DummyIntentHandler: Autoplay toggled: {on}")
    
    def on_action_btn(self, action: str, amount: Optional[int] = None) -> None:
        print(f"🎯 DummyIntentHandler: Action {action} (amount: {amount})")
    
    def on_seek(self, index: int) -> None:
        print(f"🎯 DummyIntentHandler: Seek to {index}")
    
    def on_request_hint(self) -> None:
        print("🎯 DummyIntentHandler: Hint requested")

```

---

### mvu_drivers.py

**Path**: `backend/ui/mvu/drivers.py`

```python
"""
MVU Session Drivers - Pluggable session behavior
Based on PokerPro UI Implementation Handbook v2
"""

from typing import List, Dict, Any, Optional, Callable
import threading
import time

from .types import Model, Msg, DecisionReady, UserChose, AppliedAction, StreetAdvanced, HandFinished


class ReviewDriver:
    """
    Driver for REVIEW sessions - serves pre-recorded events
    """
    
    def __init__(self, hand_data: Dict[str, Any]):
        self.hand_data = hand_data
        self.events: List[Msg] = []
        self.current_index = 0
        
        # Parse hand data into events
        self._parse_hand_events()
        
        print(f"🎬 ReviewDriver: Initialized with {len(self.events)} events")
    
    def decide(self, model: Model, seat: int, callback: Callable[[DecisionReady], None]) -> None:
        """
        In review mode, decisions are pre-recorded
        This should not be called in normal review flow
        """
        print(f"⚠️ ReviewDriver: decide() called unexpectedly for seat {seat}")
        
        # If somehow called, provide a default action
        def delayed_callback():
            time.sleep(0.1)  # Small delay to simulate decision time
            callback(DecisionReady(seat=seat, action="CHECK", amount=None))
        
        thread = threading.Thread(target=delayed_callback)
        thread.daemon = True
        thread.start()
    
    def review_event_at(self, index: int) -> Optional[Msg]:
        """Get review event at specific index"""
        print(f"🎬 ReviewDriver: Getting event at index {index}, have {len(self.events)} events")
        if 0 <= index < len(self.events):
            event = self.events[index]
            print(f"🎬 ReviewDriver: Returning event {index}: {type(event).__name__} - {event}")
            return event
        print(f"🎬 ReviewDriver: No event at index {index}")
        return None
    
    def review_length(self) -> int:
        """Get total number of review events"""
        return len(self.events)
    
    def _parse_hand_events(self) -> None:
        """
        Parse hand data into chronological events
        This converts the hand history into a sequence of messages
        """
        try:
            # Get actions from hand data
            actions = self.hand_data.get("actions", [])
            
            for i, action_data in enumerate(actions):
                # Create event based on action type
                seat = action_data.get("seat", 0)
                action = action_data.get("action", "CHECK")
                amount = action_data.get("amount")
                street = action_data.get("street", "PREFLOP")
                
                # Add the action event
                self.events.append(AppliedAction(
                    seat=seat,
                    action=action,
                    amount=amount
                ))
                
                # Check if street changes after this action
                next_action = actions[i + 1] if i + 1 < len(actions) else None
                if next_action and next_action.get("street") != street:
                    self.events.append(StreetAdvanced(street=next_action.get("street")))
            
            # Add hand finished event if we have winner data
            winners = self.hand_data.get("winners", [])
            payouts = self.hand_data.get("payouts", {})
            if winners or payouts:
                self.events.append(HandFinished(
                    winners=winners,
                    payouts=payouts
                ))
        
        except Exception as e:
            print(f"⚠️ ReviewDriver: Error parsing events: {e}")
            # Fallback to empty events
            self.events = []


class PracticeDriver:
    """
    Driver for PRACTICE sessions - human play with optional bots
    """
    
    def __init__(self, bot_seats: List[int] = None):
        self.bot_seats = bot_seats or []
        print(f"🎯 PracticeDriver: Initialized with bots on seats: {self.bot_seats}")
    
    def decide(self, model: Model, seat: int, callback: Callable[[DecisionReady], None]) -> None:
        """Make decision for given seat"""
        if seat in self.bot_seats:
            # Bot decision - simple logic for now
            self._make_bot_decision(model, seat, callback)
        else:
            # Human decision - this shouldn't be called directly
            # Human decisions come through UserChose messages
            print(f"⚠️ PracticeDriver: decide() called for human seat {seat}")
    
    def review_event_at(self, index: int) -> Optional[Msg]:
        """Not applicable for practice mode"""
        return None
    
    def review_length(self) -> int:
        """Not applicable for practice mode"""
        return 0
    
    def _make_bot_decision(self, model: Model, seat: int, callback: Callable[[DecisionReady], None]) -> None:
        """Make a simple bot decision"""
        def delayed_decision():
            # Simulate thinking time
            time.sleep(0.5 + (seat * 0.1))  # Staggered timing
            
            # Simple decision logic
            legal_actions = model.legal_actions
            
            if "CHECK" in legal_actions:
                action = "CHECK"
                amount = None
            elif "CALL" in legal_actions:
                action = "CALL"
                amount = None  # PPSM will determine call amount
            elif "FOLD" in legal_actions:
                action = "FOLD"
                amount = None
            else:
                action = "CHECK"
                amount = None
            
            callback(DecisionReady(seat=seat, action=action, amount=amount))
        
        thread = threading.Thread(target=delayed_decision)
        thread.daemon = True
        thread.start()


class GTODriver:
    """
    Driver for GTO sessions - calls GTO provider for decisions
    """
    
    def __init__(self, gto_provider: Any = None):
        self.gto_provider = gto_provider
        print(f"🧠 GTODriver: Initialized with provider: {gto_provider is not None}")
    
    def decide(self, model: Model, seat: int, callback: Callable[[DecisionReady], None]) -> None:
        """Get GTO decision from provider"""
        if self.gto_provider:
            self._get_gto_decision(model, seat, callback)
        else:
            # Fallback to simple decision
            self._fallback_decision(model, seat, callback)
    
    def review_event_at(self, index: int) -> Optional[Msg]:
        """Not applicable for GTO mode"""
        return None
    
    def review_length(self) -> int:
        """Not applicable for GTO mode"""
        return 0
    
    def _get_gto_decision(self, model: Model, seat: int, callback: Callable[[DecisionReady], None]) -> None:
        """Get decision from GTO provider"""
        def gto_decision():
            try:
                # This would call your actual GTO provider
                # For now, simulate with a delay
                time.sleep(1.0)  # GTO thinking time
                
                # Placeholder GTO logic
                legal_actions = model.legal_actions
                if "RAISE" in legal_actions and len(model.board) == 0:  # Preflop aggression
                    action = "RAISE"
                    amount = model.pot * 2  # 2x pot raise
                elif "BET" in legal_actions and len(model.board) >= 3:  # Post-flop betting
                    action = "BET"
                    amount = int(model.pot * 0.75)  # 3/4 pot bet
                elif "CALL" in legal_actions:
                    action = "CALL"
                    amount = None
                else:
                    action = "CHECK"
                    amount = None
                
                callback(DecisionReady(seat=seat, action=action, amount=amount))
                
            except Exception as e:
                print(f"⚠️ GTODriver: Error getting GTO decision: {e}")
                self._fallback_decision(model, seat, callback)
        
        thread = threading.Thread(target=gto_decision)
        thread.daemon = True
        thread.start()
    
    def _fallback_decision(self, model: Model, seat: int, callback: Callable[[DecisionReady], None]) -> None:
        """Fallback decision when GTO provider fails"""
        def simple_decision():
            time.sleep(0.3)
            
            legal_actions = model.legal_actions
            if "CHECK" in legal_actions:
                action = "CHECK"
            elif "CALL" in legal_actions:
                action = "CALL"
            else:
                action = "FOLD"
            
            callback(DecisionReady(seat=seat, action=action, amount=None))
        
        thread = threading.Thread(target=simple_decision)
        thread.daemon = True
        thread.start()


def create_driver(session_mode: str, **kwargs) -> Any:
    """Factory function to create appropriate driver"""
    
    if session_mode == "REVIEW":
        hand_data = kwargs.get("hand_data", {})
        return ReviewDriver(hand_data)
    
    elif session_mode == "PRACTICE":
        bot_seats = kwargs.get("bot_seats", [1, 2, 3, 4, 5])  # All except seat 0 (human)
        return PracticeDriver(bot_seats)
    
    elif session_mode == "GTO":
        gto_provider = kwargs.get("gto_provider")
        return GTODriver(gto_provider)
    
    else:
        raise ValueError(f"Unknown session mode: {session_mode}")

```

---

### mvu_init.py

**Path**: `backend/ui/mvu/__init__.py`

```python
"""
MVU (Model-View-Update) Architecture Package
Based on PokerPro UI Implementation Handbook v2

This package implements a clean, testable MVU architecture for the poker table UI.
All timing, state management, and effects are handled through pure reducers and command execution.
"""

from .types import (
    Model, SeatState, Action, GtoHint, Banner,
    Msg, NextPressed, AutoPlayToggled, UserChose, DecisionReady, LoadHand,
    Cmd, PlaySound, Speak, Animate,
    SessionDriver, IntentHandler, TableRendererProps
)

from .update import update

from .store import MVUStore, MVUIntentHandler

from .view import MVUPokerTableRenderer

from .drivers import ReviewDriver, PracticeDriver, GTODriver, create_driver

from .hands_review_mvu import MVUHandsReviewTab

__all__ = [
    # Core types
    "Model", "SeatState", "Action", "GtoHint", "Banner",
    "Msg", "NextPressed", "AutoPlayToggled", "UserChose", "DecisionReady", "LoadHand",
    "Cmd", "PlaySound", "Speak", "Animate",
    "SessionDriver", "IntentHandler", "TableRendererProps",
    
    # Core functions
    "update",
    
    # Store
    "MVUStore", "MVUIntentHandler",
    
    # View
    "MVUPokerTableRenderer",
    
    # Drivers
    "ReviewDriver", "PracticeDriver", "GTODriver", "create_driver",
    
    # Complete implementations
    "MVUHandsReviewTab"
]

```

---

## MVU IMPLEMENTATION - HANDS REVIEW

### hands_review_mvu.py

**Path**: `backend/ui/mvu/hands_review_mvu.py`

```python
"""
MVU-based Hands Review Tab
Replaces the existing HandsReviewTab with clean MVU architecture
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict, Any, List
import json

from .types import Model, TableRendererProps, LoadHand, SeatState
from .store import MVUStore, MVUIntentHandler
from .view import MVUPokerTableRenderer
from .drivers import create_driver


class MVUHandsReviewTab(ttk.Frame):
    """
    MVU-based Hands Review Tab
    Clean, testable, and follows the architecture handbook
    """
    
    def __init__(
        self,
        parent: tk.Widget,
        services: Any = None,
        **kwargs
    ):
        super().__init__(parent, **kwargs)
        
        self.services = services
        
        # Get required services
        self.effect_bus = services.get_app("effect_bus") if services else None
        self.game_director = services.get_app("game_director") if services else None
        self.event_bus = services.get_app("event_bus") if services else None
        self.theme_manager = services.get_app("theme") if services else None
        
        # MVU components
        self.store: Optional[MVUStore] = None
        self.intent_handler: Optional[MVUIntentHandler] = None
        self.table_renderer: Optional[MVUPokerTableRenderer] = None
        
        # Hand data
        self.hands_data: List[Dict[str, Any]] = []
        self.current_hand_index = 0
        
        # UI components
        self.hand_selector: Optional[ttk.Combobox] = None
        self.hand_info_label: Optional[ttk.Label] = None
        
        # Props memoization
        self._last_props: Optional[TableRendererProps] = None
        
        self._setup_ui()
        self._initialize_mvu()
        self._load_hands_data()
        
        print("🎬 MVUHandsReviewTab: Initialized with clean MVU architecture")
    
    def _setup_ui(self) -> None:
        """Setup the UI layout"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Top controls frame
        controls_frame = ttk.Frame(self)
        controls_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        controls_frame.grid_columnconfigure(1, weight=1)
        
        # Hand selector
        ttk.Label(controls_frame, text="Hand:").grid(row=0, column=0, padx=5)
        
        self.hand_selector = ttk.Combobox(
            controls_frame,
            state="readonly",
            width=30
        )
        self.hand_selector.grid(row=0, column=1, padx=5, sticky="w")
        self.hand_selector.bind("<<ComboboxSelected>>", self._on_hand_selected)
        
        # Hand info
        self.hand_info_label = ttk.Label(
            controls_frame,
            text="No hand loaded"
        )
        self.hand_info_label.grid(row=0, column=2, padx=10, sticky="w")
        
        # Refresh button
        refresh_btn = ttk.Button(
            controls_frame,
            text="Refresh Hands",
            command=self._load_hands_data
        )
        refresh_btn.grid(row=0, column=3, padx=5)
        
        # Table renderer will be added in _initialize_mvu()
    
    def _initialize_mvu(self) -> None:
        """Initialize MVU components - FIXED VERSION"""
        
        # Create initial model for REVIEW mode
        initial_model = Model.initial(session_mode="REVIEW")
        
        # Create store
        self.store = MVUStore(
            initial_model=initial_model,
            effect_bus=self.effect_bus,
            game_director=self.game_director,
            event_bus=self.event_bus,
            ppsm=None  # We'll set this up when we have PPSM integration
        )
        
        # Create intent handler
        self.intent_handler = MVUIntentHandler(self.store)
        
        # Create table renderer
        self.table_renderer = MVUPokerTableRenderer(
            parent=self,
            intent_handler=self.intent_handler,
            theme_manager=self.theme_manager
        )
        self.table_renderer.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Flag to prevent double initialization and race conditions
        self._mvu_initialized = True
        self._first_render_complete = False
        
        print("🎬 MVUHandsReviewTab: MVU components initialized")
    
    def _load_hands_data(self) -> None:
        """Load hands data for review"""
        try:
            # Try to load from GTO hands file (as in original implementation)
            import os
            gto_file = os.path.join(
                os.path.dirname(__file__), "..", "..", "..", "gto_hands.json"
            )
            
            if os.path.exists(gto_file):
                with open(gto_file, 'r') as f:
                    raw_data = json.load(f)
                    
                self.hands_data = self._parse_hands_data(raw_data)
                print(f"📊 MVUHandsReviewTab: Loaded {len(self.hands_data)} hands")
                
            else:
                # Fallback to sample data
                self.hands_data = self._create_sample_hands()
                print("📊 MVUHandsReviewTab: Using sample hands data")
            
            self._update_hand_selector()
            
            # CRITICAL FIX: Only load hand if MVU is initialized and we have data
            if self.hands_data and hasattr(self, '_mvu_initialized') and self._mvu_initialized:
                # Subscribe AFTER we have hand data ready
                if not hasattr(self, 'unsubscribe'):
                    self.unsubscribe = self.store.subscribe(self._on_model_changed)
                
                # Load first hand immediately (no defer)
                self._load_hand(0)
        
        except Exception as e:
            print(f"⚠️ MVUHandsReviewTab: Error loading hands: {e}")
            self.hands_data = self._create_sample_hands()
            self._update_hand_selector()
    
    def _parse_hands_data(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Parse raw hands data into MVU format"""
        hands = []
        
        try:
            # Handle different data formats
            if isinstance(raw_data, dict):
                if "hands" in raw_data:
                    hands_list = raw_data["hands"]
                else:
                    hands_list = [raw_data]  # Single hand
            elif isinstance(raw_data, list):
                hands_list = raw_data
            else:
                return []
            
            for i, hand_data in enumerate(hands_list):
                parsed_hand = self._parse_single_hand(hand_data, i)
                if parsed_hand:
                    hands.append(parsed_hand)
        
        except Exception as e:
            print(f"⚠️ MVUHandsReviewTab: Error parsing hands data: {e}")
        
        return hands
    
    def _parse_single_hand(self, hand_data: Dict[str, Any], index: int) -> Optional[Dict[str, Any]]:
        """Parse a single hand into MVU format"""
        try:
            hand_id = hand_data.get("hand_id", f"Hand_{index + 1}")
            
            # Parse players/seats
            seats = {}
            stacks = {}
            
            players = hand_data.get("players", [])
            for i, player in enumerate(players[:6]):  # Max 6 players
                seat_state = {
                    "player_uid": player.get("name", f"Player_{i}"),
                    "name": player.get("name", f"Player {i}"),
                    "stack": player.get("stack", 1000),
                    "chips_in_front": 0,
                    "folded": False,
                    "all_in": False,
                    "cards": player.get("hole_cards", []),
                    "position": i
                }
                seats[i] = seat_state
                stacks[i] = seat_state["stack"]
            
            # Parse actions
            actions = []
            raw_actions = hand_data.get("actions", [])
            
            for action_data in raw_actions:
                if isinstance(action_data, dict):
                    actions.append({
                        "seat": action_data.get("player_index", 0),
                        "action": action_data.get("action", "CHECK"),
                        "amount": action_data.get("amount"),
                        "street": action_data.get("street", "PREFLOP")
                    })
            
            return {
                "hand_id": hand_id,
                "seats": seats,
                "stacks": stacks,
                "board": hand_data.get("board", []),
                "pot": hand_data.get("pot", 0),
                "actions": actions,
                "review_len": len(actions),
                "to_act_seat": 0,  # Start with first seat
                "legal_actions": ["CHECK", "CALL", "BET", "RAISE", "FOLD"]
            }
        
        except Exception as e:
            print(f"⚠️ MVUHandsReviewTab: Error parsing hand {index}: {e}")
            return None
    
    def _create_sample_hands(self) -> List[Dict[str, Any]]:
        """Create sample hands for testing"""
        return [
            {
                "hand_id": "SAMPLE_001",
                "seats": {
                    0: {
                        "player_uid": "hero",
                        "name": "Hero",
                        "stack": 1000,
                        "chips_in_front": 0,
                        "folded": False,
                        "all_in": False,
                        "cards": ["As", "Kh"],
                        "position": 0
                    },
                    1: {
                        "player_uid": "villain",
                        "name": "Villain",
                        "stack": 1000,
                        "chips_in_front": 0,
                        "folded": False,
                        "all_in": False,
                        "cards": ["Qd", "Jc"],
                        "position": 1
                    }
                },
                "stacks": {0: 1000, 1: 1000},
                "board": ["7h", "8s", "9d"],
                "pot": 60,
                "actions": [
                    {"seat": 0, "action": "RAISE", "amount": 30, "street": "PREFLOP"},
                    {"seat": 1, "action": "CALL", "amount": 30, "street": "PREFLOP"},
                    {"seat": 0, "action": "BET", "amount": 50, "street": "FLOP"},
                    {"seat": 1, "action": "FOLD", "amount": None, "street": "FLOP"}
                ],
                "review_len": 4,
                "to_act_seat": 0,
                "legal_actions": ["CHECK", "CALL", "BET", "RAISE", "FOLD"]
            },
            {
                "hand_id": "SAMPLE_002",
                "seats": {
                    0: {
                        "player_uid": "hero",
                        "name": "Hero",
                        "stack": 800,
                        "chips_in_front": 0,
                        "folded": False,
                        "all_in": False,
                        "cards": ["Kd", "Kc"],
                        "position": 0
                    },
                    1: {
                        "player_uid": "villain",
                        "name": "Villain",
                        "stack": 1200,
                        "chips_in_front": 0,
                        "folded": False,
                        "all_in": False,
                        "cards": ["Ad", "Qh"],
                        "position": 1
                    }
                },
                "stacks": {0: 800, 1: 1200},
                "board": ["2h", "7c", "Ks", "4d", "8h"],
                "pot": 400,
                "actions": [
                    {"seat": 1, "action": "RAISE", "amount": 40, "street": "PREFLOP"},
                    {"seat": 0, "action": "CALL", "amount": 40, "street": "PREFLOP"},
                    {"seat": 0, "action": "CHECK", "amount": None, "street": "FLOP"},
                    {"seat": 1, "action": "BET", "amount": 60, "street": "FLOP"},
                    {"seat": 0, "action": "RAISE", "amount": 180, "street": "FLOP"},
                    {"seat": 1, "action": "CALL", "amount": 120, "street": "FLOP"}
                ],
                "review_len": 6,
                "to_act_seat": 1,
                "legal_actions": ["CHECK", "BET"]
            }
        ]
    
    def _update_hand_selector(self) -> None:
        """Update the hand selector combobox"""
        hand_names = [hand["hand_id"] for hand in self.hands_data]
        self.hand_selector["values"] = hand_names
        
        if hand_names:
            self.hand_selector.current(0)
    
    def _on_hand_selected(self, event=None) -> None:
        """Handle hand selection"""
        try:
            index = self.hand_selector.current()
            if 0 <= index < len(self.hands_data):
                self._load_hand(index)
        except Exception as e:
            print(f"⚠️ MVUHandsReviewTab: Error selecting hand: {e}")
    
    def _load_hand(self, index: int) -> None:
        """Load a specific hand into the MVU store"""
        if not (0 <= index < len(self.hands_data)):
            return
        
        self.current_hand_index = index
        hand_data = self.hands_data[index]
        
        # Update hand info
        hand_id = hand_data["hand_id"]
        num_actions = hand_data.get("review_len", 0)
        self.hand_info_label.config(
            text=f"{hand_id} ({num_actions} actions)"
        )
        
        # Create and set session driver
        driver = create_driver("REVIEW", hand_data=hand_data)
        self.store.set_session_driver(driver)
        
        # Dispatch LoadHand message to store
        load_msg = LoadHand(hand_data=hand_data)
        self.store.dispatch(load_msg)
        
        print(f"📋 MVUHandsReviewTab: Loaded hand {hand_id}")
    
    def _on_model_changed(self, model: Model) -> None:
        """Handle model changes - FIXED VERSION"""
        try:
            # Skip first empty model notification
            if not self._first_render_complete and len(model.seats) == 0:
                print(f"🔄 MVUHandsReviewTab: Skipping initial empty model render")
                self._first_render_complete = True
                return
            
            print(f"🔄 MVUHandsReviewTab: Model changed - {len(model.seats)} seats, pot={model.pot}")
            
            # Convert model to props
            props = TableRendererProps.from_model(model)
            
            # Use props caching to prevent re-renders
            if hasattr(self, '_last_props') and props == self._last_props:
                print(f"🔄 MVUHandsReviewTab: Props unchanged, skipping render")
                return
            
            print(f"🔄 MVUHandsReviewTab: Props changed, updating renderer")
            self._last_props = props
            
            # Render table
            if self.table_renderer:
                self.table_renderer.render(props)
        
        except Exception as e:
            print(f"⚠️ MVUHandsReviewTab: Error updating view: {e}")
            import traceback
            traceback.print_exc()
    
    def dispose(self) -> None:
        """Clean up resources"""
        if hasattr(self, 'unsubscribe') and self.unsubscribe:
            self.unsubscribe()
        
        if self.store:
            self.store.cleanup()
        
        print("🧹 MVUHandsReviewTab: Disposed")

```

---

## TABLE RENDERING SYSTEM

### poker_table_renderer.py

**Path**: `backend/ui/renderers/poker_table_renderer.py`

```python
"""
Pure state-driven poker table renderer.
This component ONLY renders – no business logic, no state management.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Callable
from tkinter import ttk

from ..tableview.canvas_manager import CanvasManager
from ..tableview.layer_manager import LayerManager
from ..tableview.renderer_pipeline import RendererPipeline
from ..tableview.components.table_felt import TableFelt
from ..tableview.components.seats import Seats
from ..tableview.components.community import Community
from ..tableview.components.pot_display import PotDisplay
from ..tableview.components.bet_display import BetDisplay
from ..tableview.components.dealer_button import DealerButton
from ..tableview.components.player_highlighting import PlayerHighlighting


from ..table.state import PokerTableState


class PokerTableRenderer(ttk.Frame):
    """
    Pure rendering component for poker table.
    Renders state, emits intents, no business logic.
    """

    def __init__(
        self,
        parent,
        intent_handler: Optional[Callable[[Dict[str, Any]], None]] = None,
        theme_manager: Any = None,
    ) -> None:
        super().__init__(parent)
        self.intent_handler = intent_handler or (lambda _: None)
        self.theme_manager = theme_manager

        self._setup_rendering_pipeline()
        self.current_state: Optional[PokerTableState] = None
        self.renderer = None  # Will be initialized when canvas is ready
        self._ready_callbacks = []  # Callbacks to call when renderer is ready

    def _setup_rendering_pipeline(self) -> None:
        # Create CanvasManager first; it will initialize canvas lazily
        self.canvas_manager = CanvasManager(self)

        # Prepare components
        self.components = [
            TableFelt(),
            Seats(),
            Community(),
            BetDisplay(),
            PotDisplay(),
            DealerButton(),
            PlayerHighlighting(),
        ]

        # LayerManager depends on a real canvas; set up when ready
        def _finalize_pipeline():
            try:
                print(f"🔧 PokerTableRenderer: Starting pipeline finalization...")
                print(f"🔧 PokerTableRenderer: Canvas: {self.canvas_manager.canvas}")
                print(f"🔧 PokerTableRenderer: Overlay: {self.canvas_manager.overlay}")
                
                self.layer_manager = LayerManager(
                    self.canvas_manager.canvas, self.canvas_manager.overlay
                )
                print(f"🔧 PokerTableRenderer: LayerManager created: {self.layer_manager}")
                
                self.renderer = RendererPipeline(
                    self.canvas_manager, self.layer_manager, self.components
                )
                print(f"🔧 PokerTableRenderer: Renderer created: {self.renderer is not None}")
                print(f"🔧 PokerTableRenderer: Renderer object: {self.renderer}")
                
                # Grid now that canvas exists
                try:
                    self.canvas_manager.canvas.grid(row=0, column=0, sticky="nsew")
                    print(f"🔧 PokerTableRenderer: Canvas gridded successfully")
                except Exception as grid_e:
                    print(f"⚠️ PokerTableRenderer: Canvas grid error: {grid_e}")
                    
                self.grid_columnconfigure(0, weight=1)
                self.grid_rowconfigure(0, weight=1)
                print("✅ PokerTableRenderer: Pipeline finalized successfully")
                print(f"🔍 PokerTableRenderer: Final renderer state: {hasattr(self, 'renderer')} / {self.renderer is not None}")
                
                # Notify any waiting callbacks that renderer is ready
                print(f"🔄 PokerTableRenderer: Processing {len(self._ready_callbacks)} ready callbacks")
                for i, callback in enumerate(self._ready_callbacks):
                    try:
                        print(f"🔄 PokerTableRenderer: Calling ready callback {i+1}")
                        callback()
                        print(f"✅ PokerTableRenderer: Ready callback {i+1} completed")
                    except Exception as cb_e:
                        print(f"⚠️ PokerTableRenderer: Ready callback {i+1} error: {cb_e}")
                        import traceback
                        traceback.print_exc()
                self._ready_callbacks.clear()
                print(f"🔄 PokerTableRenderer: All callbacks processed, renderer final check: {self.renderer is not None}")
                
            except Exception as e:
                print(f"⚠️ PokerTableRenderer finalize error: {e}")
                import traceback
                traceback.print_exc()
                # Initialize renderer to None to prevent AttributeError
                self.renderer = None

        if getattr(self.canvas_manager, 'is_ready', lambda: False)():
            _finalize_pipeline()
        else:
            # Defer until the canvas is created
            try:
                self.canvas_manager.defer_render(lambda: _finalize_pipeline())
            except Exception:
                pass

    def render(self, state: PokerTableState) -> None:
        if state != self.current_state:
            # Check if renderer is initialized
            has_attr = hasattr(self, 'renderer')
            is_not_none = has_attr and self.renderer is not None
            print(f"🔍 PokerTableRenderer: Render check - hasattr: {has_attr}, not None: {is_not_none}")
            
            if not has_attr or self.renderer is None:
                print("⚠️ PokerTableRenderer: Renderer not ready, deferring render")
                # Defer render until renderer is ready
                self._ready_callbacks.append(lambda: self.render(state))
                print(f"🔄 PokerTableRenderer: Render deferred via ready callback (callbacks: {len(self._ready_callbacks)})")
                return
            
            # Render table
            self.renderer.render_once(state.__dict__)
            # Process declarative effects
            self._process_effects(state.effects)
            self.current_state = state

    def _process_effects(self, effects: List[Dict[str, Any]]) -> None:
        """Emit intents for visual effects to be handled externally."""
        for effect in effects or []:
            et = effect.get("type")
            if et in {"CHIP_TO_POT", "POT_TO_WINNER", "HIGHLIGHT_PLAYER"}:
                # Pure visual effects handled here; acoustic handled by EffectBus
                self._emit_intent(
                    {"type": "REQUEST_ANIMATION", "payload": effect}
                )

    def _emit_intent(self, intent: Dict[str, Any]) -> None:
        try:
            self.intent_handler(intent)
        except Exception:
            pass



```

---

### canvas_manager.py

**Path**: `backend/ui/tableview/canvas_manager.py`

```python
import tkinter as tk
import importlib


class CanvasManager:
    def __init__(self, parent):
        # Store parent; defer canvas creation until sized to avoid small initial render
        self.parent = parent
        self.canvas = None
        self.overlay = None
        self._configure_after_id = None
        self._initialized = False
        self._pending_render = None

        # Resolve theme bg color once for initialization
        try:
            from ui.services.theme_manager import ThemeManager
            tm = ThemeManager()
            theme_colors = tm.get()
            self._canvas_bg = theme_colors.get("table.bg", theme_colors.get("panel.bg", "#000000"))
        except Exception:
            self._canvas_bg = "#000000"

        # Schedule lazy initialization after idle; we may need to retry until sized
        try:
            self.parent.after_idle(self._initialize_canvas)
        except Exception:
            # Fallback: attempt immediate init
            self._initialize_canvas()

    def _on_configure(self, event):
        if event.width <= 1 or event.height <= 1:
            return
        try:
            if self.overlay is not None and self.canvas is not None:
                self.overlay.lift(self.canvas)
        except Exception:
            pass

    def size(self):
        if not self.canvas:
            return 0, 0
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 1 or h <= 1:
            try:
                w = self.canvas.winfo_reqwidth()
                h = self.canvas.winfo_reqheight()
            except Exception:
                pass
        return w, h

    # New APIs for deferred render gating
    def is_ready(self):
        return self._initialized and self.canvas is not None

    def defer_render(self, render_func):
        if self.is_ready():
            try:
                render_func()
            except Exception:
                pass
        else:
            self._pending_render = render_func

    def _initialize_canvas(self):
        # Force geometry update and get real size; retry until reasonable
        try:
            self.parent.update_idletasks()
        except Exception:
            pass

        try:
            pw = getattr(self.parent, 'winfo_width')()
            ph = getattr(self.parent, 'winfo_height')()
        except Exception:
            pw, ph = 0, 0

        if pw <= 100 or ph <= 100:
            # ARCHITECTURE COMPLIANT: Schedule via parent's GameDirector if available
            try:
                # Try to find GameDirector through parent hierarchy
                game_director = None
                widget = self.parent
                while widget and not game_director:
                    if hasattr(widget, 'game_director'):
                        game_director = widget.game_director
                        break
                    if hasattr(widget, 'services'):
                        try:
                            game_director = widget.services.get_app("game_director")
                            break
                        except Exception:
                            pass
                    widget = getattr(widget, 'master', None)
                
                if game_director:
                    game_director.schedule(50, {
                        "type": "CANVAS_INIT_RETRY",
                        "callback": self._initialize_canvas
                    })
                else:
                    # Fallback: direct retry (violation but necessary)
                    self.parent.after(50, self._initialize_canvas)
            except Exception:
                pass
            return

        # Create canvas now with proper size and grid into parent
        try:
            self.canvas = tk.Canvas(self.parent, width=pw, height=ph, bg=self._canvas_bg, highlightthickness=0)
            self.canvas.grid(row=0, column=0, sticky="nsew")
            try:
                self.canvas.bind("<Configure>", self._on_configure, add="+")
            except Exception:
                pass
            self._initialized = True

            # Execute any pending render deferral
            if self._pending_render is not None:
                pending = self._pending_render
                self._pending_render = None
                try:
                    pending()
                except Exception:
                    pass
        except Exception:
            # ARCHITECTURE COMPLIANT: Last resort retry via GameDirector
            try:
                # Try to find GameDirector through parent hierarchy
                game_director = None
                widget = self.parent
                while widget and not game_director:
                    if hasattr(widget, 'game_director'):
                        game_director = widget.game_director
                        break
                    if hasattr(widget, 'services'):
                        try:
                            game_director = widget.services.get_app("game_director")
                            break
                        except Exception:
                            pass
                    widget = getattr(widget, 'master', None)
                
                if game_director:
                    game_director.schedule(50, {
                        "type": "CANVAS_INIT_LAST_RESORT",
                        "callback": self._initialize_canvas
                    })
                else:
                    # Final fallback: direct retry (violation but necessary for bootstrap)
                    self.parent.after(50, self._initialize_canvas)
            except Exception:
                pass



```

---

### renderer_pipeline.py

**Path**: `backend/ui/tableview/renderer_pipeline.py`

```python
class RendererPipeline:
    def __init__(self, canvas_manager, layer_manager, components):
        self.cm = canvas_manager
        self.lm = layer_manager
        self.components = components

    def render_once(self, state, force=False):
        # Gate rendering until the canvas is created/sized to avoid small initial artifacts
        if not self.cm.is_ready() and not force:
            self.cm.defer_render(lambda: self.render_once(state, force=True))
            return

        c = self.cm.canvas
        if c is None:
            return

        w, h = self.cm.size()
        if w <= 100 or h <= 100:
            # Skip rendering on invalid size; a deferred render will occur on ready
            print(f"⚠️ Skipping render - invalid dimensions: {w}x{h}")
            return

        # Thorough clear to ensure no remnants from any previous pass
        try:
            c.delete("all")
        except Exception:
            pass

        # Render all components
        for component in self.components:
            try:
                component.render(state, self.cm, self.lm)
            except Exception as e:
                print(f"⚠️ Component {component.__class__.__name__} render error: {e}")

        # Apply layer ordering
        try:
            self.lm.raise_to_policy()
        except Exception as e:
            print(f"⚠️ Layer manager error: {e}")

        print(f"🎨 Rendered poker table: {w}x{h} with {len(self.components)} components")



```

---

### layer_manager.py

**Path**: `backend/ui/tableview/layer_manager.py`

```python
class LayerManager:
    ORDER = [
        "layer:felt",
        "layer:seats",       # seat backgrounds and player names
        "layer:hole_cards",  # player hole cards (must be above seats)
        "layer:stacks",      # player stacks (must be above hole cards)
        "layer:community",   # community cards and card backs
        "layer:bets",        # bet/call chip stacks (must be above community)
        "layer:pot",         # pot chips and display
        "layer:action",      # acting highlight ring and labels
        "layer:status",      # folded/winner labels
        "layer:overlay",     # overlays and UI elements
        # transient animation/helper tags kept last so they stay visible
        "temp_animation", "flying_chip", "motion_glow", "pot_pulse",
    ]

    def __init__(self, canvas, overlay):
        self.canvas = canvas
        self.overlay = overlay

    def raise_to_policy(self) -> None:
        c = self.canvas
        for tag in self.ORDER:
            try:
                c.tag_raise(tag)
            except Exception:
                pass
        if self.overlay is not None:
            try:
                self.overlay.lift(self.canvas)
            except Exception:
                pass



```

---

## TABLE COMPONENTS - VISUAL

### seats.py

**Path**: `backend/ui/tableview/components/seats.py`

```python
"""
Player Seats Component
Renders player seats, hole cards, and stack information on the poker table.
"""

import math
from typing import List, Dict, Any, Optional
from .sizing_utils import create_sizing_system

# Fallback chip graphics if premium_chips module is not available
try:
    from .premium_chips import draw_chip_stack
except Exception:
    def draw_chip_stack(canvas, x, y, denom_key="chip.gold", text="", r=14, tags=None):
        fill = "#D97706"  # goldish
        canvas.create_oval(x-r, y-r, x+r, y+r, fill=fill, outline="black", width=1, tags=tags or ())

# Fallback theme if theme manager is not available
THEME = {
    "seat.bg": "#1F2937",
    "seat.border": "#6B7280",
    "card.faceFg": "#F8FAFC",
    "card.border": "#0B1220",
    "card.back.bg": "#8B0000",
    "card.back.border": "#2F4F4F",
    "card.back.pattern": "#AA0000",
    "stack.bg": "#10B981",
    "stack.border": "#059669",
}

# Fallback fonts
FONTS = {
    "font.body": ("Arial", 12, "bold"),
    "font.small": ("Arial", 10, "bold"),
}


class Seats:
    """Renders player seats, hole cards, and stack information."""
    
    def __init__(self):
        self.sizing_system = None
        self._stack_chips = {}
        self._blind_elements = {}
    
    def render(self, state, canvas_manager, layer_manager) -> None:
        """Render all player seats on the table."""
        # Get canvas and dimensions
        canvas = canvas_manager.canvas
        w, h = canvas_manager.size()
        
        if w <= 1 or h <= 1:
            return
        
        # Get seats data from state
        seats_data = state.get("seats", [])
        if not seats_data:
            return
        
        # Initialize sizing system if not already done
        if not self.sizing_system:
            num_players = len(seats_data)
            self.sizing_system = create_sizing_system(w, h, num_players)
        
        # Get card size from sizing system
        card_width, card_height = self.sizing_system.get_card_size()
        
        # Use consistent seat positions from geometry helper
        from ...state.selectors import get_seat_positions
        seat_positions = get_seat_positions(state, seat_count=len(seats_data), 
                                          canvas_width=w, canvas_height=h)
        
        print(f"🪑 Seats rendering: {len(seats_data)} seats, canvas: {w}x{h}")
        print(f"🪑 Using consistent seat positions from geometry helper")
        
        for idx, (x, y) in enumerate(seat_positions):
            print(f"🪑 Seat {idx} position: ({x}, {y}) - within canvas bounds: {0 <= x <= w and 0 <= y <= h}")
        
        # Check if any seats are outside canvas bounds
        seats_outside = [(i, x, y) for i, (x, y) in enumerate(seat_positions) if not (0 <= x <= w and 0 <= y <= h)]
        if seats_outside:
            print(f"⚠️ Warning: {len(seats_outside)} seats are outside canvas bounds:")
            for i, x, y in seats_outside:
                print(f"   Seat {i}: ({x}, {y}) - canvas size: {w}x{h}")
        
        # Render each seat
        for idx, seat in enumerate(seats_data):
            x, y = seat_positions[idx]
            
            print(f"🪑 Rendering seat {idx}: {seat.get('name', 'Unknown')} at ({x}, {y})")
            print(f"   Cards: {seat.get('cards', [])}")
            print(f"   Stack: {seat.get('stack', 0)}")
            print(f"   Position: {seat.get('position', '')}")
            
            # Render seat background
            self._render_seat_background(canvas, x, y, idx, seat)
            
            # Render player name
            self._render_player_name(canvas, x, y, idx, seat)
            
            # Render hole cards
            if seat.get('cards'):
                self._render_hole_cards(canvas, x, y, idx, seat, card_width, card_height)
            
            # Render player stack chips
            if seat.get('stack', 0) > 0:
                self._render_stack_chips(canvas, x, y, idx, seat)
            
            # Draw SB/BB indicators if applicable
            position = seat.get('position', '')
            if position in ['SB', 'BB']:
                self._draw_blind_indicator(canvas, x, y, position, seat, idx)
        
        print(f"🪑 Calculated positions for {len(seats_data)} seats on {w}x{h} canvas")
        print(f"🪑 Seat positions: {seat_positions}")
    
    def _render_seat_background(self, canvas, x: int, y: int, idx: int, seat: dict):
        """Render seat background circle."""
        # Get seat size from sizing system
        seat_size = self.sizing_system.get_chip_size('stack') * 2  # Seat is 2x stack chip size
        
        # Create seat background
        seat_bg = canvas.create_oval(
            x - seat_size, y - seat_size,
            x + seat_size, y + seat_size,
            fill=THEME.get("seat.bg", "#1F2937"),
            outline=THEME.get("seat.border", "#6B7280"),
            width=2,
            tags=("layer:seats", f"seat_bg:{idx}")
        )
        
        # Add seat number label
        label_y = y + seat_size + 15
        seat_label = canvas.create_text(
            x, label_y,
            text=f"Seat {idx + 1}",
            font=FONTS.get("font.small", ("Arial", 10, "bold")),
            fill="#FFFFFF",
            tags=("layer:seats", f"seat_label:{idx}"),
        )
    
    def _render_player_name(self, canvas, x: int, y: int, idx: int, seat: dict):
        """Render player name above the seat."""
        # Get text size from sizing system
        name_size = self.sizing_system.get_text_size('player_name')
        
        # Position name above seat
        name_y = y - 40
        
        name_text = canvas.create_text(
            x, name_y,
            text=seat.get('name', f'Player{idx + 1}'),
            font=("Arial", name_size, "bold"),
            fill="#FFFFFF",
            tags=("layer:seats", f"player_name:{idx}")
        )
    
    def _render_hole_cards(self, canvas, x: int, y: int, idx: int, seat: dict, 
                          card_width: int, card_height: int):
        """Render player's hole cards."""
        cards = seat.get('cards', [])
        if not cards:
            return
        
        # Get text sizes from sizing system
        rank_size = self.sizing_system.get_text_size('card_rank')
        suit_size = self.sizing_system.get_text_size('card_suit')
        
        # Calculate card positions (side by side)
        card_spacing = self.sizing_system.get_spacing('card_gap')
        total_width = len(cards) * card_width + (len(cards) - 1) * card_spacing
        start_x = x - total_width // 2
        
        print(f"🃏 Rendering {len(cards)} hole cards for seat {idx} at position ({x}, {y})")
        
        for i, card in enumerate(cards):
            card_x = start_x + i * (card_width + card_spacing) + card_width // 2
            card_y = y + 35  # Further below the seat for better visibility
            
            # Create card background
            card_bg = canvas.create_rectangle(
                card_x - card_width // 2, card_y - card_height // 2,
                card_x + card_width // 2, card_y + card_height // 2,
                fill=THEME.get("card.faceFg", "#F8FAFC"),
                outline=THEME.get("card.border", "#0B1220"),
                width=2,
                tags=("layer:hole_cards", f"hole_card:{idx}:{i}")
            )
            
            # Parse card
            if len(card) >= 2:
                rank = card[0]
                suit = card[1]
                
                # Render rank
                rank_text = canvas.create_text(
                    card_x, card_y - card_height // 4,
                    text=rank,
                    font=("Arial", rank_size, "bold"),
                    fill="#000000",
                    tags=("layer:hole_cards", f"hole_card:{idx}:{i}", "card_rank")
                )
                
                # Render suit
                suit_text = canvas.create_text(
                    card_x, card_y + card_height // 4,
                    text=suit,
                    font=("Arial", suit_size, "bold"),
                    fill=self._get_suit_color(suit),
                    tags=("layer:hole_cards", f"hole_card:{idx}:{i}", "card_suit")
                )
        
        print(f"🃏 Rendering cards for seat {idx}: {cards}, size: {card_width}x{card_height}, players: {self.sizing_system.num_players}")
    
    def _render_stack_chips(self, canvas, x: int, y: int, idx: int, seat: dict):
        """Render player's stack chips."""
        stack_amount = seat.get('stack', 0)
        if stack_amount <= 0:
            return
        
        # Get chip size from sizing system
        chip_size = self.sizing_system.get_chip_size('stack')
        
        # Position stack below the seat
        stack_x = x
        stack_y = y + 50
        
        # Create stack background
        stack_bg = canvas.create_oval(
            stack_x - chip_size, stack_y - chip_size,
            stack_x + chip_size, stack_y + chip_size,
            fill=THEME.get("stack.bg", "#10B981"),
            outline=THEME.get("stack.border", "#059669"),
            width=2,
            tags=("layer:stacks", f"stack_bg:{idx}")
        )
        
        # Create stack amount text
        stack_text_size = self.sizing_system.get_text_size('stack_amount')
        stack_text = canvas.create_text(
            stack_x, stack_y,
            text=f"${stack_amount}",
            font=("Arial", stack_text_size, "bold"),
            fill="#FFFFFF",
            tags=("layer:stacks", f"stack_text:{idx}")
        )
        
        # Store for cleanup
        self._stack_chips[idx] = [stack_bg, stack_text]
    
    def _draw_blind_indicator(self, canvas, x: int, y: int, position: str, seat: dict, idx: int):
        """Draw small blind or big blind indicator with chip graphics."""
        # Get chip size from sizing system
        chip_size = self.sizing_system.get_chip_size('bet')
        
        # Position blind indicator above the seat
        blind_x = x
        blind_y = y - 60
        
        # Get blind amount
        if position == 'SB':
            amount = seat.get('small_blind', 5)  # Default small blind
            color = "#F59E0B"  # Orange for small blind
            label = "SB"
        else:  # BB
            amount = seat.get('big_blind', 10)  # Default big blind
            color = "#EF4444"  # Red for big blind
            label = "BB"
        
        # Create blind chip background
        chip_bg = canvas.create_oval(
            blind_x - chip_size, blind_y - chip_size,
            blind_x + chip_size, blind_y + chip_size,
            fill=color,
            outline="#FFFFFF",
            width=2,
            tags=("layer:blinds", f"blind_chip:{idx}")
        )
        
        # Create blind amount text
        amount_text_size = self.sizing_system.get_text_size('blind_label')
        amount_text = canvas.create_text(
            blind_x, blind_y,
            text=f"${amount}",
            font=("Arial", amount_text_size, "bold"),
            fill="#FFFFFF",
            tags=("layer:blinds", f"blind_amount:{idx}")
        )
        
        # Create blind label (SB/BB)
        label_y = blind_y - chip_size - 10
        label_text = canvas.create_text(
            blind_x, label_y,
            text=label,
            font=("Arial", amount_text_size, "bold"),
            fill=color,
            tags=("layer:blinds", f"blind_label:{idx}")
        )
        
        # Store for cleanup
        if idx not in self._blind_elements:
            self._blind_elements[idx] = {}
        self._blind_elements[idx].update({
            'chip_bg': chip_bg,
            'amount_text': amount_text,
            'label_text': label_text
        })
    
    def _get_suit_color(self, suit: str) -> str:
        """Get color for card suit."""
        if suit in ['♥', '♦']:
            return "#FF0000"  # Red for hearts and diamonds
        else:
            return "#000000"  # Black for clubs and spades

```

---

### community.py

**Path**: `backend/ui/tableview/components/community.py`

```python
"""
Community Cards Component
Renders the community cards (flop, turn, river) on the poker table.
"""

import math
from typing import List, Tuple, Optional
from .sizing_utils import create_sizing_system


class Community:
    """Renders community cards on the poker table."""
    
    def __init__(self):
        self.community_cards = []
        self.sizing_system = None
    
    def render(self, state, canvas_manager, layer_manager) -> None:
        """Render community cards on the table with professional poker app behavior."""
        # Get canvas and dimensions
        canvas = canvas_manager.canvas
        w, h = canvas_manager.size()
        
        if w <= 1 or h <= 1:
            return
        
        # Get board cards from state
        board_cards = state.get("board", [])
        
        # Professional poker behavior: Always show 5 card positions
        # Show card backs initially, reveal as game progresses
        street = state.get("street", "PREFLOP")
        
        # Determine how many cards to show face-up based on street
        if street == "PREFLOP":
            revealed_cards = 0
        elif street == "FLOP":
            revealed_cards = 3
        elif street == "TURN":
            revealed_cards = 4
        elif street in ["RIVER", "SHOWDOWN"]:
            revealed_cards = 5
        else:
            revealed_cards = len(board_cards)  # Fallback
        
        # Get seats data for player count
        seats_data = state.get("seats", [])
        num_players = len(seats_data) if seats_data else 6
        
        # Initialize sizing system if not already done
        if not self.sizing_system:
            self.sizing_system = create_sizing_system(w, h, num_players)
        
        # Get card size from sizing system
        card_w, card_h = self.sizing_system.get_card_size()
        
        # Calculate table center and board position
        cx, cy = w // 2, int(h * 0.45)  # Board above center
        
        # Calculate spacing between cards
        spacing = self.sizing_system.get_spacing('card_gap')
        
        # Always render 5 card positions (professional poker standard)
        total_cards = 5
        total_width = total_cards * card_w + (total_cards - 1) * spacing
        start_x = cx - total_width // 2
        
        # Store positions for other components
        positions = []
        
        print(f"🃏 Community cards positioning: center=({cx},{cy}), card_size={card_w}x{card_h}, spacing={spacing}")
        print(f"🃏 Street: {street}, revealed: {revealed_cards}/{total_cards}")
        
        # Render all 5 card positions
        for i in range(total_cards):
            card_x = start_x + i * (card_w + spacing) + card_w // 2
            card_y = cy
            
            # Store position for other components
            positions.append((card_x, card_y))
            
            # Determine what to show for this card position
            if i < revealed_cards and i < len(board_cards):
                # Show face-up card
                card = board_cards[i]
                self._render_card(canvas, card_x, card_y, card, card_w, card_h, face_up=True)
            else:
                # Show card back
                self._render_card_back(canvas, card_x, card_y, card_w, card_h)
        
        print(f"🃏 Community rendering: {total_cards} positions, {revealed_cards} revealed, canvas: {w}x{h}")
        print(f"🃏 Board positions on {w}x{h}: center=({cx},{cy}), card_size={card_w}x{card_h}, positions={positions}")
    
    def _render_card(self, canvas, x: int, y: int, card: str, card_w: int, card_h: int, face_up: bool = True):
        """Render a single community card face-up."""
        # Get text sizes from sizing system
        rank_size = self.sizing_system.get_text_size('card_rank')
        suit_size = self.sizing_system.get_text_size('card_suit')
        
        # Create card background
        card_bg = canvas.create_rectangle(
            x - card_w // 2, y - card_h // 2,
            x + card_w // 2, y + card_h // 2,
            fill="#FFFFFF",
            outline="#000000",
            width=2,
            tags=("layer:community", "community_card")
        )
        
        # Parse and render card face
        if len(card) >= 2:
            rank = card[0]
            suit = card[1]
            
            # Render rank
            rank_text = canvas.create_text(
                x, y - card_h // 4,
                text=rank,
                font=("Arial", rank_size, "bold"),
                fill="#000000",
                tags=("layer:community", "community_card", "card_rank")
            )
            
            # Render suit
            suit_text = canvas.create_text(
                x, y + card_h // 4,
                text=suit,
                font=("Arial", suit_size, "bold"),
                fill=self._get_suit_color(suit),
                tags=("layer:community", "community_card", "card_suit")
            )
    
    def _render_card_back(self, canvas, x: int, y: int, card_w: int, card_h: int):
        """Render a card back (professional poker style)."""
        # Create card background with darker color for back
        card_bg = canvas.create_rectangle(
            x - card_w // 2, y - card_h // 2,
            x + card_w // 2, y + card_h // 2,
            fill="#8B0000",  # Dark red background
            outline="#000000",
            width=2,
            tags=("layer:community", "community_card_back")
        )
        
        # Add card back pattern (simple diamond pattern)
        # Inner border
        inner_border = canvas.create_rectangle(
            x - card_w // 2 + 4, y - card_h // 2 + 4,
            x + card_w // 2 - 4, y + card_h // 2 - 4,
            fill="",
            outline="#AA0000",
            width=1,
            tags=("layer:community", "community_card_back")
        )
        
        # Center diamond
        diamond_size = min(card_w, card_h) // 4
        canvas.create_polygon(
            x, y - diamond_size,  # Top
            x + diamond_size, y,  # Right
            x, y + diamond_size,  # Bottom
            x - diamond_size, y,  # Left
            fill="#AA0000",
            outline="#FFFFFF",
            width=1,
            tags=("layer:community", "community_card_back")
        )
    
    def _get_suit_color(self, suit: str) -> str:
        """Get color for card suit."""
        if suit in ['♥', '♦']:
            return "#FF0000"  # Red for hearts and diamonds
        else:
            return "#000000"  # Black for clubs and spades


```

---

### pot_display.py

**Path**: `backend/ui/tableview/components/pot_display.py`

```python
from ...services.theme_manager import ThemeManager
from .chip_graphics import ChipGraphics

try:
    from .premium_chips import draw_pot_chip, pulse_pot_glow
except Exception:
    def draw_pot_chip(canvas, x, y, theme, fonts, scale=1.0, tags=()):
        r = int(10*scale)
        canvas.create_oval(x-r, y-r, x+r, y+r, fill=theme.get("chip.gold","#D97706"), outline="black", width=1, tags=tags)
    def pulse_pot_glow(canvas, pot_bg_id, theme):
        # simple glow by toggling outline width
        try:
            w = int(canvas.itemcget(pot_bg_id, "width") or 2)
            canvas.itemconfig(pot_bg_id, width=(w%4)+1)
        except Exception:
            pass


def _tokens(canvas):
    # Prefer ThemeManager from widget tree
    w = canvas
    while w is not None:
        try:
            if hasattr(w, "services"):
                tm = w.services.get_app("theme")  # type: ignore[attr-defined]
                if isinstance(tm, ThemeManager):
                    return tm.get_theme(), tm.get_fonts()
        except Exception:
            pass
        w = getattr(w, "master", None)
    # Fallbacks
    return (
        {"pot.valueText": "#F8FAFC", "chip_gold": "#FFD700"}, 
        {"font.display": ("Arial", 28, "bold")}
    )


class PotDisplay:
    def __init__(self) -> None:
        self._pot_bg_id = None
        self._pot_text_id = None
        self._pot_label_id = None
        self._chip_graphics = None
        self._pot_chips = []  # Track pot chip elements

    def render(self, state, canvas_manager, layer_manager) -> None:
        THEME, FONTS = _tokens(canvas_manager.canvas)
        c = canvas_manager.canvas
        w, h = canvas_manager.size()
        if w <= 1 or h <= 1:
            return
        
        # Initialize chip graphics if needed
        if self._chip_graphics is None:
            self._chip_graphics = ChipGraphics(c)
        
        center_x, center_y = w // 2, int(h * 0.58)
        
        # Get pot amount from state - handle both formats
        pot_data = state.get("pot", {})
        if isinstance(pot_data, dict):
            amount = int(pot_data.get("amount", 0))
        else:
            amount = int(pot_data or 0)
        
        text_value = f"${amount:,}" if amount > 0 else "$0"

        # Use theme tokens (prefer badge keys; fall back to legacy)
        text_fill = THEME.get("pot.valueText", THEME.get("text.primary", "#F6EFDD"))
        bg_fill = (THEME.get("pot.badgeBg") or
                   THEME.get("pot.bg") or "#15212B")
        border_color = (THEME.get("pot.badgeRing") or
                        THEME.get("pot.border") or "#C9B47A")
        font = FONTS.get("font.display", ("Arial", 24, "bold"))
        label_font = FONTS.get("font.body", ("Arial", 12, "normal"))

        # Pot background (rounded rectangle)
        bg_width, bg_height = 120, 50
        if not self._pot_bg_id:
            self._pot_bg_id = c.create_rectangle(
                center_x - bg_width//2,
                center_y - bg_height//2,
                center_x + bg_width//2,
                center_y + bg_height//2,
                fill=bg_fill,
                outline=border_color,
                width=2,
                tags=("layer:pot", "pot_bg"),
            )
        else:
            # Update background position and colors
            c.coords(
                self._pot_bg_id,
                center_x - bg_width//2,
                center_y - bg_height//2,
                center_x + bg_width//2,
                center_y + bg_height//2
            )
            c.itemconfig(self._pot_bg_id, fill=bg_fill, outline=border_color)

        # Pot label ("POT")
        if not self._pot_label_id:
            self._pot_label_id = c.create_text(
                center_x,
                center_y - 15,
                text="POT",
                font=label_font,
                fill=THEME.get("pot.label", "#9CA3AF"),
                tags=("layer:pot", "pot_label"),
            )
        else:
            c.coords(self._pot_label_id, center_x, center_y - 15)
            c.itemconfig(self._pot_label_id, fill=THEME.get("pot.label", "#9CA3AF"))

        # Pot amount
        if not self._pot_text_id:
            self._pot_text_id = c.create_text(
                center_x,
                center_y + 5,
                text=text_value,
                font=font,
                fill=text_fill,
                tags=("layer:pot", "pot_text"),
            )
        else:
            c.coords(self._pot_text_id, center_x, center_y + 5)
            c.itemconfig(self._pot_text_id, text=text_value, fill=text_fill, font=font)
            
        # Clear old pot chips
        for chip_id in self._pot_chips:
            try:
                c.delete(chip_id)
            except Exception:
                pass
        self._pot_chips = []
        
        # Render premium pot chips if amount > 0
        if amount > 0:
            self._render_premium_pot_chips(c, center_x, center_y, amount, THEME)
        
        # Ensure proper layering
        c.addtag_withtag("layer:pot", self._pot_bg_id or "")
        c.addtag_withtag("layer:pot", self._pot_label_id or "")
        c.addtag_withtag("layer:pot", self._pot_text_id or "")
        for chip_id in self._pot_chips:
            c.addtag_withtag("layer:pot", chip_id)

    def _render_premium_pot_chips(self, canvas, center_x: int, center_y: int, 
                                  amount: int, tokens: dict) -> None:
        """Render premium pot chips in an elegant arrangement around the pot."""
        if amount <= 0:
            return
        
        # Elegant chip arrangement around the pot badge
        chip_positions = [
            (center_x - 35, center_y + 25),   # Left
            (center_x + 35, center_y + 25),   # Right  
            (center_x - 20, center_y + 40),   # Left-center
            (center_x + 20, center_y + 40),   # Right-center
            (center_x, center_y + 45),        # Center bottom
        ]
        
        # Determine number of chip positions based on pot size
        if amount < 100:
            positions = chip_positions[:1]  # Just center
        elif amount < 500:
            positions = chip_positions[:3]  # Left, right, center
        else:
            positions = chip_positions  # All positions for big pots
        
        # Draw premium pot chips at each position
        chip_r = 12  # Slightly smaller for elegant clustering
        for i, (chip_x, chip_y) in enumerate(positions):
            # Vary chip values for visual interest
            if i == 0:  # Center/first chip gets highest value
                chip_value = min(amount // 2, 1000)
            else:
                chip_value = min(amount // len(positions), 500)
            
            if chip_value > 0:
                # Add subtle breathing effect for large pots
                breathing = amount > 1000
                chip_id = draw_pot_chip(
                    canvas, chip_x, chip_y, chip_value, tokens,
                    r=chip_r, breathing=breathing,
                    tags=("layer:pot", "pot_chips", f"pot_chip_{i}")
                )
                self._pot_chips.append(chip_id)

    def pulse_pot_increase(self, center_pos: tuple) -> None:
        """Trigger a pulsing glow effect when the pot increases."""
        # Get theme tokens for glow effect
        THEME, _ = _tokens(self._canvas if hasattr(self, '_canvas') else None)
        if THEME:
            pulse_pot_glow(self._canvas, center_pos, THEME, r=20, pulses=2)



```

---

### dealer_button.py

**Path**: `backend/ui/tableview/components/dealer_button.py`

```python
from ...state.selectors import (
    get_seat_positions,
    get_dealer_position,
)
from ...services.theme_manager import ThemeManager


def _tokens(canvas):
    # Prefer ThemeManager from widget tree
    w = canvas
    while w is not None:
        try:
            if hasattr(w, "services"):
                tm = w.services.get_app("theme")  # type: ignore[attr-defined]
                if isinstance(tm, ThemeManager):
                    return tm.get_theme(), tm.get_fonts()
        except Exception:
            pass
        w = getattr(w, "master", None)
    # Fallbacks
    return (
        {"dealer.buttonBg": "#FDE68A", "dealer.buttonFg": "#0B1220"}, 
        {"font.body": ("Arial", 12, "bold")}
    )


class DealerButton:
    def __init__(self):
        self._button_id = None
        self._text_id = None
    
    def render(self, state, canvas_manager, layer_manager) -> None:
        THEME, FONTS = _tokens(canvas_manager.canvas)
        c = canvas_manager.canvas
        w, h = canvas_manager.size()
        if w <= 1 or h <= 1:
            return
        
        # Get seat count from state - use direct seats array if available
        seats_data = state.get('seats', [])
        count = len(seats_data) if seats_data else 6  # Default to 6 seats
            
        dealer_pos = get_dealer_position(state)
        
        # Use consistent seat positions from geometry helper  
        positions = get_seat_positions(
            state, seat_count=count, 
            canvas_width=w, canvas_height=h
        )
        
        print(f"🏷️ DealerButton on {w}x{h}: {count} seats, "
              f"dealer pos: {dealer_pos}")
            
        if dealer_pos < 0 or dealer_pos >= len(positions):
            print(f"🏷️ Invalid dealer position {dealer_pos}, using 0")
            dealer_pos = 0
            
        seat_x, seat_y = positions[dealer_pos]
        
        # Position dealer button outside the seat, towards table center
        center_x, center_y = w // 2, int(h * 0.52)
        
        # Calculate direction from seat to center
        dx = center_x - seat_x
        dy = center_y - seat_y
        distance = (dx*dx + dy*dy) ** 0.5
        
        if distance > 0:
            # Normalize and position button closer to table center
            offset = 25  # Distance from seat center
            button_x = seat_x + (dx / distance) * offset
            button_y = seat_y + (dy / distance) * offset
        else:
            button_x, button_y = seat_x + 25, seat_y
        
        # Make dealer button more prominent
        button_radius = int(min(w, h) * 0.025)  # Larger button
        
        # Dealer button background with border
        if not self._button_id:
            self._button_id = c.create_oval(
                button_x - button_radius,
                button_y - button_radius,
                button_x + button_radius,
                button_y + button_radius,
                fill=THEME.get("dealer.buttonBg", "#FDE68A"),
                outline=THEME.get("dealer.buttonBorder", "#D97706"),
                width=2,
                tags=("layer:seats", "dealer_button"),
            )
        else:
            c.coords(
                self._button_id,
                button_x - button_radius,
                button_y - button_radius,
                button_x + button_radius,
                button_y + button_radius
            )
            c.itemconfig(
                self._button_id,
                fill=THEME.get("dealer.buttonBg", "#FDE68A"),
                outline=THEME.get("dealer.buttonBorder", "#D97706")
            )
        
        # Dealer button text
        if not self._text_id:
            self._text_id = c.create_text(
                button_x,
                button_y,
                text="D",
                font=FONTS.get("font.body", ("Arial", 14, "bold")),
                fill=THEME.get("dealer.buttonFg", "#0B1220"),
                tags=("layer:seats", "dealer_button_label"),
            )
        else:
            c.coords(self._text_id, button_x, button_y)
            c.itemconfig(
                self._text_id,
                fill=THEME.get("dealer.buttonFg", "#0B1220")
            )
        
        # Ensure proper layering
        c.addtag_withtag("layer:seats", self._button_id or "")
        c.addtag_withtag("layer:seats", self._text_id or "")



```

---

### table_felt.py

**Path**: `backend/ui/tableview/components/table_felt.py`

```python
from ...services.theme_manager import ThemeManager


class TableFelt:
    def render(self, state, canvas_manager, layer_manager) -> None:
        # Persisted theme via ThemeManager
        # Note: We locate the theme service via the parent Frame stored on canvas
        # Find ThemeManager by walking up the widget tree
        theme_service = None
        w = canvas_manager.canvas
        while w is not None and theme_service is None:
            try:
                if hasattr(w, "services"):
                    theme_service = w.services.get_app("theme")  # type: ignore[attr-defined]
                    break
            except Exception:
                pass
            w = getattr(w, "master", None)
        if isinstance(theme_service, ThemeManager):
            THEME = theme_service.get_theme()
        else:
            THEME = {"table.felt": "#2B2F36", "table_rail": None}
        c = canvas_manager.canvas
        if c is None:
            return
        w, h = canvas_manager.size()
        
        # Validate dimensions; skip if not ready to avoid small remnants
        if w <= 100 or h <= 100:
            print(f"⚠️ TableFelt: Skipping render - invalid size {w}x{h}")
            return
            
        felt_color = THEME.get("table.felt", THEME.get("table_felt", "#1B4D3A"))
        rail_color = THEME.get("table.rail", THEME.get("table_rail", "#2E4F76"))
        edge_glow = THEME.get("table.edgeGlow", "#0B2F24")
        inlay_color = THEME.get("table.inlay", "#C6A664")
        
        print(f"🎨 Professional TableFelt rendering: {w}x{h}, felt: {felt_color}, rail: {rail_color}")
        
        # === CLEAR OLD LAYERS TO PREVENT COLOR CARRY-OVER ===
        c.delete("layer:felt")
        c.delete("canvas_bg")
        c.delete("table_rail")
        c.delete("rail_accent")
        c.delete("felt_surface")
        c.delete("center_highlight")
        c.delete("edge_glow")
        
        # === PROFESSIONAL OVAL POKER TABLE (MATCHING OLD UI SCREENSHOT) ===
        
        # Get additional theme colors for professional look
        rail_highlight = THEME.get("table.railHighlight", "#DAA520")  # Gold accents
        center_color = THEME.get("table.center", "#154035")  # Center highlight
        
        # Table center and sizing for oval shape
        cx, cy = w//2, h//2
        
        # 1. Background canvas (very dark)  
        c.create_rectangle(
            0, 0, w, h,
            fill=THEME.get("primary_bg", "#0A1A0A"),
            outline="",
            tags=("layer:felt", "canvas_bg"),
        )
        
        # 2. Professional oval table rail (bronze/copper) - main table shape
        rail_width = min(w-60, int(h*1.6)) // 2  # Proper oval proportions
        rail_height = min(h-60, int(w*0.6)) // 2
        c.create_oval(
            cx - rail_width, cy - rail_height, 
            cx + rail_width, cy + rail_height,
            fill=rail_color,
            outline="",
            tags=("layer:felt", "table_rail"),
        )
        
        # 3. Gold accent lines on rail (matching screenshot)
        c.create_oval(
            cx - rail_width + 8, cy - rail_height + 8,
            cx + rail_width - 8, cy + rail_height - 8,
            fill="", 
            outline=rail_highlight, 
            width=3,
            tags=("layer:felt", "rail_accent"),
        )
        
        # 4. Outer edge glow (dark border for depth)
        felt_width = rail_width - 22
        felt_height = rail_height - 22
        c.create_oval(
            cx - felt_width - 2, cy - felt_height - 2,
            cx + felt_width + 2, cy + felt_height + 2,
            fill="", 
            outline=edge_glow, 
            width=2,
            tags=("layer:felt", "edge_glow"),
        )
        
        # 5. Main oval felt surface (deep professional green)
        c.create_oval(
            cx - felt_width, cy - felt_height,
            cx + felt_width, cy + felt_height,
            fill=felt_color,
            outline="",
            tags=("layer:felt", "felt_main"),
        )
        
        # 5.5. Soft edge vignette for Monet midnight gradient effect
        # Four translucent rectangles for velvet rim under low light
        vignette_width = 20
        c.create_rectangle(0, 0, w, vignette_width, 
                          fill=edge_glow, outline="", stipple="gray25", 
                          tags=("layer:felt", "vignette_top"))
        c.create_rectangle(0, h-vignette_width, w, h, 
                          fill=edge_glow, outline="", stipple="gray25", 
                          tags=("layer:felt", "vignette_bottom"))
        c.create_rectangle(0, 0, vignette_width, h, 
                          fill=edge_glow, outline="", stipple="gray25", 
                          tags=("layer:felt", "vignette_left"))
        c.create_rectangle(w-vignette_width, 0, w, h, 
                          fill=edge_glow, outline="", stipple="gray25", 
                          tags=("layer:felt", "vignette_right"))
        
        # 6. Subtle center oval for community cards (like screenshot)
        center_width = min(180, felt_width // 2)
        center_height = min(90, felt_height // 3)
        c.create_oval(
            cx - center_width, cy - center_height,
            cx + center_width, cy + center_height,
            fill="", 
            outline=center_color, 
            width=1,
            tags=("layer:felt", "center_oval"),
        )
        
        # 7. Professional inlay accents (6 decorative spots around table)
        import math
        for i, angle in enumerate([0, 60, 120, 180, 240, 300]):
            rad = math.radians(angle)
            accent_x = cx + (felt_width * 0.75) * math.cos(rad)
            accent_y = cy + (felt_height * 0.75) * math.sin(rad)
            c.create_oval(
                accent_x-4, accent_y-4, accent_x+4, accent_y+4,
                fill=inlay_color,
                outline="",
                tags=("layer:felt", f"inlay_accent_{i}"),
            )


```

---

### enhanced_cards.py

**Path**: `backend/ui/tableview/components/enhanced_cards.py`

```python
"""
Enhanced Card Graphics with Token-Driven Colors
Professional card rendering using the complete theme token system
"""

import math

class EnhancedCards:
    def __init__(self, theme_manager):
        self.theme = theme_manager
        
    # Suit symbols
    SUIT_SYMBOLS = {
        'h': '♥', 'd': '♦', 'c': '♣', 's': '♠'
    }
    
    def draw_card_face(self, canvas, x, y, rank, suit, w=58, h=82, tags=None):
        """Draw a face-up card with token-driven colors"""
        tokens = self.theme.get_all_tokens()
        
        # Card colors from tokens
        bg = tokens.get("card.face.bg", "#F8F8FF")
        border = tokens.get("card.face.border", "#2F4F4F")
        pip_red = tokens.get("card.pip.red", "#DC2626")
        pip_black = tokens.get("card.pip.black", "#111827")
        
        # Determine suit color
        suit_color = pip_red if suit.lower() in ('h', 'd') else pip_black
        suit_symbol = self.SUIT_SYMBOLS.get(suit.lower(), '?')
        
        # Create tags
        card_tags = ["card_face"]
        if tags:
            card_tags.extend(tags)
        
        # Main card rectangle with rounded corners effect
        canvas.create_rectangle(
            x, y, x + w, y + h,
            fill=bg, outline=border, width=2,
            tags=tuple(card_tags)
        )
        
        # Inner border for depth
        canvas.create_rectangle(
            x + 2, y + 2, x + w - 2, y + h - 2,
            fill="", outline=border, width=1,
            tags=tuple(card_tags)
        )
        
        # Calculate font sizes based on card size
        rank_font_size = max(10, w // 5)
        suit_font_size = max(8, w // 6)
        center_font_size = max(14, w // 3)
        
        # Top-left rank and suit
        canvas.create_text(
            x + w//8, y + h//8,
            text=rank, font=("Inter", rank_font_size, "bold"),
            fill=suit_color, anchor="nw", tags=tuple(card_tags)
        )
        
        canvas.create_text(
            x + w//8, y + h//8 + rank_font_size + 2,
            text=suit_symbol, font=("Inter", suit_font_size, "bold"),
            fill=suit_color, anchor="nw", tags=tuple(card_tags)
        )
        
        # Center suit symbol (larger)
        canvas.create_text(
            x + w//2, y + h//2,
            text=suit_symbol, font=("Inter", center_font_size, "bold"),
            fill=suit_color, anchor="center", tags=tuple(card_tags)
        )
        
        # Bottom-right rank and suit (rotated appearance)
        canvas.create_text(
            x + w - w//8, y + h - h//8,
            text=rank, font=("Inter", rank_font_size, "bold"),
            fill=suit_color, anchor="se", tags=tuple(card_tags)
        )
        
        canvas.create_text(
            x + w - w//8, y + h - h//8 - rank_font_size - 2,
            text=suit_symbol, font=("Inter", suit_font_size, "bold"),
            fill=suit_color, anchor="se", tags=tuple(card_tags)
        )
        
        return card_tags
    
    def draw_card_back(self, canvas, x, y, w=58, h=82, tags=None):
        """Draw a face-down card back with theme integration"""
        tokens = self.theme.get_all_tokens()
        
        # Card back colors from tokens
        bg = tokens.get("card.back.bg", "#7F1D1D")
        border = tokens.get("card.back.border", "#2F4F4F")
        pattern = tokens.get("card.back.pattern", "#991B1B")
        
        # Create tags
        card_tags = ["card_back"]
        if tags:
            card_tags.extend(tags)
        
        # Main card rectangle
        canvas.create_rectangle(
            x, y, x + w, y + h,
            fill=bg, outline=border, width=2,
            tags=tuple(card_tags)
        )
        
        # Inner border for depth
        canvas.create_rectangle(
            x + 2, y + 2, x + w - 2, y + h - 2,
            fill="", outline=pattern, width=1,
            tags=tuple(card_tags)
        )
        
        # Diamond lattice pattern
        step = max(6, w // 8)
        for i in range(0, w + step, step):
            # Diagonal lines creating diamond pattern
            canvas.create_line(
                x + i, y, x, y + i,
                fill=pattern, width=1, tags=tuple(card_tags)
            )
            canvas.create_line(
                x + w - i, y, x + w, y + i,
                fill=pattern, width=1, tags=tuple(card_tags)
            )
            canvas.create_line(
                x + i, y + h, x, y + h - i,
                fill=pattern, width=1, tags=tuple(card_tags)
            )
            canvas.create_line(
                x + w - i, y + h, x + w, y + h - i,
                fill=pattern, width=1, tags=tuple(card_tags)
            )
        
        # Center decorative element
        center_size = min(w, h) // 4
        canvas.create_rectangle(
            x + w//2 - center_size//2, y + h//2 - center_size//4,
            x + w//2 + center_size//2, y + h//2 + center_size//4,
            fill="", outline=pattern, width=1,
            tags=tuple(card_tags)
        )
        
        return card_tags
    
    def draw_community_board(self, canvas, tokens, slots=5, card_w=58, gap=8):
        """Draw community card area with token-driven styling"""
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        
        # Calculate board position
        x0, y0 = w * 0.5, h * 0.4
        total_w = slots * card_w + (slots - 1) * gap
        left = x0 - total_w / 2
        top = y0 - 4
        height = card_w * 0.2
        
        # Board colors from tokens
        slot_bg = tokens.get("board.slotBg", "#334155")
        border_color = tokens.get("board.border", "#475569")
        shadow_color = tokens.get("board.shadow", "#1E293B")
        
        # Clear previous board
        canvas.delete("board:underlay")
        
        # Shadow (offset slightly)
        canvas.create_rectangle(
            left - 8, top - 8, left + total_w + 12, top + height + 12,
            fill=shadow_color, outline="",
            tags=("board:underlay", "board_shadow")
        )
        
        # Main underlay
        canvas.create_rectangle(
            left - 10, top - 10, left + total_w + 10, top + height + 10,
            fill=slot_bg, outline=border_color, width=2,
            tags=("board:underlay", "board_main")
        )
        
        # Individual card slots
        for i in range(slots):
            slot_x = left + i * (card_w + gap)
            slot_y = top - card_w * 0.6
            
            # Slot outline
            canvas.create_rectangle(
                slot_x - 2, slot_y - 2, slot_x + card_w + 2, slot_y + card_w * 1.4 + 2,
                fill="", outline=border_color, width=1, stipple="gray25",
                tags=("board:underlay", f"slot_{i}")
            )
    
    def animate_card_flip(self, canvas, x, y, w, h, from_card, to_card, callback=None):
        """Animate card flip with token-aware colors"""
        flip_steps = 10
        
        def flip_step(step):
            if step >= flip_steps:
                if callback:
                    callback()
                return
            
            # Calculate flip progress (0 to 1)
            progress = step / flip_steps
            
            # Clear previous flip frame
            canvas.delete("card_flip")
            
            if progress < 0.5:
                # First half: shrink to nothing (show original card)
                scale = 1 - (progress * 2)
                scaled_w = int(w * scale)
                
                if scaled_w > 0:
                    if from_card and from_card != "XX":
                        rank, suit = from_card[:-1], from_card[-1]
                        self.draw_card_face(canvas, x + (w - scaled_w)//2, y, 
                                          rank, suit, scaled_w, h, ["card_flip"])
                    else:
                        self.draw_card_back(canvas, x + (w - scaled_w)//2, y, 
                                          scaled_w, h, ["card_flip"])
            else:
                # Second half: grow from nothing (show new card)
                scale = (progress - 0.5) * 2
                scaled_w = int(w * scale)
                
                if scaled_w > 0:
                    if to_card and to_card != "XX":
                        rank, suit = to_card[:-1], to_card[-1]
                        self.draw_card_face(canvas, x + (w - scaled_w)//2, y,
                                          rank, suit, scaled_w, h, ["card_flip"])
                    else:
                        self.draw_card_back(canvas, x + (w - scaled_w)//2, y,
                                          scaled_w, h, ["card_flip"])
            
            # Schedule next step
            canvas.after(40, lambda: flip_step(step + 1))
        
        flip_step(0)
    
    def add_card_glow(self, canvas, x, y, w, h, glow_type="soft"):
        """Add subtle glow effect around card"""
        tokens = self.theme.get_all_tokens()
        glow_color = tokens.get(f"glow.{glow_type}", tokens.get("a11y.focus", "#22C55E"))
        
        # Create glow effect with multiple rings
        for i in range(3):
            offset = (i + 1) * 2
            canvas.create_rectangle(
                x - offset, y - offset, x + w + offset, y + h + offset,
                fill="", outline=glow_color, width=1,
                tags=("card_glow",)
            )
    
    def clear_card_effects(self, canvas):
        """Clear all card animation and effect elements"""
        canvas.delete("card_flip")
        canvas.delete("card_glow")

```

---

## TABLE COMPONENTS - ANIMATIONS

### chip_animations.py

**Path**: `backend/ui/tableview/components/chip_animations.py`

```python
"""
Chip Animation System - Flying Chips for Bet→Pot and Pot→Winner
Token-driven animations with smooth easing and particle effects
"""

import math
from ...services.theme_utils import ease_in_out_cubic

class ChipAnimations:
    def __init__(self, theme_manager):
        self.theme = theme_manager
        self.active_animations = {}
        
    def draw_chip(self, canvas, x, y, denom_key, text="", r=14, tags=None):
        """Draw a single chip with token-driven colors"""
        tokens = self.theme.get_all_tokens()
        
        # Get chip colors from tokens
        chip_color = tokens.get(denom_key, "#2E86AB")  # Default to $1 blue
        rim_color = tokens.get("chip.rim", "#000000")
        text_color = tokens.get("chip.text", "#F8F7F4")
        
        chip_tags = ["chip"]
        if tags:
            chip_tags.extend(tags)
        
        # Main chip circle
        chip_id = canvas.create_oval(
            x - r, y - r, x + r, y + r,
            fill=chip_color, outline=rim_color, width=2,
            tags=tuple(chip_tags)
        )
        
        # Inner ring for depth
        inner_r = r - 3
        canvas.create_oval(
            x - inner_r, y - inner_r, x + inner_r, y + inner_r,
            fill="", outline=rim_color, width=1,
            tags=tuple(chip_tags)
        )
        
        # Value text (if provided)
        if text:
            canvas.create_text(
                x, y, text=text, fill=text_color,
                font=("Inter", 8, "bold"), anchor="center",
                tags=tuple(chip_tags)
            )
        
        return chip_id
    
    def stack_height(self, amount):
        """Calculate stack height based on amount"""
        return min(8, max(1, int(amount / 50)))  # 50 units per chip
    
    def draw_chip_stack(self, canvas, x, y, amount, tags=None):
        """Draw a stack of chips representing the total value"""
        if amount <= 0:
            return []
        
        # Determine chip denominations to show
        denom_keys = ["chip.$1", "chip.$5", "chip.$25", "chip.$100", "chip.$500", "chip.$1k"]
        levels = self.stack_height(amount)
        
        chip_ids = []
        for i in range(levels):
            # Cycle through denominations for visual variety
            denom = denom_keys[i % len(denom_keys)]
            chip_y = y - (i * 4)  # Stack with 4px offset
            
            chip_id = self.draw_chip(canvas, x, chip_y, denom, tags=tags)
            chip_ids.append(chip_id)
        
        return chip_ids
    
    def fly_chips_to_pot(self, canvas, from_x, from_y, to_x, to_y, amount, callback=None):
        """Animate chips flying from player bet area to pot - ONLY at end of street"""
        animation_id = f"bet_to_pot_{from_x}_{from_y}"
        tokens = self.theme.get_all_tokens()
        
        # Create temporary chips for animation with proper denominations
        chip_plan = self._break_down_amount(amount)
        chip_ids = []
        
        for i, denom in enumerate(chip_plan):
            # Slight spread for natural look
            start_x = from_x + (i - len(chip_plan)//2) * 8
            start_y = from_y + (i - len(chip_plan)//2) * 4
            
            # Create chip with proper denomination and label
            chip_size = 12  # Standard chip size for animations
            chip_id = self._create_chip_with_label(canvas, start_x, start_y, denom, 
                                                 tokens, chip_size, tags=["flying_chip", "temp_animation"])
            chip_ids.append((chip_id, start_x, start_y, denom))
        
        # Animation parameters - slower for visibility
        frames = 30  # Increased from 20 for better visibility
        
        def animate_step(frame):
            if frame >= frames:
                # Animation complete
                self._cleanup_flying_chips(canvas, chip_ids)
                if animation_id in self.active_animations:
                    del self.active_animations[animation_id]
                if callback:
                    callback()
                return
            
            # Calculate progress with easing
            progress = frame / frames
            eased_progress = ease_in_out_cubic(progress)
            
            # Update each chip position
            for i, (chip_id, start_x, start_y, denom) in enumerate(chip_ids):
                # Calculate current position with slight arc
                current_x = start_x + (to_x - start_x) * eased_progress
                current_y = start_y + (to_y - start_y) * eased_progress
                
                # Add arc effect (parabolic path)
                arc_height = 30 * math.sin(progress * math.pi)
                current_y -= arc_height
                
                # Add slight randomness for natural movement
                wobble_x = math.sin(frame * 0.3 + i) * 3
                wobble_y = math.cos(frame * 0.2 + i) * 2
                
                # Update chip position
                try:
                    canvas.coords(chip_id, 
                                current_x + wobble_x - 14, current_y + wobble_y - 14,
                                current_x + wobble_x + 14, current_y + wobble_y + 14)
                except:
                    pass  # Chip may have been deleted
            
            # Add motion blur/glow effect
            if frame % 2 == 0:  # Every 2nd frame for more glow
                glow_color = tokens.get("bet.glow", "#FFD700")
                for _, (chip_id, _, _, _) in enumerate(chip_ids):
                    try:
                        bbox = canvas.bbox(chip_id)
                        if bbox:
                            x1, y1, x2, y2 = bbox
                            canvas.create_oval(
                                x1 - 4, y1 - 4, x2 + 4, y2 + 4,
                                outline=glow_color, width=2,
                                tags=("motion_glow", "temp_animation")
                            )
                    except:
                        pass
            
            # Schedule next frame - slower for visibility
            canvas.after(80, lambda: animate_step(frame + 1))  # Increased from 40ms
        
        self.active_animations[animation_id] = animate_step
        animate_step(0)
    
    def fly_pot_to_winner(self, canvas, pot_x, pot_y, winner_x, winner_y, amount, callback=None):
        """Animate pot chips flying to winner with celebration effect"""
        animation_id = f"pot_to_winner_{winner_x}_{winner_y}"
        tokens = self.theme.get_all_tokens()
        
        # Create explosion of chips from pot
        explosion_positions = []
        num_stacks = 6
        
        for i in range(num_stacks):
            angle = (i / num_stacks) * 2 * math.pi
            radius = 30
            exp_x = pot_x + radius * math.cos(angle)
            exp_y = pot_y + radius * math.sin(angle)
            explosion_positions.append((exp_x, exp_y))
        
        # Create chip stacks for animation
        all_chip_ids = []
        for exp_x, exp_y in explosion_positions:
            stack_chips = self.draw_chip_stack(canvas, exp_x, exp_y, amount // num_stacks,
                                             tags=["flying_chip", "temp_animation"])
            all_chip_ids.extend([(chip_id, exp_x, exp_y) for chip_id in stack_chips])
        
        frames = 30
        
        def animate_step(frame):
            if frame >= frames:
                # Show winner celebration
                self._show_winner_celebration(canvas, winner_x, winner_y, tokens)
                self._cleanup_flying_chips(canvas, all_chip_ids)
                if animation_id in self.active_animations:
                    del self.active_animations[animation_id]
                if callback:
                    callback()
                return
            
            progress = frame / frames
            eased_progress = ease_in_out_cubic(progress)
            
            # Move all chips toward winner
            for chip_id, start_x, start_y in all_chip_ids:
                # Calculate trajectory with arc
                current_x = start_x + (winner_x - start_x) * eased_progress
                current_y = start_y + (winner_y - start_y) * eased_progress
                
                # Higher arc for dramatic effect
                arc_height = 40 * math.sin(progress * math.pi)
                current_y -= arc_height
                
                try:
                    canvas.coords(chip_id,
                                current_x - 14, current_y - 14,
                                current_x + 14, current_y + 14)
                except:
                    pass
            
            canvas.after(35, lambda: animate_step(frame + 1))
        
        self.active_animations[animation_id] = animate_step
        animate_step(0)
    
    def place_bet_chips(self, canvas, x, y, amount, tokens, tags=()):
        """Place bet chips in front of player (NOT flying to pot) - for betting rounds"""
        # Get chip size from sizing system if available
        chip_size = 14  # Default fallback
        if hasattr(self, 'theme') and hasattr(self.theme, 'get_all_tokens'):
            try:
                # Try to get sizing system from theme
                sizing_system = getattr(self.theme, 'sizing_system', None)
                if sizing_system:
                    chip_size = sizing_system.get_chip_size('bet')
            except Exception:
                pass
        
        chip_plan = self._break_down_amount(amount)
        chip_ids = []
        
        # Position chips in a neat stack in front of player
        for i, denom in enumerate(chip_plan):
            chip_x = x + (i - len(chip_plan)//2) * 6  # Horizontal spread
            chip_y = y - (i * 3)  # Vertical stack
            
            # Create chip with denomination label
            chip_id = self._create_chip_with_label(canvas, chip_x, chip_y, denom, 
                                                 tokens, chip_size, tags=tags + (f"bet_chip_{i}",))
            chip_ids.append(chip_id)
        
        # Add total amount label above the chips
        label_y = y - (len(chip_plan) * 3) - 20
        
        # Get text size from sizing system if available
        text_size = 12  # Default fallback
        if hasattr(self, 'theme') and hasattr(self.theme, 'get_all_tokens'):
            try:
                sizing_system = getattr(self.theme, 'sizing_system', None)
                if sizing_system:
                    text_size = sizing_system.get_text_size('bet_amount')
            except Exception:
                pass
        
        label_id = canvas.create_text(
            x, label_y,
            text=f"${amount}",
            font=("Arial", text_size, "bold"),
            fill="#FFFFFF",
            tags=tags + ("bet_label",)
        )
        
        return chip_ids + [label_id]
    
    def _create_chip_with_label(self, canvas, x, y, denom, tokens, chip_size, tags=()):
        """Create a chip with denomination label"""
        # Get chip colors based on denomination
        bg_color, ring_color, text_color = self._get_chip_colors(denom, tokens)
        
        # Create chip body
        chip_id = canvas.create_oval(
            x - chip_size, y - chip_size, x + chip_size, y + chip_size,
            fill=bg_color, outline=ring_color, width=2,
            tags=tags
        )
        
        # Get text size from sizing system if available
        text_size = max(8, int(chip_size * 0.4))  # Default proportional sizing
        if hasattr(self, 'theme') and hasattr(self.theme, 'get_all_tokens'):
            try:
                sizing_system = getattr(self.theme, 'sizing_system', None)
                if sizing_system:
                    text_size = sizing_system.get_text_size('action_label')
            except Exception:
                pass
        
        # Create denomination label
        label_id = canvas.create_text(
            x, y,
            text=f"${denom}",
            font=("Arial", text_size, "bold"),
            fill=text_color,
            tags=tags
        )
        
        return chip_id
    
    def _get_chip_colors(self, denom, tokens):
        """Get appropriate colors for chip denomination"""
        if denom >= 1000:
            return "#2D1B69", "#FFD700", "#FFFFFF"  # Purple with gold ring
        elif denom >= 500:
            return "#8B0000", "#FFD700", "#FFFFFF"  # Red with gold ring
        elif denom >= 100:
            return "#006400", "#FFFFFF", "#FFFFFF"  # Green with white ring
        elif denom >= 25:
            return "#4169E1", "#FFFFFF", "#FFFFFF"  # Blue with white ring
        else:
            return "#FFFFFF", "#000000", "#000000"  # White with black ring
    
    def _break_down_amount(self, amount):
        """Break down amount into chip denominations"""
        denominations = [1000, 500, 100, 25, 5, 1]
        chip_plan = []
        remaining = amount
        
        for denom in denominations:
            if remaining >= denom:
                count = min(remaining // denom, 5)  # Max 5 chips per denomination
                chip_plan.extend([denom] * count)
                remaining -= denom * count
                
            if len(chip_plan) >= 8:  # Max 8 chips total
                break
        
        # If we still have remaining, add smaller denominations
        if remaining > 0 and len(chip_plan) < 8:
            remaining_space = 8 - len(chip_plan)
            chip_plan.extend([1] * min(remaining_space, remaining))
        
        return chip_plan
    
    def _show_winner_celebration(self, canvas, x, y, tokens):
        """Show celebration effect at winner position"""
        celebration_color = tokens.get("label.winner.bg", "#FFD700")
        
        # Create particle burst
        for i in range(12):
            angle = (i / 12) * 2 * math.pi
            
            # Particle trajectory
            end_x = x + 60 * math.cos(angle)
            end_y = y + 60 * math.sin(angle)
            
            # Create particle
            particle_id = canvas.create_oval(
                x - 3, y - 3, x + 3, y + 3,
                fill=celebration_color, outline="",
                tags=("celebration_particle", "temp_animation")
            )
            
            # Animate particle outward
            self._animate_particle(canvas, particle_id, x, y, end_x, end_y)
        
        # Winner text flash
        canvas.create_text(
            x, y - 40, text="WINNER!", 
            font=("Inter", 18, "bold"), fill=celebration_color,
            tags=("winner_flash", "temp_animation")
        )
        
        # Auto-cleanup after 2 seconds
        canvas.after(2000, lambda: canvas.delete("celebration_particle", "winner_flash"))
    
    def _animate_particle(self, canvas, particle_id, start_x, start_y, end_x, end_y):
        """Animate a single celebration particle"""
        frames = 15
        
        def particle_step(frame):
            if frame >= frames:
                try:
                    canvas.delete(particle_id)
                except:
                    pass
                return
            
            progress = frame / frames
            current_x = start_x + (end_x - start_x) * progress
            current_y = start_y + (end_y - start_y) * progress
            
            try:
                canvas.coords(particle_id,
                            current_x - 3, current_y - 3,
                            current_x + 3, current_y + 3)
            except:
                pass
            
            canvas.after(30, lambda: particle_step(frame + 1))
        
        particle_step(0)
    
    def _cleanup_flying_chips(self, canvas, chip_ids):
        """Clean up temporary animation chips"""
        for chip_data in chip_ids:
            if isinstance(chip_data, tuple):
                chip_id = chip_data[0]
            else:
                chip_id = chip_data
            try:
                canvas.delete(chip_id)
            except:
                pass
        
        # Clean up motion effects
        canvas.delete("motion_glow")
    
    def pulse_pot(self, canvas, pot_x, pot_y, tokens):
        """Subtle pot pulse when amount increases"""
        glow_color = tokens.get("glow.medium", "#FFD700")
        
        def pulse_step(radius, intensity):
            if intensity <= 0:
                canvas.delete("pot_pulse")
                return
            
            # Create expanding ring
            canvas.create_oval(
                pot_x - radius, pot_y - radius,
                pot_x + radius, pot_y + radius,
                outline=glow_color, width=2,
                tags=("pot_pulse", "temp_animation")
            )
            
            canvas.after(60, lambda: pulse_step(radius + 8, intensity - 1))
        
        pulse_step(20, 5)
    
    def stop_all_animations(self):
        """Stop all active chip animations"""
        self.active_animations.clear()
    
    def cleanup_temp_elements(self, canvas):
        """Clean up all temporary animation elements"""
        canvas.delete("temp_animation")
        canvas.delete("flying_chip")
        canvas.delete("motion_glow")
        canvas.delete("pot_pulse")

```

---

### chip_graphics.py

**Path**: `backend/ui/tableview/components/chip_graphics.py`

```python
"""
Luxury Themed Chip Graphics System
Renders poker chips with theme-aware styling for bets, calls, and pot displays.
"""
import math
import tkinter as tk
from typing import Dict, List, Tuple, Optional
from ...services.theme_manager import ThemeManager


def _tokens(canvas):
    """Get theme tokens and fonts from widget tree."""
    w = canvas
    while w is not None:
        try:
            if hasattr(w, "services"):
                tm = w.services.get_app("theme")
                if isinstance(tm, ThemeManager):
                    return tm.get_theme(), tm.get_fonts()
        except Exception:
            pass
        w = getattr(w, "master", None)
    # Fallbacks
    return ({"chip.primary": "#DAA520", "chip.secondary": "#8B4513"}, {"body": ("Arial", 10, "bold")})


class ChipGraphics:
    """Renders luxury themed poker chips with animations."""
    
    def __init__(self, canvas):
        self.canvas = canvas
        self.chip_stacks = {}  # Track chip positions for animations
        self.animation_queue = []  # Queue for chip animations
        
    def get_chip_colors_for_value(self, value: int, theme: Dict) -> Tuple[str, str, str]:
        """Get themed chip colors based on value."""
        # Standard poker chip color scheme with theme variations
        if value >= 1000:
            # High value - use theme's luxury colors
            return (
                theme.get("chip.luxury.bg", "#2D1B69"),      # Deep purple/navy
                theme.get("chip.luxury.ring", "#FFD700"),    # Gold ring
                theme.get("chip.luxury.accent", "#E6E6FA")   # Light accent
            )
        elif value >= 500:
            # Medium-high value - theme primary colors
            return (
                theme.get("chip.high.bg", "#8B0000"),        # Deep red
                theme.get("chip.high.ring", "#FFD700"),      # Gold ring
                theme.get("chip.high.accent", "#FFFFFF")     # White accent
            )
        elif value >= 100:
            # Medium value - theme secondary colors
            return (
                theme.get("chip.medium.bg", "#006400"),      # Forest green
                theme.get("chip.medium.ring", "#FFFFFF"),    # White ring
                theme.get("chip.medium.accent", "#90EE90")   # Light green accent
            )
        elif value >= 25:
            # Low-medium value
            return (
                theme.get("chip.low.bg", "#4169E1"),         # Royal blue
                theme.get("chip.low.ring", "#FFFFFF"),       # White ring
                theme.get("chip.low.accent", "#ADD8E6")      # Light blue accent
            )
        else:
            # Lowest value - theme accent colors
            return (
                theme.get("chip.minimal.bg", "#FFFFFF"),     # White
                theme.get("chip.minimal.ring", "#000000"),   # Black ring
                theme.get("chip.minimal.accent", "#D3D3D3")  # Light gray accent
            )
    
    def render_chip(self, x: int, y: int, value: int, chip_type: str = "bet", 
                   size: int = 20, tags: Tuple = ()) -> List[int]:
        """Render a single luxury themed chip."""
        theme, fonts = _tokens(self.canvas)
        
        # Get themed colors for this chip value
        bg_color, ring_color, accent_color = self.get_chip_colors_for_value(value, theme)
        
        # Adjust colors based on chip type
        if chip_type == "pot":
            # Pot chips get special treatment with theme's pot colors
            bg_color = theme.get("pot.chipBg", bg_color)
            ring_color = theme.get("pot.badgeRing", ring_color)
        elif chip_type == "call":
            # Call chips get muted colors
            bg_color = theme.get("chip.call.bg", "#6B7280")
            ring_color = theme.get("chip.call.ring", "#9CA3AF")
        
        elements = []
        
        # Main chip body with luxury gradient effect
        chip_id = self.canvas.create_oval(
            x - size, y - size,
            x + size, y + size,
            fill=bg_color,
            outline=ring_color,
            width=3,
            tags=tags + ("chip", f"chip_{chip_type}")
        )
        elements.append(chip_id)
        
        # Inner highlight for 3D effect
        highlight_size = size - 4
        highlight_id = self.canvas.create_oval(
            x - highlight_size, y - highlight_size + 2,
            x + highlight_size, y - highlight_size + 8,
            fill=accent_color,
            outline="",
            tags=tags + ("chip_highlight",)
        )
        elements.append(highlight_id)
        
        # Luxury center pattern based on theme
        pattern_color = theme.get("chip.pattern", ring_color)
        
        # Theme-specific chip patterns
        theme_name = theme.get("_theme_name", "default")
        if "monet" in theme_name.lower():
            # Impressionist water lily pattern
            for angle in [0, 60, 120, 180, 240, 300]:
                rad = math.radians(angle)
                px = x + (size // 3) * math.cos(rad)
                py = y + (size // 3) * math.sin(rad)
                dot_id = self.canvas.create_oval(
                    px - 2, py - 2, px + 2, py + 2,
                    fill=pattern_color, outline="",
                    tags=tags + ("chip_pattern",)
                )
                elements.append(dot_id)
                
        elif "caravaggio" in theme_name.lower():
            # Baroque cross pattern
            cross_size = size // 2
            # Vertical line
            line1_id = self.canvas.create_line(
                x, y - cross_size, x, y + cross_size,
                fill=pattern_color, width=2,
                tags=tags + ("chip_pattern",)
            )
            elements.append(line1_id)
            # Horizontal line
            line2_id = self.canvas.create_line(
                x - cross_size, y, x + cross_size, y,
                fill=pattern_color, width=2,
                tags=tags + ("chip_pattern",)
            )
            elements.append(line2_id)
            
        elif "klimt" in theme_name.lower():
            # Art Nouveau geometric pattern
            square_size = size // 3
            square_id = self.canvas.create_rectangle(
                x - square_size, y - square_size,
                x + square_size, y + square_size,
                fill="", outline=pattern_color, width=2,
                tags=tags + ("chip_pattern",)
            )
            elements.append(square_id)
            
        else:
            # Default diamond pattern
            diamond_size = size // 2
            diamond_points = [
                x, y - diamond_size,  # Top
                x + diamond_size, y,  # Right
                x, y + diamond_size,  # Bottom
                x - diamond_size, y   # Left
            ]
            diamond_id = self.canvas.create_polygon(
                diamond_points,
                fill="", outline=pattern_color, width=2,
                tags=tags + ("chip_pattern",)
            )
            elements.append(diamond_id)
        
        # Value text (for larger chips)
        if size >= 15 and value >= 5:
            font_size = max(8, size // 3)
            text_font = (fonts.get("body", ("Arial", 10))[0], font_size, "bold")
            
            # Format value display
            if value >= 1000:
                display_value = f"{value//1000}K"
            else:
                display_value = str(value)
            
            text_id = self.canvas.create_text(
                x, y + size // 4,
                text=display_value,
                font=text_font,
                fill=theme.get("chip.text", "#FFFFFF"),
                tags=tags + ("chip_text",)
            )
            elements.append(text_id)
        
        return elements
    
    def render_chip_stack(self, x: int, y: int, total_value: int, 
                         chip_type: str = "bet", max_chips: int = 5,
                         tags: Tuple = ()) -> List[int]:
        """Render a stack of chips representing a total value."""
        theme, _ = _tokens(self.canvas)
        
        # Calculate chip denominations for the stack
        chip_values = self._calculate_chip_breakdown(total_value, max_chips)
        
        elements = []
        stack_height = 0
        
        for i, (value, count) in enumerate(chip_values):
            for j in range(count):
                # Stack chips with slight offset for 3D effect
                chip_x = x + j
                chip_y = y - stack_height - (j * 2)
                
                # Render individual chip
                chip_elements = self.render_chip(
                    chip_x, chip_y, value, chip_type,
                    size=18, tags=tags + (f"stack_{i}_{j}",)
                )
                elements.extend(chip_elements)
                
            stack_height += count * 3  # Increase stack height
        
        return elements
    
    def _calculate_chip_breakdown(self, total_value: int, max_chips: int) -> List[Tuple[int, int]]:
        """Calculate optimal chip breakdown for a given value."""
        denominations = [1000, 500, 100, 25, 5, 1]
        breakdown = []
        remaining = total_value
        chips_used = 0
        
        for denom in denominations:
            if chips_used >= max_chips:
                break
                
            if remaining >= denom:
                count = min(remaining // denom, max_chips - chips_used)
                if count > 0:
                    breakdown.append((denom, count))
                    remaining -= denom * count
                    chips_used += count
        
        # If we still have remaining value and room for chips, add smaller denominations
        if remaining > 0 and chips_used < max_chips:
            breakdown.append((remaining, 1))
        
        return breakdown
    
    def animate_chips_to_pot(self, start_x: int, start_y: int, 
                           end_x: int, end_y: int, chip_value: int,
                           duration: int = 500, callback=None):
        """Animate chips moving from player position to pot."""
        theme, _ = _tokens(self.canvas)
        
        # Create temporary chips for animation
        temp_chips = self.render_chip_stack(
            start_x, start_y, chip_value, "bet",
            tags=("animation", "temp_chip")
        )
        
        # Animation parameters
        steps = 20
        step_duration = duration // steps
        dx = (end_x - start_x) / steps
        dy = (end_y - start_y) / steps
        
        def animate_step(step: int):
            if step >= steps:
                # Animation complete - remove temp chips and call callback
                for chip_id in temp_chips:
                    try:
                        self.canvas.delete(chip_id)
                    except tk.TclError:
                        pass
                if callback:
                    callback()
                return
            
            # Move chips
            for chip_id in temp_chips:
                try:
                    self.canvas.move(chip_id, dx, dy)
                except tk.TclError:
                    pass
            
            # Schedule next step
            self.canvas.after(step_duration, lambda: animate_step(step + 1))
        
        # Start animation
        animate_step(0)
    
    def animate_pot_to_winner(self, pot_x: int, pot_y: int,
                            winner_x: int, winner_y: int, pot_value: int,
                            duration: int = 800, callback=None):
        """Animate pot chips moving to winner."""
        theme, _ = _tokens(self.canvas)
        
        # Create celebration effect
        self._create_winner_celebration(winner_x, winner_y, pot_value)
        
        # Create pot chips for animation
        temp_chips = self.render_chip_stack(
            pot_x, pot_y, pot_value, "pot",
            max_chips=8, tags=("animation", "pot_to_winner")
        )
        
        # Animation with arc trajectory
        steps = 25
        step_duration = duration // steps
        
        def animate_step(step: int):
            if step >= steps:
                # Animation complete
                for chip_id in temp_chips:
                    try:
                        self.canvas.delete(chip_id)
                    except tk.TclError:
                        pass
                if callback:
                    callback()
                return
            
            # Calculate arc position
            progress = step / steps
            # Parabolic arc
            arc_height = -50 * math.sin(math.pi * progress)
            
            current_x = pot_x + (winner_x - pot_x) * progress
            current_y = pot_y + (winner_y - pot_y) * progress + arc_height
            
            # Move chips to calculated position
            for i, chip_id in enumerate(temp_chips):
                try:
                    # Get current position
                    coords = self.canvas.coords(chip_id)
                    if len(coords) >= 4:
                        old_x = (coords[0] + coords[2]) / 2
                        old_y = (coords[1] + coords[3]) / 2
                        
                        # Calculate new position with slight spread
                        spread = i * 3
                        new_x = current_x + spread
                        new_y = current_y
                        
                        # Move chip
                        self.canvas.move(chip_id, new_x - old_x, new_y - old_y)
                except tk.TclError:
                    pass
            
            # Schedule next step
            self.canvas.after(step_duration, lambda: animate_step(step + 1))
        
        # Start animation
        animate_step(0)
    
    def _create_winner_celebration(self, x: int, y: int, pot_value: int):
        """Create celebration effect around winner."""
        theme, fonts = _tokens(self.canvas)
        
        # Celebration burst effect
        for i in range(8):
            angle = (i * 45) * math.pi / 180
            distance = 30
            star_x = x + distance * math.cos(angle)
            star_y = y + distance * math.sin(angle)
            
            # Create star burst
            star_id = self.canvas.create_text(
                star_x, star_y,
                text="✨",
                font=("Arial", 16),
                fill=theme.get("celebration.color", "#FFD700"),
                tags=("celebration", "temp")
            )
            
            # Fade out after delay
            self.canvas.after(1000, lambda sid=star_id: self._fade_element(sid))
    
    def _fade_element(self, element_id: int):
        """Fade out and remove an element."""
        try:
            self.canvas.delete(element_id)
        except tk.TclError:
            pass


class BetDisplay:
    """Renders themed bet amounts with chip graphics."""
    
    def __init__(self, canvas):
        self.canvas = canvas
        self.chip_graphics = ChipGraphics(canvas)
    
    def render(self, x: int, y: int, amount: int, bet_type: str = "bet",
               tags: Tuple = ()) -> List[int]:
        """Render bet display with chips and text."""
        theme, fonts = _tokens(self.canvas)
        
        elements = []
        
        if amount > 0:
            # Render chip stack
            chip_elements = self.chip_graphics.render_chip_stack(
                x, y - 15, amount, bet_type, max_chips=3,
                tags=tags + ("bet_chips",)
            )
            elements.extend(chip_elements)
            
            # Render amount text
            text_color = theme.get("bet.text", "#FFFFFF")
            if bet_type == "call":
                text_color = theme.get("bet.call.text", "#9CA3AF")
            elif bet_type == "raise":
                text_color = theme.get("bet.raise.text", "#EF4444")
            
            text_id = self.canvas.create_text(
                x, y + 20,
                text=f"${amount:,}",
                font=fonts.get("body", ("Arial", 10, "bold")),
                fill=text_color,
                tags=tags + ("bet_text",)
            )
            elements.append(text_id)
        
        return elements


class WinnerBadge:
    """Renders themed winner announcement badges."""
    
    def __init__(self, canvas):
        self.canvas = canvas
    
    def render(self, x: int, y: int, player_name: str, amount: int,
               hand_description: str = "", tags: Tuple = ()) -> List[int]:
        """Render luxury winner badge with theme styling."""
        theme, fonts = _tokens(self.canvas)
        
        elements = []
        
        # Badge dimensions
        badge_width = 200
        badge_height = 80
        
        # Theme-aware colors
        badge_bg = theme.get("winner.bg", "#1F2937")
        badge_border = theme.get("winner.border", "#FFD700")
        badge_accent = theme.get("winner.accent", "#FEF3C7")
        
        # Main badge background with luxury styling
        badge_id = self.canvas.create_rectangle(
            x - badge_width//2, y - badge_height//2,
            x + badge_width//2, y + badge_height//2,
            fill=badge_bg,
            outline=badge_border,
            width=3,
            tags=tags + ("winner_badge",)
        )
        elements.append(badge_id)
        
        # Luxury gradient highlight
        highlight_id = self.canvas.create_rectangle(
            x - badge_width//2 + 3, y - badge_height//2 + 3,
            x + badge_width//2 - 3, y - badge_height//2 + 12,
            fill=badge_accent,
            outline="",
            tags=tags + ("winner_highlight",)
        )
        elements.append(highlight_id)
        
        # Winner crown symbol
        crown_id = self.canvas.create_text(
            x - badge_width//3, y - 10,
            text="👑",
            font=("Arial", 20),
            tags=tags + ("winner_crown",)
        )
        elements.append(crown_id)
        
        # Winner text
        winner_text = f"WINNER: {player_name}"
        text_id = self.canvas.create_text(
            x, y - 15,
            text=winner_text,
            font=fonts.get("heading", ("Arial", 12, "bold")),
            fill=theme.get("winner.text", "#FFFFFF"),
            tags=tags + ("winner_text",)
        )
        elements.append(text_id)
        
        # Amount won
        amount_id = self.canvas.create_text(
            x, y + 5,
            text=f"${amount:,}",
            font=fonts.get("body", ("Arial", 14, "bold")),
            fill=theme.get("winner.amount", "#FFD700"),
            tags=tags + ("winner_amount",)
        )
        elements.append(amount_id)
        
        # Hand description (if provided)
        if hand_description:
            hand_id = self.canvas.create_text(
                x, y + 20,
                text=hand_description,
                font=fonts.get("caption", ("Arial", 9, "italic")),
                fill=theme.get("winner.description", "#D1D5DB"),
                tags=tags + ("winner_hand",)
            )
            elements.append(hand_id)
        
        return elements
    
    def animate_winner_announcement(self, x: int, y: int, player_name: str,
                                  amount: int, hand_description: str = "",
                                  duration: int = 3000):
        """Animate winner badge with entrance and exit effects."""
        # Create badge elements
        elements = self.render(x, y, player_name, amount, hand_description,
                             tags=("winner_animation",))
        
        # Entrance animation - scale up
        self._animate_scale(elements, 0.1, 1.0, 300)
        
        # Exit animation after duration
        self.canvas.after(duration, lambda: self._animate_fade_out(elements, 500))
    
    def _animate_scale(self, elements: List[int], start_scale: float,
                      end_scale: float, duration: int):
        """Animate scaling of elements."""
        steps = 15
        step_duration = duration // steps
        scale_step = (end_scale - start_scale) / steps
        
        def scale_step_func(step: int):
            if step >= steps:
                return
            
            current_scale = start_scale + scale_step * step
            
            for element_id in elements:
                try:
                    # Get element center
                    coords = self.canvas.coords(element_id)
                    if len(coords) >= 2:
                        if len(coords) == 4:  # Rectangle
                            center_x = (coords[0] + coords[2]) / 2
                            center_y = (coords[1] + coords[3]) / 2
                        else:  # Text or other
                            center_x, center_y = coords[0], coords[1]
                        
                        # Apply scaling (simplified - just adjust position)
                        # In a full implementation, you'd use canvas.scale()
                        pass
                except tk.TclError:
                    pass
            
            self.canvas.after(step_duration, lambda: scale_step_func(step + 1))
        
        scale_step_func(0)
    
    def _animate_fade_out(self, elements: List[int], duration: int):
        """Fade out and remove elements."""
        # Simplified fade - just remove after duration
        self.canvas.after(duration, lambda: self._remove_elements(elements))
    
    def _remove_elements(self, elements: List[int]):
        """Remove elements from canvas."""
        for element_id in elements:
            try:
                self.canvas.delete(element_id)
            except tk.TclError:
                pass

```

---

### premium_chips.py

**Path**: `backend/ui/tableview/components/premium_chips.py`

```python
"""
Premium Casino Chip System
==========================

Theme-aware chip rendering with distinct visual types:
- Stack chips (player stacks): calm, readable, less saturated
- Bet/Call chips (flying chips): vivid with theme accent for motion tracking  
- Pot chips (pot visualization): prestigious metal-leaning design

Features:
- Consistent casino denominations with theme-tinted colors
- Radial stripe patterns for instant denomination recognition
- Hover states, glow effects, and animation support
- Automatic theme integration via token system
"""

import math
from typing import Tuple, List, Optional


# Standard casino denominations with base colors
CHIP_DENOMINATIONS = [
    (1,    "#2E86AB"),  # $1  – blue
    (5,    "#B63D3D"),  # $5  – red
    (25,   "#2AA37A"),  # $25 – green
    (100,  "#3C3A3A"),  # $100 – black/graphite
    (500,  "#6C4AB6"),  # $500 – purple
    (1000, "#D1B46A"),  # $1k – gold
]


def get_denom_color(amount: int) -> str:
    """Get the base color for a chip denomination."""
    for denom, color in CHIP_DENOMINATIONS:
        if amount <= denom:
            return color
    return CHIP_DENOMINATIONS[-1][1]  # Default to highest denom color


def draw_chip_base(canvas, x: int, y: int, r: int, face: str, edge: str, rim: str, 
                   denom_color: str, text: str, text_color: str, tags: tuple = ()) -> int:
    """
    Draw the base chip structure with radial stripes and denomination text.
    
    Args:
        canvas: Tkinter canvas widget
        x, y: Center coordinates
        r: Chip radius
        face: Base face color
        edge: Outer edge color  
        rim: Inner ring color
        denom_color: Denomination stripe color
        text: Text to display (e.g., "$25")
        text_color: Text color
        tags: Canvas tags for the chip elements
        
    Returns:
        Canvas item ID of the main chip disc
    """
    # Main chip disc
    chip_id = canvas.create_oval(
        x - r, y - r, x + r, y + r,
        fill=face, outline=edge, width=2,
        tags=tags
    )
    
    # Radial stripes (8 wedges) for denomination recognition
    for i in range(8):
        angle_start = i * 45  # 360/8 = 45 degrees per stripe
        angle_extent = 15     # Width of each stripe
        canvas.create_arc(
            x - r + 3, y - r + 3, x + r - 3, y + r - 3,
            start=angle_start, extent=angle_extent,
            outline="", fill=denom_color, width=0,
            tags=tags
        )
    
    # Inner ring for premium look
    inner_r = int(r * 0.70)
    canvas.create_oval(
        x - inner_r, y - inner_r, x + inner_r, y + inner_r,
        outline=rim, fill="", width=2,
        tags=tags
    )
    
    # Denomination text
    font_size = max(8, int(r * 0.4))  # Scale text with chip size
    canvas.create_text(
        x, y, text=text, fill=text_color,
        font=("Inter", font_size, "bold"),
        tags=tags
    )
    
    return chip_id


def draw_stack_chip(canvas, x: int, y: int, amount: int, tokens: dict, 
                    r: int = 14, tags: tuple = ()) -> int:
    """
    Draw a single stack chip (calm, readable design for player stacks).
    
    Args:
        canvas: Tkinter canvas widget
        x, y: Center coordinates
        amount: Dollar amount for denomination
        tokens: Theme token dictionary
        r: Chip radius
        tags: Canvas tags
        
    Returns:
        Canvas item ID of the chip
    """
    denom_color = get_denom_color(amount)
    return draw_chip_base(
        canvas, x, y, r,
        face=tokens.get("chip.stack.face", "#4A4A4A"),
        edge=tokens.get("chip.stack.edge", "#666666"), 
        rim=tokens.get("chip.stack.rim", "#888888"),
        denom_color=denom_color,
        text=f"${amount}",
        text_color=tokens.get("chip.stack.text", "#F8F7F4"),
        tags=tags
    )


def draw_bet_chip(canvas, x: int, y: int, amount: int, tokens: dict,
                  r: int = 14, hovering: bool = False, tags: tuple = ()) -> int:
    """
    Draw a bet/call chip (vivid design with theme accent for motion tracking).
    
    Args:
        canvas: Tkinter canvas widget
        x, y: Center coordinates
        amount: Dollar amount for denomination
        tokens: Theme token dictionary
        r: Chip radius
        hovering: Whether to show hover glow effect
        tags: Canvas tags
        
    Returns:
        Canvas item ID of the chip
    """
    denom_color = get_denom_color(amount)
    chip_id = draw_chip_base(
        canvas, x, y, r,
        face=tokens.get("chip.bet.face", "#6B4AB6"),
        edge=tokens.get("chip.bet.edge", "#8A6BC8"),
        rim=tokens.get("chip.bet.rim", "#A888CC"),
        denom_color=denom_color,
        text=f"${amount}",
        text_color=tokens.get("chip.bet.text", "#F8F7F4"),
        tags=tags
    )
    
    # Optional hover glow
    if hovering:
        glow_color = tokens.get("chip.bet.glow", "#A888CC")
        canvas.create_oval(
            x - r - 4, y - r - 4, x + r + 4, y + r + 4,
            outline=glow_color, fill="", width=2,
            tags=tags + ("glow",)
        )
    
    return chip_id


def draw_pot_chip(canvas, x: int, y: int, amount: int, tokens: dict,
                  r: int = 16, breathing: bool = False, tags: tuple = ()) -> int:
    """
    Draw a pot chip (prestigious metal-leaning design).
    
    Args:
        canvas: Tkinter canvas widget
        x, y: Center coordinates  
        amount: Dollar amount for denomination
        tokens: Theme token dictionary
        r: Chip radius (slightly larger than other chips)
        breathing: Whether to show breathing glow effect
        tags: Canvas tags
        
    Returns:
        Canvas item ID of the chip
    """
    denom_color = get_denom_color(amount)
    chip_id = draw_chip_base(
        canvas, x, y, r,
        face=tokens.get("chip.pot.face", "#D1B46A"),
        edge=tokens.get("chip.pot.edge", "#B8A157"),
        rim=tokens.get("chip.pot.rim", "#E6D078"),
        denom_color=denom_color,
        text=f"${amount}",
        text_color=tokens.get("chip.pot.text", "#0B0B0E"),
        tags=tags
    )
    
    # Optional breathing glow for pot increases
    if breathing:
        glow_color = tokens.get("chip.pot.glow", "#E6D078")
        canvas.create_oval(
            x - r - 5, y - r - 5, x + r + 5, y + r + 5,
            outline=glow_color, fill="", width=2,
            tags=tags + ("glow",)
        )
    
    return chip_id


def draw_chip_stack(canvas, x: int, y: int, total_amount: int, tokens: dict,
                    r: int = 14, max_height: int = 15, tags: tuple = ()) -> List[int]:
    """
    Draw a stack of chips representing a player's total amount.
    
    Args:
        canvas: Tkinter canvas widget
        x, y: Base center coordinates (bottom of stack)
        total_amount: Total dollar amount to represent
        tokens: Theme token dictionary
        r: Chip radius
        max_height: Maximum number of chips to show (for UI space)
        tags: Canvas tags
        
    Returns:
        List of canvas item IDs for all chips in the stack
    """
    if total_amount <= 0:
        return []
    
    # Break down amount into chip denominations (largest first)
    chip_plan = []
    remaining = total_amount
    
    for denom, _ in reversed(CHIP_DENOMINATIONS):
        if remaining >= denom:
            count = min(remaining // denom, max_height - len(chip_plan))
            chip_plan.extend([denom] * count)
            remaining -= denom * count
            
        if len(chip_plan) >= max_height:
            break
    
    # If we still have remaining amount and space, add smaller denominations
    if remaining > 0 and len(chip_plan) < max_height:
        # Fill remaining space with $1 chips
        remaining_space = max_height - len(chip_plan)
        chip_plan.extend([1] * min(remaining_space, remaining))
    
    # Draw soft shadow
    shadow_color = tokens.get("chip.stack.shadow", "#000000")
    canvas.create_oval(
        x - r - 4, y + 3, x + r + 4, y + 11,
        fill=shadow_color, outline="",
        tags=tags + ("shadow",)
    )
    
    # Draw chips from bottom to top
    chip_ids = []
    chip_spacing = 6  # Vertical spacing between chips
    
    for i, denom in enumerate(chip_plan):
        chip_y = y - (i * chip_spacing)
        chip_id = draw_stack_chip(
            canvas, x, chip_y, denom, tokens, r=r,
            tags=tags + (f"stack_chip_{i}",)
        )
        chip_ids.append(chip_id)
    
    return chip_ids


def animate_chip_bet(canvas, start_pos: Tuple[int, int], end_pos: Tuple[int, int],
                     amount: int, tokens: dict, r: int = 14, frames: int = 20,
                     callback: Optional[callable] = None) -> None:
    """
    Animate a chip flying from start to end position (bet → pot).
    
    Args:
        canvas: Tkinter canvas widget
        start_pos: (x, y) starting coordinates
        end_pos: (x, y) ending coordinates
        amount: Dollar amount for the chip
        tokens: Theme token dictionary
        r: Chip radius
        frames: Number of animation frames
        callback: Optional function to call when animation completes
    """
    x0, y0 = start_pos
    x1, y1 = end_pos
    glow_color = tokens.get("chip.bet.glow", "#A888CC")
    
    def animate_frame(frame: int):
        if frame >= frames:
            if callback:
                callback()
            return
        
        # Cubic easing for smooth motion
        t = frame / frames
        ease_t = t * t * (3 - 2 * t)
        
        # Position with arc (parabolic path)
        x = x0 + (x1 - x0) * ease_t
        y = y0 + (y1 - y0) * ease_t - 20 * math.sin(math.pi * ease_t)
        
        # Clear previous frame
        canvas.delete("flying_chip")
        
        # Draw chip at current position
        draw_bet_chip(
            canvas, int(x), int(y), amount, tokens, r=r, hovering=True,
            tags=("flying_chip",)
        )
        
        # Schedule next frame
        canvas.after(50, lambda: animate_frame(frame + 1))
    
    # Start animation
    animate_frame(0)


def pulse_pot_glow(canvas, center_pos: Tuple[int, int], tokens: dict,
                   r: int = 18, pulses: int = 3) -> None:
    """
    Create a pulsing glow effect at the pot center when pot increases.
    
    Args:
        canvas: Tkinter canvas widget
        center_pos: (x, y) center coordinates
        tokens: Theme token dictionary
        r: Base radius for the pulse
        pulses: Number of pulse cycles
    """
    x, y = center_pos
    glow_color = tokens.get("chip.pot.glow", "#E6D078")
    
    pulse_sequence = [0.0, 0.4, 0.8, 1.0, 0.8, 0.4, 0.0]
    
    def animate_pulse(pulse_num: int, frame: int):
        if pulse_num >= pulses:
            canvas.delete("pot_pulse")
            return
            
        if frame >= len(pulse_sequence):
            # Move to next pulse
            canvas.after(100, lambda: animate_pulse(pulse_num + 1, 0))
            return
        
        # Clear previous pulse
        canvas.delete("pot_pulse")
        
        # Draw current pulse ring
        intensity = pulse_sequence[frame]
        pulse_r = r + int(8 * intensity)
        alpha_val = int(255 * (0.6 - 0.4 * intensity))  # Fade as it expands
        
        canvas.create_oval(
            x - pulse_r, y - pulse_r, x + pulse_r, y + pulse_r,
            outline=glow_color, fill="", width=max(1, int(3 * (1 - intensity))),
            tags=("pot_pulse",)
        )
        
        # Schedule next frame
        canvas.after(80, lambda: animate_pulse(pulse_num, frame + 1))
    
    # Start pulsing
    animate_pulse(0, 0)


def clear_chip_animations(canvas) -> None:
    """Clear all chip animation elements from the canvas."""
    canvas.delete("flying_chip")
    canvas.delete("pot_pulse")
    canvas.delete("glow")

```

---

### micro_interactions.py

**Path**: `backend/ui/tableview/components/micro_interactions.py`

```python
"""
Micro-Interactions System
Subtle glows, pulses, and state transitions for premium feel
"""

import math
from ...services.theme_utils import ease_color_transition, lighten, alpha_over

class MicroInteractions:
    def __init__(self, theme_manager):
        self.theme = theme_manager
        self.active_pulses = {}
        self.active_glows = {}
        
    def pulse_seat_ring(self, canvas, seat_x, seat_y, seat_w, seat_h, duration_ms=1000):
        """Subtle pulsing ring around acting player seat"""
        tokens = self.theme.get_all_tokens()
        focus_color = tokens.get("a11y.focus", "#22C55E")
        
        pulse_id = f"seat_pulse_{seat_x}_{seat_y}"
        
        # Clear any existing pulse
        if pulse_id in self.active_pulses:
            canvas.after_cancel(self.active_pulses[pulse_id])
        
        frames = duration_ms // 50  # 20 FPS
        
        def pulse_step(frame):
            if frame >= frames:
                canvas.delete(f"pulse_{pulse_id}")
                if pulse_id in self.active_pulses:
                    del self.active_pulses[pulse_id]
                return
            
            # Calculate pulse intensity (sine wave)
            progress = (frame / frames) * 2 * math.pi
            intensity = (math.sin(progress) + 1) / 2  # 0 to 1
            
            # Clear previous pulse frame
            canvas.delete(f"pulse_{pulse_id}")
            
            # Draw pulsing ring with varying alpha
            ring_width = 2 + int(intensity * 2)  # 2-4px width
            alpha = 0.3 + (intensity * 0.4)  # 30-70% alpha
            
            # Create multiple rings for glow effect
            for i in range(3):
                offset = i * 2
                canvas.create_rectangle(
                    seat_x - seat_w//2 - offset, seat_y - seat_h//2 - offset,
                    seat_x + seat_w//2 + offset, seat_y + seat_h//2 + offset,
                    outline=focus_color, width=ring_width - i,
                    tags=(f"pulse_{pulse_id}",)
                )
            
            # Schedule next frame
            timer_id = canvas.after(50, lambda: pulse_step(frame + 1))
            self.active_pulses[pulse_id] = timer_id
        
        pulse_step(0)
    
    def flash_pot_increase(self, canvas, pot_x, pot_y, pot_w, pot_h):
        """Brief flash when pot amount increases"""
        tokens = self.theme.get_all_tokens()
        metal_color = tokens.get("table.inlay", "#C9A86A")
        flash_color = lighten(metal_color, 0.25)
        
        flash_frames = 8  # Quick flash
        
        def flash_step(frame):
            if frame >= flash_frames:
                canvas.delete("pot_flash")
                return
            
            # Fade from bright to normal
            progress = frame / flash_frames
            current_color = ease_color_transition(flash_color, metal_color, progress)
            
            # Clear previous flash
            canvas.delete("pot_flash")
            
            # Draw flash ring around pot
            canvas.create_rectangle(
                pot_x - pot_w//2 - 3, pot_y - pot_h//2 - 3,
                pot_x + pot_w//2 + 3, pot_y + pot_h//2 + 3,
                outline=current_color, width=2,
                tags=("pot_flash",)
            )
            
            canvas.after(60, lambda: flash_step(frame + 1))
        
        flash_step(0)
    
    def hover_glow(self, canvas, element_id, x, y, w, h, glow_type="soft"):
        """Add hover glow effect to UI element"""
        tokens = self.theme.get_all_tokens()
        glow_color = tokens.get(f"glow.{glow_type}", tokens.get("a11y.focus", "#22C55E"))
        
        glow_tag = f"hover_glow_{element_id}"
        
        # Clear existing glow
        canvas.delete(glow_tag)
        
        # Create soft glow with multiple rings
        for i in range(4):
            offset = (i + 1) * 2
            alpha = 1.0 - (i * 0.2)  # Fade outward
            
            canvas.create_rectangle(
                x - offset, y - offset, x + w + offset, y + h + offset,
                outline=glow_color, width=1,
                tags=(glow_tag,)
            )
    
    def remove_hover_glow(self, canvas, element_id):
        """Remove hover glow effect"""
        canvas.delete(f"hover_glow_{element_id}")
    
    def button_press_feedback(self, canvas, btn_x, btn_y, btn_w, btn_h):
        """Quick visual feedback for button press"""
        tokens = self.theme.get_all_tokens()
        active_color = tokens.get("btn.primary.activeBorder", "#FFD700")
        
        feedback_frames = 6
        
        def feedback_step(frame):
            if frame >= feedback_frames:
                canvas.delete("button_feedback")
                return
            
            # Quick expand and contract
            progress = frame / feedback_frames
            scale = 1.0 + (0.1 * math.sin(progress * math.pi))  # Slight scale pulse
            
            offset = int((scale - 1.0) * min(btn_w, btn_h) / 2)
            
            canvas.delete("button_feedback")
            canvas.create_rectangle(
                btn_x - offset, btn_y - offset,
                btn_x + btn_w + offset, btn_y + btn_h + offset,
                outline=active_color, width=2,
                tags=("button_feedback",)
            )
            
            canvas.after(30, lambda: feedback_step(frame + 1))
        
        feedback_step(0)
    
    def card_reveal_shimmer(self, canvas, card_x, card_y, card_w, card_h):
        """Subtle shimmer effect when card is revealed"""
        tokens = self.theme.get_all_tokens()
        shimmer_color = tokens.get("glow.medium", "#FFD700")
        
        shimmer_frames = 12
        
        def shimmer_step(frame):
            if frame >= shimmer_frames:
                canvas.delete("card_shimmer")
                return
            
            # Moving highlight across card
            progress = frame / shimmer_frames
            highlight_x = card_x + (progress * card_w)
            
            canvas.delete("card_shimmer")
            
            # Vertical highlight line
            canvas.create_line(
                highlight_x, card_y, highlight_x, card_y + card_h,
                fill=shimmer_color, width=2,
                tags=("card_shimmer",)
            )
            
            # Soft glow around line
            canvas.create_line(
                highlight_x - 1, card_y, highlight_x - 1, card_y + card_h,
                fill=shimmer_color, width=1,
                tags=("card_shimmer",)
            )
            canvas.create_line(
                highlight_x + 1, card_y, highlight_x + 1, card_y + card_h,
                fill=shimmer_color, width=1,
                tags=("card_shimmer",)
            )
            
            canvas.after(40, lambda: shimmer_step(frame + 1))
        
        shimmer_step(0)
    
    def dealer_button_move_trail(self, canvas, from_x, from_y, to_x, to_y):
        """Subtle trail effect when dealer button moves"""
        tokens = self.theme.get_all_tokens()
        trail_color = tokens.get("dealer.buttonBorder", "#C9A86A")
        
        trail_frames = 15
        
        def trail_step(frame):
            if frame >= trail_frames:
                canvas.delete("dealer_trail")
                return
            
            progress = frame / trail_frames
            
            # Create fading trail points
            for i in range(5):
                trail_progress = max(0, progress - (i * 0.1))
                if trail_progress <= 0:
                    continue
                
                trail_x = from_x + (to_x - from_x) * trail_progress
                trail_y = from_y + (to_y - from_y) * trail_progress
                
                # Fading circle
                alpha = (1.0 - i * 0.2) * (1.0 - progress)
                radius = 8 - i
                
                canvas.create_oval(
                    trail_x - radius, trail_y - radius,
                    trail_x + radius, trail_y + radius,
                    outline=trail_color, width=1,
                    tags=("dealer_trail",)
                )
            
            canvas.after(50, lambda: trail_step(frame + 1))
        
        trail_step(0)
    
    def winner_confetti_burst(self, canvas, center_x, center_y):
        """Celebration confetti burst for winner"""
        tokens = self.theme.get_all_tokens()
        colors = [
            tokens.get("chip.$25", "#2AA37A"),
            tokens.get("chip.$100", "#3C3A3A"),
            tokens.get("chip.$500", "#6C4AB6"),
            tokens.get("table.inlay", "#C9A86A"),
        ]
        
        # Create 20 confetti pieces
        confetti_pieces = []
        for i in range(20):
            angle = (i / 20) * 2 * math.pi
            velocity = 30 + (i % 3) * 10  # Varying speeds
            
            piece_data = {
                'x': center_x,
                'y': center_y,
                'vx': velocity * math.cos(angle),
                'vy': velocity * math.sin(angle),
                'color': colors[i % len(colors)],
                'size': 3 + (i % 2),
                'rotation': 0,
                'id': None
            }
            confetti_pieces.append(piece_data)
        
        confetti_frames = 30
        
        def confetti_step(frame):
            if frame >= confetti_frames:
                canvas.delete("confetti")
                return
            
            canvas.delete("confetti")
            
            for piece in confetti_pieces:
                # Update position
                piece['x'] += piece['vx'] * 0.8  # Slow down over time
                piece['y'] += piece['vy'] * 0.8
                piece['vy'] += 1  # Gravity
                piece['rotation'] += 10
                
                # Draw confetti piece
                size = piece['size']
                canvas.create_rectangle(
                    piece['x'] - size, piece['y'] - size,
                    piece['x'] + size, piece['y'] + size,
                    fill=piece['color'], outline="",
                    tags=("confetti",)
                )
            
            canvas.after(50, lambda: confetti_step(frame + 1))
        
        confetti_step(0)
    
    def stop_all_interactions(self):
        """Stop all active micro-interactions"""
        # Cancel all active pulses
        for pulse_id, timer_id in self.active_pulses.items():
            try:
                # Note: canvas.after_cancel would need canvas reference
                pass
            except:
                pass
        self.active_pulses.clear()
        self.active_glows.clear()
    
    def cleanup_effects(self, canvas):
        """Clean up all visual effects"""
        canvas.delete("pot_flash")
        canvas.delete("card_shimmer")
        canvas.delete("dealer_trail")
        canvas.delete("confetti")
        canvas.delete("button_feedback")
        
        # Clean up all hover glows
        for glow_id in list(self.active_glows.keys()):
            canvas.delete(f"hover_glow_{glow_id}")
        
        # Clean up all pulses
        for pulse_id in list(self.active_pulses.keys()):
            canvas.delete(f"pulse_{pulse_id}")

```

---

## AUDIO SYSTEM

### effect_bus.py

**Path**: `backend/ui/services/effect_bus.py`

```python
#!/usr/bin/env python3
"""
EffectBus - Coordinates sounds & animations; integrates with GameDirector.
"""
from __future__ import annotations

import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, field

# Import VoiceManager for human voice announcements
try:
    from ...utils.voice_manager import VoiceManager
except ImportError:
    try:
        from utils.voice_manager import VoiceManager
    except ImportError:
        try:
            from backend.utils.voice_manager import VoiceManager
        except ImportError:
            VoiceManager = None


# Minimal effect representation
@dataclass
class Effect:
    type: str
    id: Optional[str] = None
    name: Optional[str] = None
    ms: int = 200
    args: Dict[str, Any] = field(default_factory=dict)


class EffectBus:
    def __init__(self, game_director=None, sound_manager=None, event_bus=None, renderer=None):
        self.director = game_director
        self.sound = sound_manager
        self.event_bus = event_bus
        self.renderer = renderer
        self.enabled = True
        self.effects: List[Effect] = []
        self.next_id = 0
        
        # Initialize VoiceManager for human voice announcements
        self.voice_manager = None
        if VoiceManager:
            try:
                self.voice_manager = VoiceManager()
                print("🔊 EffectBus: VoiceManager initialized for human voice announcements")
            except Exception as e:
                print(f"⚠️ EffectBus: VoiceManager not available: {e}")
        
        # Initialize pygame mixer for audio
        try:
            import pygame
            pygame.mixer.init(
                frequency=22050, size=-16, channels=2, buffer=512
            )
            self.pygame_available = True
            print("🔊 EffectBus: Pygame mixer initialized for audio")
        except Exception as e:
            self.pygame_available = False
            print(f"⚠️ EffectBus: Pygame mixer not available: {e}")
        
        # Load sound configuration from file
        self.sound_mapping = {}
        self.config: Dict[str, Any] = {}
        self._load_sound_config()
        
        # Load sound files
        self.sounds = {}
        self._load_sounds()
    
    def _load_sound_config(self):
        """Load sound configuration from JSON file."""
        try:
            config_file = os.path.join(
                os.path.dirname(__file__), '..', '..', 'sounds',
                'poker_sound_config.json'
            )

            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)

                # Save full config for voice lookups
                self.config = config

                # Load sound mappings
                self.sound_mapping = config.get("sounds", {})

                # Load global settings
                self.master_volume = config.get("master_volume", 1.0)
                self.sounds_enabled = config.get("sounds_enabled", True)
                self.voice_enabled = config.get("voice_enabled", True)
                self.voice_type = config.get("voice_type", "announcer_female")

                # Optional base directory for sounds
                self.sound_dir_hint = Path(config.get("sound_directory", "sounds"))

                print(f"🔊 EffectBus: Loaded sound config with {len(self.sound_mapping)} mappings")
            else:
                print(f"⚠️ EffectBus: Sound config file not found: {config_file}")
                # Use empty mapping - let the UI handle defaults
                self.config = {}
                self.sound_mapping = {}
                self.master_volume = 1.0
                self.sounds_enabled = True
                self.voice_enabled = True
                self.voice_type = "announcer_female"
                self.sound_dir_hint = Path("sounds")

        except Exception as e:
            print(f"⚠️ EffectBus: Error loading sound config: {e}")
            # Fallback to empty mappings
            self.config = {}
            self.sound_mapping = {}
            self.master_volume = 1.0
            self.sounds_enabled = True
            self.voice_enabled = True
            self.voice_type = "announcer_female"
            self.sound_dir_hint = Path("sounds")
    
    def reload_sound_config(self):
        """Dynamically reload sound configuration from file."""
        print("🔄 EffectBus: Reloading sound configuration...")
        self._load_sound_config()
        # Clear existing loaded sounds to force reload
        self.sounds.clear()
        # Reload sounds with new mapping
        self._load_sounds()
        print(f"✅ EffectBus: Reloaded sound config with {len(self.sound_mapping)} mappings")

    def set_game_director(self, game_director):
        """Set the game director for coordinating effects timing."""
        self.director = game_director
        print(f"🔊 EffectBus: Connected to GameDirector")

    def set_event_bus(self, event_bus):
        """Set the event bus for publishing effect events."""
        self.event_bus = event_bus
        print(f"🔊 EffectBus: Connected to EventBus")
        # Bridge basic animate events to ChipAnimations if a renderer is present
        try:
            if self.event_bus is not None:
                self.event_bus.subscribe("effect_bus:animate", self._on_animation_request)
        except Exception:
            pass

    def _resolve_sound_path(self, rel_or_abs: str) -> Optional[Path]:
        """Resolve a sound path robustly across likely locations."""
        try:
            # Absolute path as-is
            p = Path(rel_or_abs)
            if p.is_file():
                return p

            # Relative to configured sounds dir if provided
            if hasattr(self, 'sound_dir_hint'):
                cand = self.sound_dir_hint / rel_or_abs
                if cand.is_file():
                    return cand

            # Relative to this module's ../../sounds
            here = Path(__file__).parent
            cand2 = (here / '..' / '..' / 'sounds').resolve() / rel_or_abs
            if cand2.is_file():
                return cand2

            # Relative to CWD/sounds
            cand3 = Path.cwd() / 'sounds' / rel_or_abs
            if cand3.is_file():
                return cand3
        except Exception:
            pass
        return None

    def _load_sounds(self):
        """Load all available sound files."""
        if not self.pygame_available:
            return
            
        try:
            import pygame
            for action, filename in self.sound_mapping.items():
                resolved = self._resolve_sound_path(filename)
                if resolved and resolved.exists() and resolved.stat().st_size > 100:
                    try:
                        sound = pygame.mixer.Sound(str(resolved))
                        self.sounds[action.upper()] = sound
                        print(f"🔊 EffectBus: Loaded sound {action} -> {resolved}")
                    except Exception as e:
                        print(f"⚠️ EffectBus: Failed to load {filename}: {e}")
                else:
                    print(f"⚠️ EffectBus: Sound file not found or empty: {filename}")
                    
            print(f"🔊 EffectBus: Loaded {len(self.sounds)} sound files")
        except Exception as e:
            print(f"⚠️ EffectBus: Error loading sounds: {e}")

    def add_effect(self, effect: Effect) -> str:
        """Add an effect to the queue."""
        if not self.enabled:
            return ""
            
        effect.id = f"{effect.type}_{self.next_id}"
        self.next_id += 1
        self.effects.append(effect)
        
        # Notify event bus
        if self.event_bus:
            self.event_bus.publish(f"effect_bus:{effect.type}", {
                "id": effect.id,
                "name": effect.name,
                "ms": effect.ms,
                "args": effect.args
            })
        
        return effect.id

    def add_sound_effect(self, sound_name: str, ms: int = 200):
        """Add sound effect with proper gating, even if pygame audio fails."""
        # try to play; don't crash if mixer is unavailable
        played = False
        try:
            if hasattr(self, 'pygame_available') and self.pygame_available:
                import pygame
                # First try to use pre-loaded sound from self.sounds
                if sound_name in self.sounds:
                    try:
                        sound = self.sounds[sound_name]
                        sound.set_volume(self.master_volume)
                        sound.play()
                        played = True
                        print(f"🔊 EffectBus: Playing pre-loaded sound: {sound_name}")
                    except Exception as e:
                        print(f"⚠️ EffectBus: Failed to play pre-loaded sound {sound_name}: {e}")
                        played = False
                else:
                    # Fallback: try to load from file mapping
                    sound_file = self.sound_mapping.get(sound_name.upper(), "")
                    if sound_file:
                        resolved = self._resolve_sound_path(sound_file)
                        try:
                            if resolved and resolved.exists():
                                sound = pygame.mixer.Sound(str(resolved))
                                sound.set_volume(self.master_volume)
                                sound.play()
                                played = True
                                print(f"🔊 EffectBus: Playing sound {sound_name} -> {resolved}")
                            else:
                                print(f"⚠️ EffectBus: Could not resolve sound path for {sound_file}")
                                played = False
                        except Exception as e:
                            print(f"⚠️ EffectBus: Failed to play {sound_file}: {e}")
                            played = False
                    else:
                        print(f"⚠️ EffectBus: No sound mapping found for {sound_name}")
        except Exception as e:
            print(f"⚠️ EffectBus: Error in add_sound_effect: {e}")
            played = False

        # Gate autoplay regardless of audio success. Use the director to schedule
        # a SOUND_COMPLETE event so the autoplay rhythm stays deterministic.
        if self.director:
            try:
                self.director.gate_begin()
                # Use ms even if sound didn't play to keep timing consistent
                self.director.schedule(ms, {"type": "SOUND_COMPLETE", "id": sound_name},
                                       callback=self.director.notify_sound_complete)
            except Exception:
                # Ensure gate_end still occurs in case schedule failed
                try:
                    self.director.gate_end()
                except Exception:
                    pass

        # optional: telemetry/log
        if self.event_bus:
            self.event_bus.publish("effect_bus:sound", {"id": sound_name, "ms": ms})

    def add_animation_effect(self, name: str, ms: int = 250, args: dict | None = None):
        """Add animation effect with proper gating."""
        args = args or {}
        if self.event_bus:
            self.event_bus.publish("effect_bus:animate", {"name": name, "ms": ms, "args": args})

        if self.director:
            self.director.gate_begin()
            self.director.schedule(ms, {"type": "ANIM_COMPLETE", "name": name},
                                   callback=self.director.notify_animation_complete)

    # --- Animation bridge ---
    def _on_animation_request(self, payload: dict):
        """Translate simple animate events to ChipAnimations drawing calls.
        Requires renderer with canvas and theme_manager context.
        """
        try:
            name = (payload or {}).get("name", "")
            args = (payload or {}).get("args", {}) or {}
            renderer = getattr(self, "renderer", None)
            if renderer is None:
                return
            canvas = getattr(renderer, "canvas_manager", None)
            canvas = getattr(canvas, "canvas", None)
            theme_manager = getattr(renderer, "theme_manager", None)
            if canvas is None or theme_manager is None:
                return
            from ..tableview.components.chip_animations import ChipAnimations
            anim = ChipAnimations(theme_manager)

            if name == "chips_to_pot":
                anim.fly_chips_to_pot(
                    canvas,
                    args.get("from_x", 0), args.get("from_y", 0),
                    args.get("to_x", 0), args.get("to_y", 0),
                    int(args.get("amount", 0)),
                )
            elif name == "pot_to_winner":
                anim.fly_pot_to_winner(
                    canvas,
                    args.get("pot_x", 0), args.get("pot_y", 0),
                    args.get("winner_x", 0), args.get("winner_y", 0),
                    int(args.get("amount", 0)),
                )
        except Exception:
            pass

    def add_banner_effect(self, message: str, banner_type: str = "info", ms: int = 2000) -> str:
        """Add a banner notification effect."""
        effect = Effect(
            type="banner",
            name=message,
            ms=ms,
            args={"type": banner_type}
        )
        return self.add_effect(effect)

    def add_poker_action_effects(self, action_type: str, player_name: str = ""):
        """Add poker action effects with proper sound mapping and gating."""
        action_type = (action_type or "").upper()
        
        # Debug: log what we're receiving
        print(f"🔊 DEBUG: EffectBus received action_type: '{action_type}'")

        # Use config-driven sound mapping from poker_sound_config.json
        # The sound_map is loaded dynamically from the config file
        sound_map = self.sound_mapping
        
        maybe = sound_map.get(action_type)
        if maybe:
            print(f"🔊 DEBUG: Found sound mapping for '{action_type}' -> '{maybe}'")
            self.add_sound_effect(action_type, ms=220)   # Pass action_type, not filename
        else:
            print(f"🔊 DEBUG: No sound mapping found for '{action_type}'")
            print(f"🔊 DEBUG: Available sound mappings: {list(sound_map.keys())}")

        # Add voice announcements for key actions via event bus and direct playback
        voice_action = self._map_action_to_voice(action_type)
        if self.voice_enabled and voice_action and hasattr(self, 'voice_manager') and self.voice_manager:
            try:
                print(f"🔊 DEBUG: Playing voice for action '{action_type}' -> '{voice_action}'")
                self.voice_manager.play_action_voice(voice_action.lower(), 0)
            except Exception as e:
                print(f"🔊 DEBUG: Voice playback failed: {e}")
        elif self.voice_enabled:
            # 1) Publish event for listeners
            if self.event_bus:
                self.event_bus.publish(
                    "effect_bus:voice",
                    {"type": "POKER_ACTION", "action": voice_action, "player": player_name},
                )
            print(f"🔊 EffectBus: Emitted voice event: {voice_action}")

            # 2) Direct playback via VoiceManager if available
            try:
                if self.voice_manager:
                    voice_sounds = (self.config or {}).get("voice_sounds", {})
                    voice_table = voice_sounds.get(self.voice_type or "", {})
                    file_rel = voice_table.get(voice_action)
                    if file_rel:
                        self.voice_manager.play(file_rel)
            except Exception as e:
                print(f"⚠️ EffectBus: Voice playback failed: {e}")

        if action_type == "SHOWDOWN":
            self.add_sound_effect("ui_winner", ms=700)

        # Publish simple banner text (optional)
        if self.event_bus:
            txt = f"{player_name or 'Player'} {action_type}"
            self.event_bus.publish("effect_bus:banner_show", {"style": "action", "text": txt})

        # Publish animation events for chip movements
        if action_type in ("DEAL_BOARD", "DEAL_FLOP", "DEAL_TURN", "DEAL_RIVER"):
            self.add_animation_effect("chips_to_pot", ms=260)

        if action_type in ("SHOWDOWN", "END_HAND"):
            self.add_animation_effect("pot_to_winner", ms=520)
            if self.event_bus:
                self.event_bus.publish("effect_bus:banner_show",
                    {"style": "winner", "text": f"{player_name or 'Player'} wins!"})

    def update(self):
        """Update effect processing."""
        if not self.enabled:
            return
            
        # Process effects
        for effect in self.effects[:]:
            if effect.type == "sound":
                self._play_sound(effect)
            elif effect.type == "animation":
                self._start_animation(effect)
            elif effect.type == "banner":
                self._show_banner(effect)
            
            # Remove processed effects
            self.effects.remove(effect)

    def _play_sound(self, effect: Effect):
        """Play a sound effect."""
        if not self.pygame_available or not self.sounds:
            return
            
        try:
            sound_name = effect.name
            if sound_name in self.sounds:
                # Gate effects while sound plays
                if self.director:
                    self.director.gate_begin()
                
                # Play the sound
                try:
                    self.sounds[sound_name].play()
                except Exception:
                    pass
                print(f"🔊 EffectBus: Playing sound: {sound_name}")
                
                # Schedule gate end through GameDirector only (no Tk timers)
                if self.director:
                    try:
                        self.director.schedule(
                            effect.ms,
                            {"type": "SOUND_COMPLETE", "id": effect.id},
                            callback=self.director.notify_sound_complete,
                        )
                    except Exception:
                        try:
                            self.director.gate_end()
                        except Exception:
                            pass
            else:
                print(f"⚠️ EffectBus: Sound not found: {sound_name}")
        except Exception as e:
            print(f"⚠️ EffectBus: Error playing sound: {e}")
            if self.director:
                self.director.gate_end()

    def _start_animation(self, effect: Effect):
        """Start an animation effect."""
        try:
            # Gate effects while animation runs
            if self.director:
                self.director.gate_begin()
            
            print(f"🎬 EffectBus: Started animation: {effect.name}")
            
            # Publish animation event
            if self.event_bus:
                self.event_bus.publish("effect_bus:animate", {
                    "id": effect.id,
                    "name": effect.name,
                    "ms": effect.ms,
                    "args": effect.args
                })
            
            # Schedule gate end through GameDirector only (no Tk timers)
            if self.director:
                try:
                    self.director.schedule(
                        effect.ms,
                        {"type": "ANIM_COMPLETE", "name": effect.name},
                        callback=self.director.notify_animation_complete,
                    )
                except Exception:
                    try:
                        self.director.gate_end()
                    except Exception:
                        pass
        except Exception as e:
            print(f"⚠️ EffectBus: Error starting animation: {e}")
            if self.director:
                self.director.gate_end()

    def _show_banner(self, effect: Effect):
        """Show a banner notification."""
        try:
            # Publish banner event
            if self.event_bus:
                self.event_bus.publish("effect_bus:banner_show", {
                    "id": effect.id,
                    "message": effect.name,
                    "type": effect.args.get("type", "info"),
                    "ms": effect.ms
                })
                print(f"🎭 EffectBus: Added banner effect: {effect.name}")
        except Exception as e:
            print(f"⚠️ EffectBus: Error showing banner: {e}")

    def clear_queue(self):
        """Clear all pending effects."""
        self.effects.clear()

    def stop_all_effects(self):
        """Stop all running effects."""
        if self.pygame_available:
            try:
                import pygame
                pygame.mixer.stop()
            except:
                pass
        self.clear_queue()

    def get_status(self) -> Dict[str, Any]:
        """Get current status."""
        return {
            "enabled": self.enabled,
            "effects_count": len(self.effects),
            "sounds_loaded": len(self.sounds),
            "pygame_available": self.pygame_available
        }

    def set_effect_enabled(self, enabled: bool):
        """Enable/disable effects."""
        self.enabled = enabled

    def _map_action_to_voice(self, action_type: str) -> str:
        """Map poker action types to voice announcement actions."""
        voice_map = {
            "BET": "bet",
            "RAISE": "raise", 
            "CALL": "call",
            "CHECK": "check",
            "FOLD": "fold",
            "ALL_IN": "all_in",
            "DEAL_HOLE": "dealing",
            "DEAL_BOARD": "dealing",
            "POST_BLIND": "dealing",
            "SHOWDOWN": "winner",
            "END_HAND": "winner"
        }
        return voice_map.get(action_type, "")


class NoopEffectBus:
    """No-op EffectBus for testing."""
    def __init__(self, *args, **kwargs):
        pass
    
    def __getattr__(self, name):
        return lambda *args, **kwargs: None

```

---

### sound_manager.py

**Path**: `backend/utils/sound_manager.py`

```python
#!/usr/bin/env python3
"""
Sound Manager for Poker Strategy Practice System

Handles audio playback for poker actions, card sounds, and UI feedback.
Uses pygame for cross-platform audio support.
"""

import os
import json
import pygame
from typing import Optional
from .voice_manager import VoiceManager


class SoundManager:
    """Manages sound effects for the poker application."""
    
    def __init__(self, sounds_dir: Optional[str] = None, test_mode: bool = False):
        """Initialize the sound manager.
        
        Args:
            sounds_dir: Directory containing sound files (defaults to ../sounds/)
            test_mode: If True, disables voice activation to speed up testing
        """
        self.sounds_dir = sounds_dir or os.path.join(
            os.path.dirname(__file__), '..', 'sounds'
        )
        self.sound_cache: dict[str, pygame.mixer.Sound] = {}
        self.enabled = True
        self.volume = 0.7
        self.test_mode = test_mode
        self.animation_mode = False  # Track if we're in animation mode
        
        # Initialize voice manager
        self.voice_manager = VoiceManager()
        
        # Initialize pygame mixer
        try:
            pygame.mixer.init(
                frequency=44100, size=-16, channels=2, buffer=512
            )
            # Sound system initialized successfully
            self._load_sound_mapping()
        except (pygame.error, OSError) as e:
            # Could not initialize sound system - using fallback mode
            self.enabled = False
    
    def _load_sound_mapping(self):
        """Load sound mapping configuration."""
        # First try to load the new poker sound configuration
        poker_config_file = os.path.join(self.sounds_dir, 'poker_sound_config.json')
        print(f"🔥 SOUND_DEBUG: Looking for config at: {poker_config_file}")
        print(f"🔥 SOUND_DEBUG: Config file exists: {os.path.exists(poker_config_file)}")
        if os.path.exists(poker_config_file):
            try:
                with open(poker_config_file, 'r') as f:
                    poker_config = json.load(f)
                self.poker_sound_events = poker_config.get("poker_sound_events", {})
                print(f"🔥 SOUND_DEBUG: Loaded {len(self.poker_sound_events)} poker sound events")
                print(f"🔥 SOUND_DEBUG: Voice events: {[k for k in self.poker_sound_events.keys() if 'player_action' in k]}")
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"🔥 SOUND_DEBUG: Error loading config: {e}")
                self.poker_sound_events = {}
        else:
            print(f"🔥 SOUND_DEBUG: Config file not found, using empty events")
            self.poker_sound_events = {}
        
        # Load the legacy sound mapping for backward compatibility
        mapping_file = os.path.join(self.sounds_dir, 'sound_mapping.json')
        try:
            with open(mapping_file, 'r') as f:
                self.sound_mapping = json.load(f)
        except FileNotFoundError:
            # Create default mapping based on available files
            self.sound_mapping = {
                "poker_actions": {
                    "check": "player_check.wav",
                    "call": "player_call.wav", 
                    "bet": "player_bet.wav",
                    "raise": "player_raise.wav",
                    "fold": "player_fold.wav",
                    "all_in": "player_all_in.wav"
                },
                "card_actions": {
                    "deal": "card_deal.wav",
                    "shuffle": "shuffle-cards-46455.mp3"
                },
                "chip_actions": {
                    "bet": "chip_bet.wav",
                    "collect": "pot_split.wav",
                    "multiple": "chip_bet_multiple.wav",
                    "single": "chip_bet_single.wav"
                },
                "ui_actions": {
                    "notification": "turn_notify.wav",
                    "winner": "winner_announce.wav"
                }
            }
    
    def _get_sound_path(self, sound_name: str) -> Optional[str]:
        """Get the full path to a sound file.
        
        Args:
            sound_name: Name of the sound file
            
        Returns:
            Full path to the sound file, or None if not found
        """
        # Try exact match first
        sound_path = os.path.join(self.sounds_dir, sound_name)
        if os.path.exists(sound_path):
            return sound_path
        
        # Try with .wav extension
        sound_path = os.path.join(self.sounds_dir, f"{sound_name}.wav")
        if os.path.exists(sound_path):
            return sound_path
        
        # Try with .mp3 extension
        sound_path = os.path.join(self.sounds_dir, f"{sound_name}.mp3")
        if os.path.exists(sound_path):
            return sound_path
        
        return None
    
    def _load_sound(self, sound_name: str) -> Optional[pygame.mixer.Sound]:
        """Load a sound file into memory.
        
        Args:
            sound_name: Name of the sound file
            
        Returns:
            pygame Sound object, or None if loading failed
        """
        if not self.enabled:
            return None
        
        # Check cache first
        if sound_name in self.sound_cache:
            return self.sound_cache[sound_name]
        
        sound_path = self._get_sound_path(sound_name)
        if not sound_path:
            # Sound file not found - using silent fallback
            return None
        
        try:
            sound = pygame.mixer.Sound(sound_path)
            sound.set_volume(self.volume)
            self.sound_cache[sound_name] = sound
            return sound
        except Exception as e:
            # Could not load sound - using silent fallback
            return None
    
    def play(self, sound_name: str):
        """Play a sound by name.
        
        Args:
            sound_name: Name of the sound file to play
        """
        print(f"🔥 SOUND_DEBUG: play() called with: {sound_name}")
        print(f"🔥 SOUND_DEBUG: Sound system enabled: {self.enabled}")
        
        if not self.enabled:
            print(f"🔥 SOUND_DEBUG: Sound system disabled, returning from play()")
            return
        
        print(f"🔥 SOUND_DEBUG: Loading sound: {sound_name}")
        sound = self._load_sound(sound_name)
        print(f"🔥 SOUND_DEBUG: Sound loaded: {sound is not None}")
        
        if sound:
            try:
                print(f"🔥 SOUND_DEBUG: About to call sound.play()")
                sound.play()
                print(f"🔥 SOUND_DEBUG: sound.play() completed successfully")
            except Exception as e:
                print(f"🔥 SOUND_DEBUG: ERROR in sound.play(): {e}")
                # Could not play sound - continuing silently
                pass
        else:
            print(f"🔥 SOUND_DEBUG: No sound object to play")
    
    def play_action_sound(self, action: str, amount: float = 0):
        """Play a sound for a poker action.
        
        Args:
            action: The poker action (check, call, bet, raise, fold, all_in)
            amount: The bet amount (used to determine sound type)
        """
        if not self.enabled:
            return
        
        # Skip voice activation in test mode or animation mode to speed up testing
        if not self.test_mode and not self.animation_mode and hasattr(self, 'voice_manager'):
            # Try to play voice announcement first
            try:
                self.voice_manager.play_action_voice(action, amount)
            except Exception as e:
                # Could not play voice - continuing with sound effects only
                pass
        
        # Also play sound effects
        action_sounds = self.sound_mapping.get("poker_actions", {})
        sound_name = action_sounds.get(action)
        
        if sound_name:
            self.play(sound_name)
        else:
            # Fallback to generic sounds
            if action == "fold":
                self.play("player_fold.wav")
            elif action in ["bet", "raise"]:
                self.play("player_bet.wav")
            elif action == "call":
                self.play("player_call.wav")
            elif action == "check":
                self.play("player_check.wav")
            elif action == "all_in":
                self.play("player_all_in.wav")
        
        # For money actions (bet, call, raise, all_in), also play chip sound
        if action in ["bet", "call", "raise", "all_in"] and amount > 0:
            # Play chip sound immediately after voice (no delay needed)
            self.play_chip_sound("bet")
            # Debug log for chip sound
            # Chip sound played for action with amount
    
    def play_card_sound(self, card_action: str):
        """Play a sound for card-related actions.
        
        Args:
            card_action: The card action (deal, shuffle, flip)
        """
        if not self.enabled:
            return
        
        # Use new configuration system if available
        if hasattr(self, 'poker_sound_events') and self.poker_sound_events:
            if card_action == "deal":
                sound_file = self.poker_sound_events.get("card_dealing")
                if sound_file:
                    self.play(sound_file)
                    return
            elif card_action == "shuffle":
                sound_file = self.poker_sound_events.get("card_shuffle")
                if sound_file:
                    self.play(sound_file)
                    return
        
        # Fallback to legacy mapping
        card_sounds = self.sound_mapping.get("card_actions", {})
        sound_name = card_sounds.get(card_action)
        
        if sound_name:
            self.play(sound_name)
        else:
            # Fallback
            if card_action == "deal":
                self.play("card_deal.wav")
            elif card_action == "shuffle":
                self.play("shuffle-cards-46455.mp3")
    
    def play_poker_event_sound(self, event_name: str):
        """Play a sound for a poker event using the configuration system.
        
        Args:
            event_name: The poker event name (e.g., 'card_dealing', 'winner_announce')
        """
        print(f"🔥 SOUND_DEBUG: play_poker_event_sound called with: {event_name}")
        print(f"🔥 SOUND_DEBUG: Sound system enabled: {self.enabled}")
        
        if not self.enabled:
            print(f"🔥 SOUND_DEBUG: Sound system disabled, returning")
            return
        
        # Use new configuration system
        if hasattr(self, 'poker_sound_events') and self.poker_sound_events:
            sound_file = self.poker_sound_events.get(event_name)
            print(f"🔥 SOUND_DEBUG: Found sound file for {event_name}: {sound_file}")
            if sound_file:
                print(f"🔥 SOUND_DEBUG: About to call self.play({sound_file})")
                self.play(sound_file)
                print(f"🔥 SOUND_DEBUG: self.play() call completed")
                return
        
        # Fallback to legacy system for common events
        fallback_mapping = {
            "card_dealing": "card_deal.wav",
            "card_shuffle": "shuffle-cards-46455.mp3",
            "chip_bet": "chip_bet.wav",
            "chip_collect": "pot_split.wav",
            "winner_announce": "winner_announce.wav",
            "turn_notification": "turn_notify.wav",
            "ui_click": "button_move.wav"
        }
        
        fallback_sound = fallback_mapping.get(event_name)
        if fallback_sound:
            print(f"🔥 SOUND_DEBUG: Using fallback sound: {fallback_sound}")
            self.play(fallback_sound)
        else:
            print(f"🔥 SOUND_DEBUG: No sound found for event: {event_name}")
    
    def get_action_sound_duration(self, action: str) -> float:
        """Get estimated duration of action sound in seconds.
        
        Args:
            action: The poker action (fold, call, bet, raise, check)
            
        Returns:
            float: Duration in seconds
        """
        # Voice duration estimates for GameDirector timing
        voice_durations = {
            "check": 0.8,   # "Check"
            "call": 0.8,    # "Call"  
            "bet": 0.9,     # "Bet"
            "raise": 1.0,   # "Raise"
            "fold": 0.8     # "Fold"
        }
        
        base_duration = voice_durations.get(action.lower(), 0.8)
        
        # Add sound effect duration if not in test mode
        if not self.test_mode and self.enabled:
            return base_duration
        else:
            # Shorter duration for test mode
            return 0.1
    
    def play_chip_sound(self, chip_action: str):
        """Play a sound for chip-related actions.
        
        Args:
            chip_action: The chip action (bet, collect, stack)
        """
        if not self.enabled:
            return
        
        chip_sounds = self.sound_mapping.get("chip_actions", {})
        sound_name = chip_sounds.get(chip_action)
        
        if sound_name:
            self.play(sound_name)
        else:
            # Fallback
            if chip_action == "bet":
                self.play("chip_bet.wav")
            elif chip_action == "collect":
                self.play("pot_split.wav")
    
    def play_ui_sound(self, ui_action: str):
        """Play a sound for UI actions.
        
        Args:
            ui_action: The UI action (click, error, success, notification)
        """
        if not self.enabled:
            return
        
        ui_sounds = self.sound_mapping.get("ui_actions", {})
        sound_name = ui_sounds.get(ui_action)
        
        if sound_name:
            self.play(sound_name)
        else:
            # Fallback
            if ui_action == "notification":
                self.play("turn_notify.wav")
            elif ui_action == "winner":
                self.play("winner_announce.wav")
    
    def set_volume(self, volume: float):
        """Set the volume for all sounds.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.volume = max(0.0, min(1.0, volume))
        for sound in self.sound_cache.values():
            sound.set_volume(self.volume)
    
    def enable(self):
        """Enable sound playback."""
        self.enabled = True
    
    def disable(self):
        """Disable sound playback."""
        self.enabled = False
    
    def set_test_mode(self, test_mode: bool):
        """Set test mode to disable voice activation during testing.
        
        Args:
            test_mode: If True, voice activation will be skipped
        """
        self.test_mode = test_mode
    
    def set_animation_mode(self, animation_mode: bool):
        """Set animation mode to disable voice during animations.
        
        Args:
            animation_mode: If True, voice activation will be skipped during animations
        """
        self.animation_mode = animation_mode
    
    def cleanup(self):
        """Clean up resources."""
        try:
            pygame.mixer.quit()
        except (pygame.error, OSError):
            pass 
```

---

### voice_manager.py

**Path**: `backend/utils/voice_manager.py`

```python
#!/usr/bin/env python3
"""
Voice Manager for Poker Strategy Practice System

Handles human voice announcements for poker actions and game events.
Uses pygame for cross-platform audio support.
"""

import os
import random
import pygame
from typing import Optional, Dict, List


class VoiceManager:
    """Manages human voice announcements for poker actions."""
    
    def __init__(self, voice_dir: str = None):
        """Initialize the voice manager.
        
        Args:
            voice_dir: Directory containing voice files (defaults to ../sounds/voice/)
        """
        self.voice_dir = voice_dir or os.path.join(
            os.path.dirname(__file__), '..', 'sounds', 'voice'
        )
        self.voice_cache = {}
        self.enabled = True
        self.volume = 0.8
        self.current_voice_type = "announcer_female"  # Default voice
        
        # Available voice types
        self.voice_types = [
            "announcer_female", "announcer_male", 
            "dealer_female", "dealer_male",
            "hostess_female", "tournament_female"
        ]
        
        # Voice mappings for different actions
        self.voice_mappings = {
            "check": "check.wav",
            "call": "call.wav", 
            "bet": "bet.wav",
            "raise": "raise.wav",
            "fold": "fold.wav",
            "all_in": "all_in.wav",
            "dealing": "dealing.wav",
            "shuffling": "shuffling.wav",
            "your_turn": "your_turn.wav",
            "winner": "winner.wav"
        }
    
    def set_voice_type(self, voice_type: str):
        """Set the voice type to use.
        
        Args:
            voice_type: One of the available voice types
        """
        if voice_type in self.voice_types:
            self.current_voice_type = voice_type
    
    def get_available_voice_types(self):
        """Get list of available voice types.
        
        Returns:
            List of available voice type names
        """
        return self.voice_types.copy()
    
    def get_current_voice_type(self):
        """Get the currently selected voice type.
        
        Returns:
            Current voice type name
        """
        return self.current_voice_type
    
    def _get_voice_path(self, action: str) -> Optional[str]:
        """Get the full path to a voice file.
        
        Args:
            action: The action to get voice for
            
        Returns:
            Full path to the voice file, or None if not found
        """
        if action not in self.voice_mappings:
            return None
        
        voice_file = self.voice_mappings[action]
        voice_path = os.path.join(self.voice_dir, self.current_voice_type, voice_file)
        
        if os.path.exists(voice_path):
            return voice_path
        
        return None
    
    def _load_voice(self, action: str) -> Optional[pygame.mixer.Sound]:
        """Load a voice file into memory.
        
        Args:
            action: The action to load voice for
            
        Returns:
            pygame Sound object, or None if loading failed
        """
        if not self.enabled:
            return None
        
        # Check cache first
        cache_key = f"{self.current_voice_type}_{action}"
        if cache_key in self.voice_cache:
            return self.voice_cache[cache_key]
        
        voice_path = self._get_voice_path(action)
        if not voice_path:
            # Voice file not found - using silent fallback
            return None
        
        try:
            voice = pygame.mixer.Sound(voice_path)
            voice.set_volume(self.volume)
            self.voice_cache[cache_key] = voice
            return voice
        except Exception as e:
            # Could not load voice - using silent fallback
            return None
    
    def play_voice(self, action: str):
        """Play a voice announcement for an action.
        
        Args:
            action: The action to announce (check, call, bet, raise, fold, etc.)
        """
        if not self.enabled:
            return
        
        voice = self._load_voice(action)
        if voice:
            try:
                voice.play()
            except Exception as e:
                print(f"Warning: Could not play voice for {action}: {e}")
    
    def play_action_voice(self, action: str, amount: float = 0):
        """Play voice for a poker action.
        
        Args:
            action: The poker action
            amount: The bet amount (for context)
        """
        if action == "all_in":
            self.play_voice("all_in")
        elif action in ["bet", "raise"]:
            self.play_voice("raise" if amount > 0 else "bet")
        elif action == "call":
            self.play_voice("call")
        elif action == "check":
            self.play_voice("check")
        elif action == "fold":
            self.play_voice("fold")
    
    def speak(self, message: str):
        """Speak a message (alias for play_voice for compatibility).
        
        Args:
            message: The message to speak
        """
        # Map common messages to voice actions
        message_lower = message.lower()
        if "all in" in message_lower or "all-in" in message_lower:
            self.play_voice("all_in")
        elif "raise" in message_lower:
            self.play_voice("raise")
        elif "bet" in message_lower:
            self.play_voice("bet")
        elif "call" in message_lower:
            self.play_voice("call")
        elif "check" in message_lower:
            self.play_voice("check")
        elif "fold" in message_lower:
            self.play_voice("fold")
        else:
            # Default to a generic announcement
            self.play_voice("your_turn")

    # --- Direct file playback support for EffectBus ---
    def play(self, rel_path: str) -> None:
        """Play a specific audio file path (relative or absolute).

        This is used by the EffectBus when a config maps voice lines
        directly to files. It attempts several resolution strategies:
        - Absolute path as provided
        - Relative to configured voice_dir
        - Relative to the project's sounds directory next to this module
        """
        if not self.enabled:
            return
        try:
            # Candidate 1: use path as-is
            path_candidates = [rel_path]

            # Candidate 2: under voice_dir
            path_candidates.append(os.path.join(self.voice_dir, rel_path))

            # Candidate 3: backend/sounds/<rel_path>
            here = os.path.dirname(__file__)
            path_candidates.append(os.path.join(here, '..', 'sounds', rel_path))

            chosen = None
            for p in path_candidates:
                p_abs = os.path.abspath(p)
                if os.path.exists(p_abs) and os.path.getsize(p_abs) > 0:
                    chosen = p_abs
                    break

            if not chosen:
                print(f"⚠️ VoiceManager: missing voice file {rel_path}")
                return

            try:
                snd = pygame.mixer.Sound(chosen)
                snd.set_volume(self.volume)
                snd.play()
            except Exception as e:
                print(f"⚠️ VoiceManager: failed to play {chosen}: {e}")
        except Exception as e:
            print(f"⚠️ VoiceManager: error resolving {rel_path}: {e}")
    
    def play_game_voice(self, game_event: str):
        """Play voice for game events.
        
        Args:
            game_event: The game event (dealing, shuffling, your_turn, winner)
        """
        if game_event in self.voice_mappings:
            self.play_voice(game_event)
    
    def set_volume(self, volume: float):
        """Set the volume for all voices.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.volume = max(0.0, min(1.0, volume))
        for voice in self.voice_cache.values():
            voice.set_volume(self.volume)
    
    def enable(self):
        """Enable voice announcements."""
        self.enabled = True
    
    def disable(self):
        """Disable voice announcements."""
        self.enabled = False
    
    def get_available_voices(self) -> List[str]:
        """Get list of available voice types."""
        return self.voice_types.copy()
    
    def cleanup(self):
        """Clean up resources."""
        self.voice_cache.clear() 
```

---

### poker_sound_config.json

**Path**: `backend/sounds/poker_sound_config.json`

```json
{
  "master_volume": 1.0,
  "sounds_enabled": true,
  "voice_enabled": true,
  "sound_directory": "sounds",
  "sounds": {
    "BET": "poker_chips1-87592.mp3",
    "RAISE": "201807__fartheststar__poker_chips1.wav",
    "CALL": "poker_chips1-87592.mp3",
    "CHECK": "player_check.wav",
    "FOLD": "player_fold.wav",
    "ALL_IN": "allinpushchips-96121.mp3",
    "DEAL_HOLE": "shuffle-cards-46455 (1).mp3",
    "DEAL_BOARD": "deal-hole-cards.wav",
    "DEAL_FLOP": "deal-hole-cards.wav",
    "DEAL_TURN": "deal-hole-cards.wav",
    "DEAL_RIVER": "deal-hole-cards.wav",
    "SHOWDOWN": "game-start-6104.mp3",
    "END_HAND": "click-345983.mp3",
    "HAND_START": "click-1-384917.mp3",
    "ROUND_START": "turn_notify.wav",
    "ROUND_END": "turn_notify.wav",
    "POST_BLIND": "poker_chips1-87592.mp3",
    "POST_SMALL_BLIND": "poker_chips1-87592.mp3",
    "POST_BIG_BLIND": "poker_chips1-87592.mp3",
    "CHIP_BET": "chip_bet.wav",
    "CHIP_COLLECT": "pot_split.wav",
    "POT_RAKE": "pot_rake.wav",
    "POT_SPLIT": "pot_split.wav",
    "TURN_NOTIFY": "turn_notify.wav",
    "BUTTON_MOVE": "button_move.wav",
    "ACTION_TIMEOUT": "turn_notify.wav",
    "CARD_SHUFFLE": "card_deal.wav",
    "CARD_FOLD": "card_fold.wav",
    "CHIP_MULTIPLE": "chip_bet.wav",
    "CHIP_SINGLE": "chip_bet.wav",
    "MONEY_BAG": "chip_bet.wav",
    "COIN_DROP": "chip_bet.wav",
    "CASH_REGISTER": "pot_split.wav",
    "NOTIFICATION": "turn_notify.wav",
    "UI_CLICK": "button_move.wav",
    "DEALING_VARIATION": "571577__el_boss__playing-card-deal-variation-1.wav",
    "POKER_CHIPS": "201807__fartheststar__poker_chips1.wav"
  },
  "voice_sounds": {
    "announcer_female": {
      "all_in": "voice/announcer_female/all_in.wav",
      "bet": "voice/announcer_female/bet.wav",
      "call": "voice/announcer_female/call.wav",
      "check": "voice/announcer_female/check.wav",
      "dealing": "voice/announcer_female/dealing.wav",
      "fold": "voice/announcer_female/fold.wav",
      "raise": "voice/announcer_female/raise.wav",
      "shuffling": "voice/announcer_female/shuffling.wav",
      "winner": "voice/announcer_female/winner.wav",
      "your_turn": "voice/announcer_female/your_turn.wav"
    },
    "announcer_male": {
      "all_in": "voice/announcer_male/all_in.wav",
      "bet": "voice/announcer_male/bet.wav",
      "call": "voice/announcer_male/call.wav",
      "check": "voice/announcer_male/check.wav",
      "dealing": "voice/announcer_male/dealing.wav",
      "fold": "voice/announcer_male/fold.wav",
      "raise": "voice/announcer_male/raise.wav",
      "shuffling": "voice/announcer_male/shuffling.wav",
      "winner": "voice/announcer_male/winner.wav",
      "your_turn": "voice/announcer_male/your_turn.wav"
    },
    "dealer_female": {
      "all_in": "voice/dealer_female/all_in.wav",
      "bet": "voice/dealer_female/bet.wav",
      "call": "voice/dealer_female/call.wav",
      "check": "voice/dealer_female/check.wav",
      "dealing": "voice/dealer_female/dealing.wav",
      "fold": "voice/dealer_female/fold.wav",
      "raise": "voice/dealer_female/raise.wav",
      "shuffling": "voice/dealer_female/shuffling.wav",
      "winner": "voice/dealer_female/winner.wav",
      "your_turn": "voice/dealer_female/your_turn.wav"
    },
    "dealer_male": {
      "all_in": "voice/dealer_male/all_in.wav",
      "bet": "voice/dealer_male/bet.wav",
      "call": "voice/dealer_male/call.wav",
      "check": "voice/dealer_male/check.wav",
      "dealing": "voice/dealer_male/dealing.wav",
      "fold": "voice/dealer_male/fold.wav",
      "raise": "voice/dealer_male/raise.wav",
      "shuffling": "voice/dealer_male/shuffling.wav",
      "winner": "voice/dealer_male/winner.wav",
      "your_turn": "voice/dealer_male/your_turn.wav"
    },
    "hostess_female": {
      "all_in": "voice/hostess_female/all_in.wav",
      "bet": "voice/hostess_female/bet.wav",
      "call": "voice/hostess_female/call.wav",
      "check": "voice/hostess_female/check.wav",
      "dealing": "voice/hostess_female/dealing.wav",
      "fold": "voice/hostess_female/fold.wav",
      "raise": "voice/hostess_female/raise.wav",
      "shuffling": "voice/hostess_female/shuffling.wav",
      "winner": "voice/hostess_female/winner.wav",
      "your_turn": "voice/hostess_female/your_turn.wav"
    },
    "tournament_female": {
      "all_in": "voice/tournament_female/all_in.wav",
      "bet": "voice/tournament_female/bet.wav",
      "call": "voice/tournament_female/call.wav",
      "check": "voice/tournament_female/check.wav",
      "dealing": "voice/tournament_female/dealing.wav",
      "fold": "voice/tournament_female/fold.wav",
      "raise": "voice/tournament_female/raise.wav",
      "shuffling": "voice/tournament_female/shuffling.wav",
      "winner": "voice/tournament_female/winner.wav",
      "your_turn": "voice/tournament_female/your_turn.wav"
    }
  }
}
```

---

## SERVICE LAYER

### service_container.py

**Path**: `backend/ui/services/service_container.py`

```python
from typing import Any, Dict


class ServiceContainer:
    """
    Lightweight service registry with app-wide and session-scoped services.
    """

    def __init__(self) -> None:
        self.app_scope: Dict[str, Any] = {}
        self.session_scopes: Dict[str, Dict[str, Any]] = {}

    def provide_app(self, name: str, service: Any) -> None:
        self.app_scope[name] = service

    def get_app(self, name: str) -> Any:
        return self.app_scope[name]

    def provide_session(
        self, session_id: str, name: str, service: Any
    ) -> None:
        self.session_scopes.setdefault(session_id, {})[name] = service

    def get_session(self, session_id: str, name: str) -> Any:
        return self.session_scopes[session_id][name]

    def dispose_session(self, session_id: str) -> None:
        scope = self.session_scopes.pop(session_id, {})
        for service in scope.values():
            if hasattr(service, "dispose"):
                try:
                    service.dispose()
                except Exception:
                    # Best-effort cleanup
                    pass

```

---

### theme_manager.py

**Path**: `backend/ui/services/theme_manager.py`

```python
from __future__ import annotations

from typing import Dict, Any, Callable, List
import importlib
import json
import os

# Import the new token-driven theme system
try:
    from .theme_factory import build_all_themes
    from .theme_loader import get_theme_loader
    from .state_styler import (
        get_state_styler,
        get_selection_styler,
        get_emphasis_bar_styler
    )
    TOKEN_DRIVEN_THEMES_AVAILABLE = True
except ImportError:
    TOKEN_DRIVEN_THEMES_AVAILABLE = False


# Default theme name for fallbacks
DEFAULT_THEME_NAME = "Forest Green Professional 🌿"  # Updated to match JSON


class ThemeManager:
    """
    App-scoped theme service that owns THEME/FONTS tokens and persistence.
    - Token access via dot paths (e.g., "table.felt", "pot.valueText").
    - Registers multiple theme packs and persists selected pack + fonts.
    - Now fully config-driven using poker_themes.json
    """

    CONFIG_PATH = os.path.join("backend", "ui", "theme_config.json")

    def __init__(self) -> None:
        self._theme: Dict[str, Any]
        self._fonts: Dict[str, Any]
        self._themes: Dict[str, Dict[str, Any]] = {}
        self._current: str | None = None
        self._subs: List[Callable[["ThemeManager"], None]] = []
        # Load defaults from codebase
        try:
            gm = importlib.import_module("backend.core.gui_models")
            self._theme = dict(getattr(gm, "THEME", {}))
            self._fonts = dict(getattr(gm, "FONTS", {}))
        except Exception:
            self._theme = {"table_felt": "#2B2F36", "text": "#E6E9EF"}
            self._fonts = {
                "main": ("Arial", 20),  # Base font at 20px for readability
                "pot_display": ("Arial", 28, "bold"),  # +8 for pot display
                "bet_amount": ("Arial", 24, "bold"),  # +4 for bet amounts
                "body": ("Consolas", 20),  # Same as main for body text
                "small": ("Consolas", 16),  # -4 for smaller text
                "header": ("Arial", 22, "bold")  # +2 for headers
            }
        # Apply persisted config if present
        # Register built-in packs
        packs = self._builtin_packs()
        for name, tokens in packs.items():
            self.register(name, tokens)
        self._load_config()
        if not self._current:
            # Use Forest Green Professional as safe default
            if DEFAULT_THEME_NAME in self._themes:
                self._current = DEFAULT_THEME_NAME
                self._theme = dict(self._themes[DEFAULT_THEME_NAME])
            else:
                # Fallback: choose first pack or defaults
                self._current = next(iter(self._themes.keys()), None)

    def _builtin_packs(self) -> Dict[str, Dict[str, Any]]:
        """Get built-in theme packs - now using token-driven system"""
        if TOKEN_DRIVEN_THEMES_AVAILABLE:
            try:
                # Use the new deterministic token system
                themes = build_all_themes()
                print(f"🎨 ThemeManager: Loaded {len(themes)} themes: {list(themes.keys())}")
                return themes
            except Exception as e:
                print(f"⚠️ ThemeManager: Config-driven themes failed: {e}")
                return self._legacy_builtin_packs()
        else:
            print("⚠️ ThemeManager: Token-driven themes not available, using legacy")
            # Fallback to legacy themes if token system not available
            return self._legacy_builtin_packs()
    
    def _legacy_builtin_packs(self) -> Dict[str, Dict[str, Any]]:
        """Minimal legacy fallback if config system completely fails."""
        return {
            "Forest Green Professional 🌿": {
                "table.felt": "#2D5A3D",
                "table.rail": "#4A3428", 
                "text.primary": "#EDECEC",
                "panel.bg": "#1F2937",
                "panel.fg": "#E5E7EB"
            }
        }

    def get_theme(self) -> Dict[str, Any]:
        return self._theme

    def get_fonts(self) -> Dict[str, Any]:
        return self._fonts
    
    def reload(self):
        """Reload themes from file - critical for Theme Manager integration."""
        print("🔄 ThemeManager: Reloading themes from file...")
        
        # Clear cached themes
        self._themes = {}
        
        # Reload using the same logic as __init__
        if TOKEN_DRIVEN_THEMES_AVAILABLE:
            try:
                # Force reload from file
                loader = get_theme_loader()
                if hasattr(loader, 'reload'):
                    loader.reload()
                
                # Rebuild all themes
                themes = build_all_themes()
                
                # Register all themes
                for name, tokens in themes.items():
                    self.register(name, tokens)
                
                print(f"🔄 ThemeManager: Reloaded {len(themes)} themes from file")
                
                # Reload current theme if it still exists
                current_name = self.current_profile_name()
                if current_name in self._themes:
                    self._theme = self._themes[current_name]
                    print(f"🎯 ThemeManager: Restored current theme: {current_name}")
                else:
                    # Fallback to first available theme
                    if self._themes:
                        first_theme_name = list(self._themes.keys())[0]
                        self._theme = self._themes[first_theme_name]
                        self._current_profile = first_theme_name
                        print(f"🔄 ThemeManager: Switched to: {first_theme_name}")
                
            except Exception as e:
                print(f"⚠️ ThemeManager: Reload failed: {e}")
        else:
            print("⚠️ ThemeManager: Token-driven themes not available for reload")

    def set_fonts(self, fonts: Dict[str, Any]) -> None:
        self._fonts = fonts
        self._save_config()
    
    def get_dimensions(self) -> Dict[str, Any]:
        """Get theme dimensions for consistent spacing and sizing."""
        try:
            # Try to get dimensions from theme config
            theme_data = self.get_theme()
            if theme_data and "dimensions" in theme_data:
                return theme_data["dimensions"]
            
            # Fallback to default dimensions
            return {
                "padding": {"small": 5, "medium": 8, "large": 16, "xlarge": 18},
                "text_height": {"small": 3, "medium": 4, "large": 6},
                "border_width": {"thin": 1, "medium": 2, "thick": 3},
                "widget_width": {"narrow": 5, "medium": 8, "wide": 12}
            }
        except Exception:
            # Ultimate fallback
            return {
                "padding": {"small": 5, "medium": 8, "large": 16, "xlarge": 18},
                "text_height": {"small": 3, "medium": 4, "large": 6},
                "border_width": {"thin": 1, "medium": 2, "thick": 3},
                "widget_width": {"narrow": 5, "medium": 8, "wide": 12}
            }

    def register(self, name: str, tokens: Dict[str, Any]) -> None:
        self._themes[name] = tokens

    def names(self) -> list[str]:
        """Return all registered theme names from config-driven system."""
        if TOKEN_DRIVEN_THEMES_AVAILABLE:
            # Try to get theme names from config-driven system
            try:
                loader = get_theme_loader()
                theme_list = loader.get_theme_list()
                return [theme_info["name"] for theme_info in theme_list]
            except Exception:
                pass
        
        # Fallback: return all registered theme names
        return list(self._themes.keys())

    def register_all(self, packs: Dict[str, Dict[str, Any]]) -> None:
        """Register all themes from packs dictionary."""
        for name, tokens in packs.items():
            self.register(name, tokens)

    def current(self) -> str | None:
        """Return current theme name."""
        return self._current

    def set_profile(self, name: str) -> None:
        if name in self._themes:
            self._current = name
            self._theme = dict(self._themes[name])
            self._save_config()
            for fn in list(self._subs):
                fn(self)

    def _load_config(self) -> None:
        try:
            if os.path.exists(self.CONFIG_PATH):
                with open(self.CONFIG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                prof = data.get("profile")
                if prof and prof in self._themes:
                    self._current = prof
                    self._theme = dict(self._themes[prof])
                fonts = data.get("fonts")
                if isinstance(fonts, dict):
                    self._fonts.update(fonts)
        except Exception:
            pass

    def _save_config(self) -> None:
        try:
            os.makedirs(os.path.dirname(self.CONFIG_PATH), exist_ok=True)
            payload = {"profile": self.current_profile_name(), "fonts": self._fonts}
            with open(self.CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
        except Exception:
            pass

    def current_profile_name(self) -> str:
        for name, theme in self._themes.items():
            if all(self._theme.get(k) == theme.get(k) for k in ("table.felt",)):
                return name
        return "Custom"

    def get(self, token: str, default=None):
        # Dot-path lookup in current theme; fallback to fonts when font.* requested
        if token.startswith("font."):
            return self._theme.get(token) or self._fonts.get(token[5:], default)
        cur = self._theme
        for part in token.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                return self._theme.get(token, default)
        return cur
    
    def get_all_tokens(self) -> Dict[str, Any]:
        """Get complete token dictionary for current theme"""
        return dict(self._theme)
    
    def get_base_colors(self) -> Dict[str, str]:
        """Get the base color palette for current theme (if available)"""
        if TOKEN_DRIVEN_THEMES_AVAILABLE:
            # Try new config-driven system first
            try:
                loader = get_theme_loader()
                # Convert display name to theme ID using proper mapping
                name_to_id_map = {
                    "Forest Green Professional 🌿": "forest-green-pro",
                    "Velvet Burgundy 🍷": "velvet-burgundy", 
                    "Emerald Aurora 🌌": "emerald-aurora",
                    "Imperial Jade 💎": "imperial-jade",
                    "Ruby Royale ❤️‍🔥": "ruby-royale",
                    "Coral Royale 🪸": "coral-royale",
                    "Golden Dusk 🌇": "golden-dusk",
                    "Klimt Royale ✨": "klimt-royale",
                    "Deco Luxe 🏛️": "deco-luxe",
                    "Oceanic Aqua 🌊": "oceanic-aqua",
                    "Royal Sapphire 🔷": "royal-sapphire",
                    "Monet Twilight 🎨": "monet-twilight",
                    "Caravaggio Sepia Noir 🕯️": "caravaggio-sepia-noir",
                    "Stealth Graphite Steel 🖤": "stealth-graphite-steel",
                    "Sunset Mirage 🌅": "sunset-mirage",
                    "Cyber Neon ⚡": "cyber-neon"
                }
                theme_id = name_to_id_map.get(self._current, "forest-green-pro") if self._current else "forest-green-pro"
                theme_config = loader.get_theme_by_id(theme_id)
                return theme_config.get("palette", {})
            except Exception:
                pass
        return {}
    
    def get_current_theme_id(self) -> str:
        """Get current theme ID for config-driven styling."""
        if self._current:
            # Convert display name to kebab-case ID (remove emojis)
            theme_id = self._current.lower()
            # Remove emojis and extra spaces
            for emoji in ["🌿", "🍷", "💎", "🌌", "❤️‍🔥", "🪸", "🌇", "✨", "🏛️", "🌊", "🔷", "🎨", "🕯️", "🖤", "🌅", "⚡"]:
                theme_id = theme_id.replace(emoji, "")
            theme_id = theme_id.strip().replace(" ", "-")
            return theme_id
        return "forest-green-pro"
    
    def get_state_styler(self):
        """Get state styler for player state effects."""
        if TOKEN_DRIVEN_THEMES_AVAILABLE:
            return get_state_styler()
        return None
    
    def get_selection_styler(self):
        """Get selection styler for list/tree highlighting."""
        if TOKEN_DRIVEN_THEMES_AVAILABLE:
            return get_selection_styler()
        return None
    
    def get_emphasis_bar_styler(self):
        """Get emphasis bar styler for luxury text bars."""
        if TOKEN_DRIVEN_THEMES_AVAILABLE:
            return get_emphasis_bar_styler()
        return None
    
    def get_theme_metadata(self, theme_name: str) -> Dict[str, str]:
        """Get theme metadata like intro and persona from config."""
        if TOKEN_DRIVEN_THEMES_AVAILABLE:
            try:
                loader = get_theme_loader()
                theme_list = loader.get_theme_list()
                for theme_info in theme_list:
                    if theme_info["name"] == theme_name:
                        theme_config = loader.get_theme_by_id(theme_info["id"])
                        return {
                            "intro": theme_config.get("intro", ""),
                            "persona": theme_config.get("persona", ""),
                            "id": theme_config.get("id", "")
                        }
            except Exception:
                pass
        return {"intro": "", "persona": "", "id": ""}

    def subscribe(self, fn: Callable[["ThemeManager"], None]) -> Callable[[], None]:
        self._subs.append(fn)
        def _unsub():
            try:
                self._subs.remove(fn)
            except ValueError:
                pass
        return _unsub

```

---

### game_director.py

**Path**: `backend/services/game_director.py`

```python

```

---

### event_bus.py

**Path**: `backend/ui/services/event_bus.py`

```python
from collections import defaultdict
from typing import Any, Callable, Dict, List


class EventBus:
    """
    Simple in-memory pub/sub event bus with string topics.

    Topics should be namespaced using a session identifier to prevent
    cross-talk between tabs/sessions.
    Example: f"{session_id}:ui:action".
    """

    def __init__(self) -> None:
        self._subs: Dict[str, List[Callable[[Any], None]]] = defaultdict(list)

    def topic(self, session_id: str, name: str) -> str:
        return f"{session_id}:{name}"

    def subscribe(
        self, topic: str, handler: Callable[[Any], None]
    ) -> Callable[[], None]:
        self._subs[topic].append(handler)

        def unsubscribe() -> None:
            try:
                self._subs[topic].remove(handler)
            except ValueError:
                pass

        return unsubscribe

    def publish(self, topic: str, payload: Any) -> None:
        # Copy list to avoid mutation during iteration
        for handler in list(self._subs.get(topic, [])):
            handler(payload)



```

---

## HAND DATA SOURCES

### legendary_hands_sample.json

**Path**: `backend/data/legendary_hands_normalized.json`

```json
{
  "note": "Large JSON file - showing first 50 lines for reference",
  "full_file_location": "backend/data/legendary_hands_normalized.json",
  {
    "hands": [
      {
        "metadata": {
          "table_id": "Legendary-Table-1",
          "hand_id": "BB001",
          "variant": "NLHE",
          "max_players": 2,
          "small_blind": 5,
          "big_blind": 10,
          "ante": 0,
          "rake": 0,
          "currency": "CHIPS",
          "started_at_utc": null,
          "ended_at_utc": null,
          "run_count": 1,
          "session_type": "review",
          "bot_strategy": null,
          "analysis_tags": [],
          "button_seat_no": 1,
          "hole_cards": {
            "seat1": [
              "Kh",
              "Kd"
            ],
            "seat2": [
              "Ad",
              "2c"
            ]
          }
        },
        "seats": [
          {
            "seat_no": 1,
            "player_uid": "seat1",
            "display_name": "Player 1",
            "starting_stack": 1000,
            "is_button": true
          },
          {
            "seat_no": 2,
            "player_uid": "seat2",
            "display_name": "Player 2",
            "starting_stack": 1000,
            "is_button": false
          }
        ],
        "hero_player_uid": "seat1",
        "streets": {
          "PREFLOP": {
  "...": "truncated for brevity"
}
```

---

### gto_hands_sample.json

**Status**: ⚠️ File not found at `gto_hands.json`

---

## TESTING INFRASTRUCTURE

### test_mvu_simple.py

**Path**: `backend/test_mvu_simple.py`

```python
#!/usr/bin/env python3
"""
Simple MVU Test - Just test the store directly
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from ui.mvu import MVUStore, Model, NextPressed, LoadHand
from ui.mvu.drivers import create_driver


def main():
    """Test MVU store directly"""
    print("🧪 Testing MVU Store Directly...")
    
    # Create initial model
    initial_model = Model.initial(session_mode="REVIEW")
    
    # Create store
    store = MVUStore(initial_model=initial_model)
    
    # Create sample hand data
    hand_data = {
        "hand_id": "SIMPLE_TEST",
        "seats": {
            0: {
                "player_uid": "hero",
                "name": "Hero", 
                "stack": 1000,
                "chips_in_front": 0,
                "folded": False,
                "all_in": False,
                "cards": ["As", "Kh"],
                "position": 0
            },
            1: {
                "player_uid": "villain",
                "name": "Villain",
                "stack": 1000,
                "chips_in_front": 0,
                "folded": False,
                "all_in": False,
                "cards": ["Qd", "Jc"],
                "position": 1
            }
        },
        "stacks": {0: 1000, 1: 1000},
        "board": [],
        "pot": 0,
        "actions": [
            {"seat": 0, "action": "RAISE", "amount": 30, "street": "PREFLOP"},
            {"seat": 1, "action": "CALL", "amount": 30, "street": "PREFLOP"},
            {"seat": 0, "action": "BET", "amount": 50, "street": "FLOP"},
            {"seat": 1, "action": "FOLD", "amount": None, "street": "FLOP"}
        ],
        "review_len": 4,
        "to_act_seat": 0,
        "legal_actions": ["CHECK", "CALL", "BET", "RAISE", "FOLD"]
    }
    
    # Create and set driver
    driver = create_driver("REVIEW", hand_data=hand_data)
    store.set_session_driver(driver)
    
    # Load hand
    print("\n📋 Loading hand...")
    store.dispatch(LoadHand(hand_data=hand_data))
    
    # Print initial state
    model = store.get_model()
    print(f"\n🎯 Initial state: cursor={model.review_cursor}, len={model.review_len}, to_act={model.to_act_seat}")
    
    # Click Next button 5 times
    for i in range(5):
        print(f"\n🖱️ === BUTTON CLICK #{i+1} ===")
        store.dispatch(NextPressed())
        
        # Print state after click
        model = store.get_model()
        print(f"🎯 After click {i+1}: cursor={model.review_cursor}, len={model.review_len}, to_act={model.to_act_seat}, pot={model.pot}")
        
        # Print seat states
        for seat_num, seat in model.seats.items():
            print(f"  Seat {seat_num}: {seat.name} - Stack: ${seat.stack}, Bet: ${seat.chips_in_front}, Folded: {seat.folded}, Acting: {seat.acting}")
    
    print("\n✅ Test completed!")


if __name__ == "__main__":
    main()

```

---

### test_mvu_implementation.py

**Path**: `backend/test_mvu_implementation.py`

```python
#!/usr/bin/env python3
"""
Test MVU Implementation
Simple test to verify our MVU poker table architecture works
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from ui.mvu import MVUHandsReviewTab


def main():
    """Test the MVU implementation"""
    print("🧪 Testing MVU Implementation...")
    
    # Create root window
    root = tk.Tk()
    root.title("MVU Poker Table Test")
    root.geometry("1200x800")
    
    # Create a simple services mock
    class MockServices:
        def __init__(self):
            self._services = {}
        
        def get_app(self, name):
            return self._services.get(name)
        
        def provide_app(self, name, service):
            self._services[name] = service
    
    services = MockServices()
    
    # Create MVU Hands Review Tab
    try:
        review_tab = MVUHandsReviewTab(root, services=services)
        review_tab.pack(fill="both", expand=True)
        
        print("✅ MVU HandsReviewTab created successfully!")
        print("🎮 Use the UI to test the MVU architecture")
        
        # Add cleanup on close
        def on_closing():
            review_tab.dispose()
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Start the UI
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error creating MVU tab: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

```

---

## APPLICATION SHELL

### app_shell.py

**Path**: `backend/ui/app_shell.py`

```python
import tkinter as tk
from tkinter import ttk
import uuid

from .services.event_bus import EventBus
from .services.service_container import ServiceContainer
from .services.timer_manager import TimerManager
from .services.theme_manager import ThemeManager
from .services.hands_repository import HandsRepository, StudyMode
from .state.store import Store
from .state.reducers import root_reducer
from .mvu.hands_review_mvu import MVUHandsReviewTab as HandsReviewTab
from .tabs.practice_session_tab import PracticeSessionTab
from .tabs.gto_session_tab import GTOSessionTab

from .menu_integration import add_theme_manager_to_menu


class AppShell(ttk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root  # Store root reference for menu integration
        self.pack(fill="both", expand=True)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # app-scoped services
        self.services = ServiceContainer()
        self.services.provide_app("event_bus", EventBus())
        self.services.provide_app("theme", ThemeManager())
        self.services.provide_app("hands_repository", HandsRepository())
        
        # Create global GameDirector for action sequencing
        from .services.game_director import GameDirector
        game_director = GameDirector(event_bus=self.services.get_app("event_bus"))
        self.services.provide_app("game_director", game_director)
        
        # Create global EffectBus service for sound management
        from .services.effect_bus import EffectBus
        effect_bus = EffectBus(
            game_director=game_director,
            event_bus=self.services.get_app("event_bus")
        )
        self.services.provide_app("effect_bus", effect_bus)
        
        # Create architecture compliant hands review controller
        from .services.hands_review_event_controller import HandsReviewEventController
        
        # Initialize Store with initial state and reducer
        initial_state = {
            "table": {"dim": {"width": 800, "height": 600}},
            "seats": [],
            "board": [],
            "pot": {"amount": 0},
            "dealer": {},
            "review": {},
            "enhanced_rpgw": {},
            "event_bus": self.services.get_app("event_bus")
        }
        store = Store(initial_state, root_reducer)
        self.services.provide_app("store", store)
        
        hands_review_controller = HandsReviewEventController(
            event_bus=self.services.get_app("event_bus"),
            store=store,
            services=self.services
        )
        self.services.provide_app("hands_review_controller", hands_review_controller)
        
        # Subscribe to voice events to keep architecture event-driven
        def _on_voice(payload):
            try:
                action = (payload or {}).get("action")
                vm = getattr(effect_bus, "voice_manager", None)
                if not (vm and action):
                    return
                cfg = getattr(effect_bus, "config", {}) or {}
                voice_type = getattr(effect_bus, "voice_type", "")
                table = (cfg.get("voice_sounds", {}) or {}).get(voice_type, {})
                rel = table.get(action)
                if rel:
                    vm.play(rel)
            except Exception:
                pass
        self.services.get_app("event_bus").subscribe("effect_bus:voice", _on_voice)
        
        # Create shared store for poker game state (per architecture doc)
        initial_state = {
            "table": {"dim": (0, 0)},
            "pot": {"amount": 0},
            "seats": [],
            "board": [],
            "dealer": 0,
            "active_tab": "",
            "review": {
                "hands": [],
                "filter": {},
                "loaded_hand": None,
                "study_mode": StudyMode.REPLAY.value,
                "collection": None
            }
        }
        self.services.provide_app("store", Store(initial_state, root_reducer))

        # Create menu system
        self._create_menu_system()
        
        # tabs (order: Practice, GTO, Hands Review - main product features only)
        self._add_tab("Practice Session", PracticeSessionTab)
        self._add_tab("GTO Session", GTOSessionTab)
        self._add_tab("Hands Review", HandsReviewTab)
        # Bind global font size shortcuts (Cmd/Ctrl - and =)
        self._bind_font_shortcuts(root)

    def _add_tab(self, title: str, TabClass):
        session_id = str(uuid.uuid4())
        timers = TimerManager(self)
        self.services.provide_session(session_id, "timers", timers)

        # Update active tab in shared store
        store = self.services.get_app("store")
        store.dispatch({"type": "SET_ACTIVE_TAB", "name": title})
        
        # Create tab with services
        tab = TabClass(self.notebook, self.services)
        self.notebook.add(tab, text=title)
        
        # Call on_show if available
        if hasattr(tab, "on_show"):
            tab.on_show()

    def _create_menu_system(self):
        """Create the application menu system."""
        # Create menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Session", command=self._new_session)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Zoom In", accelerator="Cmd+=", command=lambda: self._increase_font(None))
        view_menu.add_command(label="Zoom Out", accelerator="Cmd+-", command=lambda: self._decrease_font(None))
        view_menu.add_command(label="Reset Zoom", accelerator="Cmd+0", command=lambda: self._reset_font(None))
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        
        # Theme management
        settings_menu.add_command(label="Theme Editor", command=self._open_theme_editor)
        settings_menu.add_command(label="Sound Settings", command=self._open_sound_settings)
        settings_menu.add_separator()
        
        # Add Theme Manager to Settings menu using our integration helper
        add_theme_manager_to_menu(settings_menu, self.root, self._on_theme_changed)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
        
    def _new_session(self):
        """Start a new session."""
        print("🔄 New session requested")
        # TODO: Implement session reset
        
    def _on_theme_changed(self):
        """Called when theme is changed via Theme Manager."""
        print("🎨 Theme changed - refreshing UI...")
        
        try:
            # Reload theme manager to get latest changes
            theme_manager = self.services.get_app("theme")
            if hasattr(theme_manager, 'reload'):
                theme_manager.reload()
            
            # Force rebuild themes to pick up any live changes
            try:
                from .services.theme_factory import build_all_themes
                themes = build_all_themes()
                # Register updated themes
                for name, tokens in themes.items():
                    theme_manager.register(name, tokens)
                print(f"🔄 Rebuilt and registered {len(themes)} themes")
            except Exception as e:
                print(f"⚠️ Theme rebuild warning: {e}")
            
            # Refresh all tabs with new theme
            for i in range(self.notebook.index("end")):
                try:
                    tab = self.notebook.nametowidget(self.notebook.tabs()[i])
                    
                    # Try multiple refresh methods
                    if hasattr(tab, '_refresh_ui_colors'):
                        tab._refresh_ui_colors()
                        print(f"✅ Refreshed tab {i} via _refresh_ui_colors")
                    elif hasattr(tab, 'refresh_theme'):
                        tab.refresh_theme()
                        print(f"✅ Refreshed tab {i} via refresh_theme")
                    elif hasattr(tab, '_on_theme_changed'):
                        tab._on_theme_changed()
                        print(f"✅ Refreshed tab {i} via _on_theme_changed")
                    else:
                        print(f"ℹ️ Tab {i} has no theme refresh method")
                        
                except Exception as e:
                    print(f"⚠️ Error refreshing tab {i}: {e}")
            
            print("✅ Live theme refresh completed")
            
        except Exception as e:
            print(f"❌ Theme refresh error: {e}")
            import traceback
            traceback.print_exc()
        
    def _show_about(self):
        """Show about dialog."""
        from tkinter import messagebox
        messagebox.showinfo(
            "About Poker Pro Trainer",
            "Poker Pro Trainer\n\n"
            "Advanced poker training with luxury themes\n"
            "and professional game analysis.\n\n"
            "🎨 Theme Manager integrated\n"
            "🃏 16 luxury themes available\n"
            "📊 Comprehensive hand review\n"
            "🤖 AI-powered training"
        )

    def _bind_font_shortcuts(self, root):
        # macOS Command key bindings (Cmd - decreases, Cmd = increases)
        root.bind_all("<Command-minus>", self._decrease_font)
        root.bind_all("<Command-equal>", self._increase_font)  # This is Cmd = (increase)
        root.bind_all("<Command-0>", self._reset_font)
        
        # Additional symbols that might work
        root.bind_all("<Command-plus>", self._increase_font)   # Shift+= gives +
        
        # Numpad variants
        root.bind_all("<Command-KP_Subtract>", self._decrease_font)
        root.bind_all("<Command-KP_Add>", self._increase_font)
        
        # Windows/Linux Control variants  
        root.bind_all("<Control-minus>", self._decrease_font)
        root.bind_all("<Control-equal>", self._increase_font)
        root.bind_all("<Control-plus>", self._increase_font)
        root.bind_all("<Control-0>", self._reset_font)
        
        print("🔧 Font shortcuts bound successfully")

    def _set_global_font_scale(self, delta: int | None):
        print(f"🔧 Font scale called with delta: {delta}")
        theme: ThemeManager = self.services.get_app("theme")
        fonts = dict(theme.get_fonts())
        base = list(fonts.get("main", ("Arial", 20, "normal")))
        print(f"🔧 Current base font: {base}")
        
        if delta is None:
            new_base_size = 20  # Default 20px size for readability
        else:
            new_base_size = max(10, min(40, int(base[1]) + delta))
        
        print(f"🔧 New base size: {new_base_size}")
        
        # Scale all fonts proportionally from 20px base
        fonts["main"] = (base[0], new_base_size, base[2] if len(base) > 2 else "normal")
        fonts["pot_display"] = (base[0], new_base_size + 8, "bold")  # +8 for pot display
        fonts["bet_amount"] = (base[0], new_base_size + 4, "bold")   # +4 for bet amounts
        fonts["body"] = ("Consolas", max(new_base_size, 12))         # Same as main for body text
        fonts["small"] = ("Consolas", max(new_base_size - 4, 10))    # -4 for smaller text
        fonts["header"] = (base[0], max(new_base_size + 2, 14), "bold") # +2 for headers
        
        print(f"🔧 Updated fonts: {fonts}")
        theme.set_fonts(fonts)
        
        # Force all tabs to re-render with new fonts
        for idx in range(self.notebook.index("end")):
            tab_widget = self.notebook.nametowidget(self.notebook.tabs()[idx])
            if hasattr(tab_widget, "on_show"):
                tab_widget.on_show()
            # Also force font refresh if the widget has that method
            if hasattr(tab_widget, "_refresh_fonts"):
                tab_widget._refresh_fonts()
        print("🔧 Font scaling complete")

    def _increase_font(self, event=None):
        print("🔧 Increase font called!")
        self._set_global_font_scale(+1)

    def _decrease_font(self, event=None):
        print("🔧 Decrease font called!")
        self._set_global_font_scale(-1)

    def _reset_font(self, event=None):
        print("🔧 Reset font called!")
        self._set_global_font_scale(None)

    def _open_theme_editor(self):
        """Open the Theme Editor in a new window."""
        try:
            from .tabs.theme_editor_tab import ThemeEditorTab
            # Create a new toplevel window for the theme editor
            theme_window = tk.Toplevel(self.root)
            theme_window.title("Theme Editor - Poker Pro Trainer")
            theme_window.geometry("900x700")
            theme_window.resizable(True, True)
            
            # Center the window on screen
            theme_window.update_idletasks()
            x = (theme_window.winfo_screenwidth() // 2) - (900 // 2)
            y = (theme_window.winfo_screenheight() // 2) - (700 // 2)
            theme_window.geometry(f"900x700+{x}+{y}")
            
            # Create the theme editor tab in the new window
            theme_editor = ThemeEditorTab(theme_window, self.services)
            theme_editor.pack(fill=tk.BOTH, expand=True)
            
            print("🎨 Theme Editor opened in new window")
        except Exception as e:
            print(f"❌ Error opening Theme Editor: {e}")
            import traceback
            traceback.print_exc()

    def _open_sound_settings(self):
        """Open the Sound Settings in a new window."""
        try:
            from .tabs.sound_settings_tab import SoundSettingsTab
            # Create a new toplevel window for the sound settings
            sound_window = tk.Toplevel(self.root)
            sound_window.title("Sound Settings - Poker Pro Trainer")
            sound_window.geometry("1200x800")
            sound_window.resizable(True, True)
            
            # Center the window on screen
            sound_window.update_idletasks()
            x = (sound_window.winfo_screenwidth() // 2) - (1200 // 2)
            y = (sound_window.winfo_screenheight() // 2) - (800 // 2)
            sound_window.geometry(f"1200x800+{x}+{y}")
            
            # Create the sound settings tab in the new window
            sound_settings = SoundSettingsTab(sound_window, self.services)
            sound_settings.pack(fill=tk.BOTH, expand=True)
            
            print("🔊 Sound Settings opened in new window")
        except Exception as e:
            print(f"❌ Error opening Sound Settings: {e}")
            import traceback
            traceback.print_exc()



```

---

### run_new_ui.py

**Path**: `backend/run_new_ui.py`

```python
import tkinter as tk
import sys
import os

def check_terminal_compatibility():
    """Check if we're running in VS Code integrated terminal and warn user."""
    if os.environ.get('TERM_PROGRAM') == 'vscode':
        print("⚠️  WARNING: Running GUI in VS Code integrated terminal may cause crashes!")
        print("💡 RECOMMENDED: Run this from macOS Terminal app instead:")
        print(f"   cd {os.getcwd()}")
        print(f"   python3 {os.path.basename(__file__)}")
        print("🚀 Continuing automatically...")
        print()
        
        # Commented out for convenience during development
        # response = input("Continue anyway? (y/N): ").lower().strip()
        # if response not in ['y', 'yes']:
        #     print("Exiting safely. Run from external terminal for best experience.")
        #     sys.exit(0)

try:  # Prefer package-relative import (python -m backend.run_new_ui)
    from .ui.app_shell import AppShell  # type: ignore
except Exception:
    try:  # Running as a script from backend/ (python backend/run_new_ui.py)
        from ui.app_shell import AppShell  # type: ignore
    except Exception:
        # Last resort: ensure repo root is on sys.path then import absolute
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from ui.app_shell import AppShell  # type: ignore


def main() -> None:
    # Apply runtime fixes before starting the application
    try:
        print("🔧 Applying runtime fixes...")
        from fix_runtime_errors import main as apply_fixes
        apply_fixes()
        print("✅ Runtime fixes applied successfully!")
    except Exception as e:
        print(f"⚠️ Warning: Could not apply runtime fixes: {e}")
        print("🎯 Continuing anyway...")
    
    # Check terminal compatibility before creating GUI
    check_terminal_compatibility()
    
    root = tk.Tk()
    root.title("Poker Trainer — New UI Preview")
    
    # Configure window size and position (70% of screen, centered)
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Calculate 70% size
    window_width = int(screen_width * 0.7)
    window_height = int(screen_height * 0.7)
    
    # Calculate center position
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    
    # Set window geometry (width x height + x_offset + y_offset)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # Set minimum size (50% of calculated size)
    root.minsize(int(window_width * 0.5), int(window_height * 0.5))
    
    AppShell(root)
    root.mainloop()


if __name__ == "__main__":
    main()


```

---

## 📋 **IMPLEMENTATION SUMMARY**

### ✅ **Key Components Included**

1. **Complete Requirements**: Industry-strength functional and technical specifications
2. **MVU Architecture**: Infinite-loop-proof implementation with immutable state
3. **Visual System**: Professional poker table rendering with animations
4. **Audio Integration**: Human voice and mechanical sound effects
5. **Theme Support**: Full integration with 16 professional themes
6. **Session Reusability**: Compatible with Practice, GTO, and Review managers
7. **Testing Framework**: Comprehensive test suite for reliability

### 🎯 **Development Priorities**

1. **MVU Compliance**: Follow all infinite loop prevention patterns
2. **Visual Excellence**: 60 FPS animations with professional polish
3. **Audio-Visual Sync**: Perfect timing between sounds and actions
4. **Performance**: Sub-100ms response times for all interactions
5. **Accessibility**: WCAG 2.1 AA compliance for inclusive design

### 🚀 **Next Steps**

1. **Phase 1**: Implement core MVU infrastructure with state protection
2. **Phase 2**: Add professional visual rendering and animations
3. **Phase 3**: Integrate audio system with perfect synchronization
4. **Phase 4**: Add advanced features (auto-play, analysis overlays)
5. **Phase 5**: Comprehensive testing and performance optimization

## 📋 **END OF HANDS REVIEW MEGA DOCUMENT**

*This comprehensive document provides everything needed to implement industry-strength hands review functionality with the MVU architecture pattern.*
