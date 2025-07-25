# filename: json_to_markdown.py
"""
JSON to Markdown Strategy Converter

Version 1.2 (Memorization Update)

- The script now formats the Preflop HS table into the memorizable Tier system.
- A new "Hand Tiers" column has been added to all decision tables. This column
  translates the HS thresholds into the corresponding hand tiers (e.g., "Tier 1+",
  "Tier 2 Hands"), making the strategy much more intuitive and easier to learn.
- This version correctly processes all streets (Flop, Turn, River).
"""
import json

def load_strategy(filename='strategy.json'):
    """Loads the strategy from the JSON file."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: '{filename}' not found. Please create it first.")
        return None

def get_tier_from_hs(hs_value, is_range=False):
    """Helper function to convert an HS value or range to a Tier description."""
    if isinstance(hs_value, list): # It's a range like [20, 25]
        lower_bound = hs_value[0]
        if lower_bound >= 30: return "Tier 1"
        if lower_bound >= 20: return "Tier 2"
        if lower_bound >= 15: return "Tier 3"
        if lower_bound >= 10: return "Tier 4"
        return "Tier 5"
    else: # It's a threshold like >= 30
        if hs_value >= 30: return "Tier 1+"
        if hs_value >= 20: return "Tier 2+"
        if hs_value >= 15: return "Tier 3+"
        if hs_value >= 10: return "Tier 4+"
        return "Tier 5+"

def format_preflop_hs(hs_table):
    """Formats the preflop HS table into tiers for memorization."""
    tiers = {
        "Tier 1: Elite Hands (HS 30+)": [], "Tier 2: Premium Hands (HS 20-25)": [],
        "Tier 3: Gold Hands (HS 15)": [], "Tier 4: Silver Hands (HS 10)": [],
        "Tier 5: Speculative Hands (HS 5)": [],
    }
    for hand, hs in sorted(hs_table.items(), key=lambda item: item[1], reverse=True):
        if hs >= 30: tiers["Tier 1: Elite Hands (HS 30+)"].append(f"{hand} ({hs})")
        elif hs >= 20: tiers["Tier 2: Premium Hands (HS 20-25)"].append(f"{hand} ({hs})")
        elif hs == 15: tiers["Tier 3: Gold Hands (HS 15)"].append(f"{hand} ({hs})")
        elif hs == 10: tiers["Tier 4: Silver Hands (HS 10)"].append(f"{hand} ({hs})")
        elif hs == 5: tiers["Tier 5: Speculative Hands (HS 5)"].append(f"{hand} ({hs})")

    md = "## Preflop Hand Strength (HS)\n\n"
    for tier_name, hands in tiers.items():
        md += f"### {tier_name}\n"
        md += "- " + ", ".join(hands) + "\n\n"
    return md

def format_postflop_hs(hs_table):
    """Formats the postflop HS table."""
    md = "## Postflop Hand Strength (HS)\n\n"
    md += "| Hand Rank | HS Value |\n"
    md += "|---|---|\n"
    for rank, hs in sorted(hs_table.items(), key=lambda item: item[1], reverse=True):
        md += f"| {rank.replace('_', ' ').title()} | {hs} |\n"
    return md + "\n"

def format_open_rules(rules):
    """Formats the preflop opening rules with Tier descriptions."""
    md = "## Preflop: Open Rule Table\n\n"
    md += "| Position | Open Threshold (HS) | Hand Tiers | Sizing (BB) |\n"
    md += "|---|---|---|---|\n"
    for pos, rule in rules.items():
        tiers = get_tier_from_hs(rule['threshold'])
        md += f"| {pos} | >= {rule['threshold']} | **{tiers}** | {rule['sizing']:.1f}x |\n"
    return md + "\n"

def format_vs_raise(rules):
    """Formats the preflop vs raise rules with Tier descriptions."""
    md = "## Preflop: Facing a Raise (3-Bet Table)\n\n"
    md += "| Position | IP/OOP | Value 3-Bet (HS) | Call Range (HS) | Hand Tiers (Call) | Sizing |\n"
    md += "|---|---|---|---|---|---|\n"
    for pos, pos_rules in rules.items():
        for ip_oop, rule in pos_rules.items():
            value_tiers = get_tier_from_hs(rule['value_thresh'])
            call_tiers = get_tier_from_hs(rule['call_range'])
            md += f"| {pos} | {ip_oop} | >= {rule['value_thresh']} ({value_tiers}) | {rule['call_range'][0]}-{rule['call_range'][1]} | **{call_tiers} Hands** | {rule['sizing']:.1f}x |\n"
    return md + "\n"

def format_pfa(rules):
    """Formats the postflop PFA rules for all streets."""
    md = "## Postflop: As Pre-Flop Aggressor (PFA)\n\n"
    for street, street_rules in rules.items():
        md += f"### {street.title()} - PFA Rule Table\n\n"
        md += "| Position | IP/OOP | Value Bet (HS) | Check (HS) |\n"
        md += "|---|---|---|---|\n"
        for pos, pos_rules in street_rules.items():
            for ip_oop, rule in pos_rules.items():
                md += f"| {pos} | {ip_oop} | >= {rule['val_thresh']} | >= {rule['check_thresh']} |\n"
        md += "\n"
    return md

def format_caller(rules):
    """Formats the postflop caller rules for all streets."""
    md = "## Postflop: As Caller (Facing a Bet)\n\n"
    for street, street_rules in rules.items():
        md += f"### {street.title()} - Facing Bet Table\n\n"
        md += "| Position | IP/OOP | vs Small Bet (<50%) | vs Medium Bet (50-100%) | vs Large Bet (>100%) |\n"
        md += "|---|---|---|---|---|\n"
        for pos, pos_rules in street_rules.items():
            for ip_oop, rule in pos_rules.items():
                s_bet = f"Raise >= {rule['small_bet'][0]} / Call >= {rule['small_bet'][1]}"
                m_bet = f"Raise >= {rule['medium_bet'][0]} / Call >= {rule['medium_bet'][1]}"
                l_bet = f"Raise >= {rule['large_bet'][0]} / Call >= {rule['large_bet'][1]}"
                md += f"| {pos} | {ip_oop} | {s_bet} | {m_bet} | {l_bet} |\n"
        md += "\n"
    return md

def main():
    """Main function to generate the full Markdown report."""
    strategy = load_strategy()
    if not strategy:
        return

    full_report = "# Hold'em Strategy Tables\n\n"
    full_report += format_preflop_hs(strategy['hand_strength_tables']['preflop'])
    full_report += format_postflop_hs(strategy['hand_strength_tables']['postflop'])
    full_report += format_open_rules(strategy['preflop']['open_rules'])
    full_report += format_vs_raise(strategy['preflop']['vs_raise'])
    full_report += format_pfa(strategy['postflop']['pfa'])
    full_report += format_caller(strategy['postflop']['caller'])

    print(full_report)

if __name__ == '__main__':
    main()
