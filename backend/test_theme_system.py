#!/usr/bin/env python3
"""
Non-GUI test script for the theme system.
Safe to run in VS Code integrated terminal.
"""

import sys
import os

# Add the backend directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(__file__))

def test_theme_system():
    """Test the theme system without GUI components."""
    print("🧪 Testing Theme System (Non-GUI)")
    print("=" * 50)
    
    try:
        # Test theme loader
        print("1. Testing theme loader...")
        from ui.services.theme_loader_consolidated import get_consolidated_theme_loader
        
        loader = get_consolidated_theme_loader()
        config = loader.load_themes()
        themes = config.get("themes", [])
        
        print(f"   ✅ Loaded {len(themes)} themes")
        current_file = loader.get_current_file()
        print(f"   ✅ Current file: {current_file.name if current_file else 'embedded fallback'}")
        
        # Test theme access
        print("\n2. Testing theme access...")
        if themes:
            first_theme = themes[0]
            theme_name = first_theme.get("name", "Unknown")
            theme_id = first_theme.get("id", "unknown")
            palette = first_theme.get("palette", {})
            
            print(f"   ✅ First theme: {theme_name} (id: {theme_id})")
            print(f"   ✅ Palette has {len(palette)} colors")
            
            # Show a few colors
            sample_colors = ["felt", "rail", "accent", "text"]
            for color_key in sample_colors:
                if color_key in palette:
                    print(f"      {color_key}: {palette[color_key]}")
        
        # Test defaults
        print("\n3. Testing defaults...")
        defaults = loader.get_defaults()
        print(f"   ✅ Defaults loaded with {len(defaults)} sections")
        
        if "state_styling" in defaults:
            states = defaults["state_styling"]
            print(f"   ✅ State styling has {len(states)} states")
        
        # Test theme list
        print("\n4. Testing theme list...")
        theme_list = loader.get_theme_list()
        print(f"   ✅ Theme list has {len(theme_list)} entries")
        
        for i, theme_info in enumerate(theme_list[:3]):  # Show first 3
            name = theme_info.get("name", "Unknown")
            theme_id = theme_info.get("id", "unknown")
            print(f"      {i+1}. {name} (id: {theme_id})")
        
        if len(theme_list) > 3:
            print(f"      ... and {len(theme_list) - 3} more")
        
        # Test color utilities
        print("\n5. Testing color utilities...")
        from ui.theme_manager import hex_to_rgbf, rgbf_to_hex, apply_hsl_nudge
        
        test_color = "#FF0000"  # Red
        rgb = hex_to_rgbf(test_color)
        back_to_hex = rgbf_to_hex(rgb)
        print(f"   ✅ Color conversion: {test_color} -> {rgb} -> {back_to_hex}")
        
        # Test HSL nudging
        nudged = apply_hsl_nudge(test_color, dh=0.1, ds=0.0, dl=0.0)  # Shift hue
        print(f"   ✅ HSL nudge: {test_color} -> {nudged}")
        
        print("\n🎉 All theme system tests passed!")
        print("\n💡 To test the GUI components:")
        print("   1. Open macOS Terminal app")
        print(f"   2. cd {os.getcwd()}")
        print("   3. python3 demo_theme_manager.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_theme_system()
    sys.exit(0 if success else 1)
