#!/usr/bin/env python3
"""
Clean up legendary hands to exactly 120 hands:
- 100 main legendary hands (GEN-001 to GEN-098 from existing file)
- 10 heads-up hands (HU-001 to HU-010)
- 10 YouTube popular hands (YT-HS-001 to YT-HS-010)
"""

import sys
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.hands_database import LegendaryHandsPHHLoader


def extract_clean_main_hands():
    """Extract exactly 100 GEN hands from the corrupted main file."""
    print("🧹 Cleaning main legendary hands file...")
    
    # Load the current corrupted file
    loader = LegendaryHandsPHHLoader('data/legendary_hands.phh')
    hands = loader.load_hands()
    
    # Filter to GEN hands only and take first 100
    gen_hands = [h for h in hands if getattr(h.metadata, 'id', '').startswith('GEN-')]
    first_100_gen = gen_hands[:100]
    
    print(f"📋 Selected {len(first_100_gen)} GEN hands")
    print(f"   Range: {getattr(first_100_gen[0].metadata, 'id', 'Unknown')} to {getattr(first_100_gen[-1].metadata, 'id', 'Unknown')}")
    
    # Read the original file and extract only the GEN hand sections
    with open('data/legendary_hands.phh', 'r') as f:
        content = f.read()
    
    # Find all GEN hand sections
    lines = content.split('\n')
    gen_sections = []
    current_section = []
    in_gen_hand = False
    gen_count = 0
    
    for line in lines:
        stripped = line.strip()
        
        # Check if this is the start of a GEN hand
        if stripped.startswith('# Hand GEN-'):
            # Save previous section if we were in a GEN hand
            if in_gen_hand and current_section and gen_count < 100:
                gen_sections.append('\n'.join(current_section))
                gen_count += 1
            
            # Start new section if we haven't reached 100 yet
            if gen_count < 100:
                current_section = [line]
                in_gen_hand = True
            else:
                in_gen_hand = False
                current_section = []
                
        elif in_gen_hand:
            current_section.append(line)
            
        # Check for next hand starting (to close current section)
        elif stripped.startswith('# Hand ') and in_gen_hand:
            if current_section and gen_count < 100:
                gen_sections.append('\n'.join(current_section))
                gen_count += 1
            in_gen_hand = False
            current_section = []
    
    # Add the last section if needed
    if in_gen_hand and current_section and gen_count < 100:
        gen_sections.append('\n'.join(current_section))
        gen_count += 1
    
    print(f"📝 Extracted {len(gen_sections)} complete hand sections")
    
    # Create the clean file
    header = """# Legendary Poker Hands Database
# 100 carefully curated legendary poker hands across multiple categories
# Format: PHH v1 (Poker Hand History)

############################################################
# 100 Main Legendary Hands (10 categories × 10 hands each)
############################################################

"""
    
    clean_content = header + '\n\n'.join(gen_sections)
    
    # Save to a backup first
    with open('data/legendary_hands_backup.phh', 'w') as f:
        f.write(content)
    print("💾 Created backup of original file")
    
    # Write the clean file
    with open('data/legendary_hands.phh', 'w') as f:
        f.write(clean_content)
    
    print(f"✅ Created clean main file with {len(gen_sections)} hands")
    return len(gen_sections)


def verify_final_count():
    """Verify we have exactly 120 hands total."""
    print("\n🎯 Final verification...")
    
    files = [
        ('Main Legendary', 'data/legendary_hands.phh'),
        ('Heads-Up', 'data/legendary_heads_up_hands.phh'),
        ('YouTube Popular', 'data/legendary_youtube_popular_hands.phh')
    ]
    
    total = 0
    for name, path in files:
        if Path(path).exists():
            loader = LegendaryHandsPHHLoader(path)
            hands = loader.load_hands()
            count = len(hands)
            total += count
            print(f"   📋 {name}: {count} hands")
        else:
            print(f"   ❌ {name}: File not found")
    
    print(f"\n🏆 TOTAL: {total} hands")
    print(f"🎯 TARGET: 120 hands")
    
    if total == 120:
        print("✅ PERFECT! Exactly 120 legendary hands")
        return True
    else:
        print(f"❌ Wrong count: {total}")
        return False


def main():
    """Clean up and verify legendary hands."""
    print("🚀 LEGENDARY HANDS CLEANUP")
    print("=" * 40)
    
    # Clean main file
    main_count = extract_clean_main_hands()
    
    # Verify total
    success = verify_final_count()
    
    if success:
        print("\n🎉 CLEANUP SUCCESSFUL!")
        print("Ready for comprehensive RPGW validation with exactly 120 hands")
    else:
        print("\n⚠️  Cleanup needs adjustment")
    
    return success


if __name__ == "__main__":
    main()
