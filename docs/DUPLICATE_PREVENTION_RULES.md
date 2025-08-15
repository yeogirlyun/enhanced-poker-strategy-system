# DUPLICATE PREVENTION RULES — MANDATORY FOR AI MODELS

## 🚨 CRITICAL: ZERO TOLERANCE FOR DUPLICATES

**Every duplicate = debugging nightmare. Prevention mandatory.**

## 📋 PRE-DEVELOPMENT CHECKLIST

### ✅ MANDATORY: Run Duplicate Audit First
```bash
cd backend
python3 py_duplicate_def_auditor.py --root . --ignore "*/__pycache__/*,*/logs/*"
```

**RESULT MUST BE:**
```
✅ No REAL duplicates found! All 'duplicates' are legitimate Python patterns.
🎉 Your codebase is clean and well-structured.
```

**IF DUPLICATES FOUND:**
- ❌ **STOP IMMEDIATELY** - Fix duplicates first
- 🔧 **Re-run audit** - Ensure 0 duplicates before continuing

## 🚫 WHAT CONSTITUTES A DUPLICATE

### ❌ REAL DUPLICATES (MUST BE FIXED)
1. **Same method name defined multiple times in the same class**
2. **Same function name defined multiple times at module level**
3. **Same class name defined multiple times in the same file**
4. **Duplicate logic/code blocks** (violates DRY principle)

### ✅ LEGITIMATE PATTERNS (NOT DUPLICATES)
1. **Method overrides in inheritance** - `ChildClass.method()` overriding `ParentClass.method()`
2. **Nested classes** - `OuterClass.InnerClass` with different purposes
3. **Local functions** - Functions defined inside other functions
4. **Multiple classes in same file** - Each with unique names and purposes
5. **Interface implementations** - Different classes implementing the same interface

## 🎯 NAMING CONVENTIONS

- **Class names**: Must be unique across entire project
- **Method names**: Must be unique within each class
- **Function names**: Must be unique at module level
- **Variable names**: Must be unique within their scope

## 🏗️ ARCHITECTURE PRINCIPLES

1. **Single Responsibility**: Each class/function = one clear purpose
2. **DRY**: Never duplicate logic - extract to shared utilities
3. **Composition over Inheritance**: Reduces method name conflicts
4. **Module Separation**: Related functionality in separate modules

## 🤖 AI MODEL REQUIREMENTS

### Before Writing ANY Code
1. **🔍 Search existing codebase** for similar functionality
2. **📊 Run duplicate audit** to ensure clean state
3. **📝 Check naming conflicts** with existing classes/methods
4. **🧠 Plan architecture** to avoid duplication

### When Proposing Solutions
1. **🔄 Always suggest refactoring** if similar code exists
2. **🔗 Reuse existing components** instead of creating new ones
3. **📋 Check naming conventions** before proposing names
4. **✅ Verify no conflicts** with existing code

### After Code Changes
1. **🔍 Re-run duplicate audit** to ensure no new duplicates
2. **📝 Document any refactoring** done to eliminate duplication
3. **✅ Verify functionality** is preserved after deduplication

## 📚 EXAMPLES

### ❌ BAD: Duplicate Method in Same Class
```python
class PokerGame:
    def deal_cards(self): # First definition
        pass
    def deal_cards(self): # ❌ DUPLICATE - Same method name twice
        pass
```

### ✅ GOOD: Method Override in Inheritance
```python
class BaseGame:
    def deal_cards(self): # Base method
        pass

class PokerGame(BaseGame):
    def deal_cards(self): # ✅ GOOD - Overriding parent method
        super().deal_cards()
```

### ❌ BAD: Duplicate Function at Module Level
```python
def calculate_odds(): # First definition
    pass
def calculate_odds(): # ❌ DUPLICATE - Same function name twice
    pass
```

### ✅ GOOD: Local Function Inside Another Function
```python
def process_hand():
    def calculate_odds(): # ✅ GOOD - Local function, not duplicate
        pass
    def calculate_pot():  # ✅ GOOD - Different function name
        pass
```

## 🔧 TOOLS

### Duplicate Auditor
```bash
# Basic audit
python3 py_duplicate_def_auditor.py --root .

# With custom ignore patterns
python3 py_duplicate_def_auditor.py --root . --ignore "*/tests/*,*/docs/*"

# JSON output for CI/CD
python3 py_duplicate_def_auditor.py --root . --format json
```

### Code Search Tools
```bash
# Search for class names
grep -r "class.*:" --include="*.py" .

# Search for method names
grep -r "def.*:" --include="*.py" .

# Search for specific patterns
grep -r "calculate_odds" --include="*.py" .
```

## 🚨 ENFORCEMENT

- **Immediate rejection** of any code that introduces duplicates
- **Mandatory refactoring** before code review approval
- **Block merges** with duplicate code
- **Integrate duplicate audit** in CI/CD pipeline

---

## 🎯 REMEMBER: ZERO TOLERANCE FOR DUPLICATES

**Every duplicate is a potential debugging nightmare waiting to happen.**
**Prevention is always better than fixing later.**
**When in doubt, refactor and reuse existing code.**

**VIOLATION CONSEQUENCES**: Code with duplicates will be rejected, and developers must complete duplicate prevention training before continuing.
