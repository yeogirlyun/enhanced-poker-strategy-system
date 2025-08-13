#!/usr/bin/env python3
"""
Analyze all 130 hands to ensure proper format and sequences for FPSM natural 
progression.
"""

import json
import sys
from typing import Dict, Any


def analyze_hand_structure(hand: Dict[str, Any], hand_index: int) -> Dict[str, Any]:
    """Analyze a single hand's structure and identify issues."""
    hand_id = hand.get('id', f'Unknown-{hand_index}')
    name = hand.get('name', 'Unnamed')
    
    # Get actions structure
    actions = hand.get('actions', {})
    
    # Count actions per street
    street_counts = {}
    total_actions = 0
    for street in ['preflop', 'flop', 'turn', 'river']:
        street_actions = actions.get(street, [])
        if isinstance(street_actions, list):
            count = len(street_actions)
            street_counts[street] = count
            total_actions += count
        else:
            street_counts[street] = 0
    
    # Check for structural issues
    issues = []
    
    # Issue 1: Missing actions dictionary
    if not actions:
        issues.append("Missing actions dictionary")
    
    # Issue 2: Empty streets (no actions)
    for street, count in street_counts.items():
        if count == 0:
            issues.append(f"Empty {street} street")
    
            # Issue 3: Streets with actions but no board progression
        board = hand.get('board', {})
        if (street_counts.get('flop', 0) > 0 and 
                not board.get('flop')):
            issues.append("Flop actions but no flop board cards")
        if (street_counts.get('turn', 0) > 0 and 
                not board.get('turn')):
            issues.append("Turn actions but no turn board card")
        if (street_counts.get('river', 0) > 0 and 
                not board.get('river')):
            issues.append("River actions but no river board card")
    
    # Issue 4: Actions without proper player references
    for street, count in street_counts.items():
        if count > 0:
            street_actions = actions.get(street, [])
            for i, action in enumerate(street_actions):
                if not isinstance(action, dict):
                    issues.append(f"Invalid action format in {street}[{i}]")
                    continue
                
                required_keys = ['actor', 'player_name', 'action_type']
                missing_keys = [key for key in required_keys if key not in action]
                if missing_keys:
                    issues.append(f"Missing keys in {street}[{i}]: {missing_keys}")
    
    return {
        'hand_id': hand_id,
        'name': name,
        'street_counts': street_counts,
        'total_actions': total_actions,
        'issues': issues,
        'has_issues': len(issues) > 0
    }

def main():
    """Main analysis function."""
    try:
        # Load hands data
        with open('data/legendary_hands_complete_130_repaired.json', 'r') as f:
            data = json.load(f)
        
        hands = data.get('hands', [])
        print(f"🔍 Analyzing {len(hands)} hands for structural integrity...")
        print("=" * 80)
        
        # Analyze each hand
        analysis_results = []
        total_issues = 0
        
        for i, hand in enumerate(hands):
            result = analyze_hand_structure(hand, i)
            analysis_results.append(result)
            
            if result['has_issues']:
                total_issues += len(result['issues'])
                print(f"❌ Hand {i+1:3d}: {result['hand_id']} - {len(result['issues'])} issues")
                for issue in result['issues']:
                    print(f"    • {issue}")
            else:
                print(f"✅ Hand {i+1:3d}: {result['hand_id']} - Clean")
        
        # Summary statistics
        print("=" * 80)
        print("📊 ANALYSIS SUMMARY")
        print("=" * 80)
        
        clean_hands = sum(1 for r in analysis_results if not r['has_issues'])
        problematic_hands = len(hands) - clean_hands
        
        print(f"Total hands analyzed: {len(hands)}")
        print(f"Clean hands: {clean_hands}")
        print(f"Problematic hands: {problematic_hands}")
        print(f"Total issues found: {total_issues}")
        
        # Street distribution analysis
        print("\n🎯 STREET DISTRIBUTION:")
        street_totals = {'preflop': 0, 'flop': 0, 'turn': 0, 'river': 0}
        for result in analysis_results:
            for street, count in result['street_counts'].items():
                street_totals[street] += count
        
        for street, total in street_totals.items():
            print(f"  {street.capitalize()}: {total} actions")
        
        # Action count distribution
        print("\n📈 ACTION COUNT DISTRIBUTION:")
        action_counts = [r['total_actions'] for r in analysis_results]
        if action_counts:
            print(f"  Min actions: {min(action_counts)}")
            print(f"  Max actions: {max(action_counts)}")
            print(f"  Average actions: {sum(action_counts) / len(action_counts):.1f}")
        
        # Detailed issue breakdown
        if total_issues > 0:
            print("\n🚨 ISSUE BREAKDOWN:")
            issue_types = {}
            for result in analysis_results:
                for issue in result['issues']:
                    issue_types[issue] = issue_types.get(issue, 0) + 1
            
            for issue, count in sorted(issue_types.items(), key=lambda x: x[1], reverse=True):
                print(f"  {issue}: {count} occurrences")
        
        print("\n" + "=" * 80)
        
        if total_issues == 0:
            print("🎉 All hands are properly formatted and ready for FPSM natural progression!")
        else:
            print(f"⚠️  {total_issues} issues found. Hands need fixing before FPSM can progress naturally.")
        
        return total_issues == 0
        
    except Exception as e:
        print(f"❌ Error analyzing hands: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
