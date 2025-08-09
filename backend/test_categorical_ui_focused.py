#!/usr/bin/env python3
"""
Focused Categorical UI Test with Extensive Debug Logging
=======================================================

This test selects a few hands from different categories and performs complete GUI testing
with extensive debug logging to identify exactly where issues are occurring.

Selected hands for testing:
1. GEN-001: Heads-up hand (2 players)
2. GEN-004: 6-max hand (6 players) 
3. GEN-010: Full ring hand (9 players)
4. GEN-020: Mid-stakes hand
5. GEN-030: High-stakes hand

The test will:
- Load each hand in the GUI
- Step through every action with detailed logging
- Compare expected vs actual sequences
- Stop immediately on any discrepancy
- Log card displays, sound events, and UI updates
"""

import sys
import os
import time
import tkinter as tk
from tkinter import ttk
import threading
import json
from typing import List, Dict, Any, Optional

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.json_hands_database import JSONHandsDatabase, HandCategory
from ui.components.enhanced_fpsm_hands_review_panel import EnhancedFPSMHandsReviewPanel

class CategoricalUITest:
    """Test runner for categorical UI testing with extensive logging."""
    
    def __init__(self):
        self.root = None
        self.panel = None
        self.current_test_hand = None
        self.expected_sequence = []
        self.actual_sequence = []
        self.test_results = {}
        self.debug_log = []
        
        # Selected test hands from different categories
        self.test_hands = [
            "GEN-001",  # Heads-up (2 players)
            "GEN-004",  # 6-max (6 players)
            "GEN-010",  # Full ring (9 players)
            "GEN-020",  # Mid-stakes
            "GEN-030"   # High-stakes
        ]
        
    def log_debug(self, message: str):
        """Add debug message with timestamp."""
        timestamp = time.strftime("%H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] {message}"
        self.debug_log.append(log_entry)
        print(log_entry)
        
    def setup_gui(self):
        """Initialize the GUI components."""
        self.log_debug("🔧 Setting up GUI components...")
        
        self.root = tk.Tk()
        self.root.title("Categorical UI Test - Poker Hands Review")
        self.root.geometry("1400x900")
        
        # Create the enhanced hands review panel
        self.panel = EnhancedFPSMHandsReviewPanel(self.root)
        self.panel.font_size = 12  # Set font size after creation
        self.panel.pack(fill=tk.BOTH, expand=True)
        
        # Override some methods to capture events
        self._override_panel_methods()
        
        self.log_debug("✅ GUI setup complete")
        
    def _override_panel_methods(self):
        """Override panel methods to capture events and log them."""
        
        # Store original methods
        original_execute_action = self.panel.execute_action
        original_update_display = None
        
        # Check if poker_game_widget exists and has update_display
        if (hasattr(self.panel, 'poker_game_widget') and 
            self.panel.poker_game_widget and 
            hasattr(self.panel.poker_game_widget, 'update_display')):
            original_update_display = self.panel.poker_game_widget.update_display
        
        def logged_execute_action():
            """Wrapper for execute_action with logging."""
            self.log_debug("🎮 About to execute action...")
            
            # Check current action before execution
            if hasattr(self.panel, 'current_action_index') and hasattr(self.panel, 'current_hand_actions'):
                if self.panel.current_action_index < len(self.panel.current_hand_actions):
                    action = self.panel.current_hand_actions[self.panel.current_action_index]
                    self.log_debug(f"🎯 Current action: {action}")
                    self.actual_sequence.append(action)
                else:
                    self.log_debug("🏁 No more actions to execute")
            
            result = original_execute_action()
            
            # Check state after execution
            if hasattr(self.panel, 'poker_game_widget') and self.panel.poker_game_widget:
                widget = self.panel.poker_game_widget
                if hasattr(widget, 'state_machine') and widget.state_machine:
                    state = widget.state_machine.game_state
                    self.log_debug(f"💰 Pot after action: {state.pot}")
                    self.log_debug(f"🃏 Current street: {state.current_street}")
                    
                    # Log player states
                    for i, player in enumerate(state.players):
                        self.log_debug(f"👤 Player {i+1} ({player.name}): Stack={player.stack}, Bet={player.current_bet}, Folded={player.folded}")
                
            return result
            
        def logged_update_display():
            """Wrapper for update_display with logging."""
            self.log_debug("🖼️ Updating display...")
            if original_update_display:
                result = original_update_display()
                self.log_debug("✅ Display update complete")
                return result
                
        # Replace methods
        self.panel.execute_action = logged_execute_action
        
        # Only override update_display if it exists
        if original_update_display:
            self.panel.poker_game_widget.update_display = logged_update_display
            
    def load_hand_data(self, hand_id: str) -> Optional[Dict[str, Any]]:
        """Load hand data from the JSON database."""
        self.log_debug(f"📊 Loading hand data for {hand_id}...")
        
        try:
            db = JSONHandsDatabase("data/legendary_hands_complete_130_fixed.json")
            hands = db.get_all_hands()
            
            for hand in hands:
                if hand.metadata.hand_id == hand_id:
                    self.log_debug(f"✅ Found hand {hand_id}: {hand.metadata.description}")
                    self.log_debug(f"📈 Stakes: {hand.metadata.stakes}")
                    self.log_debug(f"👥 Players: {len(hand.parsed_hand.players)} players")
                    self.log_debug(f"🎯 Actions: {len(hand.parsed_hand.actions)} actions")
                    return hand
                    
            self.log_debug(f"❌ Hand {hand_id} not found in database")
            return None
            
        except Exception as e:
            self.log_debug(f"💥 Error loading hand {hand_id}: {e}")
            return None
            
    def prepare_expected_sequence(self, hand_data) -> List[Dict[str, Any]]:
        """Extract expected action sequence from hand data."""
        self.log_debug("📋 Preparing expected sequence...")
        
        expected = []
        for i, action in enumerate(hand_data.parsed_hand.actions):
            action_info = {
                'index': i,
                'player_name': action.get('player_name', ''),
                'action_type': action.get('action_type', ''),
                'amount': action.get('amount', 0),
                'street': action.get('street', 'preflop')
            }
            expected.append(action_info)
            self.log_debug(f"📝 Expected Action {i+1}: {action_info}")
            
        self.log_debug(f"✅ Expected sequence prepared: {len(expected)} actions")
        return expected
        
    def test_single_hand(self, hand_id: str) -> Dict[str, Any]:
        """Test a single hand with complete GUI simulation."""
        self.log_debug(f"\n{'='*60}")
        self.log_debug(f"🃏 TESTING HAND: {hand_id}")
        self.log_debug(f"{'='*60}")
        
        self.current_test_hand = hand_id
        self.actual_sequence = []
        test_result = {
            'hand_id': hand_id,
            'success': False,
            'errors': [],
            'cards_visible': False,
            'sounds_played': False,
            'sequence_match': False,
            'actions_completed': 0
        }
        
        try:
            # Load hand data
            hand_data = self.load_hand_data(hand_id)
            if not hand_data:
                test_result['errors'].append("Failed to load hand data")
                return test_result
                
            self.expected_sequence = self.prepare_expected_sequence(hand_data)
            
            # Load hand in GUI
            self.log_debug(f"🖥️ Loading hand {hand_id} in GUI...")
            self.panel.load_hand(hand_data)
            
            # Give GUI time to initialize
            self.root.update()
            time.sleep(0.5)
            
            # Check initial state
            self._check_initial_display(test_result)
            
            # Execute actions one by one
            self._execute_actions_with_validation(test_result)
            
            # Final validation
            self._validate_final_state(test_result)
            
        except Exception as e:
            self.log_debug(f"💥 Test error for {hand_id}: {e}")
            test_result['errors'].append(str(e))
            
        return test_result
        
    def _check_initial_display(self, test_result: Dict[str, Any]):
        """Check if cards and initial state are visible."""
        self.log_debug("🔍 Checking initial display...")
        
        if hasattr(self.panel, 'poker_game_widget') and self.panel.poker_game_widget:
            widget = self.panel.poker_game_widget
            
            # Check canvas size
            if hasattr(widget, 'canvas'):
                canvas_width = widget.canvas.winfo_width()
                canvas_height = widget.canvas.winfo_height()
                self.log_debug(f"📐 Canvas size: {canvas_width}x{canvas_height}")
                
                if canvas_width > 100 and canvas_height > 100:
                    test_result['canvas_proper_size'] = True
                    self.log_debug("✅ Canvas has proper size")
                else:
                    self.log_debug("❌ Canvas size too small")
                    
            # Check if player seats exist
            if hasattr(widget, 'player_seats') and widget.player_seats:
                self.log_debug(f"👥 Player seats: {len(widget.player_seats)} seats created")
                test_result['seats_created'] = len(widget.player_seats)
                
                # Check if cards are visible
                cards_found = 0
                for i, seat in enumerate(widget.player_seats):
                    if seat and hasattr(seat, 'card_frames'):
                        for card_frame in seat.card_frames:
                            if card_frame and card_frame.winfo_exists():
                                cards_found += 1
                                
                if cards_found > 0:
                    test_result['cards_visible'] = True
                    self.log_debug(f"🃏 Cards visible: {cards_found} card frames found")
                else:
                    self.log_debug("❌ No cards visible")
            else:
                self.log_debug("❌ No player seats found")
                
    def _execute_actions_with_validation(self, test_result: Dict[str, Any]):
        """Execute actions one by one with validation."""
        self.log_debug("🎮 Starting action execution with validation...")
        
        action_count = 0
        max_actions = len(self.expected_sequence)
        
        while action_count < max_actions:
            self.log_debug(f"\n--- ACTION {action_count + 1} / {max_actions} ---")
            
            # Execute one action
            try:
                self.panel.execute_action()
                action_count += 1
                test_result['actions_completed'] = action_count
                
                # Give GUI time to update
                self.root.update()
                time.sleep(0.2)  # Small delay to see changes
                
                # Check for sounds (mock check - we'll log if sound system is being called)
                if hasattr(self.panel.poker_game_widget, 'sound_manager'):
                    self.log_debug("🔊 Sound manager exists")
                    test_result['sounds_played'] = True
                    
                # Validate against expected sequence
                if action_count <= len(self.actual_sequence):
                    expected_action = self.expected_sequence[action_count - 1]
                    actual_action = self.actual_sequence[action_count - 1] if len(self.actual_sequence) >= action_count else None
                    
                    if actual_action:
                        match = self._compare_actions(expected_action, actual_action)
                        if not match:
                            self.log_debug(f"❌ ACTION MISMATCH at step {action_count}")
                            self.log_debug(f"Expected: {expected_action}")
                            self.log_debug(f"Actual: {actual_action}")
                            test_result['errors'].append(f"Action mismatch at step {action_count}")
                            break
                        else:
                            self.log_debug(f"✅ Action {action_count} matches expected")
                    
            except Exception as e:
                self.log_debug(f"💥 Error executing action {action_count + 1}: {e}")
                test_result['errors'].append(f"Action execution error: {e}")
                break
                
        # Check if we completed all actions successfully
        if action_count == max_actions and len(test_result['errors']) == 0:
            test_result['sequence_match'] = True
            self.log_debug("✅ All actions completed successfully")
        else:
            self.log_debug(f"⚠️ Completed {action_count}/{max_actions} actions")
            
    def _compare_actions(self, expected: Dict[str, Any], actual: Dict[str, Any]) -> bool:
        """Compare expected vs actual action."""
        # For now, just check basic fields
        return (expected.get('player_name') == actual.get('player_name') and
                expected.get('action_type') == actual.get('action_type'))
                
    def _validate_final_state(self, test_result: Dict[str, Any]):
        """Validate final state after all actions."""
        self.log_debug("🏁 Validating final state...")
        
        if hasattr(self.panel, 'poker_game_widget') and self.panel.poker_game_widget:
            widget = self.panel.poker_game_widget
            if hasattr(widget, 'state_machine') and widget.state_machine:
                state = widget.state_machine.game_state
                self.log_debug(f"💰 Final pot: {state.pot}")
                self.log_debug(f"🃏 Final street: {state.current_street}")
                
                # Check if hand is complete
                if state.current_street == "showdown" or all(p.folded for p in state.players[1:]):
                    test_result['hand_complete'] = True
                    self.log_debug("✅ Hand reached completion")
                else:
                    self.log_debug("⚠️ Hand did not reach completion")
                    
        # Overall success determination
        test_result['success'] = (
            test_result.get('cards_visible', False) and
            test_result.get('sequence_match', False) and
            len(test_result['errors']) == 0
        )
        
    def run_categorical_tests(self):
        """Run tests on all selected categorical hands."""
        self.log_debug("🚀 Starting Categorical UI Tests...")
        self.log_debug(f"📋 Testing hands: {self.test_hands}")
        
        self.setup_gui()
        
        all_results = {}
        
        for hand_id in self.test_hands:
            result = self.test_single_hand(hand_id)
            all_results[hand_id] = result
            
            self.log_debug(f"\n📊 RESULT for {hand_id}: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
            
            if not result['success']:
                self.log_debug("🛑 STOPPING TESTS - Found issues to investigate")
                break
                
            # Small pause between tests
            time.sleep(1)
            
        self._print_summary(all_results)
        
        # Keep GUI open for manual inspection
        self.log_debug("\n🔍 GUI remaining open for manual inspection...")
        self.log_debug("Close the window when finished.")
        self.root.mainloop()
        
    def _print_summary(self, results: Dict[str, Dict[str, Any]]):
        """Print comprehensive test summary."""
        self.log_debug(f"\n{'='*60}")
        self.log_debug("📊 CATEGORICAL UI TEST SUMMARY")
        self.log_debug(f"{'='*60}")
        
        total_tests = len(results)
        successful_tests = sum(1 for r in results.values() if r['success'])
        
        self.log_debug(f"✅ Successful: {successful_tests}/{total_tests}")
        self.log_debug(f"❌ Failed: {total_tests - successful_tests}/{total_tests}")
        
        for hand_id, result in results.items():
            self.log_debug(f"\n🃏 {hand_id}: {'✅ PASS' if result['success'] else '❌ FAIL'}")
            self.log_debug(f"   Cards Visible: {'✅' if result.get('cards_visible') else '❌'}")
            self.log_debug(f"   Sounds: {'✅' if result.get('sounds_played') else '❌'}")
            self.log_debug(f"   Sequence Match: {'✅' if result.get('sequence_match') else '❌'}")
            self.log_debug(f"   Actions Completed: {result.get('actions_completed', 0)}")
            
            if result['errors']:
                for error in result['errors']:
                    self.log_debug(f"   ❌ Error: {error}")


def main():
    """Run the categorical UI test."""
    print("🎯 Categorical UI Test - Poker Hands Review")
    print("=" * 50)
    
    tester = CategoricalUITest()
    tester.run_categorical_tests()


if __name__ == "__main__":
    main()
