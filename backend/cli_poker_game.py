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
        print("\n" + Colors.colorize("═" * 80, Colors.BRIGHT_BLUE))
        print(Colors.colorize(f"🎮 TEXAS HOLD'EM - HAND #{self.hand_number + 1}", Colors.BRIGHT_CYAN))
        print(Colors.colorize("═" * 80, Colors.BRIGHT_BLUE))

        # Game state info
        state_display = game_info['state'].upper().replace('_', ' ')
        print(f"\n📍 {Colors.colorize(state_display, Colors.YELLOW)}")
        print(f"💰 POT: {Colors.colorize(f'${game_info["pot"]:.2f}', Colors.BRIGHT_GREEN)}")
        
        if game_info['current_bet'] > 0:
            print(f"📊 CURRENT BET: {Colors.colorize(f'${game_info["current_bet"]:.2f}', Colors.BRIGHT_YELLOW)}")
            print(f"📈 MIN RAISE: {Colors.colorize(f'${game_info["min_raise"]:.2f}', Colors.YELLOW)}")
        
        # Board display
        if game_info['board']:
            print(f"\n🃏 BOARD: {self._format_cards_enhanced(game_info['board'])}")

        # Players table
        print("\n" + Colors.colorize("─" * 80, Colors.BLUE))
        print(Colors.colorize("PLAYERS:", Colors.BRIGHT_CYAN))
        print(Colors.colorize("─" * 80, Colors.BLUE))
        
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
        
        print(player_line)

        # Show human player's cards
        if index == 0 and player_info['is_active']:
            cards = player_info['cards']
            if cards and cards != ["**", "**"]:
                formatted_cards = self._format_cards_enhanced(cards)
                print(f"  🂠 Your cards: {formatted_cards}")

    def _display_hand_strength_analysis(self):
        """Display detailed hand strength analysis for human player."""
        player = self.state_machine.game_state.players[0]
        if not player.is_active or not player.cards:
            return

        print("\n" + Colors.colorize("─" * 80, Colors.BLUE))
        print(Colors.colorize("HAND ANALYSIS:", Colors.BRIGHT_CYAN))
        print(Colors.colorize("─" * 80, Colors.BLUE))

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
            print(f"🎯 Hand Type: {emoji} {Colors.colorize(description, Colors.BRIGHT_YELLOW)}")
        
        # Display strength meter
        meter = self.hand_indicator.get_strength_meter(strength_percent)
        print(f"💪 Strength: {meter} {Colors.colorize(f'{strength_percent:.0f}%', Colors.BRIGHT_WHITE)}")
        
        # Calculate and display equity
        if board:
            active_opponents = len([p for p in self.state_machine.game_state.players 
                                  if p.is_active and p != player])
            equity = self.state_machine.estimate_hand_equity(player.cards, board, active_opponents)
            equity_percent = equity * 100
            
            equity_color = Colors.GREEN if equity_percent >= 50 else Colors.YELLOW if equity_percent >= 30 else Colors.RED
            print(f"📊 Win Probability: {Colors.colorize(f'{equity_percent:.1f}%', equity_color)}")
        
        # Action recommendation
        pot_odds = 0
        if self.state_machine.game_state.current_bet > 0:
            call_amount = self.state_machine.game_state.current_bet - player.current_bet
            if call_amount > 0:
                pot_odds = self.state_machine.calculate_pot_odds(call_amount)
        
        recommendation = self.hand_indicator.get_action_recommendation(
            strength_percent, pot_odds, player.position
        )
        print(f"\n{recommendation}")

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
            print(f"  {Colors.colorize('fold', Colors.RED)} - Give up hand")
        
        elif action == "check":
            print(f"  {Colors.colorize('check', Colors.CYAN)} - Pass action (no bet)")
        
        elif action == "call":
            call_amount = current_bet - player.current_bet
            if call_amount >= player.stack:
                print(f"  {Colors.colorize('call', Colors.BRIGHT_YELLOW)} - Go ALL-IN (${player.stack:.2f})")
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
                
                print(f"  {Colors.colorize('call', Colors.YELLOW)} - Match bet (${call_amount:.2f}) - Pot odds: {pot_odds:.1f}:1 {profit_indicator}")
        
        elif action == "bet":
            print(f"  {Colors.colorize('bet', Colors.GREEN)} - Make first bet (max ${player.stack:.2f})")
        
        elif action == "raise":
            min_raise_total = current_bet + min_raise
            max_raise = player.current_bet + player.stack
            print(f"  {Colors.colorize('raise', Colors.BRIGHT_GREEN)} - Increase bet (min ${min_raise_total:.2f}, max ${max_raise:.2f})")
        
        elif action == "allin":
            print(f"  {Colors.colorize('allin', Colors.BRIGHT_MAGENTA)} - Go ALL-IN with ${player.stack:.2f} 🚀")

    def _get_human_action(self, player):
        """Get human action with enhanced UI."""
        print(f"\n{Colors.colorize('🎯 YOUR TURN', Colors.BRIGHT_MAGENTA)} ({player.name})")
        
        valid_actions = self._get_valid_actions()
        print(Colors.colorize("💡 Available actions:", Colors.CYAN))
        
        for action in valid_actions:
            self._display_action_help_enhanced(action, player)
        
        # Add shortcuts hint
        print(f"\n{Colors.colorize('Shortcuts:', Colors.CYAN)} f=fold, c=call/check, b=bet, r=raise, a=all-in")
        
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
                    print(Colors.colorize(f"❌ Invalid action. Valid: {', '.join(valid_actions)}", Colors.RED))
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
                    print(Colors.colorize("❌ Action validation errors:", Colors.RED))
                    for error in errors: 
                        print(Colors.colorize(f"  • {error}", Colors.RED))
                    continue
                
                # Special handling for all-in calls
                if action_input == "call":
                    call_amount = self.state_machine.game_state.current_bet - player.current_bet
                    if call_amount >= player.stack:
                        print(Colors.colorize(f"🔥 You're going ALL-IN with ${player.stack:.2f}!", Colors.BRIGHT_YELLOW))
                        confirm = input(Colors.colorize("Confirm all-in call? (y/n): ", Colors.YELLOW)).lower().strip()
                        if confirm != 'y':
                            continue
                
                print(Colors.colorize(f"✅ Executing: {action_input.upper()} ${amount:.2f}", Colors.GREEN))
                self.state_machine.execute_action(player, action_type, amount)
                break
                
            except KeyboardInterrupt: 
                raise
            except Exception as e: 
                print(Colors.colorize(f"❌ Error: {e}", Colors.RED))

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
                    print(Colors.colorize("❌ Amount cannot be empty", Colors.RED))
                    retry_count += 1
                    continue
                
                amount = float(amount_input)
                
                if amount <= 0:
                    print(Colors.colorize("❌ Amount must be positive", Colors.RED))
                    retry_count += 1
                    continue
                
                if amount > player.stack:
                    print(Colors.colorize(f"❌ Amount ${amount:.2f} exceeds stack ${player.stack:.2f}", Colors.RED))
                    retry_count += 1
                    continue
                
                if action_type == "raise":
                    if amount <= current_bet:
                        print(Colors.colorize(f"❌ Raise must be more than current bet ${current_bet:.2f}", Colors.RED))
                        retry_count += 1
                        continue
                    min_raise_total = current_bet + min_raise
                    if amount < min_raise_total:
                        print(Colors.colorize(f"❌ Minimum raise is ${min_raise_total:.2f}", Colors.RED))
                        retry_count += 1
                        continue
                
                return amount
                
            except ValueError:
                print(Colors.colorize("❌ Please enter a valid number", Colors.RED))
                retry_count += 1
            except KeyboardInterrupt:
                return None
        
        print(Colors.colorize(f"⚠️  Too many invalid attempts. Canceling {action_type} action.", Colors.YELLOW))
        return None

    def _handle_hand_complete(self):
        """Handle when hand is complete."""
        print("\n" + Colors.colorize("=" * 80, Colors.BRIGHT_GREEN))
        print(Colors.colorize("🏁 HAND COMPLETE!", Colors.BRIGHT_GREEN))
        self._display_final_state()
        self._display_hand_summary()
        print(Colors.colorize("=" * 80, Colors.BRIGHT_GREEN))
        self.hand_number += 1

    def _handle_round_complete(self):
        """Handle when round is complete."""
        state = self.state_machine.get_current_state().value.upper()
        print(f"\n{Colors.colorize(f'--- ✅ ROUND COMPLETE: {state} ---', Colors.GREEN)}")

    def _handle_state_change(self, new_state):
        """Handle state changes."""
        if new_state in [PokerState.DEAL_FLOP, PokerState.DEAL_TURN, PokerState.DEAL_RIVER]:
            self._display_board_update()

    def _display_board_update(self):
        """Display board when new cards are dealt."""
        board = self.state_machine.game_state.board
        if board:
            print(f"\n🃏 BOARD: {self._format_cards_enhanced(board)}")

    def _display_final_state(self):
        """Display final state with showdown information."""
        game_info = self.state_machine.get_game_info()
        if not game_info:
            return
        
        print("\n" + Colors.colorize("=" * 80, Colors.BRIGHT_BLUE))
        print(Colors.colorize("🏁 FINAL STATE", Colors.BRIGHT_CYAN))
        print(Colors.colorize("=" * 80, Colors.BRIGHT_BLUE))
        
        print(f"💰 FINAL POT: {Colors.colorize(f'${game_info["pot"]:.2f}', Colors.BRIGHT_GREEN)}")
        if game_info['board']:
            print(f"🃏 BOARD: {self._format_cards_enhanced(game_info['board'])}")
        
        print(f"\n{Colors.colorize('📋 ACTIVE PLAYERS:', Colors.CYAN)}")
        for i, player_info in enumerate(game_info['players']):
            if player_info['is_active']:
                actual_player = next(p for p in self.state_machine.game_state.players 
                                  if p.name == player_info['name'])
                cards = actual_player.cards
                
                status_emoji = "🔥" if player_info['is_all_in'] else "👤"
                print(f"  {status_emoji} {player_info['name']}: {self._format_cards_enhanced(cards)}")
                print(f"     Stack: ${player_info['stack']:.2f} | Total Invested: ${player_info['total_invested']:.2f}")

    def _display_hand_summary(self):
        """Display hand summary with profit/loss."""
        game_info = self.state_machine.get_game_info()
        if not game_info:
            return
        
        print(f"\n{Colors.colorize('📊 HAND SUMMARY:', Colors.CYAN)}")
        print(Colors.colorize("-" * 50, Colors.BLUE))
        
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
                
                print(f"  {emoji} {player_info['name']}: {result_display} (invested ${player_info['total_invested']:.2f})")

    def start_hand(self):
        """Start a new hand."""
        print(f"\n{Colors.colorize(f'🎮 STARTING HAND #{self.hand_number + 1}', Colors.BRIGHT_CYAN)}")
        print(Colors.colorize("=" * 80, Colors.BLUE))

        dealer_name = self.state_machine.game_state.players[self.state_machine.dealer_position].name if self.state_machine.game_state else "TBD"
        print(f"🔘 Dealer: {Colors.colorize(dealer_name, Colors.YELLOW)}")

        self.state_machine.start_hand()

        print(f"\n🃏 {Colors.colorize('Cards dealt! Players have received their hole cards.', Colors.GREEN)}")
        self._display_game_state_enhanced()

        self.state_machine.handle_current_player_action()

    def run_game(self, num_hands=3):
        """Run the enhanced poker game."""
        self._clear_screen()
        
        print(Colors.colorize("🎰 ENHANCED CLI POKER GAME", Colors.BRIGHT_MAGENTA))
        print(Colors.colorize("=" * 80, Colors.MAGENTA))
        
        strategy_name = "Default"
        if self.strategy_data and hasattr(self.strategy_data, 'current_strategy_file'):
            strategy_name = self.strategy_data.current_strategy_file or "Default"
        
        print(f"📋 Strategy: {Colors.colorize(strategy_name, Colors.CYAN)}")
        print(f"👥 Players: {Colors.colorize('6 (1 human + 5 bots)', Colors.CYAN)}")
        print(f"🎯 Hands to play: {Colors.colorize(str(num_hands), Colors.CYAN)}")
        print(Colors.colorize("=" * 80, Colors.MAGENTA))

        for i in range(num_hands):
            try:
                self.start_hand()

                if i < num_hands - 1:
                    input(f"\n{Colors.colorize('🔄 Press Enter to start next hand...', Colors.YELLOW)}")
                    self._clear_screen()
            except KeyboardInterrupt:
                print(f"\n\n{Colors.colorize('👋 Game interrupted by user', Colors.YELLOW)}")
                break

        print(f"\n{Colors.colorize('🎉 GAME COMPLETE!', Colors.BRIGHT_GREEN)}")
        self._display_game_summary()
        print(Colors.colorize("=" * 80, Colors.GREEN))

    def _display_game_summary(self):
        """Display final game summary."""
        game_info = self.state_machine.get_game_info()
        if not game_info:
            return
        
        print("\n" + Colors.colorize("=" * 80, Colors.BRIGHT_BLUE))
        print(Colors.colorize("🏆 GAME SUMMARY", Colors.BRIGHT_CYAN))
        print(Colors.colorize("=" * 80, Colors.BRIGHT_BLUE))
        
        players_with_stacks = [(p['name'], p['stack']) for p in game_info['players']]
        players_with_stacks.sort(key=lambda x: x[1], reverse=True)
        
        print(Colors.colorize("📈 FINAL STANDINGS:", Colors.CYAN))
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
            
            print(f"  {rank_emoji} {Colors.colorize(name, color)}: ${stack:.2f} ({profit_emoji} {profit_display})")


