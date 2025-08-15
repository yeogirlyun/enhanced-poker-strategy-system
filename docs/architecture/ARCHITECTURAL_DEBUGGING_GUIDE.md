# Architectural Debugging Guide
## Ensuring Fixes Go to the Right Inheritance Level

### 🎯 **PRINCIPLE: Fix at the Correct Abstraction Level**

When debugging, we must identify whether an issue belongs to:
1. **FPSM (Core Logic)** - Game rules, state transitions, action validation
2. **FPSM Children** - Specialized game behaviors (Practice, HandsReview, Test)
3. **RPGW (Base UI)** - Common UI patterns, hook system, basic rendering
4. **RPGW Children** - Specialized UI behaviors (Practice actions, HandsReview visibility)

---

## 🔍 **DEBUGGING DECISION TREE**

### **Step 1: Identify the Problem Domain**
- **Game Logic Issue?** → Check FPSM hierarchy
- **UI Display Issue?** → Check RPGW hierarchy
- **Integration Issue?** → Check communication between hierarchies

### **Step 2: Determine Scope**
- **Affects ALL widgets/sessions?** → Fix belongs in BASE class (FPSM/RPGW)
- **Affects ONE widget type?** → Fix belongs in CHILD class
- **Affects widget interaction?** → Fix belongs in hook methods

---

## 🧩 **INHERITANCE LEVEL GUIDELINES**

### **FPSM (FlexiblePokerStateMachine) - BASE**
**Fix HERE if issue affects ALL game types:**
- ✅ Core poker rules (betting, folding, hand evaluation)
- ✅ State transition logic (preflop → flop → turn → river)
- ✅ Action validation (legal bet amounts, turn order)
- ✅ Game state management (pot, stacks, cards)
- ✅ Event emission system

**Example Issues:**
- "Pot calculation is wrong in all game modes"
- "State transitions skip streets"
- "Action validation allows illegal moves"

### **FPSM Children - SPECIALIZED BEHAVIOR**
**Fix HERE if issue affects ONLY specific game type:**

#### **PracticeSessionPokerStateMachine**
- ✅ Bot auto-play logic
- ✅ Human player designation
- ✅ GTO strategy integration
- ✅ Performance tracking
- ✅ Educational feedback generation

#### **HandsReviewPokerStateMachine**
- ✅ Hand replay logic
- ✅ Step-by-step progression
- ✅ Analysis data generation
- ✅ Historical action tracking

#### **TestablePokerStateMachine**
- ✅ Test data generation
- ✅ Controlled scenarios
- ✅ Auto-advancement for testing

**Example Issues:**
- "Bots get stuck in practice mode" → PracticeSessionPSM
- "Hand replay doesn't show all actions" → HandsReviewPSM
- "Test data is inconsistent" → TestablePSM

### **RPGW (ReusablePokerGameWidget) - BASE**
**Fix HERE if issue affects ALL widget types:**
- ✅ Hook system implementation
- ✅ Basic card rendering
- ✅ Common UI patterns (player seats, pot display)
- ✅ Event handling framework
- ✅ Animation system
- ✅ Sound system integration

**Example Issues:**
- "Hook methods not being called"
- "Card widgets not rendering properly"
- "Animation system broken for all widgets"

### **RPGW Children - SPECIALIZED UI**

#### **PracticeSessionPokerWidget**
- ✅ Action button implementation
- ✅ Human player highlighting
- ✅ Educational UI elements
- ✅ Performance display
- ✅ Interactive features

#### **HandsReviewPokerWidget**
- ✅ Card visibility policy (show all cards)
- ✅ Folded player styling
- ✅ Review-specific annotations
- ✅ Study mode features

**Example Issues:**
- "Action buttons not working" → PracticeSessionPW
- "Cards not visible in hands review" → HandsReviewPW
- "Human player not highlighted properly" → PracticeSessionPW

---

## 🛠 **DEBUGGING WORKFLOW**

### **1. Reproduce the Issue**
```bash
# Test in isolation
python3 -c "from ui.components.practice_session_poker_widget import PracticeSessionPokerWidget; print('Import OK')"
```

### **2. Add Debugging Prints**
Add layer-specific debug prints to identify where the issue occurs:

```python
# In FPSM (base)
print(f"🔧 FPSM BASE: {method_name} called with {params}")

# In PracticeSessionPSM (child)  
print(f"🎓 PRACTICE PSM: {method_name} called with {params}")

# In RPGW (base)
print(f"🎨 RPGW BASE: {method_name} called with {params}")

# In PracticeSessionPW (child)
print(f"🎮 PRACTICE PW: {method_name} called with {params}")
```

### **3. Trace the Call Stack**
Identify which level the issue originates from:
- Base class not providing expected behavior?
- Child class not overriding correctly?
- Hook not being called?
- Integration problem between hierarchies?

### **4. Apply Fix at Correct Level**

#### **Base Class Fix** (affects all children):
```python
# Fix in FPSM or RPGW base class
def core_method(self):
    # Fix core logic that all children depend on
    pass
```

#### **Child Class Fix** (affects only specific widget):
```python
# Fix in child class
def _hook_method(self):
    # Override hook to provide specialized behavior
    pass
```

#### **Integration Fix** (communication between layers):
```python
# Fix in the connection points
def on_event(self, event):
    # Fix how FPSM events reach RPGW
    pass
```

---

## ⚠️ **ANTI-PATTERNS TO AVOID**

### **❌ DON'T: Fix child-specific issues in base class**
```python
# BAD: Adding practice-specific logic to FPSM base
def execute_action(self, player, action, amount):
    if self.is_practice_mode:  # ❌ Wrong level!
        # practice-specific logic
    # core logic
```

### **❌ DON'T: Duplicate base functionality in child**
```python
# BAD: Reimplementing core logic in child
def _set_player_cards_from_display_state(self, player_index, cards):
    # ❌ Duplicating parent's card rendering logic
    # instead of using hooks properly
```

### **❌ DON'T: Put UI logic in state machine**
```python
# BAD: UI concerns in game logic
def transition_to(self, new_state):
    # game logic
    self.widget.update_button_colors()  # ❌ Wrong layer!
```

### **✅ DO: Use proper separation of concerns**
```python
# GOOD: Base provides hooks, children customize
def _should_show_card(self, player_index, card):
    return card != "**"  # Base behavior

# GOOD: Child overrides for specialization  
def _should_show_card(self, player_index, card):
    return True  # HandsReview: show all cards
```

---

## 🎯 **TESTING STRATEGY**

### **Test Each Level Independently**
1. **FPSM Base**: Unit tests for core game logic
2. **FPSM Children**: Integration tests for specialized behaviors
3. **RPGW Base**: UI component tests for common functionality
4. **RPGW Children**: Widget tests for specialized UI features

### **Test Integration Points**
- FPSM → RPGW event communication
- Hook method calling and overrides
- State machine → widget synchronization

### **Regression Testing**
- Ensure base class changes don't break children
- Ensure child changes don't rely on base class internals
- Ensure hook system maintains contracts

---

## 📋 **DEBUGGING CHECKLIST**

Before making any fix, ask:

1. **🎯 Scope**: Does this issue affect all widgets or just one?
2. **🏗️ Layer**: Is this game logic, UI logic, or integration?
3. **🔗 Dependencies**: Will this change affect other components?
4. **🧪 Testing**: Can I test this fix in isolation?
5. **📚 Documentation**: Does this change the public contract?

**Remember: The goal is clean separation of concerns with each class having a single, well-defined responsibility.**
