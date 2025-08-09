#!/usr/bin/env python3
"""
Debug script to analyze timeout hands individually.
Shows detailed action-by-action progress and stack validation.
"""

import sys
import os
import time
import tkinter as tk
from typing import Dict, List, Any
from ui.components.fpsm_hands_review_panel import FPSMHandsReviewPanel

class TimeoutHandDebugger:
    def __init__(self):
        # Timeout hands from the test
        self.timeout_hands = [
            "GEN-012",  # Hand 12
            "GEN-013",  # Hand 13 
            "GEN-018",  # Hand 18
            "GEN-019",  # Hand 19
            "GEN-020",  # Hand 20
        ]
        
        self.root = tk.Tk()
        self.root.withdraw()
        self.panel = FPSMHandsReviewPanel(self.root)
        
    def debug_hand(self, hand_id: str):
        """Debug a specific hand with detailed logging."""
        print(f"\n{'='*80}")
        print(f"🔍 DEBUGGING HAND: {hand_id}")
        print(f"{'='*80}")
        
        # Find the hand
        hand = None
        hand_index = None
        for i, h in enumerate(self.panel.legendary_hands):
            if getattr(h.metadata, 'id', f'Hand {i+1}') == hand_id:
                hand = h
                hand_index = i
                break
                
        if not hand:
            print(f"❌ Hand {hand_id} not found!")
            return False
            
        # Print hand info
        note = getattr(hand.metadata, 'note', 'No description available')
        game_info = getattr(hand, 'game', {})
        print(f"📋 Hand: {note}")
        print(f"👥 Players: {len(hand.players)}")
        print(f"🎮 Game: {game_info}")
        print(f"🎯 Expected Actions: {sum(len(actions) if isinstance(actions, list) else 0 for actions in hand.actions.values())}")
        
        # Print original player stacks
        print(f"\n💰 ORIGINAL PLAYER STACKS:")
        for i, player in enumerate(hand.players):
            name = player.get('name', f'Player {i+1}') if isinstance(player, dict) else getattr(player, 'name', f'Player {i+1}')
            stack = player.get('stack', 0) if isinstance(player, dict) else getattr(player, 'stack', 0)
            print(f"  {i+1:2d}. {name:20s} = ${stack:,}")
            
        # Print expected board
        if hasattr(hand, 'board') and hand.board:
            print(f"\n🎴 EXPECTED BOARD: {hand.board}")
            
        # Setup hand
        self.panel.current_hand = hand
        self.panel.current_hand_index = hand_index
        
        try:
            start_time = time.time()
            print(f"\n🚀 Starting simulation...")
            
            self.panel.start_hand_simulation()
            
            if not (self.panel.simulation_active and self.panel.fpsm):
                print(f"❌ Failed to setup simulation")
                return False
                
            # Enable headless mode for speed
            if hasattr(self.panel.poker_game_widget, 'headless_mode'):
                self.panel.poker_game_widget.headless_mode = True
                
            # Track action-by-action progress
            action_count = 0
            max_actions = 100
            last_street = None
            street_action_counts = {"preflop": 0, "flop": 0, "turn": 0, "river": 0}
            
            print(f"\n📋 ACTION-BY-ACTION PROGRESS:")
            print(f"{'#':>3} {'Player':>20} {'Action':>10} {'Amount':>12} {'State':>15} {'Street':>8}")
            print(f"{'-'*80}")
            
            while (not self.panel.hand_completed and 
                   action_count < max_actions and 
                   (time.time() - start_time) < 120):  # 2 minute timeout
                
                # Get current state info
                if self.panel.fpsm:
                    current_state = self.panel.fpsm.current_state.name if self.panel.fpsm.current_state else "UNKNOWN"
                    current_player = None
                    
                    # Get current player info
                    if hasattr(self.panel.fpsm, 'get_current_player'):
                        try:
                            current_player = self.panel.fpsm.get_current_player()
                        except:
                            pass
                    
                    # Determine current street
                    current_street = "unknown"
                    if "PREFLOP" in current_state:
                        current_street = "preflop"
                    elif "FLOP" in current_state:
                        current_street = "flop" 
                    elif "TURN" in current_state:
                        current_street = "turn"
                    elif "RIVER" in current_state:
                        current_street = "river"
                    elif current_state in ["SHOWDOWN", "END_HAND"]:
                        current_street = "showdown"
                        
                    # Check for street transition
                    if last_street and last_street != current_street and current_street in street_action_counts:
                        print(f"\n🎪 STREET TRANSITION: {last_street} → {current_street}")
                        self._validate_stacks_at_street_end(hand, last_street)
                        street_action_counts[current_street] = 0
                        
                    last_street = current_street
                    
                    # Show current action info
                    player_name = current_player.name if current_player else "Unknown"
                    
                try:
                    action_start = time.time()
                    self.panel.next_action()
                    action_time = time.time() - action_start
                    action_count += 1
                    street_action_counts[current_street] += 1
                    
                    # Log the action
                    print(f"{action_count:>3} {player_name:>20} {'???':>10} {'???':>12} {current_state:>15} {current_street:>8} ({action_time:.2f}s)")
                    
                    # Check for unusually slow actions
                    if action_time > 5.0:
                        print(f"⚠️  SLOW ACTION: {action_time:.2f}s - potential bottleneck!")
                        
                except Exception as e:
                    print(f"❌ Action failed: {e}")
                    break
                    
                # Check for loops (same state repeated)
                if action_count > 50:
                    print(f"⚠️  Many actions ({action_count}) - possible loop")
                    
            elapsed = time.time() - start_time
            
            # Final results
            print(f"\n{'='*80}")
            print(f"⏱️  SIMULATION RESULTS:")
            print(f"⏱️  Total time: {elapsed:.2f}s")
            print(f"📊 Actions executed: {action_count}")
            print(f"📊 Actions per street: {street_action_counts}")
            print(f"✅ Completed: {self.panel.hand_completed}")
            print(f"🎯 Final state: {self.panel.fpsm.current_state.name if self.panel.fpsm else 'Unknown'}")
            
            if elapsed > 60:
                print(f"🐌 TIMEOUT ANALYSIS:")
                print(f"   - Average per action: {elapsed/action_count:.2f}s")
                print(f"   - Possible causes: Complex logic, UI rendering, infinite loops")
                
            # Final stack validation
            if self.panel.fpsm:
                self._validate_final_stacks(hand)
                
            return self.panel.hand_completed
            
        except Exception as e:
            print(f"💥 Debug failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def _validate_stacks_at_street_end(self, hand, street):
        """Validate stack sizes match expected values at street end."""
        print(f"💰 STACK VALIDATION - End of {street}:")
        
        if not self.panel.fpsm:
            print("   ❌ No FPSM available for validation")
            return
            
        try:
            # Get current stacks from FPSM
            fpsm_players = self.panel.fpsm.players
            
            for i, fpsm_player in enumerate(fpsm_players):
                if i < len(hand.players):
                    player_data = hand.players[i]
                    original_stack = player_data.get('stack', 0) if isinstance(player_data, dict) else getattr(player_data, 'stack', 0)
                else:
                    original_stack = "N/A"
                current_stack = fpsm_player.stack
                
                status = "✅" if isinstance(original_stack, (int, float)) else "?"
                print(f"   {i+1:2d}. {fpsm_player.name:20s}: ${current_stack:>10,} (orig: ${original_stack:>10,}) {status}")
                
        except Exception as e:
            print(f"   ❌ Stack validation failed: {e}")
            
    def _validate_final_stacks(self, hand):
        """Validate final stack sizes."""
        print(f"\n💰 FINAL STACK VALIDATION:")
        
        if not self.panel.fpsm:
            print("   ❌ No FPSM available for validation")
            return
            
        try:
            fpsm_players = self.panel.fpsm.players
            total_discrepancy = 0
            
            for i, fpsm_player in enumerate(fpsm_players):
                if i < len(hand.players):
                    player_data = hand.players[i]
                    original_stack = player_data.get('stack', 0) if isinstance(player_data, dict) else getattr(player_data, 'stack', 0)
                    current_stack = fpsm_player.stack
                    diff = abs(current_stack - original_stack)
                    total_discrepancy += diff
                    
                    status = "✅" if diff < 1 else f"❌ Δ${diff:,}"
                    print(f"   {i+1:2d}. {fpsm_player.name:20s}: ${current_stack:>10,} vs ${original_stack:>10,} {status}")
                    
            print(f"   📊 Total discrepancy: ${total_discrepancy:,}")
            
        except Exception as e:
            print(f"   ❌ Final validation failed: {e}")
    
    def run_debug_session(self):
        """Debug all timeout hands."""
        print(f"🔍 TIMEOUT HANDS DEBUGGER")
        print(f"Analyzing {len(self.timeout_hands)} timeout hands...")
        
        results = {}
        
        for hand_id in self.timeout_hands:
            success = self.debug_hand(hand_id)
            results[hand_id] = success
            
            # Brief pause between hands
            time.sleep(1)
            
        print(f"\n{'='*80}")
        print(f"🏆 TIMEOUT HANDS SUMMARY")
        print(f"{'='*80}")
        
        for hand_id, success in results.items():
            status = "✅ FIXED" if success else "❌ STILL TIMEOUT"
            print(f"{hand_id}: {status}")
            
        success_count = sum(results.values())
        print(f"\n📊 Results: {success_count}/{len(self.timeout_hands)} hands fixed")
        
        self.root.destroy()

if __name__ == "__main__":
    debugger = TimeoutHandDebugger()
    debugger.run_debug_session()
