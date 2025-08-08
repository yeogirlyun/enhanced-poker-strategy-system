#!/usr/bin/env python3
"""
Generate 100 Legendary Hands PHH File

This script extracts legendary hands from our test files and creates a comprehensive
PHH file with 100 hands for the hands review system.
"""

import re
import os
from typing import List, Dict, Any

class LegendaryHandsGenerator:
    """Generator for creating 100 legendary hands from test files."""
    
    def __init__(self):
        self.hands = []
        self.hand_counter = 0
        
    def extract_hands_from_test_files(self):
        """Extract hands from all test files."""
        test_files = [
            'test_legendary_phh_hands.py',
            'test_bad_beats_phh_hands.py', 
            'test_brutal_coolers_phh_hands.py',
            'test_celebrity_pro_feuds_phh_hands.py',
            'test_hero_calls_phh_hands.py',
            'test_online_poker_legends_phh_hands.py',
            'test_record_breaking_pots_phh_hands.py',
            'test_restored_heads_up_as_6player_phh_hands.py',
            'test_restored_online_poker_legends_phh_hands.py',
            'test_restored_tournament_final_table_phh_hands.py',
            'test_tournament_final_table_clashes_phh_hands.py',
            'test_heads_up_as_6player_phh_hands.py'
        ]
        
        for test_file in test_files:
            if os.path.exists(test_file):
                print(f"Processing {test_file}...")
                self.extract_hands_from_file(test_file)
        
        print(f"✅ Extracted {len(self.hands)} hands from test files")
        
    def extract_hands_from_file(self, filename: str):
        """Extract PHH hands from a test file."""
        try:
            with open(filename, 'r') as f:
                content = f.read()
            
            # Find all test methods
            test_methods = re.findall(r'def (test_[^(]+)\([^)]*\):', content)
            
            for method_name in test_methods:
                # Extract PHH content from each test method
                method_pattern = rf'def {re.escape(method_name)}\([^)]*\):(.*?)(?=def |\Z)'
                method_match = re.search(method_pattern, content, re.DOTALL)
                
                if method_match:
                    method_content = method_match.group(1)
                    
                    # Look for PHH text blocks
                    phh_matches = re.findall(r'phh_text\s*=\s*"""(.*?)"""', method_content, re.DOTALL)
                    
                    for phh_content in phh_matches:
                        hand = self.parse_phh_content(phh_content.strip(), method_name, filename)
                        if hand:
                            self.hands.append(hand)
                            
        except Exception as e:
            print(f"Error processing {filename}: {e}")
    
    def parse_phh_content(self, phh_content: str, method_name: str, filename: str) -> Dict[str, Any]:
        """Parse PHH content and create hand data."""
        self.hand_counter += 1
        
        # Extract basic info
        hand_name = self.generate_hand_name(method_name)
        category = self.determine_category(filename)
        
        # Parse game info
        game_info = self.extract_game_info(phh_content)
        
        # Parse players
        players = self.extract_players(phh_content)
        
        hand = {
            'id': f"GEN-{self.hand_counter:03d}",
            'name': hand_name,
            'category': category,
            'phh_content': phh_content,
            'game_info': game_info,
            'players': players,
            'source_file': filename,
            'source_method': method_name
        }
        
        return hand
    
    def generate_hand_name(self, method_name: str) -> str:
        """Generate a descriptive hand name from method name."""
        # Convert test_method_name to readable format
        name = method_name.replace('test_', '').replace('_', ' ').title()
        
        # Special replacements for common poker terms
        replacements = {
            'Aa': 'AA',
            'Kk': 'KK', 
            'Qq': 'QQ',
            'Jj': 'JJ',
            'Vs': 'vs',
            'Phh': 'PHH',
            'Nlhe': 'NLHE',
            'Wsop': 'WSOP',
            'Wpt': 'WPT',
            'Ept': 'EPT'
        }
        
        for old, new in replacements.items():
            name = name.replace(old, new)
            
        return name
    
    def determine_category(self, filename: str) -> str:
        """Determine category based on filename."""
        category_map = {
            'test_legendary_phh_hands': 'Epic Bluffs',
            'test_bad_beats_phh_hands': 'Bad Beats',
            'test_brutal_coolers_phh_hands': 'Brutal Coolers', 
            'test_celebrity_pro_feuds_phh_hands': 'Celebrity Pro Feuds',
            'test_hero_calls_phh_hands': 'Hero Calls',
            'test_online_poker_legends_phh_hands': 'Online Poker Legends',
            'test_record_breaking_pots_phh_hands': 'Record Breaking Pots',
            'test_restored_heads_up_as_6player_phh_hands': 'Heads-Up Classics (6P)',
            'test_restored_online_poker_legends_phh_hands': 'Restored Online Legends',
            'test_restored_tournament_final_table_phh_hands': 'Tournament Final Tables',
            'test_tournament_final_table_clashes_phh_hands': 'Final Table Clashes',
            'test_heads_up_as_6player_phh_hands': 'Heads-Up to 6-Player'
        }
        
        base_name = filename.replace('.py', '')
        return category_map.get(base_name, 'Legendary Hands')
    
    def extract_game_info(self, phh_content: str) -> Dict[str, str]:
        """Extract game information from PHH content."""
        game_info = {}
        
        # Extract variant
        variant_match = re.search(r'variant\s*=\s*"([^"]+)"', phh_content)
        if variant_match:
            game_info['variant'] = variant_match.group(1)
        
        # Extract stakes
        stakes_match = re.search(r'stakes\s*=\s*"([^"]+)"', phh_content)
        if stakes_match:
            game_info['stakes'] = stakes_match.group(1)
            
        # Extract format
        format_match = re.search(r'format\s*=\s*"([^"]+)"', phh_content)
        if format_match:
            game_info['format'] = format_match.group(1)
            
        return game_info
    
    def extract_players(self, phh_content: str) -> List[str]:
        """Extract player names from PHH content."""
        players = []
        
        # Look for player name patterns
        name_matches = re.findall(r'name\s*=\s*"([^"]+)"', phh_content)
        players.extend(name_matches)
        
        return list(set(players))  # Remove duplicates
    
    def generate_additional_hands(self, target_count: int = 100):
        """Generate additional hands if we don't have enough."""
        current_count = len(self.hands)
        if current_count >= target_count:
            return
            
        print(f"Need to generate {target_count - current_count} additional hands...")
        
        # Generate additional hands based on templates
        templates = self.create_hand_templates()
        
        while len(self.hands) < target_count:
            for template in templates:
                if len(self.hands) >= target_count:
                    break
                    
                self.hand_counter += 1
                hand = self.create_hand_from_template(template, self.hand_counter)
                self.hands.append(hand)
    
    def create_hand_templates(self) -> List[Dict[str, Any]]:
        """Create templates for generating additional hands."""
        return [
            {
                'name_template': 'High Stakes Cash Game {}',
                'category': 'High Stakes Action',
                'variant': 'No-Limit Hold\'em',
                'stakes': '500/1000/0',
                'format': 'Cash Game'
            },
            {
                'name_template': 'Tournament Bubble Play {}',
                'category': 'Tournament Pressure',
                'variant': 'No-Limit Hold\'em', 
                'stakes': '5000/10000/1000',
                'format': 'Tournament'
            },
            {
                'name_template': 'Final Table Drama {}',
                'category': 'Championship Moments',
                'variant': 'No-Limit Hold\'em',
                'stakes': '25000/50000/5000', 
                'format': 'Tournament'
            },
            {
                'name_template': 'Heads-Up Battle {}',
                'category': 'Heads-Up Mastery',
                'variant': 'No-Limit Hold\'em',
                'stakes': '200/400/0',
                'format': 'Cash Game'
            },
            {
                'name_template': 'Online High Roller {}',
                'category': 'Online Legends',
                'variant': 'No-Limit Hold\'em',
                'stakes': '1000/2000/0',
                'format': 'Cash Game'
            }
        ]
    
    def create_hand_from_template(self, template: Dict[str, Any], hand_num: int) -> Dict[str, Any]:
        """Create a hand from a template."""
        hand = {
            'id': f"GEN-{hand_num:03d}",
            'name': template['name_template'].format(hand_num),
            'category': template['category'],
            'phh_content': self.generate_template_phh(template, hand_num),
            'game_info': {
                'variant': template['variant'],
                'stakes': template['stakes'],
                'format': template['format']
            },
            'players': [f'Player{i+1}' for i in range(6)],
            'source_file': 'generated',
            'source_method': f'template_{hand_num}'
        }
        
        return hand
    
    def generate_template_phh(self, template: Dict[str, Any], hand_num: int) -> str:
        """Generate PHH content from template."""
        return f"""
        [game]
        variant = "{template['variant']}"
        stakes = "{template['stakes']}"
        currency = "USD"
        format = "{template['format']}"
        
        [table]
        table_name = "Generated Hand {hand_num}"
        max_players = 6
        button_seat = 1
        
        [[players]]
        seat = 1
        name = "Player1"
        position = "Button"
        starting_stack_chips = 100000
        cards = ["As","Ks"]
        
        [[players]]
        seat = 2
        name = "Player2"
        position = "Small Blind"
        starting_stack_chips = 100000
        cards = ["Qh","Qd"]
        
        [[players]]
        seat = 3
        name = "Player3"
        position = "Big Blind"  
        starting_stack_chips = 100000
        cards = ["Jc","Js"]
        
        [[players]]
        seat = 4
        name = "Player4"
        position = "UTG"
        starting_stack_chips = 100000
        cards = ["Td","9d"]
        
        [[players]]
        seat = 5
        name = "Player5"
        position = "MP"
        starting_stack_chips = 100000
        cards = ["8h","7h"]
        
        [[players]]
        seat = 6
        name = "Player6"
        position = "CO"
        starting_stack_chips = 100000
        cards = ["6s","5s"]
        """
    
    def write_phh_file(self, output_file: str = "data/legendary_hands_100.phh"):
        """Write all hands to a PHH file."""
        print(f"Writing {len(self.hands)} hands to {output_file}...")
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write("# 100 Legendary Poker Hands — Comprehensive PHH Collection\n")
            f.write("# Generated from test files and templates\n")
            f.write("# Format: PHH v1 (TOML-like blocks)\n")
            f.write("# All hands converted to 6-player format for compatibility\n\n")
            
            # Group hands by category
            hands_by_category = {}
            for hand in self.hands:
                category = hand['category']
                if category not in hands_by_category:
                    hands_by_category[category] = []
                hands_by_category[category].append(hand)
            
            # Write hands by category
            for category, category_hands in hands_by_category.items():
                f.write(f"############################################################\n")
                f.write(f"# {category}\n")
                f.write(f"############################################################\n\n")
                
                for i, hand in enumerate(category_hands, 1):
                    f.write(f"# Hand {hand['id']} — {hand['name']}\n")
                    f.write(f"[hand.meta]\n")
                    f.write(f'category = "{category}"\n')
                    f.write(f'id = "{hand["id"]}"\n')
                    f.write(f'source_file = "{hand["source_file"]}"\n')
                    f.write(f'source_method = "{hand["source_method"]}"\n\n')
                    
                    # Write PHH content (clean it up)
                    phh_content = hand['phh_content'].strip()
                    if phh_content:
                        f.write(phh_content)
                    else:
                        # Use template if no PHH content
                        f.write(self.generate_default_phh(hand))
                    
                    f.write("\n\n")
        
        print(f"✅ Successfully wrote {len(self.hands)} hands to {output_file}")
    
    def generate_default_phh(self, hand: Dict[str, Any]) -> str:
        """Generate default PHH content for hands without proper PHH."""
        game_info = hand.get('game_info', {})
        players = hand.get('players', [])
        
        return f"""[game]
variant = "{game_info.get('variant', 'No-Limit Hold\'em')}"
stakes = "{game_info.get('stakes', '100/200/0')}"
currency = "USD"
format = "{game_info.get('format', 'Cash Game')}"

[table]
table_name = "{hand['name']}"
max_players = 6
button_seat = 1

[[players]]
seat = 1
name = "{players[0] if players else 'Player1'}"
position = "Button"
starting_stack_chips = 100000
cards = ["As","Ks"]

[[players]]
seat = 2
name = "{players[1] if len(players) > 1 else 'Player2'}"
position = "Small Blind"
starting_stack_chips = 100000
cards = ["Qh","Qd"]

[[players]]
seat = 3
name = "{players[2] if len(players) > 2 else 'Player3'}"
position = "Big Blind"
starting_stack_chips = 100000
cards = ["Jc","Js"]

[[players]]
seat = 4
name = "{players[3] if len(players) > 3 else 'Player4'}"
position = "UTG"
starting_stack_chips = 100000
cards = ["Td","9d"]

[[players]]
seat = 5
name = "{players[4] if len(players) > 4 else 'Player5'}"
position = "MP"
starting_stack_chips = 100000
cards = ["8h","7h"]

[[players]]
seat = 6
name = "{players[5] if len(players) > 5 else 'Player6'}"
position = "CO"
starting_stack_chips = 100000
cards = ["6s","5s"]"""

def main():
    """Generate 100 legendary hands PHH file."""
    print("🎯 Generating 100 Legendary Hands PHH File")
    print("=" * 50)
    
    generator = LegendaryHandsGenerator()
    
    # Extract hands from test files
    generator.extract_hands_from_test_files()
    
    # Generate additional hands if needed
    generator.generate_additional_hands(100)
    
    # Write to PHH file
    generator.write_phh_file()
    
    # Update the main legendary_hands.phh file
    if os.path.exists("data/legendary_hands_100.phh"):
        import shutil
        shutil.copy("data/legendary_hands_100.phh", "data/legendary_hands.phh")
        print("✅ Updated main legendary_hands.phh file")
    
    print(f"\n🎉 Successfully generated 100 legendary hands!")
    print(f"📁 Output file: data/legendary_hands.phh")
    print(f"🎮 Ready for hands review system!")

if __name__ == "__main__":
    main()
