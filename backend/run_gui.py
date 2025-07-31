#!/usr/bin/env python3
"""
GUI Poker Strategy Development System Launcher

This script launches the enhanced GUI poker strategy development system.
"""

import sys
import os

# Add gui_version to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'gui_version'))

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared'))

if __name__ == "__main__":
    from enhanced_main_gui_v2 import EnhancedMainGUIV2
    
    print("🎮 Starting Enhanced GUI Poker Strategy Development System...")
    print("=" * 60)
    
    app = EnhancedMainGUIV2()
    app.run() 