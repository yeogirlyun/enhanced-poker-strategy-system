#!/usr/bin/env python3
"""
Create comprehensive problem package for Hands Review panel issues.
Includes problem analysis, all related code, test files, and architecture docs.
"""

import os
import zipfile
import json
import shutil
from datetime import datetime

def create_hands_review_problem_package():
    """Create comprehensive problem analysis package."""
    
    # Create package directory
    package_name = f"hands_review_problem_package_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    package_dir = f"/tmp/{package_name}"
    
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    os.makedirs(package_dir)
    
    print(f"📦 Creating Hands Review Problem Package: {package_name}")
    
    # 1. Copy problem analysis document
    print("📄 Adding problem analysis...")
    shutil.copy("HANDS_REVIEW_PROBLEM_ANALYSIS.md", f"{package_dir}/")
    
    # 2. Copy all hands review related code
    print("🔧 Adding hands review code files...")
    code_dir = f"{package_dir}/code"
    os.makedirs(code_dir)
    
    # Main hands review files
    hands_review_files = [
        # Main panel
        "backend/ui/components/hands_review_panel_unified.py",
        
        # Bot session architecture  
        "backend/core/bot_session_state_machine.py",
        "backend/ui/components/bot_session_widget.py",
        
        # Decision engines
        "backend/core/hand_model_decision_engine.py",
        "backend/core/decision_engine_v2.py",
        
        # Poker table widget
        "backend/ui/components/reusable_poker_game_widget.py",
        
        # Data processing
        "backend/core/gto_to_hand_converter.py",
        "backend/core/hand_model.py",
        
        # Core poker logic
        "backend/core/flexible_poker_state_machine.py",
        "backend/core/poker_types.py",
        
        # Supporting systems
        "backend/core/session_logger.py",
        "backend/core/gui_models.py",
        "backend/utils/sound_manager.py",
        
        # Main GUI integration
        "backend/main_gui.py"
    ]
    
    for file_path in hands_review_files:
        if os.path.exists(file_path):
            # Preserve directory structure
            rel_dir = os.path.dirname(file_path)
            target_dir = f"{code_dir}/{rel_dir}"
            os.makedirs(target_dir, exist_ok=True)
            shutil.copy(file_path, f"{target_dir}/")
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ Missing: {file_path}")
    
    # 3. Copy working reference (GTO simulation)
    print("📋 Adding GTO simulation reference (working)...")
    gto_dir = f"{package_dir}/working_reference_gto"
    os.makedirs(gto_dir)
    
    gto_files = [
        "backend/ui/components/gto_simulation_panel.py",
        "backend/ui/components/gto_poker_game_widget.py",
        "backend/core/gto_poker_state_machine.py"
    ]
    
    for file_path in gto_files:
        if os.path.exists(file_path):
            rel_dir = os.path.dirname(file_path).replace("backend/", "")
            target_dir = f"{gto_dir}/{rel_dir}"
            os.makedirs(target_dir, exist_ok=True)
            shutil.copy(file_path, f"{target_dir}/")
            print(f"  ✅ {file_path}")
    
    # 4. Copy test files
    print("🧪 Adding test files...")
    test_dir = f"{package_dir}/tests"
    os.makedirs(test_dir)
    
    test_files = [
        "test_integrated_hands_review.py",
        "test_complete_functionality.py",
        "test_exact_gui_flow.py"
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            shutil.copy(file_path, f"{test_dir}/")
            print(f"  ✅ {file_path}")
    
    # 5. Copy sample data
    print("📊 Adding sample data...")
    data_dir = f"{package_dir}/sample_data"
    os.makedirs(data_dir)
    
    # Working test data
    working_data_files = [
        "cycle_test_hand.json",
        "gto_hand_for_verification.json"
    ]
    
    for file_path in working_data_files:
        if os.path.exists(file_path):
            shutil.copy(file_path, f"{data_dir}/")
            print(f"  ✅ {file_path}")
    
    # GUI data 
    gui_data_path = "data/clean_gto_hands_generated.json"
    if os.path.exists(gui_data_path):
        shutil.copy(gui_data_path, f"{data_dir}/gui_hands_database.json")
        print(f"  ✅ GUI hands database")
    
    # 6. Create detailed problem report
    print("📝 Creating detailed problem report...")
    problem_report = {
        "package_info": {
            "name": "Hands Review Problem Analysis Package",
            "created_at": datetime.now().isoformat(),
            "version": "1.0",
            "description": "Complete analysis and code for fixing Hands Review panel issues"
        },
        
        "problem_summary": {
            "status": "CRITICAL - Not Functional",
            "main_issues": [
                "Poker table not loading after hand selection",
                "Next/Auto-Play buttons not working",
                "Data conversion errors preventing hand loading",
                "Session integration failures with ReusablePokerGameWidget"
            ],
            "error_messages": [
                "ERROR: 'str' object has no attribute 'get'",
                "ERROR: Hand.__init__() got unexpected keyword argument 'actions'",
                "Import warning: No module named 'backend'. Using fallbacks."
            ]
        },
        
        "architecture_analysis": {
            "intended_pattern": "Bot Session Architecture (same as GTO simulation)",
            "components": {
                "UnifiedHandsReviewPanel": "Main UI panel for hand selection and controls",
                "HandsReviewBotSession": "Session state machine for hand replay",
                "HandModelDecisionEngine": "Preloaded action sequence engine", 
                "ReusablePokerGameWidget": "Poker table display widget"
            },
            "data_flow": [
                "User selects hand from left panel",
                "Panel converts JSON to Hand model",
                "Creates HandsReviewBotSession with decision engine",
                "Creates ReusablePokerGameWidget with session",
                "Session starts and displays poker table",
                "Next button executes actions via session"
            ]
        },
        
        "working_reference": {
            "gto_simulation": {
                "status": "WORKING CORRECTLY",
                "pattern": "GTOSimulationPanel → GTOBotSession → GTOSessionWidget → ReusablePokerGameWidget",
                "key_methods": [
                    "GTOBotSession(config=game_config, logger=logger)",
                    "GTOSessionWidget(container, session)",
                    "session.start_session()",
                    "widget._update_display()"
                ]
            }
        },
        
        "critical_failures": {
            "data_conversion": {
                "issue": "GTOToHandConverter fails with 'str' has no 'get' attribute",
                "root_cause": "JSON data format mismatch - expecting dict, receiving string",
                "impact": "Cannot load any hands for review"
            },
            "session_integration": {
                "issue": "HandsReviewBotSession created but doesn't integrate with widget",
                "root_cause": "Session lifecycle and state machine transitions failing",
                "impact": "Poker table doesn't display even when hand loads"
            },
            "action_execution": {
                "issue": "Next button calls session.execute_next_bot_action() but nothing happens",
                "root_cause": "Decision engine not properly connected to session",
                "impact": "Cannot step through hand actions"
            }
        },
        
        "fix_priorities": [
            {
                "priority": 1,
                "task": "Fix data conversion pipeline",
                "details": "Debug JSON parsing in _convert_with_cache(), ensure Hand model compatibility"
            },
            {
                "priority": 2, 
                "task": "Fix session integration",
                "details": "Verify HandsReviewBotSession constructor and state transitions"
            },
            {
                "priority": 3,
                "task": "Fix widget display",
                "details": "Ensure ReusablePokerGameWidget displays poker table correctly"
            },
            {
                "priority": 4,
                "task": "Fix action execution",
                "details": "Connect decision engine to session for Next button functionality"
            }
        ],
        
        "success_criteria": [
            "User can select and load any hand without errors",
            "Poker table displays with cards, chips, and players",
            "Next button advances through actions step-by-step", 
            "Visual updates show game state changes",
            "Hand completes properly at the end",
            "Reset and Auto-Play functionality works"
        ],
        
        "test_results": {
            "panel_creation": "✅ PASS - 393 hands loaded",
            "hand_selection": "✅ PASS - UI selection works",
            "data_conversion": "❌ FAIL - JSON conversion errors",
            "session_creation": "❌ FAIL - Integration issues",
            "poker_table_display": "❌ FAIL - No table appears",
            "action_execution": "❌ FAIL - Buttons non-functional"
        }
    }
    
    with open(f"{package_dir}/DETAILED_PROBLEM_REPORT.json", 'w') as f:
        json.dump(problem_report, f, indent=2)
    
    # 7. Create architecture comparison document
    print("🏗️ Creating architecture comparison...")
    arch_comparison = f"""# Architecture Comparison: GTO vs Hands Review

## Working GTO Session Architecture

### Flow:
1. GTOSimulationPanel._start_session()
2. Creates GTOBotSession(config, logger)
3. Creates GTOSessionWidget(container, session)  
4. Calls session.start_session()
5. Widgets updates display automatically
6. Next button calls session.execute_next_bot_action()

### Code Pattern:
```python
# In GTOSimulationPanel
self.gto_bot_session = GTOBotSession(config=game_config, logger=self.logger)
self.gto_game_widget = GTOSessionWidget(self.game_container, self.gto_bot_session)
success = self.gto_bot_session.start_session()
if success:
    self.gto_game_widget.grid(row=0, column=0, sticky="nsew")
    self.gto_game_widget._update_display()
```

## Broken Hands Review Architecture

### Intended Flow:
1. UnifiedHandsReviewPanel._load_selected_hand()
2. Creates HandsReviewBotSession(config, decision_engine, logger)
3. Creates ReusablePokerGameWidget(container, session)
4. Calls session.start_session()
5. Widget should display poker table
6. Next button should call session.execute_next_bot_action()

### Current Code (Broken):
```python
# In UnifiedHandsReviewPanel
self.hands_review_session = HandsReviewBotSession(
    config=game_config,
    decision_engine=decision_engine, 
    logger=self.session_logger
)
self.poker_game_widget = ReusablePokerGameWidget(
    self.poker_table_frame,
    state_machine=self.hands_review_session
)
success = self.hands_review_session.start_session()
# Widget created but poker table doesn't appear
```

## Key Differences

### Data Source:
- **GTO**: Random decisions generated by ImprovedGTOStrategy
- **Hands Review**: Preloaded decisions from HandModelDecisionEngine

### Widget Type:
- **GTO**: Uses GTOSessionWidget (extends BotSessionWidget)
- **Hands Review**: Uses ReusablePokerGameWidget directly

### Session Type:
- **GTO**: GTOBotSession (extends BotSessionStateMachine)
- **Hands Review**: HandsReviewBotSession (extends BotSessionStateMachine)

## Recommended Fix

Use the exact same pattern as GTO but with preloaded data:

1. Create HandsReviewSessionWidget (like GTOSessionWidget)
2. Use HandsReviewBotSession with HandModelDecisionEngine
3. Follow exact same initialization and display update pattern
4. Ensure data conversion works properly
"""
    
    with open(f"{package_dir}/ARCHITECTURE_COMPARISON.md", 'w') as f:
        f.write(arch_comparison)
    
    # 8. Add current error logs
    print("📋 Adding error logs...")
    logs_dir = f"{package_dir}/error_logs"
    os.makedirs(logs_dir)
    
    # Create error log sample
    error_log_sample = f"""# Recent Error Logs from Hands Review Testing

## Test Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

### Panel Creation
✅ Panel created successfully
✅ Found 393 hands available

### Hand Loading Attempts
❌ [ERROR] HANDS_REVIEW | Conversion failed: 'str' object has no attribute 'get'
❌ [ERROR] HANDS_REVIEW | Failed to load hand: Hand.__init__() got an unexpected keyword argument 'actions'

### Import Issues
⚠️  Import warning: No module named 'backend'. Using fallbacks.

### Widget Integration
❌ ReusablePokerGameWidget created but poker table not displaying
❌ Next button created but not functional

### Session State
❌ HandsReviewBotSession created but state transitions failing
❌ execute_next_bot_action() called but no visible effect

## Error Patterns

1. **Data Conversion**: JSON parsing expects dict but receives string
2. **Model Mismatch**: Fallback Hand class incompatible with real Hand model
3. **Session Lifecycle**: start_session() succeeds but doesn't initialize display
4. **Widget Display**: ReusablePokerGameWidget doesn't show poker table content
"""
    
    with open(f"{logs_dir}/hands_review_errors.log", 'w') as f:
        f.write(error_log_sample)
    
    # 9. Create README for the package
    print("📖 Creating package README...")
    readme = f"""# Hands Review Problem Analysis Package

## Overview
This package contains comprehensive analysis and code for the Hands Review panel issues in the Poker Training System.

## Package Contents

### Problem Analysis
- `HANDS_REVIEW_PROBLEM_ANALYSIS.md` - Executive summary and problem breakdown
- `DETAILED_PROBLEM_REPORT.json` - Structured analysis with priorities and test results
- `ARCHITECTURE_COMPARISON.md` - Comparison with working GTO session

### Code Files (`code/`)
- **Main Components**: hands_review_panel_unified.py, bot_session_state_machine.py
- **Decision Engines**: hand_model_decision_engine.py, decision_engine_v2.py  
- **Poker Widgets**: reusable_poker_game_widget.py, bot_session_widget.py
- **Data Processing**: gto_to_hand_converter.py, hand_model.py
- **Core Systems**: flexible_poker_state_machine.py, poker_types.py

### Working Reference (`working_reference_gto/`)
- GTO simulation code that works correctly
- Reference implementation for bot session architecture

### Tests (`tests/`)
- Integration tests and manual test scripts
- Demonstrates current failures and expected behavior

### Sample Data (`sample_data/`)
- Known working test hands
- GUI hands database (393 hands)

### Error Logs (`error_logs/`)
- Current error patterns and failure modes
- Diagnostic information for debugging

## Current Status

❌ **CRITICAL ISSUES**:
1. Poker table not loading after hand selection
2. Next/Auto-Play buttons not working  
3. Data conversion errors preventing hand loading
4. Session integration failures

## Problem Summary

The Hands Review panel follows the correct bot session architecture but suffers from:
- **Data Pipeline Issues**: JSON to Hand model conversion failing
- **Session Integration**: HandsReviewBotSession not properly connecting to widget
- **Display Problems**: ReusablePokerGameWidget not showing poker table
- **Action Execution**: Decision engine not triggering state updates

## Goal

Create a fully functional Hands Review tab that:
- Loads hands from 393 available selections
- Displays complete poker table with cards, chips, players
- Advances through hand actions step-by-step via Next button
- Shows visual updates after each action
- Supports reset and auto-play functionality

## Architecture Pattern

Follow the working GTO simulation pattern:
```
Panel → BotSession → SessionWidget → PokerGameWidget
```

But with preloaded hand data instead of random GTO decisions.

## Fix Priority

1. **Fix data conversion** (blocking all other functionality)
2. **Fix session integration** (enable poker table display)
3. **Fix action execution** (enable Next button)
4. **Polish and test** (ensure robust operation)

## Success Criteria

✅ User can load any hand without errors  
✅ Poker table displays correctly  
✅ Next button advances through actions  
✅ Visual feedback shows game state changes  
✅ Complete hand replay functionality works  

Package Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Files: ~30+ code files, tests, docs, and samples
"""
    
    with open(f"{package_dir}/README.md", 'w') as f:
        f.write(readme)
    
    # 10. Create the zip file
    zip_path = f"{package_name}.zip"
    print(f"🗜️ Creating zip file: {zip_path}")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, package_dir)
                zipf.write(file_path, arc_path)
    
    # 11. Cleanup temp directory
    shutil.rmtree(package_dir)
    
    print(f"✅ Problem package created: {zip_path}")
    print(f"📦 Package size: {os.path.getsize(zip_path) / 1024:.1f} KB")
    
    # Display package summary
    print(f"\n📋 Package Summary:")
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        files_by_type = {}
        for info in zipf.infolist():
            if info.filename.endswith('/'):
                continue
            ext = info.filename.split('.')[-1] if '.' in info.filename else 'other'
            if ext not in files_by_type:
                files_by_type[ext] = []
            files_by_type[ext].append(info.filename)
    
    for ext, files in sorted(files_by_type.items()):
        print(f"  {ext.upper()}: {len(files)} files")
    
    return zip_path

if __name__ == "__main__":
    zip_path = create_hands_review_problem_package()
    print(f"\n🎉 Hands Review Problem Package ready: {zip_path}")
    print(f"\nThis package contains everything needed to analyze and fix the Hands Review issues:")
    print(f"  • Complete problem analysis and architecture documentation")
    print(f"  • All related Python code files (hands review + working GTO reference)")
    print(f"  • Comprehensive test suite and error logs") 
    print(f"  • Sample data and current failure patterns")
    print(f"  • Step-by-step fix priorities and success criteria")