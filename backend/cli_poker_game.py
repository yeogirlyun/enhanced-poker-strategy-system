#!/usr/bin/env python3
"""
Enhanced CLI Poker Game with Hand Strength Indicators

Features:
- Visual hand strength meter
- Hand classification display
- Win probability estimation
- Better formatting and emojis
- Color-coded actions
"""

from shared.poker_state_machine_enhanced import ImprovedPokerStateMachine, PokerState, ActionType
from gui_models import StrategyData
import os
import sys
import argparse

# Try to enable colored output on Windows
try:
    import colorama
    colorama.init()
    COLORS_ENABLED = True
except ImportError:
    COLORS_ENABLED = False

# ANSI color codes
class Colors:
    """ANSI color codes for terminal output."""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Regular colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    @staticmethod
    def colorize(text, color):
        """Colorize text if colors are enabled."""
        if COLORS_ENABLED:
            return f"{color}{text}{Colors.RESET}"
        return text


class HandStrengthIndicator:
    """Visual hand strength indicator system."""
    
    @staticmethod
    def get_strength_meter(strength_percent):
        """Create a visual strength meter."""
        # Convert to 0-10 scale
        level = int(strength_percent / 10)
        filled = "█" * level
        empty = "░" * (10 - level)
        
        # Color based on strength
        if strength_percent >= 80:
            color = Colors.BRIGHT_GREEN
        elif strength_percent >= 60:
            color = Colors.GREEN
        elif strength_percent >= 40:
            color = Colors.YELLOW
        elif strength_percent >= 20:
            color = Colors.RED
        else:
            color = Colors.BRIGHT_RED
        
        meter = f"{filled}{empty}"
        return Colors.colorize(meter, color)
    
    @staticmethod
    def get_hand_description(hand_type):
        """Get emoji and description for hand type."""
        hand_emojis = {
            # Made hands
            "high_card": ("🎯", "High Card"),
            "pair": ("👥", "One Pair"),
            "top_pair": ("🔝", "Top Pair"),
            "top_pair_good_kicker": ("🔝+", "Top Pair (Strong Kicker)"),
            "top_pair_bad_kicker": ("🔝-", "Top Pair (Weak Kicker)"),
            "over_pair": ("👑", "Overpair"),
            "second_pair": ("2️⃣", "Second Pair"),
            "bottom_pair": ("⬇️", "Bottom Pair"),
            "two_pair": ("👥👥", "Two Pair"),
            "trips": ("🎲", "Three of a Kind"),
            "set": ("💎", "Set"),
            "straight": ("➡️", "Straight"),
            "flush": ("♠️", "Flush"),
            "nut_flush": ("♠️✨", "Nut Flush"),
            "full_house": ("🏠", "Full House"),
            "quads": ("4️⃣", "Four of a Kind"),
            "straight_flush": ("♠️➡️", "Straight Flush"),
            
            # Draws
            "gutshot_draw": ("🎯", "Gutshot Draw"),
            "open_ended_draw": ("↔️", "Open-Ended Draw"),
            "flush_draw": ("♠️?", "Flush Draw"),
            "nut_flush_draw": ("♠️✨?", "Nut Flush Draw"),
            "combo_draw": ("🎰", "Combo Draw"),
        }
        
        emoji, desc = hand_emojis.get(hand_type, ("❓", hand_type.replace("_", " ").title()))
        return emoji, desc
    
    @staticmethod
    def get_action_recommendation(strength_percent, pot_odds, position):
        """Get action recommendation based on hand strength."""
        if strength_percent >= 80:
            return Colors.colorize("💪 STRONG - Consider raising!", Colors.BRIGHT_GREEN)
        elif strength_percent >= 60:
            return Colors.colorize("👍 GOOD - Bet/Call profitable", Colors.GREEN)
        elif strength_percent >= 40:
            return Colors.colorize("🤔 MEDIUM - Proceed with caution", Colors.YELLOW)
        elif strength_percent >= 20:
            return Colors.colorize("⚠️  WEAK - Check/Fold unless good odds", Colors.RED)
        else:
            return Colors.colorize("🚫 VERY WEAK - Consider folding", Colors.BRIGHT_RED)


