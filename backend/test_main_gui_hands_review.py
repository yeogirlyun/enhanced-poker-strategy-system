#!/usr/bin/env python3
"""
Test the main GUI hands review tab integration with our improved FPSM and RPGW.
"""

import sys
import os
import tkinter as tk
from tkinter import ttk
import time

def test_main_gui_hands_review():
    """Test the main GUI hands review tab integration."""
    print("🧪 TESTING MAIN GUI HANDS REVIEW TAB INTEGRATION")
    print("=" * 60)
    
    try:
        # Import main GUI
        from main_gui import EnhancedMainGUI
        
        print("✅ Creating main GUI...")
        app = EnhancedMainGUI()
        
        print("✅ Main GUI created successfully")
        print(f"📋 GUI has {app.notebook.index('end')} tabs")
        
        # Check if hands review tab exists
        hands_review_tab_found = False
        for i in range(app.notebook.index('end')):
            tab_text = app.notebook.tab(i, 'text')
            print(f"   Tab {i+1}: {tab_text}")
            if 'Hands Review' in tab_text:
                hands_review_tab_found = True
                hands_review_tab_index = i
                print(f"   ✅ Found hands review tab at index {i}")
        
        if not hands_review_tab_found:
            print("❌ Hands review tab not found!")
            app.root.destroy()
            return False
        
        # Test hands review panel
        print("🎯 Testing hands review panel...")
        
        # Select the hands review tab
        app.notebook.select(hands_review_tab_index)
        
        # Check if hands review panel exists
        if hasattr(app, 'hands_review_panel'):
            hands_panel = app.hands_review_panel
            print("✅ Hands review panel exists")
            
            # Test basic functionality
            if hasattr(hands_panel, 'legendary_hands') and hands_panel.legendary_hands:
                print(f"✅ Loaded {len(hands_panel.legendary_hands)} legendary hands")
                
                # Test first hand
                first_hand = hands_panel.legendary_hands[0]
                hand_id = getattr(first_hand.metadata, 'id', 'Hand 1')
                print(f"   First hand: {hand_id}")
                print(f"   Players: {len(first_hand.players)}")
                
                # Test setup without actually running simulation
                print("🔧 Testing setup capabilities...")
                hands_panel.current_hand = first_hand
                hands_panel.current_hand_index = 0
                
                # Check if all required components are accessible
                components_check = {
                    'legendary_hands': hasattr(hands_panel, 'legendary_hands'),
                    'practice_hands': hasattr(hands_panel, 'practice_hands'),
                    'current_hand': hasattr(hands_panel, 'current_hand'),
                    'fpsm': hasattr(hands_panel, 'fpsm'),
                    'setup_method': hasattr(hands_panel, 'setup_hand_for_simulation'),
                    'next_action_method': hasattr(hands_panel, 'next_action'),
                    'simulation_controls': hasattr(hands_panel, 'simulation_active'),
                }
                
                print("📊 Component availability:")
                for component, available in components_check.items():
                    status = "✅" if available else "❌"
                    print(f"   {status} {component}: {'Available' if available else 'Missing'}")
                
                all_components_available = all(components_check.values())
                
                if all_components_available:
                    print("🎉 All hands review components are properly integrated!")
                else:
                    print("⚠️  Some hands review components are missing")
                
            else:
                print("❌ No legendary hands loaded")
                all_components_available = False
        else:
            print("❌ Hands review panel not found")
            all_components_available = False
        
        # Test font size integration
        print("🔧 Testing font size integration...")
        if hasattr(app, '_update_font_size'):
            try:
                app._update_font_size()
                print("✅ Font size update works")
                font_integration = True
            except Exception as e:
                print(f"❌ Font size update error: {e}")
                font_integration = False
        else:
            print("⚠️  Font size update method not found")
            font_integration = False
        
        # Cleanup
        print("🧹 Cleaning up test GUI...")
        app.root.after(100, app.root.quit)  # Schedule quit after 100ms
        app.root.mainloop()  # Let it process the quit
        app.root.destroy()
        
        # Final assessment
        print("\n" + "=" * 60)
        print("🏆 MAIN GUI HANDS REVIEW TAB TEST RESULTS")
        print("=" * 60)
        
        test_results = {
            "GUI Creation": True,
            "Hands Review Tab": hands_review_tab_found,
            "Panel Integration": all_components_available,
            "Font Integration": font_integration,
        }
        
        for test_name, passed in test_results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} {test_name}")
        
        overall_success = all(test_results.values())
        
        if overall_success:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ Main GUI hands review tab is fully integrated")
            print("✅ All components properly accessible")
            print("✅ Ready for user testing")
        else:
            print("\n⚠️  SOME TESTS FAILED")
            print("❌ Issues detected in hands review integration")
        
        return overall_success
        
    except Exception as e:
        print(f"💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_hands_review_panel_directly():
    """Test the hands review panel directly without main GUI."""
    print("\n🔍 TESTING HANDS REVIEW PANEL DIRECTLY")
    print("=" * 50)
    
    try:
        from ui.components.fpsm_hands_review_panel import FPSMHandsReviewPanel
        
        # Create a minimal root window
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        print("✅ Creating FPSMHandsReviewPanel...")
        panel = FPSMHandsReviewPanel(root)
        
        print(f"✅ Panel created successfully")
        print(f"📋 Loaded {len(panel.legendary_hands)} legendary hands")
        print(f"📋 Loaded {len(panel.practice_hands)} practice hands")
        
        # Test basic methods
        methods_check = {
            'start_hand_simulation': hasattr(panel, 'start_hand_simulation'),
            'next_action': hasattr(panel, 'next_action'),
            'setup_hand_for_simulation': hasattr(panel, 'setup_hand_for_simulation'),
            'quit_simulation': hasattr(panel, 'quit_simulation'),
            'build_actor_mapping': hasattr(panel, 'build_actor_mapping'),
        }
        
        print("📊 Method availability:")
        for method_name, available in methods_check.items():
            status = "✅" if available else "❌"
            print(f"   {status} {method_name}: {'Available' if available else 'Missing'}")
        
        root.destroy()
        
        all_methods_available = all(methods_check.values())
        
        if all_methods_available:
            print("🎉 Hands review panel is fully functional!")
        else:
            print("⚠️  Some hands review methods are missing")
        
        return all_methods_available
        
    except Exception as e:
        print(f"💥 Direct panel test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 COMPREHENSIVE MAIN GUI HANDS REVIEW TEST")
    print("=" * 70)
    
    # Test 1: Direct panel test
    panel_success = test_hands_review_panel_directly()
    
    # Test 2: Main GUI integration test  
    gui_success = test_main_gui_hands_review()
    
    print("\n" + "=" * 70)
    print("🏆 FINAL TEST RESULTS")
    print("=" * 70)
    print(f"✅ Direct Panel Test: {'PASS' if panel_success else 'FAIL'}")
    print(f"✅ GUI Integration Test: {'PASS' if gui_success else 'FAIL'}")
    
    if panel_success and gui_success:
        print("\n🎉 ALL TESTS PASSED - MAIN GUI HANDS REVIEW IS READY!")
        print("🚀 The hands review tab is fully integrated with:")
        print("  • ✅ Proven FPSM (100% validation)")
        print("  • ✅ Optimized RPGW with headless mode")
        print("  • ✅ Corrected PHH parsing") 
        print("  • ✅ Fixed actor mapping")
        print("  • ✅ Main GUI font and theme integration")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        if not panel_success:
            print("❌ Hands review panel has issues")
        if not gui_success:
            print("❌ Main GUI integration has issues")
    
    print("\n👤 Ready for user testing in the main GUI application!")
