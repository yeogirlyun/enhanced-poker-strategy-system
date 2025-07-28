# filename: strategy_guide_generator.py
"""
Strategy Guide Generator for the Advanced Hold'em Trainer

REVISION HISTORY:
================
Version 1.0 (2025-07-28) - Initial Version
- Created `strategy_guide_generator.py` by refactoring `json_to_markdown.py`.
- The script reads a strategy.json file and produces a human-readable
  strategy guide in both Markdown (.md) and PDF (.pdf) formats.
- FEATURES:
  - Accepts a strategy filename as a command-line argument.
  - Dynamically names output files based on the input strategy.
  - Formats preflop hands into a memorable 5-tier system.
  - Sub-categorizes Tier 5 (Bronze) hands for easier learning.
  - Generates a landscape-oriented PDF to fit wide tables.
  - Uses the WeasyPrint library for high-quality PDF rendering.
"""
import json
import os
import sys

try:
    import markdown
    from weasyprint import HTML, CSS
    PDF_ENABLED = True
except ImportError:
    PDF_ENABLED = False

def load_strategy(filename='strategy.json'):
    """Loads the strategy from the JSON file."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: '{filename}' not found. Please create it first with the strategy_manager.")
        return None

def get_tier_from_hs(hs_value, is_range=False):
    """Helper function to convert an HS value or range to a Tier description."""
    if isinstance(hs_value, list):
        lower_bound = hs_value[0]
        if lower_bound >= 40: return "Tier 1"
        if lower_bound >= 30: return "Tier 2"
        if lower_bound >= 20: return "Tier 3"
        if lower_bound >= 10: return "Tier 4"
        return "Tier 5"
    else:
        if hs_value >= 40: return "Tier 1+"
        if hs_value >= 30: return "Tier 2+"
        if hs_value >= 20: return "Tier 3+"
        if hs_value >= 10: return "Tier 4+"
        return "Tier 5+"

def format_preflop_hs(hs_table):
    """Formats the preflop HS table into the new 5-tier system."""
    tiers = {
        "Tier 1 (Elite): HS 40+": [], "Tier 2 (Premium): HS 30-39": [],
        "Tier 3 (Gold): HS 20-29": [], "Tier 4 (Silver): HS 10-19": [],
        "Tier 5 (Bronze): HS 1-9": []
    }
    for hand, hs in sorted(hs_table.items(), key=lambda item: item[1], reverse=True):
        if hs >= 40: tiers["Tier 1 (Elite): HS 40+"].append(f"{hand} ({hs})")
        elif hs >= 30: tiers["Tier 2 (Premium): HS 30-39"].append(f"{hand} ({hs})")
        elif hs >= 20: tiers["Tier 3 (Gold): HS 20-29"].append(f"{hand} ({hs})")
        elif hs >= 10: tiers["Tier 4 (Silver): HS 10-19"].append(f"{hand} ({hs})")
        elif hs > 0: tiers["Tier 5 (Bronze): HS 1-9"].append(f"{hand} ({hs})")

    md = "## Preflop Hand Strength (HS) - Tiers\n\n"
    for tier_name, hands_with_hs in tiers.items():
        if not hands_with_hs: continue
        md += f"### {tier_name}\n"
        if "Bronze" in tier_name:
            bronze_sub_categories = {"Small Pocket Pairs": [], "Suited Connectors": [], "Other Suited Hands": [], "Offsuit Hands": []}
            ranks, rank_values = '23456789TJQKA', {r: i for i, r in enumerate('23456789TJQKA')}
            for hand_str in hands_with_hs:
                hand = hand_str.split(" ")[0]
                if len(hand) == 2 and hand[0] == hand[1]: bronze_sub_categories["Small Pocket Pairs"].append(hand_str)
                elif hand.endswith('s'):
                    if abs(rank_values[hand[0]] - rank_values[hand[1]]) == 1: bronze_sub_categories["Suited Connectors"].append(hand_str)
                    else: bronze_sub_categories["Other Suited Hands"].append(hand_str)
                elif hand.endswith('o'): bronze_sub_categories["Offsuit Hands"].append(hand_str)
            for sub_cat_name, sub_cat_hands in bronze_sub_categories.items():
                if sub_cat_hands:
                    md += f"&nbsp;&nbsp;&nbsp;&nbsp;**{sub_cat_name}:** " + ", ".join(sub_cat_hands) + "\n"
            md += "\n"
        else:
            md += "- " + ", ".join(hands_with_hs) + "\n\n"
    return md

def format_postflop_hs(hs_table):
    md = "## Postflop Hand Strength (HS)\n\n| Hand Rank | HS Value |\n|---|---|\n"
    for rank, hs in sorted(hs_table.items(), key=lambda item: item[1], reverse=True):
        md += f"| {rank.replace('_', ' ').title()} | {hs} |\n"
    return md + "\n"

def format_open_rules(rules):
    md = "## Preflop: Open Rule Table\n\n| Position | Open Threshold (HS) | Hand Tiers | Sizing (BB) |\n|---|---|---|---|\n"
    for pos, rule in rules.items():
        md += f"| {pos} | >= {rule['threshold']} | **{get_tier_from_hs(rule['threshold'])}** | {rule['sizing']:.1f}x |\n"
    return md + "\n"

def format_vs_raise(rules):
    md = "## Preflop: Facing a Raise (3-Bet Table)\n\n| Position | IP/OOP | Value 3-Bet (HS) | Call Range (HS) | Hand Tiers (Call) | Sizing |\n|---|---|---|---|---|---|\n"
    for pos, pos_rules in rules.items():
        for ip_oop, rule in pos_rules.items():
            md += f"| {pos} | {ip_oop} | >= {rule['value_thresh']} ({get_tier_from_hs(rule['value_thresh'])}) | {rule['call_range'][0]}-{rule['call_range'][1]} | **{get_tier_from_hs(rule['call_range'])} Hands** | {rule['sizing']:.1f}x |\n"
    return md + "\n"

def format_pfa(rules):
    md = "## Postflop: As Pre-Flop Aggressor (PFA)\n\n"
    for street, street_rules in rules.items():
        md += f"### {street.title()} - PFA Rule Table\n\n| Position | IP/OOP | Value Bet (HS) | Check (HS) |\n|---|---|---|---|\n"
        for pos, pos_rules in street_rules.items():
            for ip_oop, rule in pos_rules.items():
                md += f"| {pos} | {ip_oop} | >= {rule['val_thresh']} | >= {rule['check_thresh']} |\n"
        md += "\n"
    return md

def format_caller(rules):
    md = "## Postflop: As Caller (Facing a Bet)\n\n"
    for street, street_rules in rules.items():
        md += f"### {street.title()} - Facing Bet Table\n\n| Position | IP/OOP | vs Small Bet (<50%) | vs Medium Bet (50-100%) | vs Large Bet (>100%) |\n|---|---|---|---|---|\n"
        for pos, pos_rules in street_rules.items():
            for ip_oop, rule in pos_rules.items():
                s_bet = f"Raise >= {rule['small_bet'][0]}<br>Call >= {rule['small_bet'][1]}"
                m_bet = f"Raise >= {rule['medium_bet'][0]}<br>Call >= {rule['medium_bet'][1]}"
                l_bet = f"Raise >= {rule['large_bet'][0]}<br>Call >= {rule['large_bet'][1]}"
                md += f"| {pos} | {ip_oop} | {s_bet} | {m_bet} | {l_bet} |\n"
        md += "\n"
    return md

def main():
    """Main function to generate the full Markdown and PDF report."""
    input_filename = sys.argv[1] if len(sys.argv) > 1 else 'strategy.json'

    if not input_filename.endswith('.json'):
        input_filename += '.json'
        
    base_name = os.path.splitext(input_filename)[0]
    md_filename = base_name + '.md'
    pdf_filename = base_name + '.pdf'

    strategy = load_strategy(input_filename)
    if not strategy: return

    full_report = f"# Hold'em Strategy Guide: {base_name.replace('_', ' ').title()}\n\n"
    full_report += format_preflop_hs(strategy['hand_strength_tables']['preflop'])
    full_report += format_postflop_hs(strategy['hand_strength_tables']['postflop'])
    full_report += format_open_rules(strategy['preflop']['open_rules'])
    full_report += format_vs_raise(strategy['preflop']['vs_raise'])
    full_report += format_pfa(strategy['postflop']['pfa'])
    full_report += format_caller(strategy['postflop']['caller'])

    with open(md_filename, 'w', encoding='utf-8') as f:
        f.write(full_report)
    print(f"✅ Successfully created '{md_filename}'")

    if not PDF_ENABLED:
        print("\n⚠️ PDF generation skipped. Please run 'pip install weasyprint markdown' to enable it.")
        return

    css_string = """
        @page { size: A4 landscape; margin: 1.5cm; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; line-height: 1.6; }
        h1, h2, h3 { color: #2c3e50; border-bottom: 1px solid #ccc; padding-bottom: 5px; }
        table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; font-weight: bold; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        code { background-color: #ecf0f1; padding: 2px 4px; border-radius: 4px; color: #c0392b; }
    """
    
    html_string = markdown.markdown(full_report, extensions=['markdown.extensions.tables'])
    try:
        HTML(string=html_string).write_pdf(pdf_filename, stylesheets=[CSS(string=css_string)])
        print(f"✅ Successfully created '{pdf_filename}'")
    except Exception as e:
        print(f"\n❌ PDF generation failed. (Error: {e})")

if __name__ == '__main__':
    main()