def main():
    """Enhanced main function."""
    print(Colors.colorize("🚀 Loading Enhanced Poker Game...", Colors.BRIGHT_CYAN))
    
    # Load strategy data
    strategy_data = StrategyData()
    try:
        if strategy_data.load_strategy_from_file("optimized_modern_strategy.json"):
            print(Colors.colorize("✅ Optimized modern strategy loaded", Colors.GREEN))
        elif strategy_data.load_strategy_from_file("modern_strategy.json"):
            print(Colors.colorize("✅ Modern strategy loaded", Colors.GREEN))
        else:
            print(Colors.colorize("⚠️  Using default strategy", Colors.YELLOW))
            strategy_data.load_default_tiers()
    except Exception as e:
        print(Colors.colorize(f"⚠️  Strategy loading error: {e}", Colors.YELLOW))
        print(Colors.colorize("⚠️  Using default strategy", Colors.YELLOW))
        strategy_data.load_default_tiers()

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
                print(Colors.colorize("❌ Number of hands must be positive", Colors.RED))
            except ValueError:
                print(Colors.colorize("❌ Please enter a valid number", Colors.RED))

        game.run_game(num_hands=num_hands)
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.colorize('👋 Game interrupted by user', Colors.YELLOW)}")
    except Exception as e:
        print(Colors.colorize(f"\n❌ Game error: {e}", Colors.RED))
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
