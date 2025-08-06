#!/usr/bin/env python3
"""
Comprehensive Poker Sound Testing Script

Tests all sounds used in the poker strategy app with interactive prompts.
Shows where each sound is used and allows selective testing.
"""

import time
from enhanced_sound_manager import sound_manager

class PokerSoundTester:
    """Interactive tester for all poker app sounds."""
    
    def __init__(self):
        self.sound_manager = sound_manager
        self.sound_scenarios = self._create_sound_scenarios()
        self.sound_list = self._create_sound_list()
    
    def _create_sound_scenarios(self):
        """Define all sound scenarios used in the poker app."""
        return {
            # Card Actions
            'card_deal': {
                'description': 'Card dealing sound',
                'scenario': 'When cards are dealt to players',
                'trigger': 'Dealing hole cards or community cards'
            },
            'card_shuffle': {
                'description': 'Card shuffling sound',
                'scenario': 'When deck is shuffled',
                'trigger': 'Start of new hand, deck reshuffle'
            },
            'card_fold': {
                'description': 'Card folding sound',
                'scenario': 'When player folds their cards',
                'trigger': 'Player clicks fold button'
            },
            
            # Chip Actions
            'chip_bet': {
                'description': 'Chip betting sound',
                'scenario': 'When chips are placed for betting',
                'trigger': 'Player makes a bet or raise'
            },
            'chip_collect': {
                'description': 'Chip collecting sound',
                'scenario': 'When chips are collected',
                'trigger': 'Collecting chips from pot'
            },
            'chip_stack': {
                'description': 'Chip stacking sound',
                'scenario': 'When chips are stacked',
                'trigger': 'Stacking chips in player stacks'
            },
            
            # Player Actions
            'player_bet': {
                'description': 'Player betting sound',
                'scenario': 'When player makes a bet',
                'trigger': 'Player action: bet'
            },
            'player_call': {
                'description': 'Player calling sound',
                'scenario': 'When player calls',
                'trigger': 'Player action: call'
            },
            'player_raise': {
                'description': 'Player raising sound',
                'scenario': 'When player raises',
                'trigger': 'Player action: raise'
            },
            'player_check': {
                'description': 'Player checking sound',
                'scenario': 'When player checks',
                'trigger': 'Player action: check'
            },
            'player_fold': {
                'description': 'Player folding sound',
                'scenario': 'When player folds',
                'trigger': 'Player action: fold'
            },
            'player_all_in': {
                'description': 'All-in dramatic sound',
                'scenario': 'When player goes all-in',
                'trigger': 'Player action: all-in'
            },
            
            # Pot Actions
            'pot_win': {
                'description': 'Pot winning sound',
                'scenario': 'When pot is won',
                'trigger': 'Winner collects pot'
            },
            'pot_split': {
                'description': 'Pot splitting sound',
                'scenario': 'When pot is split',
                'trigger': 'Split pot situation'
            },
            'pot_rake': {
                'description': 'Pot rake sound',
                'scenario': 'When rake is taken',
                'trigger': 'House rake collection'
            },
            
            # Winner Actions
            'winner_announce': {
                'description': 'Winner announcement sound',
                'scenario': 'When winner is announced',
                'trigger': 'Showdown winner announcement'
            },
            
            # UI Actions
            'button_click': {
                'description': 'Button click sound',
                'scenario': 'When UI buttons are clicked',
                'trigger': 'Any button interaction'
            },
            'button_hover': {
                'description': 'Button hover sound',
                'scenario': 'When hovering over buttons',
                'trigger': 'Mouse hover over buttons'
            },
            'button_move': {
                'description': 'Button move sound',
                'scenario': 'When buttons move/change',
                'trigger': 'Button state changes'
            },
            'turn_notify': {
                'description': 'Turn notification sound',
                'scenario': 'When turn changes',
                'trigger': 'Turn indicator changes'
            },
            'notification': {
                'description': 'General notification sound',
                'scenario': 'General app notifications',
                'trigger': 'System notifications'
            },
            
            # System Actions
            'success': {
                'description': 'Success sound',
                'scenario': 'When action succeeds',
                'trigger': 'Successful operations'
            },
            'error': {
                'description': 'Error sound',
                'scenario': 'When errors occur',
                'trigger': 'Error conditions'
            },
            'menu_open': {
                'description': 'Menu open sound',
                'scenario': 'When menus open',
                'trigger': 'Opening menus/panels'
            }
        }
    
    def _create_sound_list(self):
        """Create numbered list of all sounds."""
        sounds = []
        for i, (sound_name, scenario) in enumerate(self.sound_scenarios.items(), 1):
            sounds.append({
                'number': i,
                'name': sound_name,
                'description': scenario['description'],
                'scenario': scenario['scenario'],
                'trigger': scenario['trigger']
            })
        return sounds
    
    def print_sound_menu(self):
        """Print the complete sound menu."""
        print("\n🎵 POKER SOUND TESTING MENU")
        print("=" * 60)
        print("All sounds used in the poker strategy app:")
        print()
        
        for sound in self.sound_list:
            print(f"{sound['number']:2d}. {sound['name']:20s} - {sound['description']}")
            print(f"    Scenario: {sound['scenario']}")
            print(f"    Trigger:  {sound['trigger']}")
            print()
    
    def test_sound_by_number(self, number):
        """Test a specific sound by its number."""
        if 1 <= number <= len(self.sound_list):
            sound = self.sound_list[number - 1]
            print(f"\n🎵 Testing Sound #{number}: {sound['name']}")
            print(f"Description: {sound['description']}")
            print(f"Scenario: {sound['scenario']}")
            print(f"Trigger: {sound['trigger']}")
            
            response = input("Play this sound? (y/n/skip): ").lower().strip()
            
            if response in ['y', 'yes']:
                print(f"🔊 Playing {sound['name']}...")
                try:
                    self.sound_manager.play(sound['name'])
                    print("✅ Sound played successfully!")
                except Exception as e:
                    print(f"❌ Error playing sound: {e}")
            elif response in ['s', 'skip']:
                print("⏭️  Skipping this sound...")
            else:
                print("⏭️  Skipping this sound...")
            
            return True
        else:
            print(f"❌ Invalid sound number: {number}")
            return False
    
    def test_all_sounds(self):
        """Test all sounds with prompts."""
        print("\n🎵 TESTING ALL POKER SOUNDS")
        print("=" * 60)
        print("This will test each sound with a prompt.")
        print("Type 'y' to play, 'n' to skip, 's' to skip, or 'q' to quit.")
        print()
        
        for sound in self.sound_list:
            print(f"\n🎵 Sound #{sound['number']}: {sound['name']}")
            print(f"Description: {sound['description']}")
            print(f"Scenario: {sound['scenario']}")
            print(f"Trigger: {sound['trigger']}")
            
            response = input("Play this sound? (y/n/skip/q): ").lower().strip()
            
            if response in ['q', 'quit']:
                print("👋 Quitting sound testing...")
                break
            elif response in ['y', 'yes']:
                print(f"🔊 Playing {sound['name']}...")
                try:
                    self.sound_manager.play(sound['name'])
                    print("✅ Sound played successfully!")
                    time.sleep(0.5)  # Brief pause between sounds
                except Exception as e:
                    print(f"❌ Error playing sound: {e}")
            elif response in ['s', 'skip']:
                print("⏭️  Skipping...")
            else:
                print("⏭️  Skipping...")
    
    def test_specific_sounds(self):
        """Test specific sounds by number selection."""
        print("\n🎵 SELECTIVE SOUND TESTING")
        print("=" * 60)
        print("Enter sound numbers separated by commas (e.g., 1,3,5)")
        print("Or enter 'all' to test all sounds")
        print("Or enter 'q' to quit")
        print()
        
        while True:
            selection = input("Enter sound numbers: ").strip()
            
            if selection.lower() in ['q', 'quit']:
                print("👋 Quitting...")
                break
            elif selection.lower() == 'all':
                self.test_all_sounds()
                break
            else:
                try:
                    numbers = [int(n.strip()) for n in selection.split(',')]
                    for number in numbers:
                        self.test_sound_by_number(number)
                        time.sleep(0.3)  # Brief pause between sounds
                except ValueError:
                    print("❌ Invalid input. Please enter numbers separated by commas.")
    
    def print_sound_quality_report(self):
        """Print a quality report of all sounds."""
        print("\n📊 SOUND QUALITY REPORT")
        print("=" * 50)
        
        high_quality = []
        medium_quality = []
        low_quality = []
        missing_sounds = []
        
        for sound in self.sound_list:
            sound_name = sound['name']
            try:
                # Check if sound exists in sound manager
                if hasattr(self.sound_manager, 'sound_configs'):
                    if sound_name in self.sound_manager.sound_configs:
                        config = self.sound_manager.sound_configs[sound_name]
                        file_name = config.name
                        
                        # Assess quality based on file type and size
                        if 'mp3' in file_name.lower():
                            if '87543' in file_name or '86984' in file_name:
                                high_quality.append((sound_name, file_name))
                            else:
                                medium_quality.append((sound_name, file_name))
                        else:
                            low_quality.append((sound_name, file_name))
                    else:
                        missing_sounds.append(sound_name)
                else:
                    missing_sounds.append(sound_name)
            except Exception:
                missing_sounds.append(sound_name)
        
        print(f"🎯 HIGH QUALITY ({len(high_quality)}):")
        for sound_name, file_name in high_quality:
            print(f"  • {sound_name}: {file_name}")
        
        print(f"\n🎯 MEDIUM QUALITY ({len(medium_quality)}):")
        for sound_name, file_name in medium_quality:
            print(f"  • {sound_name}: {file_name}")
        
        print(f"\n🎯 LOW QUALITY ({len(low_quality)}):")
        for sound_name, file_name in low_quality:
            print(f"  • {sound_name}: {file_name}")
        
        if missing_sounds:
            print(f"\n❌ MISSING SOUNDS ({len(missing_sounds)}):")
            for sound_name in missing_sounds:
                print(f"  • {sound_name}")
        
        print(f"\n📈 SUMMARY:")
        print(f"  • Total sounds: {len(self.sound_list)}")
        print(f"  • High quality: {len(high_quality)}")
        print(f"  • Medium quality: {len(medium_quality)}")
        print(f"  • Low quality: {len(low_quality)}")
        print(f"  • Missing: {len(missing_sounds)}")
    
    def run_interactive_menu(self):
        """Run the main interactive menu."""
        while True:
            print("\n🎵 POKER SOUND TESTER")
            print("=" * 40)
            print("1. Show all sounds (numbered list)")
            print("2. Test all sounds with prompts")
            print("3. Test specific sounds by number")
            print("4. Print sound quality report")
            print("5. Quit")
            print()
            
            choice = input("Enter your choice (1-5): ").strip()
            
            if choice == '1':
                self.print_sound_menu()
            elif choice == '2':
                self.test_all_sounds()
            elif choice == '3':
                self.test_specific_sounds()
            elif choice == '4':
                self.print_sound_quality_report()
            elif choice == '5':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-5.")

def main():
    """Main function to run the sound tester."""
    print("🎵 POKER SOUND TESTING SYSTEM")
    print("=" * 50)
    print("This script will help you test all sounds used in the poker app.")
    print("You can identify which sounds need improvement.")
    print()
    
    tester = PokerSoundTester()
    tester.run_interactive_menu()

if __name__ == "__main__":
    main() 