#!/usr/bin/env python3
"""
Create a comprehensive requirements package for the Hands Review Tab.
Includes analysis, all related code, test files, and sample data.
"""

import os
import zipfile
import json
import shutil
from datetime import datetime

def create_hands_review_requirements_package():
    """Create comprehensive Hands Review tab requirements package."""
    
    # Create package directory
    package_name = f"hands_review_tab_requirements_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    package_dir = f"/tmp/{package_name}"
    
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    os.makedirs(package_dir)
    
    print(f"📦 Creating Hands Review Tab Requirements Package: {package_name}")
    
    # 1. Copy main analysis document
    print("📄 Adding analysis document...")
    shutil.copy("HANDS_REVIEW_TAB_ANALYSIS.md", f"{package_dir}/")
    
    # 2. Copy all related core code files
    print("🔧 Adding core code files...")
    core_dir = f"{package_dir}/core_modules"
    os.makedirs(core_dir)
    
    core_files = [
        # Main UI Panel
        "backend/ui/components/hands_review_panel_unified.py",
        
        # Session Management  
        "backend/core/bot_session_state_machine.py",
        "backend/core/hand_model_decision_engine.py",
        
        # UI Widgets
        "backend/ui/components/bot_session_widget.py",
        "backend/ui/components/reusable_poker_game_widget.py",
        
        # Data Processing
        "backend/core/gto_to_hand_converter.py",
        "backend/core/hand_model.py",
        
        # Supporting Systems
        "backend/core/flexible_poker_state_machine.py",
        "backend/core/decision_engine_v2.py",
        "backend/core/poker_types.py",
        "backend/core/session_logger.py",
        "backend/core/gui_models.py",
        
        # Main Application Integration
        "backend/main_gui.py"
    ]
    
    for file_path in core_files:
        if os.path.exists(file_path):
            # Create subdirectory structure
            rel_dir = os.path.dirname(file_path).replace("backend/", "")
            target_dir = f"{core_dir}/{rel_dir}"
            os.makedirs(target_dir, exist_ok=True)
            shutil.copy(file_path, f"{target_dir}/")
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ Missing: {file_path}")
    
    # 3. Copy test files
    print("🧪 Adding test files...")
    test_dir = f"{package_dir}/tests"
    os.makedirs(test_dir)
    
    test_files = [
        "test_hands_review_full_simulation.py",
        "test_exact_gui_flow.py",
        "test_gui_data_compatibility.py", 
        "test_hand_model_quick.py",
        "test_gui_hands_review_final.py",
        "test_manual_hands_review.py",
        "test_debug_hand_loading.py",
        "test_complete_functionality.py"
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            shutil.copy(file_path, f"{test_dir}/")
            print(f"  ✅ {file_path}")
    
    # 4. Copy sample data files
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
    
    # GUI data (if exists)
    gui_data_path = "/Users/yeogirlyun/Python/Poker/data/clean_gto_hands_generated.json"
    if os.path.exists(gui_data_path):
        shutil.copy(gui_data_path, f"{data_dir}/gui_hands_database.json")
        print(f"  ✅ GUI hands database")
    
    # 5. Create detailed requirements document
    print("📝 Creating detailed requirements...")
    requirements = {
        "project_name": "Poker Training System - Hands Review Tab",
        "created_at": datetime.now().isoformat(),
        "version": "1.0",
        "description": "Complete requirements package for fixing the Hands Review tab functionality",
        
        "current_status": {
            "practice_session_tab": "✅ Functional - Human vs AI gameplay working",
            "gto_simulation_tab": "✅ Functional - Bot vs bot simulation working", 
            "hands_review_tab": "❌ Non-functional - Next button doesn't work"
        },
        
        "hands_review_requirements": {
            "core_functionality": [
                "Hand selection from database/file list",
                "Load selected hand with complete game state",
                "Step-by-step action replay via Next button",
                "Display all hole cards (review mode)",
                "Show action explanations and reasoning",
                "Add/view comments for learning",
                "Reset to beginning of hand",
                "Session lifecycle management"
            ],
            
            "technical_requirements": [
                "Proper widget integration (Tkinter)",
                "Session state management", 
                "Action sequence loading and replay",
                "Data format conversion and validation",
                "Display synchronization after actions",
                "Error handling for corrupt data",
                "Performance optimization (no conversion loops)"
            ],
            
            "user_experience": [
                "Intuitive hand selection interface",
                "Responsive Next button behavior",
                "Clear visual feedback for actions",
                "Educational value with explanations",
                "Consistent behavior across all hands"
            ]
        },
        
        "critical_issues": {
            "issue_1": {
                "title": "Next Button Immediate Completion",
                "description": "Session reports complete immediately instead of executing actions",
                "impact": "Core functionality completely broken",
                "priority": "CRITICAL"
            },
            
            "issue_2": {
                "title": "Widget Integration Problems", 
                "description": "Missing methods causing AttributeError in UI",
                "impact": "UI crashes on hand loading",
                "priority": "HIGH"
            },
            
            "issue_3": {
                "title": "Data Conversion Loops",
                "description": "150+ repeated conversions causing performance issues",
                "impact": "Slow loading and potential state corruption", 
                "priority": "MEDIUM"
            },
            
            "issue_4": {
                "title": "Import Path Inconsistencies",
                "description": "Mixed relative/absolute imports causing module errors",
                "impact": "Application startup failures",
                "priority": "MEDIUM"
            }
        },
        
        "module_responsibilities": {
            "UnifiedHandsReviewPanel": "Main UI coordination and hand loading",
            "HandsReviewBotSession": "Session management and action execution", 
            "HandModelDecisionEngine": "Action sequence and completion detection",
            "HandsReviewSessionWidget": "UI controls and display integration",
            "GTOToHandConverter": "Data format conversion and validation",
            "ReusablePokerGameWidget": "Poker table display and rendering"
        },
        
        "success_criteria": [
            "User can select any hand from the list",
            "Load Selected Hand button properly initializes session",
            "Next button advances through actions one by one",
            "All hole cards visible during review",
            "Actions execute with proper explanations",
            "Hand completes when all actions finished",
            "Reset button returns to hand beginning",
            "No performance issues or crashes"
        ],
        
        "testing_approach": [
            "Unit tests for each core module",
            "Integration tests for UI and session coordination",
            "End-to-end tests simulating user interactions", 
            "Performance tests for data loading",
            "Error handling tests with corrupt data"
        ]
    }
    
    with open(f"{package_dir}/DETAILED_REQUIREMENTS.json", 'w') as f:
        json.dump(requirements, f, indent=2)
    
    # 6. Create implementation roadmap
    print("🗺️ Creating implementation roadmap...")
    roadmap = """# Hands Review Tab - Implementation Roadmap

## Phase 1: Critical Bug Fixes (Days 1-2)

### Priority 1: Fix Next Button Core Logic
- [ ] Debug HandsReviewBotSession.execute_next_bot_action()
- [ ] Fix session completion detection in HandModelDecisionEngine
- [ ] Ensure proper action sequence loading
- [ ] Validate first-to-act player identification

### Priority 2: Widget Integration
- [ ] Complete HandsReviewSessionWidget implementation  
- [ ] Add missing UI methods (_update_display, update_font_size)
- [ ] Ensure proper Tkinter widget inheritance
- [ ] Fix AttributeError issues

### Priority 3: Import Path Cleanup
- [ ] Standardize all imports to relative format
- [ ] Remove circular import dependencies
- [ ] Update module resolution paths

## Phase 2: Data and Performance (Days 3-4)

### Priority 1: Data Conversion Issues
- [ ] Implement conversion caching to prevent loops
- [ ] Fix GTOToHandConverter repeated processing
- [ ] Validate hand data integrity
- [ ] Add error handling for corrupt data

### Priority 2: Session State Management
- [ ] Ensure proper session lifecycle
- [ ] Fix action player index tracking
- [ ] Validate game state transitions
- [ ] Add session debugging logs

## Phase 3: UI and UX Polish (Days 5-6)

### Priority 1: Display Synchronization
- [ ] Ensure UI updates after each action
- [ ] Fix hole card visibility issues
- [ ] Update pot and chip displays correctly
- [ ] Add visual feedback for button clicks

### Priority 2: Error Handling
- [ ] Graceful failure for missing data
- [ ] User-friendly error messages
- [ ] Recovery mechanisms for session failures
- [ ] Logging improvements for debugging

## Phase 4: Testing and Validation (Days 7-8)

### Priority 1: Comprehensive Testing
- [ ] End-to-end functionality tests
- [ ] Performance benchmarking
- [ ] User experience validation
- [ ] Cross-platform compatibility

### Priority 2: Documentation
- [ ] Update user documentation
- [ ] Create developer guides
- [ ] Add inline code comments
- [ ] Document known limitations

## Success Metrics

- [ ] Next button works for 100% of test hands
- [ ] No crashes during normal operation
- [ ] Hand loading time < 2 seconds
- [ ] Action execution time < 500ms
- [ ] Memory usage stable during long sessions
- [ ] All UI elements respond correctly
- [ ] Error recovery works for corrupt data
- [ ] User can complete full hand review workflow

## Risk Mitigation

### High Risk Items
- Session state corruption
- UI freezing during hand loading
- Data format compatibility issues

### Mitigation Strategies
- Comprehensive unit testing
- Graceful error handling
- User feedback mechanisms
- Rollback capabilities

## Dependencies

### Internal Dependencies
- Core poker state machine stability
- Hand model data structure
- Session logging system
- UI widget framework

### External Dependencies
- Tkinter GUI framework
- JSON data processing
- File system access
- Python module system

## Definition of Done

The Hands Review tab is considered complete when:

1. A user can open the tab and see available hands
2. Selecting and loading a hand works reliably
3. The Next button advances through all actions
4. All poker elements display correctly
5. The hand completes properly at the end
6. Reset functionality returns to hand start
7. No crashes or errors during normal use
8. Performance is acceptable for typical usage
"""
    
    with open(f"{package_dir}/IMPLEMENTATION_ROADMAP.md", 'w') as f:
        f.write(roadmap)
    
    # 7. Create README for the package
    print("📖 Creating package README...")
    readme = f"""# Hands Review Tab Requirements Package

## Overview
This package contains comprehensive requirements, analysis, and code for fixing the Hands Review tab in the Poker Training System.

## Package Contents

### Analysis Documents
- `HANDS_REVIEW_TAB_ANALYSIS.md` - Complete technical analysis and requirements
- `DETAILED_REQUIREMENTS.json` - Structured requirements and specifications  
- `IMPLEMENTATION_ROADMAP.md` - Step-by-step implementation plan

### Core Code Files (`core_modules/`)
- **UI Components**: Main panel, widgets, and display logic
- **Session Management**: Bot sessions and state machines
- **Data Processing**: Hand models, converters, and decision engines
- **Supporting Systems**: Poker logic, types, and utilities

### Test Files (`tests/`)
- Unit tests for individual components
- Integration tests for full functionality
- Debug and diagnostic tests
- Manual testing scripts

### Sample Data (`sample_data/`)
- Working test hands in JSON format
- GUI database examples
- Known good and problematic data samples

## Current Problem Summary

The Hands Review tab is non-functional due to:

1. **Next Button Issue**: Immediate session completion instead of action execution
2. **Widget Integration**: Missing UI methods causing crashes
3. **Data Processing**: Excessive conversion loops causing performance issues
4. **Import Problems**: Module path inconsistencies

## Quick Start

1. Review `HANDS_REVIEW_TAB_ANALYSIS.md` for complete understanding
2. Check `DETAILED_REQUIREMENTS.json` for structured specifications
3. Follow `IMPLEMENTATION_ROADMAP.md` for step-by-step fixes
4. Use test files to validate fixes during development

## Key Modules to Focus On

1. `UnifiedHandsReviewPanel` - Main UI coordination
2. `HandsReviewBotSession` - Session and action management
3. `HandModelDecisionEngine` - Action sequence processing
4. `HandsReviewSessionWidget` - UI controls integration

## Success Criteria

✅ User can select and load hands  
✅ Next button advances through actions  
✅ All cards and game state display correctly  
✅ Hand completes properly at end  
✅ No crashes or performance issues  

## Support

This package provides everything needed to understand and fix the Hands Review tab functionality. All related code, tests, and documentation are included for comprehensive analysis and implementation.

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Package: {package_name}
"""
    
    with open(f"{package_dir}/README.md", 'w') as f:
        f.write(readme)
    
    # 8. Add current logs for debugging
    print("📋 Adding current logs...")
    logs_dir = f"{package_dir}/current_logs"
    os.makedirs(logs_dir)
    
    # Recent test logs
    log_files = [
        "gui_test.log",
        "gui_final_test.log",
        "gui_method_fix_test.log",
        "gui_widget_fix_test.log"
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            shutil.copy(log_file, f"{logs_dir}/")
            print(f"  ✅ {log_file}")
    
    # Backend logs if available
    backend_logs_dir = "backend/logs"
    if os.path.exists(backend_logs_dir):
        recent_logs = sorted([f for f in os.listdir(backend_logs_dir) if f.endswith('.log')])[-5:]
        for log_file in recent_logs:
            shutil.copy(f"{backend_logs_dir}/{log_file}", f"{logs_dir}/backend_{log_file}")
            print(f"  ✅ backend/{log_file}")
    
    # 9. Create the zip file
    zip_path = f"{package_name}.zip"
    print(f"🗜️ Creating zip file: {zip_path}")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, package_dir)
                zipf.write(file_path, arc_path)
                
    # 10. Cleanup temp directory
    shutil.rmtree(package_dir)
    
    print(f"✅ Requirements package created: {zip_path}")
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
    zip_path = create_hands_review_requirements_package()
    print(f"\n🎉 Hands Review Tab Requirements Package ready: {zip_path}")
    print(f"\nThis package contains everything needed to understand and fix the Hands Review tab:")
    print(f"  • Complete analysis and requirements documentation")
    print(f"  • All related Python code files") 
    print(f"  • Comprehensive test suite")
    print(f"  • Sample data and current logs")
    print(f"  • Step-by-step implementation roadmap")