class ImprovedCLIPokerGame:
    """Enhanced command-line poker game with better UI."""

    def __init__(self, strategy_data: StrategyData = None):
        self.strategy_data = strategy_data
        self.state_machine = ImprovedPokerStateMachine(
            num_players=6, 
            strategy_data=strategy_data
        )

        # Set up callbacks
        self.state_machine.on_action_required = self._handle_human_action_required
        self.state_machine.on_hand_complete = self._handle_hand_complete
        self.state_machine.on_round_complete = self._handle_round_complete
        self.state_machine.on_state_change = self._handle_state_change

        # Game tracking
        self.hand_number = 0
        self.game_history = []
        self.starting_stack = 100.0
        
        # UI helpers
        self.hand_indicator = HandStrengthIndicator()

    def _clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def _handle_human_action_required(self, player):
        """Handle when human action is required."""
        self._display_game_state_enhanced()
        self._get_human_action(player)

    def _display_game_state_enhanced(self):
        """Enhanced game state display with hand strength indicators."""
        game_info = self.state_machine.get_game_info()
        if not game_info:
            return

        # Clear screen for cleaner display
        if self.state_machine.game_state.street != "preflop":
            self._clear_screen()

        # Header

        # Game state info
        state_display = game_info['state'].upper().replace('_', ' ')
        
        if game_info['current_bet'] > 0:
        
        # Board display
        if game_info['board']:

        # Players table
        
        current_player_idx = game_info['action_player']
        for i, player_info in enumerate(game_info['players']):
            self._display_player_info_enhanced(i, player_info, current_player_idx)

        # Show hand strength for human player
        if current_player_idx == 0 and self.state_machine.game_state:
            self._display_hand_strength_analysis()

    def _display_player_info_enhanced(self, index, player_info, current_player_idx):
        """Enhanced player information display."""
        # Player status
        if not player_info['is_active']:
            status = Colors.colorize("❌ FOLDED", Colors.RED)
        elif player_info['is_all_in']:
            status = Colors.colorize("🔥 ALL-IN", Colors.BRIGHT_YELLOW)
        else:
            status = Colors.colorize("✅ ACTIVE", Colors.GREEN)

        # Turn indicator
        is_current = index == current_player_idx
        turn_indicator = Colors.colorize(" 👉 YOUR TURN", Colors.BRIGHT_MAGENTA) if is_current else ""
        
        # Format player line
        position = Colors.colorize(f"({player_info['position']})", Colors.CYAN)
        stack = Colors.colorize(f"${player_info['stack']:.2f}", Colors.GREEN)
        
        player_line = f"{player_info['name']} {position}: {stack} - {status}"
        
        if player_info['current_bet'] > 0:
            bet_info = Colors.colorize(f" [Bet: ${player_info['current_bet']:.2f}]", Colors.YELLOW)
            player_line += bet_info
        
        player_line += turn_indicator
        

        # Show human player's cards
        if index == 0 and player_info['is_active']:
            cards = player_info['cards']
            if cards and cards != ["**", "**"]:
                formatted_cards = self._format_cards_enhanced(cards)

    def _display_hand_strength_analysis(self):
        """Display detailed hand strength analysis for human player."""
        player = self.state_machine.game_state.players[0]
        if not player.is_active or not player.cards:
            return


        # Get hand classification
        board = self.state_machine.game_state.board
        if board:
            hand_type = self.state_machine.classify_hand(player.cards, board)
            hand_strength = self.state_machine.get_postflop_hand_strength(player.cards, board)
        else:
            hand_type = "preflop"
            hand_strength = self.state_machine.get_preflop_hand_strength(player.cards)

        # Calculate strength percentage
        strength_percent = self.state_machine.get_hand_strength_percentile(hand_strength)
        
        # Display hand type
        if hand_type != "preflop":
            emoji, description = self.hand_indicator.get_hand_description(hand_type)
        
        # Display strength meter
        meter = self.hand_indicator.get_strength_meter(strength_percent)
        
        # Calculate and display equity
        if board:
            active_opponents = len([p for p in self.state_machine.game_state.players 
                                  if p.is_active and p != player])
            equity = self.state_machine.estimate_hand_equity(player.cards, board, active_opponents)
            equity_percent = equity * 100
            
            equity_color = Colors.GREEN if equity_percent >= 50 else Colors.YELLOW if equity_percent >= 30 else Colors.RED
        
        # Action recommendation
        pot_odds = 0
        if self.state_machine.game_state.current_bet > 0:
            call_amount = self.state_machine.game_state.current_bet - player.current_bet
            if call_amount > 0:
                pot_odds = self.state_machine.calculate_pot_odds(call_amount)
        
        recommendation = self.hand_indicator.get_action_recommendation(
            strength_percent, pot_odds, player.position
        )

    def _format_cards_enhanced(self, cards):
        """Enhanced card formatting with colors and suits."""
        if not cards:
            return "[]"

        suit_symbols = {
            "h": (Colors.RED, "♥"),
            "d": (Colors.RED, "♦"),
            "c": (Colors.BLACK, "♣"),
            "s": (Colors.BLACK, "♠")
        }
        
        formatted = []
        for card in cards:
            if len(card) >= 2:
                rank = card[0]
                suit = card[1]
                
                if suit in suit_symbols:
                    color, symbol = suit_symbols[suit]
                    # Make face cards stand out
                    if rank in ['A', 'K', 'Q', 'J']:
                        rank = Colors.colorize(rank, Colors.BOLD)
                    formatted_card = f"{rank}{Colors.colorize(symbol, color)}"
                else:
                    formatted_card = card
                
                formatted.append(formatted_card)
            else:
                formatted.append(card)

        return " ".join(formatted)

    def _display_action_help_enhanced(self, action, player):
        """Enhanced action help with visual indicators."""
        game_info = self.state_machine.get_game_info()
        if not game_info:
            return
        
        current_bet = game_info['current_bet']
        min_raise = game_info['min_raise']
        pot = game_info['pot']
        
        if action == "fold":
        
        elif action == "check":
        
        elif action == "call":
            call_amount = current_bet - player.current_bet
            if call_amount >= player.stack:
            else:
                pot_odds = (pot + call_amount) / call_amount if call_amount > 0 else 0
                
                # Calculate if call is profitable
                active_opponents = len([p for p in self.state_machine.game_state.players 
                                      if p.is_active and p != player])
                equity = self.state_machine.estimate_hand_equity(player.cards, 
                                                               self.state_machine.game_state.board, 
                                                               active_opponents)
                required_equity = 1 / (pot_odds + 1)
                profitable = equity >= required_equity
                
                profit_indicator = Colors.colorize("✅", Colors.GREEN) if profitable else Colors.colorize("❌", Colors.RED)
                
        
        elif action == "bet":
        
        elif action == "raise":
            min_raise_total = current_bet + min_raise
            max_raise = player.current_bet + player.stack
        
        elif action == "allin":

    def _get_human_action(self, player):
        """Get human action with enhanced UI."""
        
        valid_actions = self._get_valid_actions()
        
        for action in valid_actions:
            self._display_action_help_enhanced(action, player)
        
        # Add shortcuts hint
        
        while True:
            try:
                action_input = input(f"\n{Colors.colorize('▶️  Enter action: ', Colors.BRIGHT_CYAN)}").lower().strip()
                
                # Handle shortcuts
                shortcuts = {
                    'f': 'fold',
                    'c': 'call' if self.state_machine.game_state.current_bet > 0 else 'check',
                    'b': 'bet',
                    'r': 'raise',
                    'a': 'allin'
                }
                
                if action_input in shortcuts:
                    action_input = shortcuts[action_input]
                
                if action_input not in valid_actions:
                    continue
                
                action_type = self._parse_action(action_input)
                amount = 0
                
                if action_input in ["bet", "raise"]:
                    amount = self._get_bet_amount(action_input, player)
                    if amount is None: 
                        continue
                elif action_input == "allin":
                    if self.state_machine.game_state.current_bet > 0:
                        amount = player.current_bet + player.stack
                        action_type = ActionType.RAISE
                    else:
                        amount = player.stack
                        action_type = ActionType.BET
                
                # Validate action
                errors = self.state_machine.validate_action(player, action_type, amount)
                if errors:
                    for error in errors: 
                    continue
                
                # Special handling for all-in calls
                if action_input == "call":
                    call_amount = self.state_machine.game_state.current_bet - player.current_bet
                    if call_amount >= player.stack:
                        confirm = input(Colors.colorize("Confirm all-in call? (y/n): ", Colors.YELLOW)).lower().strip()
                        if confirm != 'y':
                            continue
                
                self.state_machine.execute_action(player, action_type, amount)
                break
                
            except KeyboardInterrupt: 
                raise
            except Exception as e: 

    def _get_valid_actions(self):
        """Get valid actions for current player."""
        game_info = self.state_machine.get_game_info()
        if not game_info:
            return []
        
        current_bet = game_info['current_bet']
        state = self.state_machine.get_current_state()
        player = self.state_machine.get_action_player()
        
        actions = ["fold"]
        
        if state == PokerState.PREFLOP_BETTING:
            actions.extend(["call", "raise"])
        else:
            if current_bet > 0:
                actions.extend(["call", "raise"])
            else:
                actions.extend(["check", "bet"])
        
        if player and player.stack > 0:
            actions.append("allin")
        
        return actions

    def _parse_action(self, action_str):
        """Convert string to ActionType."""
        action_map = {
            "fold": ActionType.FOLD,
            "check": ActionType.CHECK,
            "call": ActionType.CALL,
            "bet": ActionType.BET,
            "raise": ActionType.RAISE,
            "allin": ActionType.RAISE,
        }
        return action_map[action_str]

    def _get_bet_amount(self, action_type, player):
        """Get bet/raise amount with improved validation."""
        game_info = self.state_machine.get_game_info()
        if not game_info:
            return None
        
        current_bet = game_info['current_bet']
        min_raise = game_info['min_raise']
        
        if action_type == "bet":
            max_amount = player.stack
            prompt = Colors.colorize(f"Enter bet amount (max ${max_amount:.2f}): ", Colors.CYAN)
        else:  # raise
            min_raise_total = current_bet + min_raise
            max_raise = player.current_bet + player.stack
            prompt = Colors.colorize(f"Enter raise total (min ${min_raise_total:.2f}, max ${max_raise:.2f}): ", Colors.CYAN)
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                amount_input = input(prompt).strip()
                if not amount_input:
                    retry_count += 1
                    continue
                
                amount = float(amount_input)
                
                if amount <= 0:
                    retry_count += 1
                    continue
                
                if amount > player.stack:
                    retry_count += 1
                    continue
                
                if action_type == "raise":
                    if amount <= current_bet:
                        retry_count += 1
                        continue
                    min_raise_total = current_bet + min_raise
                    if amount < min_raise_total:
                        retry_count += 1
                        continue
                
                return amount
                
            except ValueError:
                retry_count += 1
            except KeyboardInterrupt:
                return None
        
        return None

    def _handle_hand_complete(self):
        """Handle when hand is complete."""
        self._display_final_state()
        self._display_hand_summary()
        self.hand_number += 1

    def _handle_round_complete(self):
        """Handle when round is complete."""
        state = self.state_machine.get_current_state().value.upper()

    def _handle_state_change(self, new_state):
        """Handle state changes."""
        if new_state in [PokerState.DEAL_FLOP, PokerState.DEAL_TURN, PokerState.DEAL_RIVER]:
            self._display_board_update()

    def _display_board_update(self):
        """Display board when new cards are dealt."""
        board = self.state_machine.game_state.board
        if board:

    def _display_final_state(self):
        """Display final state with showdown information."""
        game_info = self.state_machine.get_game_info()
        if not game_info:
            return
        
        
        if game_info['board']:
        
        for i, player_info in enumerate(game_info['players']):
            if player_info['is_active']:
                actual_player = next(p for p in self.state_machine.game_state.players 
                                  if p.name == player_info['name'])
                cards = actual_player.cards
                
                status_emoji = "🔥" if player_info['is_all_in'] else "👤"

    def _display_hand_summary(self):
        """Display hand summary with profit/loss."""
        game_info = self.state_machine.get_game_info()
        if not game_info:
            return
        
        
        for player_info in game_info['players']:
            if player_info['total_invested'] > 0:
                result = player_info['stack'] - self.starting_stack
                if result > 0:
                    result_display = Colors.colorize(f"+${result:.2f}", Colors.GREEN)
                    emoji = "💰"
                elif result < 0:
                    result_display = Colors.colorize(f"-${abs(result):.2f}", Colors.RED)
                    emoji = "💸"
                else:
                    result_display = Colors.colorize(f"${result:.2f}", Colors.YELLOW)
                    emoji = "➖"
                

    def start_hand(self):
        """Start a new hand."""

        dealer_name = self.state_machine.game_state.players[self.state_machine.dealer_position].name if self.state_machine.game_state else "TBD"

        self.state_machine.start_hand()

        self._display_game_state_enhanced()

        self.state_machine.handle_current_player_action()

    def run_game(self, num_hands=3):
        """Run the enhanced poker game."""
        self._clear_screen()
        
        
        strategy_name = "Default"
        if self.strategy_data and hasattr(self.strategy_data, 'current_strategy_file'):
            strategy_name = self.strategy_data.current_strategy_file or "Default"
        

        for i in range(num_hands):
            try:
                self.start_hand()

                if i < num_hands - 1:
                    input(f"\n{Colors.colorize('🔄 Press Enter to start next hand...', Colors.YELLOW)}")
                    self._clear_screen()
            except KeyboardInterrupt:
                break

        self._display_game_summary()

    def _display_game_summary(self):
        """Display final game summary."""
        game_info = self.state_machine.get_game_info()
        if not game_info:
            return
        
        
        players_with_stacks = [(p['name'], p['stack']) for p in game_info['players']]
        players_with_stacks.sort(key=lambda x: x[1], reverse=True)
        
        for i, (name, stack) in enumerate(players_with_stacks):
            profit = stack - 100.0
            
            if i == 0:
                rank_emoji = "🥇"
                color = Colors.BRIGHT_YELLOW
            elif i == 1:
                rank_emoji = "🥈"
                color = Colors.WHITE
            elif i == 2:
                rank_emoji = "🥉"
                color = Colors.YELLOW
            else:
                rank_emoji = "📊"
                color = Colors.RESET
            
            if profit > 0:
                profit_display = Colors.colorize(f"+${profit:.2f}", Colors.GREEN)
                profit_emoji = "💰"
            elif profit < 0:
                profit_display = Colors.colorize(f"-${abs(profit):.2f}", Colors.RED)
                profit_emoji = "💸"
            else:
                profit_display = Colors.colorize(f"${profit:.2f}", Colors.YELLOW)
                profit_emoji = "➖"
            


