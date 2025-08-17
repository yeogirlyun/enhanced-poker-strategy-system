"""
Utilities for poker card rendering and display.
"""


def parse_card(card_str):
    """
    Parse a card string like 'Ah', 'Kc', '2d', 'Ts' into rank and suit.
    Returns (rank, suit, color, symbol) tuple.
    """
    if not card_str or len(card_str) < 2:
        return None, None, "#000000", ""
    
    rank = card_str[0].upper()
    suit_char = card_str[1].lower()
    
    # Suit mapping to symbols and colors
    suit_map = {
        'h': ('♥', '#DC2626'),  # Hearts - red
        'd': ('♦', '#DC2626'),  # Diamonds - red  
        'c': ('♣', '#000000'),  # Clubs - black
        's': ('♠', '#000000')   # Spades - black
    }
    
    if suit_char in suit_map:
        symbol, color = suit_map[suit_char]
        return rank, suit_char, color, symbol
    
    return rank, suit_char, "#000000", suit_char


def format_card_display(card_str, show_suits=True):
    """
    Format a card string for display.
    Returns (display_text, text_color) tuple.
    """
    rank, suit, color, symbol = parse_card(card_str)
    
    if not rank:
        return "", "#000000"
    
    if show_suits and symbol:
        display_text = f"{rank}{symbol}"
    else:
        display_text = rank
    
    return display_text, color


def is_red_card(card_str):
    """Check if a card is red (hearts or diamonds)."""
    if not card_str or len(card_str) < 2:
        return False
    suit_char = card_str[1].lower()
    return suit_char in ['h', 'd']


def is_black_card(card_str):
    """Check if a card is black (clubs or spades)."""
    if not card_str or len(card_str) < 2:
        return False
    suit_char = card_str[1].lower()
    return suit_char in ['c', 's']
