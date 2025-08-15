#!/usr/bin/env python3
"""
Package all Hand Model project files for review.
"""

import zipfile
import os
from datetime import datetime

def create_hand_model_package():
    """Create a zip file with all Hand Model project files."""
    
    # Create zip filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"hand_model_project_{timestamp}.zip"
    
    # Files to include in the package
    files_to_include = [
        # Main documentation
        "HAND_MODEL_PROJECT_REPORT.md",
        
        # Core implementation files
        "backend/core/hand_model.py",
        "backend/core/gto_to_hand_converter.py", 
        "backend/core/hand_model_decision_engine.py",
        
        # Test files
        "test_hand_model.py",
        "test_hand_model_integration.py",
        
        # Supporting modules that need review
        "backend/core/bot_session_state_machine.py",
        "backend/core/flexible_poker_state_machine.py",
        "backend/core/decision_engine_v2.py",
        "backend/core/poker_types.py",
        
        # UI integration file
        "backend/ui/components/hands_review_panel_unified.py",
        
        # Example data files (if they exist)
        "cycle_test_hand.json",
        "gto_hand_for_verification.json",
        "cycle_test_hand_hand_model.json", 
        "gto_hand_for_verification_hand_model.json",
        "example_hand.json",
        
        # Previous test cycle files
        "test_gto_to_hands_review_complete_cycle.py",
        "hands_review_replay_log.txt",
        "hands_review_replay_report.json",
        "cycle_test_gto_log.txt",
        "cycle_test_replay_log.txt",
    ]
    
    created_files = []
    missing_files = []
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in files_to_include:
            if os.path.exists(file_path):
                zipf.write(file_path)
                created_files.append(file_path)
                print(f"✅ Added: {file_path}")
            else:
                missing_files.append(file_path)
                print(f"⚠️  Missing: {file_path}")
    
    print(f"\n📦 Created package: {zip_filename}")
    print(f"   📁 Files included: {len(created_files)}")
    print(f"   ⚠️  Files missing: {len(missing_files)}")
    
    if missing_files:
        print(f"\n⚠️  Missing files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
    
    # Create a manifest file
    manifest_content = f"""# Hand Model Project Package Manifest
Generated: {datetime.now().isoformat()}
Package: {zip_filename}

## Included Files ({len(created_files)})
"""
    
    for file_path in sorted(created_files):
        manifest_content += f"- {file_path}\n"
    
    if missing_files:
        manifest_content += f"\n## Missing Files ({len(missing_files)})\n"
        for file_path in sorted(missing_files):
            manifest_content += f"- {file_path}\n"
    
    manifest_content += f"""
## Package Contents

### Core Implementation
- hand_model.py: Complete poker hand data structure
- gto_to_hand_converter.py: Converts GTO format to Hand model  
- hand_model_decision_engine.py: Robust action replay engine

### Test Suite
- test_hand_model.py: Comprehensive fuzz testing (24 test scenarios)
- test_hand_model_integration.py: End-to-end integration testing

### Supporting Files
- bot_session_state_machine.py: Session management for hands review
- flexible_poker_state_machine.py: Core poker game logic
- decision_engine_v2.py: Abstract decision engine interface
- poker_types.py: Core data type definitions

### Data Examples
- cycle_test_hand*.json: GTO session data (original and converted)
- gto_hand_for_verification*.json: Verification test data
- example_hand.json: Hand model example output

### Documentation
- HAND_MODEL_PROJECT_REPORT.md: Complete project analysis and status

## Key Issues Identified
1. Player index/name mapping inconsistency between GTO converter and session
2. Integration test infinite loop due to player mismatch
3. Need to preserve original player identities from GTO data

## Next Steps
1. Fix player naming convention in gto_to_hand_converter.py
2. Debug original GTO data format for actual player names
3. Update HandModelDecisionEngine to handle name variations
4. Complete integration testing and production deployment
"""
    
    with open("PACKAGE_MANIFEST.md", "w") as f:
        f.write(manifest_content)
    
    print(f"\n📋 Created manifest: PACKAGE_MANIFEST.md")
    print(f"\n🎯 Package ready for review!")
    print(f"   Total size: {os.path.getsize(zip_filename) / 1024:.1f} KB")
    
    return zip_filename

if __name__ == "__main__":
    package_file = create_hand_model_package()
    print(f"\n✅ Hand Model project packaged successfully!")
    print(f"📦 File: {package_file}")
    print(f"📋 Review the HAND_MODEL_PROJECT_REPORT.md for complete analysis")
