# PokerPro Trainer Documentation

This directory contains the authoritative documentation for the PokerPro Trainer project.

## 📚 Core Documents

### **Architecture & Design**
- **`PokerPro_Trainer_Complete_Architecture_v3.md`** - Comprehensive system architecture reference (Latest)
- **`PROJECT_PRINCIPLES_v2.md`** - Core architectural principles and coding standards (Latest)
- **`PokerPro_MVU_Architecture_Guide_v2.md`** - **🚨 CRITICAL: MVU Pattern & Infinite Loop Prevention** (Latest)
- **`PokerPro_UI_Implementation_Handbook.md`** - Step-by-step implementation guide for UI sessions
- **`ARCHITECTURE_VIOLATION_PREVENTION_GUIDE.md`** - Common violations and prevention patterns

### **Theme System**
- **`Complete_Theme_Color_Reference_Table_v2.md`** - Complete theme system with 11 professional themes (Latest)

## 🔄 Version History

### **Architecture Documents**
- **v3** (Current): Enhanced with UI architecture, session implementation, and Enhanced RPGW details
- **v2** (Deprecated): Basic architecture overview
- **v1** (Removed): Initial architecture concepts

### **Project Principles**
- **v2** (Current): Enhanced with AI agent compliance rules and PR acceptance checklist
- **v1** (Removed): Basic principles

### **Theme Reference**
- **v2** (Current): Complete 11-theme system with token normalization and accessibility guidelines
- **v1** (Removed): Basic theme colors

## 🧹 Recent Cleanup

The following outdated documents have been removed to prevent confusion:
- `PokerPro_Trainer_Architecture.md` - Superseded by v3
- `PokerPro_Trainer_Design.md` - Design details now in v3
- `PokerPro_Trainer_Product.md` - Product requirements now in v3
- `Theme_Integration_Complete_Reference.md` - Redundant with theme v2

## 📋 Usage Guidelines

1. **For Architecture**: Always refer to `PokerPro_Trainer_Complete_Architecture_v3.md`
2. **🚨 For MVU Implementation**: **MUST READ** `PokerPro_MVU_Architecture_Guide_v2.md` first
3. **For Implementation**: Follow `PokerPro_UI_Implementation_Handbook.md`
4. **For Coding Standards**: Adhere to `PROJECT_PRINCIPLES_v2.md`
5. **For Theming**: Use `Complete_Theme_Color_Reference_Table_v2.md`

### **⚠️ Critical MVU Guidelines**
- Before implementing any MVU components, **MUST READ** the MVU Architecture Guide
- All MVU models **MUST** use immutable collections (`tuple`, `frozenset`, `Mapping`)
- All MVU dataclasses **MUST** implement custom `__eq__` methods
- **NEVER** load data during UI initialization - always defer until components are ready
- **ALWAYS** test for infinite loops in MVU implementations

## 🚀 Next Steps

The current documentation structure provides a solid foundation for:
- Implementing the Enhanced RPGW across all sessions
- Following the state-driven architecture patterns
- Maintaining consistent theming and accessibility
- Ensuring code quality and architectural compliance

---

*Last Updated: January 2025*  
*Status: Production Ready (MVU Infinite Loop Prevention Added)*
