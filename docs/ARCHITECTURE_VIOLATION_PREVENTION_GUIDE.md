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