def main():
    """Enhanced main function with strategy selection."""
    # --- FIX STARTS HERE ---
    parser = argparse.ArgumentParser(description="Enhanced CLI Poker Game.")
    parser.add_argument(
        "--strategy", 
        type=str, 
        default="modern_strategy.json",
        help="Path to the strategy JSON file for bots to use."
    )
    parser.add_argument(
        "--interactive", 
        action="store_true",
        help="Enable interactive strategy selection."
    )
    args = parser.parse_args()

    
    strategy_data = StrategyData()
    
    if args.interactive:
        # --- NEW: Interactive Strategy Selection ---
        
        while True:
            strategy_choice = input(
                Colors.colorize("Choose bot strategy [1/2]: ", Colors.CYAN)
            ).strip()
            
            if strategy_choice == '2':
                strategy_file_to_load = "aggressive_strategy.json"
                break
            elif strategy_choice == '1':
                strategy_file_to_load = "modern_strategy.json"
                break
            else:
    else:
        strategy_file_to_load = args.strategy

    try:
        if strategy_data.load_strategy_from_file(strategy_file_to_load):
        else:
            strategy_data.load_default_tiers()
    except Exception as e:
        strategy_data.load_default_tiers()
    # --- FIX ENDS HERE ---

    # Create and run the game
    game = ImprovedCLIPokerGame(strategy_data)

    try:
        # Ask user for number of hands
        while True:
            try:
                num_hands = input(Colors.colorize("🎯 How many hands to play? (default: 3): ", Colors.CYAN)).strip()
                if not num_hands:
                    num_hands = 3
                else:
                    num_hands = int(num_hands)
                if num_hands > 0:
                    break
            except ValueError:

        game.run_game(num_hands=num_hands)
        
    except KeyboardInterrupt:
    except Exception as e:
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
