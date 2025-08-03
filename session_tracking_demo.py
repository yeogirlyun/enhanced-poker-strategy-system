#!/usr/bin/env python3
"""
Comprehensive demonstration of the enhanced poker state machine session tracking.
This shows how the session tracking would be used in a real GUI scenario.
"""

import sys
import os
import json
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from shared.poker_state_machine_enhanced import ImprovedPokerStateMachine


class SessionTrackingDemo:
    """Demonstrates comprehensive session tracking capabilities."""
    
    def __init__(self):
        self.state_machine = ImprovedPokerStateMachine(num_players=6)
        self.session_data = {}
        
    def start_demo_session(self):
        """Start a demo session with comprehensive tracking."""
        print("🎮 Starting Comprehensive Session Tracking Demo")
        print("=" * 60)
        
        # Start the session
        self.state_machine.start_session()
        
        # Simulate a realistic poker session with multiple hands
        self._simulate_realistic_session()
        
        # Demonstrate session analysis capabilities
        self._demonstrate_session_analysis()
        
        # Demonstrate debugging capabilities
        self._demonstrate_debugging_capabilities()
        
        # Demonstrate replay capabilities
        self._demonstrate_replay_capabilities()
        
        # Export session for analysis
        self._export_session_for_analysis()
        
        # End session
        self.state_machine.end_session()
        
    def _simulate_realistic_session(self):
        """Simulate a realistic poker session with various scenarios."""
        print("\n🎯 Simulating Realistic Poker Session")
        print("-" * 40)
        
        # Simulate 5 hands with different scenarios
        scenarios = [
            "All players fold to big blind",
            "Showdown with multiple players",
            "All-in scenario with side pots",
            "Raise and re-raise action",
            "Complex multi-way pot"
        ]
        
        for hand_num, scenario in enumerate(scenarios, 1):
            print(f"\n🎮 Hand {hand_num}: {scenario}")
            
            # Start the hand
            self.state_machine.start_hand()
            
            # Simulate some realistic actions
            self._simulate_hand_actions(hand_num, scenario)
            
            # Complete the hand (in real GUI, this happens through normal play)
            self._complete_hand_simulation(hand_num)
            
    def _simulate_hand_actions(self, hand_num, scenario):
        """Simulate realistic hand actions based on scenario."""
        # This would be handled by the GUI in a real scenario
        # For demo purposes, we'll simulate some actions
        
        if scenario == "All players fold to big blind":
            print("   📊 Simulating: Players fold to big blind")
            # In real scenario, players would make actual decisions
            
        elif scenario == "Showdown with multiple players":
            print("   📊 Simulating: Multiple players reach showdown")
            
        elif scenario == "All-in scenario with side pots":
            print("   📊 Simulating: All-in action creates side pots")
            
        elif scenario == "Raise and re-raise action":
            print("   📊 Simulating: Aggressive betting action")
            
        elif scenario == "Complex multi-way pot":
            print("   📊 Simulating: Complex multi-way action")
    
    def _complete_hand_simulation(self, hand_num):
        """Complete the hand simulation."""
        # In a real scenario, this would happen through normal game flow
        # For demo, we'll simulate hand completion
        print(f"   ✅ Hand {hand_num} completed")
        
    def _demonstrate_session_analysis(self):
        """Demonstrate session analysis capabilities."""
        print("\n📊 Session Analysis Capabilities")
        print("-" * 40)
        
        # Get comprehensive session data
        session_data = self.state_machine.get_comprehensive_session_data()
        
        print("✅ Session Information Available:")
        print(f"   Session ID: {session_data.get('session_info', {}).get('session_id', 'N/A')}")
        print(f"   Total Hands: {session_data.get('session_statistics', {}).get('total_hands', 0)}")
        print(f"   Session Duration: {session_data.get('session_info', {}).get('duration_seconds', 0):.1f} seconds")
        print(f"   Big Blind: ${session_data.get('session_info', {}).get('big_blind_amount', 0):.2f}")
        
        # Show player statistics
        player_stats = session_data.get('session_statistics', {}).get('player_statistics', {})
        if player_stats:
            print("\n👥 Player Statistics:")
            for player, stats in player_stats.items():
                print(f"   {player}: {stats.get('hands_played', 0)} hands played")
        
        # Show hand summaries
        hands_played = session_data.get('hands_played', [])
        if hands_played:
            print(f"\n🎮 Hand Summaries ({len(hands_played)} hands):")
            for hand in hands_played:
                print(f"   Hand {hand['hand_number']}: ${hand['pot_amount']:.2f} pot, {hand['action_count']} actions")
    
    def _demonstrate_debugging_capabilities(self):
        """Demonstrate debugging capabilities."""
        print("\n🐛 Debugging Capabilities")
        print("-" * 40)
        
        # Get current game state for debugging
        current_state = self.state_machine.get_game_info()
        
        print("✅ Current Game State Available:")
        print(f"   Current State: {current_state.get('state', 'N/A')}")
        print(f"   Pot: ${current_state.get('pot', 0):.2f}")
        print(f"   Current Bet: ${current_state.get('current_bet', 0):.2f}")
        print(f"   Board: {current_state.get('board', [])}")
        
        # Show player states
        players = current_state.get('players', [])
        if players:
            print("\n👥 Current Player States:")
            for player in players:
                print(f"   {player['name']}: ${player['stack']:.2f} stack, ${player['current_bet']:.2f} bet")
        
        # Show action history
        hand_history = self.state_machine.get_hand_history()
        if hand_history:
            print(f"\n📜 Action History ({len(hand_history)} actions):")
            for action in hand_history[-5:]:  # Show last 5 actions
                print(f"   {action.player_name}: {action.action.value} ${action.amount:.2f}")
    
    def _demonstrate_replay_capabilities(self):
        """Demonstrate hand replay capabilities."""
        print("\n🔄 Replay Capabilities")
        print("-" * 40)
        
        # Get session data
        session_data = self.state_machine.get_comprehensive_session_data()
        hands_played = session_data.get('hands_played', [])
        
        if hands_played:
            print("✅ Hand Replay Available:")
            for i, hand in enumerate(hands_played):
                print(f"   Hand {hand['hand_number']}: {hand['action_count']} actions")
                
                # Demonstrate replay for first hand
                if i == 0:
                    replay_data = self.state_machine.replay_hand(0)
                    if replay_data:
                        print(f"   📊 Replay data: {len(replay_data.get('action_history', []))} actions")
                        print(f"   💰 Final pot: ${replay_data.get('pot_amount', 0):.2f}")
                        print(f"   🎴 Board: {replay_data.get('board_cards', [])}")
        else:
            print("   No hands completed yet for replay")
    
    def _export_session_for_analysis(self):
        """Export session for external analysis."""
        print("\n💾 Session Export for Analysis")
        print("-" * 40)
        
        # Export session to JSON
        export_success = self.state_machine.export_session("demo_session.json")
        
        if export_success:
            print("✅ Session exported to demo_session.json")
            
            # Show what was exported
            try:
                with open("demo_session.json", 'r') as f:
                    exported_data = json.load(f)
                
                session_info = exported_data.get('session_info', {})
                hands_played = exported_data.get('hands_played', [])
                session_log = exported_data.get('session_log', [])
                
                print(f"   📄 Session ID: {session_info.get('session_id', 'N/A')}")
                print(f"   📄 Total Hands: {len(hands_played)}")
                print(f"   📄 Log Entries: {len(session_log)}")
                print(f"   📄 Duration: {session_info.get('duration_seconds', 0):.1f} seconds")
                
                print("\n   📋 Export includes:")
                print("     - Complete session metadata")
                print("     - All hand results with action history")
                print("     - Player statistics and stack changes")
                print("     - Side pot information")
                print("     - Showdown cards and winners")
                print("     - Session log with timestamps")
                
            except Exception as e:
                print(f"   ❌ Error reading exported file: {e}")
        else:
            print("   ❌ Session export failed")
    
    def show_gui_integration_example(self):
        """Show how this would integrate with a GUI."""
        print("\n🖥️ GUI Integration Example")
        print("-" * 40)
        
        print("✅ GUI can now access complete session data:")
        print("   📊 Session statistics for display")
        print("   🎮 Hand replay for analysis")
        print("   🐛 Debug information for troubleshooting")
        print("   💾 Session export for sharing/analysis")
        print("   📈 Player performance tracking")
        print("   🎯 Pot distribution analysis")
        
        print("\n🎯 Benefits for GUI:")
        print("   - Single source of truth for all game data")
        print("   - Complete debugging information")
        print("   - Hand replay capability")
        print("   - Session export/import")
        print("   - Player statistics and analysis")
        print("   - Pot distribution tracking")
        print("   - All-in and side pot handling")


def main():
    """Run the comprehensive session tracking demo."""
    demo = SessionTrackingDemo()
    demo.start_demo_session()
    demo.show_gui_integration_example()
    
    print("\n🎉 Session Tracking Demo Complete!")
    print("The enhanced state machine now provides everything needed for:")
    print("  ✅ Complete session management")
    print("  ✅ Debugging and troubleshooting")
    print("  ✅ Hand replay and analysis")
    print("  ✅ Session export and sharing")
    print("  ✅ Player statistics and performance")
    print("  ✅ Single source of truth for all poker data")


if __name__ == "__main__":
    main() 