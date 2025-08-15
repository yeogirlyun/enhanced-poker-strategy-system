# 🚨 DUPLICATE PREVENTION - AI QUICK REFERENCE

## ✅ MANDATORY CHECK BEFORE WRITING CODE

```bash
cd backend
python3 py_duplicate_def_auditor.py --root . --ignore "*/__pycache__/*,*/logs/*"
```

**MUST RETURN:**
```
✅ No REAL duplicates found! All 'duplicates' are legitimate Python patterns.
🎉 Your codebase is clean and well-structured.
```

## 🚫 NO DUPLICATES ALLOWED

- **Same method name twice in same class** = ❌
- **Same function name twice at module level** = ❌  
- **Same class name twice in same file** = ❌
- **Duplicate logic/code blocks** = ❌

## ✅ LEGITIMATE PATTERNS

- **Method overrides in inheritance** = ✅
- **Nested classes** = ✅
- **Local functions** = ✅
- **Multiple classes in same file** = ✅

## 🔧 IF DUPLICATES FOUND

1. **STOP** - Do not write new code
2. **FIX** - Resolve all duplicates first
3. **RE-AUDIT** - Ensure 0 duplicates
4. **THEN** - Proceed with new code

## 📖 FULL RULES

See [DUPLICATE_PREVENTION_RULES.md](DUPLICATE_PREVENTION_RULES.md) for complete guidelines.

---

**VIOLATION = CODE REJECTION + TRAINING REQUIRED**
