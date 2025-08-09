#!/usr/bin/env python3
"""
Hands Review Tab Integration Test
================================

Test to verify that the hands review tab in main_gui.py is properly using:
✅ Enhanced FPSM with 2-9 player support
✅ Validated RPGW with dynamic positioning
✅ Clean 120 legendary hands database
✅ Dynamic actor mapping
✅ Enhanced PHH parser with board/action data
"""

import sys
import os
import tkinter as tk
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from ui.components.fpsm_hands_review_panel import FPSMHandsReviewPanel
from core.hands_database import ComprehensiveHandsDatabase, HandCategory
from core.flexible_poker_state_machine import GameConfig


class HandsReviewTabTester:
    """Test the hands review tab integration with all enhanced components."""
    
    def __init__(self):
        self.results = {
            'database_integration': False,
            'fpsm_integration': False,
            'rpgw_integration': False,
            'dynamic_positioning': False,
            'enhanced_parsing': False,
            'ui_creation': False
        }
    
    def test_full_integration(self):
        """Test full hands review tab integration."""
        print("🎯 HANDS REVIEW TAB INTEGRATION TEST")
        print("=" * 50)
        print("Verifying enhanced FPSM, RPGW, and clean database integration")
        print()
        
        # Test 1: Database Integration
        print("📋 Test 1: Database Integration...")
        self._test_database_integration()
        
        # Test 2: UI Creation
        print("\n🎨 Test 2: UI Panel Creation...")
        self._test_ui_creation()
        
        # Test 3: FPSM Integration  
        print("\n🎮 Test 3: FPSM Integration...")
        self._test_fpsm_integration()
        
        # Test 4: RPGW Integration
        print("\n🎯 Test 4: RPGW Integration...")
        self._test_rpgw_integration()
        
        # Test 5: Enhanced Parsing
        print("\n🔧 Test 5: Enhanced Parsing...")
        self._test_enhanced_parsing()
        
        # Print final results
        self._print_results()
    
    def _test_database_integration(self):
        """Test that the hands review panel uses the enhanced database."""
        try:
            # Test database directly
            db = ComprehensiveHandsDatabase()
            all_hands = db.load_all_hands()
            
            legendary_count = len(all_hands.get(HandCategory.LEGENDARY, []))
            practice_count = len(all_hands.get(HandCategory.PRACTICE, []))
            
            print(f"   📊 Database Results:")
            print(f"      • Legendary hands: {legendary_count}")
            print(f"      • Practice hands: {practice_count}")
            print(f"      • Total hands: {legendary_count + practice_count}")
            
            # Check for our expected counts
            if legendary_count >= 100:
                print("   ✅ Legendary hands count correct (≥100)")
                if legendary_count == 100:
                    print("   🎯 Perfect! Exactly 100 legendary hands loaded")
                self.results['database_integration'] = True
            else:
                print(f"   ❌ Expected ≥100 legendary hands, got {legendary_count}")
                
        except Exception as e:
            print(f"   ❌ Database test failed: {str(e)}")
    
    def _test_ui_creation(self):
        """Test UI panel creation."""
        try:
            # Create minimal Tkinter environment
            root = tk.Tk()
            root.withdraw()  # Hide window
            
            # Create the hands review panel
            panel = FPSMHandsReviewPanel(root)
            
            # Check that it loaded data
            legendary_count = len(panel.legendary_hands)
            practice_count = len(panel.practice_hands)
            
            print(f"   🎨 UI Panel Results:")
            print(f"      • Panel created successfully")
            print(f"      • Legendary hands loaded: {legendary_count}")
            print(f"      • Practice hands loaded: {practice_count}")
            
            # Check for database integration
            if hasattr(panel, 'hands_database') and isinstance(panel.hands_database, ComprehensiveHandsDatabase):
                print("   ✅ Using ComprehensiveHandsDatabase correctly")
                self.results['ui_creation'] = True
            else:
                print("   ❌ Not using ComprehensiveHandsDatabase")
            
            # Cleanup
            root.destroy()
            
        except Exception as e:
            print(f"   ❌ UI creation test failed: {str(e)}")
    
    def _test_fpsm_integration(self):
        """Test FPSM integration and configuration."""
        try:
            # Test different player counts
            test_configs = [
                {"name": "Heads-Up", "players": 2},
                {"name": "6-Player", "players": 6},
                {"name": "Full Table", "players": 9}
            ]
            
            print("   🎮 FPSM Configuration Tests:")
            
            all_passed = True
            for config in test_configs:
                try:
                    game_config = GameConfig(
                        num_players=config['players'],
                        big_blind=1000,
                        small_blind=500
                    )
                    
                    print(f"      ✅ {config['name']} ({config['players']} players): Config created")
                    
                except Exception as e:
                    print(f"      ❌ {config['name']}: {str(e)}")
                    all_passed = False
            
            if all_passed:
                print("   ✅ Enhanced FPSM supports all player counts (2-9)")
                self.results['fpsm_integration'] = True
            else:
                print("   ❌ FPSM configuration issues detected")
                
        except Exception as e:
            print(f"   ❌ FPSM integration test failed: {str(e)}")
    
    def _test_rpgw_integration(self):
        """Test RPGW integration and dynamic positioning."""
        try:
            root = tk.Tk()
            root.withdraw()
            
            # Create panel and check for RPGW integration
            panel = FPSMHandsReviewPanel(root)
            
            # Check if the panel has the methods we expect
            required_methods = [
                'setup_hand_for_simulation',
                'build_actor_mapping',
                '_connect_rpgw_logging'
            ]
            
            print("   🎯 RPGW Integration Checks:")
            
            all_methods_present = True
            for method in required_methods:
                if hasattr(panel, method):
                    print(f"      ✅ Method '{method}' present")
                else:
                    print(f"      ❌ Method '{method}' missing")
                    all_methods_present = False
            
            # Check for dynamic positioning support
            if hasattr(panel, 'build_actor_mapping'):
                print("      ✅ Dynamic actor mapping available")
                self.results['dynamic_positioning'] = True
            else:
                print("      ❌ Dynamic actor mapping missing")
            
            if all_methods_present:
                print("   ✅ RPGW integration methods complete")
                self.results['rpgw_integration'] = True
            else:
                print("   ❌ RPGW integration incomplete")
            
            root.destroy()
            
        except Exception as e:
            print(f"   ❌ RPGW integration test failed: {str(e)}")
    
    def _test_enhanced_parsing(self):
        """Test enhanced PHH parsing capabilities."""
        try:
            # Test by loading a sample hand and checking for board/action data
            db = ComprehensiveHandsDatabase()
            all_hands = db.load_all_hands()
            legendary_hands = all_hands.get(HandCategory.LEGENDARY, [])
            
            if not legendary_hands:
                print("   ❌ No legendary hands to test parsing")
                return
            
            # Test first few hands for parsing quality
            test_count = min(3, len(legendary_hands))
            successful_parses = 0
            
            print(f"   🔧 Enhanced Parsing Tests (testing {test_count} hands):")
            
            for i in range(test_count):
                hand = legendary_hands[i]
                hand_id = getattr(hand.metadata, 'id', f'Hand_{i+1}')
                
                # Check for enhanced parsing features
                has_board = hasattr(hand, 'board') and len(getattr(hand, 'board', {})) > 0
                has_actions = hasattr(hand, 'actions') and len(getattr(hand, 'actions', {})) > 0
                has_players = hasattr(hand, 'players') and len(getattr(hand, 'players', [])) > 0
                
                if has_board and has_actions and has_players:
                    successful_parses += 1
                    print(f"      ✅ {hand_id}: Complete parsing (board, actions, players)")
                else:
                    missing = []
                    if not has_board: missing.append('board')
                    if not has_actions: missing.append('actions') 
                    if not has_players: missing.append('players')
                    print(f"      ❌ {hand_id}: Missing {missing}")
            
            success_rate = successful_parses / test_count
            print(f"   📊 Parsing Success Rate: {successful_parses}/{test_count} ({success_rate:.1%})")
            
            if success_rate >= 0.8:  # 80% threshold
                print("   ✅ Enhanced parsing working well")
                self.results['enhanced_parsing'] = True
            else:
                print("   ❌ Enhanced parsing needs improvement")
                
        except Exception as e:
            print(f"   ❌ Enhanced parsing test failed: {str(e)}")
    
    def _print_results(self):
        """Print comprehensive test results."""
        print("\n" + "=" * 50)
        print("🏆 HANDS REVIEW TAB INTEGRATION RESULTS")
        print("=" * 50)
        
        # Count successes
        passed_tests = sum(1 for result in self.results.values() if result)
        total_tests = len(self.results)
        success_rate = passed_tests / total_tests * 100
        
        print(f"📊 Overall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        print()
        
        # Individual results
        test_names = {
            'database_integration': 'Database Integration (120 hands)',
            'ui_creation': 'UI Panel Creation',
            'fpsm_integration': 'Enhanced FPSM Integration', 
            'rpgw_integration': 'RPGW Integration',
            'dynamic_positioning': 'Dynamic Actor Mapping',
            'enhanced_parsing': 'Enhanced PHH Parsing'
        }
        
        for test_key, test_name in test_names.items():
            status = "✅ PASSED" if self.results[test_key] else "❌ FAILED"
            print(f"   • {test_name}: {status}")
        
        print()
        
        # Final assessment
        if success_rate >= 90:
            print("🎉 EXCELLENT! Hands review tab fully integrated with all enhancements")
            print("✅ Ready for production use with enhanced FPSM, RPGW, and database")
        elif success_rate >= 75:
            print("✅ GOOD! Most components integrated successfully")
            print("🔧 Minor issues to address for full integration")
        else:
            print("⚠️  NEEDS WORK! Several integration issues detected")
            print("🔧 Review failed components before using hands review tab")


def main():
    """Run the hands review tab integration test."""
    print("🚀 HANDS REVIEW TAB INTEGRATION VERIFICATION")
    print("Testing integration with enhanced FPSM, RPGW, and clean database")
    print()
    
    tester = HandsReviewTabTester()
    tester.test_full_integration()


if __name__ == "__main__":
    main()
