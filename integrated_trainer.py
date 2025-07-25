# filename: integrated_trainer.py
"""
Integrated Advanced Hold'em Trainer

REVISION HISTORY:
================

Version 8.4 (2025-01-25) - Complete Seat-Based System Rewrite
- FIXED: Players now have fixed SEATS (0-5), not fixed positions
- FIXED: Positions (BTN, SB, BB, UTG, MP, CO) rotate based on dealer button
- FIXED: Proper action order for all streets (UTG first preflop, SB first postflop)
- FIXED: Correct blind assignment every hand (SB=button+1, BB=button+2)
- ADDED: Dynamic position calculation based on dealer button location
- ADDED: _get_position_for_seat() method for position assignment
- ADDED: _get_player_at_position() method for position queries
- ADDED: _get_action_order() method for correct action sequences
- ADDED: Seat number display in action messages
- ENSURED: All non-user players execute strategy perfectly
- Key insight: Players have permanent seats, positions rotate with button

Version 8.3 (2025-01-25) - Position System Overhaul [SUPERSEDED by 8.4]
- Initial attempt at fixing positions (incomplete solution)

Version 8.2 (2025-01-25) - Action Sequence Enhancement
- Added proper action order display showing position sequence
- Implemented sequential action announcements with clear turn indicators
- Added realistic timing delays for opponent actions
- Enhanced action flow with pot tracking and player count updates
- Improved user turn highlighting and context display
- Added comprehensive action status reporting

Version 8.1 (2025-01-25) - Logic Fixes
- Fixed BB behavior when facing no action (now checks instead of folding)
- Implemented proper stack persistence across hands
- Added realistic blind posting with stack size checking
- Fixed uncontested pot handling
- Improved action sequences and pot distribution

Version 8.0 (2025-01-25) - Complete Integration
- Integrated enhanced hand evaluation with equity calculations
- Added session logging and analytics
- Implemented advanced training modes
- Enhanced decision engine with position-adjusted strategy
- Added comprehensive user interface with color coding
- Integrated all advanced modules into single trainer

Features:
- Seat-based table system with rotating positions
- Enhanced hand evaluation with equity calculations
- Session logging and analytics
- Advanced training modes (drill, speed, blind, mistake review)
- Position-adjusted strategy calculations
- Persistent stack tracking
- Realistic action sequences
- Comprehensive performance analytics
"""

import json
import random
import sys
import time
from datetime import datetime
from collections import Counter, defaultdict

# Import our enhanced modules
try:
    from session_logger import SessionLogger, SessionAnalyzer
    from training_modes import TrainingModeManager
    from enhanced_hand_evaluation import EnhancedHandEvaluator, PositionAdjustedEvaluator
    SESSION_LOGGING = True
except ImportError as e:
    print(f"Warning: Could not import advanced modules: {e}")
    print("Some features will be disabled.")
    SESSION_LOGGING = False

# --- Global Data ---
SUITS = 'cdhs'
RANKS = '23456789TJQKA'
RANK_VALUES = {r: i for i, r in enumerate(RANKS, 2)}

# Color codes for better UI
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def get_shuffled_deck():
    deck = [r + s for r in RANKS for s in SUITS]
    random.shuffle(deck)
    return deck

class AdvancedHandEvaluator:
    """Wrapper for enhanced hand evaluation with fallback."""
    
    def __init__(self, strategy):
        self.strategy = strategy
        if SESSION_LOGGING:
            self.enhanced_evaluator = EnhancedHandEvaluator()
            self.position_evaluator = PositionAdjustedEvaluator(self.enhanced_evaluator)
        else:
            self.enhanced_evaluator = None
            self.position_evaluator = None
    
    def get_preflop_hs(self, hole):
        """Get preflop hand strength."""
        if not hole or len(hole) != 2:
            return 0
        
        r_vals = sorted([RANK_VALUES[c[0]] for c in hole], reverse=True)
        r1, r2 = RANKS[r_vals[0]-2], RANKS[r_vals[1]-2]
        suited = hole[0][1] == hole[1][1]

        # Format the hand into a key
        if r1 == r2:
            key = r1 + r2
        elif suited:
            key = r1 + r2 + 's'
        else:
            key = r1 + r2 + 'o'
        
        # Fallbacks for generic suited hands
        if key not in self.strategy['hand_strength_tables']['preflop']:
            if suited:
                if r1 == 'K': key = 'Kxs'
                elif r1 == 'Q': key = 'Qxs'
                elif r1 == 'J': key = 'Jxs'
                elif r1 == 'T': key = 'Txs'

        return self.strategy['hand_strength_tables']['preflop'].get(key, 0)
    
    def get_postflop_evaluation(self, hole, board, position='BTN', action_history=None):
        """Get comprehensive postflop evaluation."""
        if action_history is None:
            action_history = []
        
        if self.enhanced_evaluator and len(hole + board) >= 5:
            # Use enhanced evaluation
            try:
                evaluation = self.position_evaluator.evaluate_hand_in_context(
                    hole, board, position, action_history
                )
                
                # Convert to our expected format
                return {
                    'rank': self._convert_hand_rank(evaluation['hand_rank']),
                    'hs': evaluation['hand_strength'],
                    'is_draw': len(evaluation['draws']) > 0,
                    'outs': evaluation['outs'],
                    'board_texture': evaluation['board_texture'].name.lower(),
                    'equity_estimate': evaluation.get('equity_estimate', 50),
                    'nut_potential': evaluation.get('nut_potential', 'medium'),
                    'original_strength': evaluation.get('original_strength', evaluation['hand_strength'])
                }
            except Exception as e:
                print(f"Enhanced evaluation failed: {e}, falling back to basic")
        
        # Fallback to basic evaluation
        return self._basic_postflop_evaluation(hole, board)
    
    def _convert_hand_rank(self, hand_rank):
        """Convert enhanced hand rank to our string format."""
        conversion = {
            1: 'high_card',
            2: 'pair', 
            3: 'two_pair',
            4: 'set',
            5: 'straight',
            6: 'flush',
            7: 'full_house',
            8: 'quads',
            9: 'straight_flush',
            10: 'straight_flush'  # Royal flush
        }
        return conversion.get(int(hand_rank), 'high_card')
    
    def _basic_postflop_evaluation(self, hole, board):
        """Basic postflop evaluation (fallback)."""
        details = {'rank': 'high_card', 'is_draw': False, 'outs': 0}
        if not board:
            details['hs'] = 0
            return details

        all_cards = hole + board
        all_ranks = sorted([RANK_VALUES[c[0]] for c in all_cards], reverse=True)
        board_ranks = sorted([RANK_VALUES[c[0]] for c in board], reverse=True)
        hole_ranks = sorted([RANK_VALUES[c[0]] for c in hole], reverse=True)
        suit_counts = Counter(c[1] for c in all_cards)
        rank_counts = Counter(all_ranks)

        # Basic hand detection
        if 3 in rank_counts.values():
            details['rank'] = 'set'
        elif list(rank_counts.values()).count(2) >= 2:
            details['rank'] = 'two_pair'
        elif 2 in rank_counts.values():
            pair_rank = [r for r, c in rank_counts.items() if c == 2][0]
            if pair_rank in hole_ranks:
                details['rank'] = 'top_pair' if pair_rank >= board_ranks[0] else 'pair'
            else:
                details['rank'] = 'pair'

        # Check for draws
        if 4 in suit_counts.values():
            details['rank'] = 'flush_draw'
            details['is_draw'] = True
            details['outs'] = 9

        # Look up HS value
        details['hs'] = self.strategy['hand_strength_tables']['postflop'].get(details['rank'], 0)
        return details
    
def get_optimal_action(state, strategy):
    """Enhanced optimal action calculation with modern blind defense."""
    pos, street, actions, pfa, pot, to_call, is_ip = (
        state['position'], state['street'], state['history'], 
        state['was_aggressor'], state['pot'], state['to_call'], state['is_ip']
    )
    
    # Use the correct HS for the current street
    hs = state['dynamic_hs'] if street != 'preflop' else state['preflop_hs']
    pos_type = "IP" if is_ip else "OOP"

    try:
        if street == 'preflop':
            if not actions:
                # Opening action (unchanged)
                rule = strategy['preflop']['open_rules'][pos]
                return ('raise', rule['sizing']) if hs >= rule['threshold'] else ('fold', 0)
            
            elif actions == ['raise'] and pos in ['BB', 'SB']:
                # BLIND DEFENSE - Check if new blind defense rules exist
                if 'blind_defense' in strategy['preflop'] and pos in strategy['preflop']['blind_defense']:
                    # Try to determine who opened based on game state
                    # Simple heuristic: if pot is small, likely late position open
                    if pot <= 4.5:  # Likely BTN or CO open (2.5x)
                        opener = 'BTN' if pot <= 4.0 else 'CO'
                    elif pot <= 5.0:  # Likely MP open (3x)
                        opener = 'MP'
                    else:  # Likely UTG open (3x)
                        opener = 'UTG'
                    
                    # For SB facing BB raise, assume BB
                    if pos == 'SB' and to_call >= 2.5:
                        opener = 'BTN'  # Use BTN rules as default
                    
                    vs_opener = f"vs_{opener}"
                    blind_rules = strategy['preflop']['blind_defense'][pos]
                    
                    if vs_opener in blind_rules:
                        rule = blind_rules[vs_opener]
                        
                        # 3-bet for value
                        if hs >= rule['value_thresh']:
                            sizing = rule['sizing'] * to_call
                            return ('raise', sizing)
                        
                        # Call with decent hands
                        elif rule['call_range'][0] <= hs <= rule['call_range'][1]:
                            return ('call', to_call)
                        
                        # Otherwise fold (but could add defend frequency logic here)
                        else:
                            return ('fold', 0)
                
                # Fallback to standard rules if no blind defense
                if pos in strategy['preflop']['vs_raise']:
                    rule = strategy['preflop']['vs_raise'][pos][pos_type]
                    if hs >= rule['value_thresh']: 
                        return ('raise', rule['sizing'] * 3)
                    if rule['call_range'][0] <= hs <= rule['call_range'][1]: 
                        return ('call', to_call)
                    return ('fold', 0)
                else:
                    # Ultra fallback - use BTN rules
                    rule = strategy['preflop']['vs_raise']['BTN'][pos_type]
                    if hs >= rule['value_thresh']: 
                        return ('raise', rule['sizing'] * 3)
                    if rule['call_range'][0] <= hs <= rule['call_range'][1]: 
                        return ('call', to_call)
                    return ('fold', 0)
            
            elif actions == ['raise']:
                # Non-blind facing a raise (unchanged)
                rule = strategy['preflop']['vs_raise'][pos][pos_type]
                if hs >= rule['value_thresh']: 
                    return ('raise', rule['sizing'] * 3)
                if rule['call_range'][0] <= hs <= rule['call_range'][1]: 
                    return ('call', to_call)
                return ('fold', 0)
                
        else: # Postflop
            # Original postflop logic with added safety checks
            if pfa and not actions:
                # Check if position exists in strategy
                if pos in strategy['postflop']['pfa'][street]:
                    rule = strategy['postflop']['pfa'][street][pos][pos_type]
                elif 'BB' in strategy['postflop']['pfa'][street] and pos in ['BB', 'SB']:
                    # Use blind-specific rules if available
                    rule = strategy['postflop']['pfa'][street][pos][pos_type]
                else:
                    # Fallback to BTN rules
                    rule = strategy['postflop']['pfa'][street]['BTN'][pos_type]
                
                if hs >= rule['val_thresh']: 
                    return ('bet', pot * rule['sizing'])
                if hs >= rule['check_thresh']: 
                    return ('check', 0)
                return ('check', 0)
            
            if not pfa and actions == ['bet']:
                # Check if position exists in strategy
                if pos in strategy['postflop']['caller'][street]:
                    rule = strategy['postflop']['caller'][street][pos][pos_type]
                elif 'BB' in strategy['postflop']['caller'][street] and pos in ['BB', 'SB']:
                    # Use blind-specific rules if available
                    rule = strategy['postflop']['caller'][street][pos][pos_type]
                else:
                    # Fallback to BTN rules
                    rule = strategy['postflop']['caller'][street]['BTN'][pos_type]
                
                bet_ratio = to_call / pot if pot > 0 else 1
                bet_category = ('large_bet' if bet_ratio > 1 else 
                              'medium_bet' if bet_ratio >= 0.5 else 'small_bet')
                val_raise, call_thresh = rule[bet_category]
                
                # Pot odds adjustment for blinds
                if pos == 'BB' and street == 'flop':
                    # BB defends wider with good pot odds
                    call_thresh = max(5, call_thresh - 5)
                
                if hs >= val_raise: 
                    return ('raise', to_call * 2.5)
                if hs >= call_thresh: 
                    return ('call', to_call)
                return ('fold', 0)
                
    except KeyError as e:
        # Safe fallback
        print(f"Warning: Strategy lookup failed: {e}")
        return ('check' if to_call == 0 else 'fold', 0)
    
    return ('check' if to_call == 0 else 'fold', 0)


class Player:
    def __init__(self, name, seat_number, is_user=False):
        self.name = name
        self.seat_number = seat_number  # FIXED seat at the table (0-5)
        self.is_user = is_user
        self.stack = 100
        self.hole = []
        self.is_active = True
        self.contributed_this_street = 0
        self.was_aggressor = False
        self.current_position = None  # This will change each hand!

    def get_action(self, game_state, strategy, hand_evaluator):
        if self.is_user:
            return self._get_user_action(game_state)
        else:
            # ALL NON-USER PLAYERS EXECUTE STRATEGY PERFECTLY
            return get_optimal_action(game_state, strategy)
    
    def _get_user_action(self, game_state):
        """Enhanced user action interface."""
        print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
        
        # Enhanced display with color coding
        hand_str = f"{Colors.BOLD}{' '.join(self.hole)}{Colors.END}"
        hs_val = game_state['dynamic_hs'] if game_state['street'] != 'preflop' else game_state['preflop_hs']
        
        # Color code hand strength
        if hs_val >= 80:
            hs_color = Colors.GREEN
        elif hs_val >= 60:
            hs_color = Colors.YELLOW
        elif hs_val >= 40:
            hs_color = Colors.BLUE
        else:
            hs_color = Colors.RED
        
        print(f"Your Hand: {hand_str} (HS: {hs_color}{hs_val}{Colors.END})")
        print(f"Your Seat: #{self.seat_number} | Current Position: {Colors.BLUE}{self.current_position}{Colors.END}")
        
        # Show additional information if available
        if game_state['street'] != 'preflop' and 'postflop_details' in game_state:
            details = game_state['postflop_details']
            print(f"Hand Type: {Colors.CYAN}{details.get('rank', 'unknown').replace('_', ' ').title()}{Colors.END}")
            
            if details.get('is_draw'):
                print(f"Draw: {Colors.PURPLE}Yes{Colors.END} (Outs: {details.get('outs', 0)})")
            
            if 'board_texture' in details:
                texture = details['board_texture'].title()
                print(f"Board Texture: {Colors.YELLOW}{texture}{Colors.END}")
            
            if 'equity_estimate' in details:
                equity = details['equity_estimate']
                equity_color = Colors.GREEN if equity >= 60 else Colors.YELLOW if equity >= 40 else Colors.RED
                print(f"Estimated Equity: {equity_color}{equity:.1f}%{Colors.END}")
        
        if game_state['board']: 
            board_str = f"{Colors.YELLOW}{' '.join(game_state['board'])}{Colors.END}"
            print(f"Board: {board_str}")
        
        print(f"Pot: {Colors.GREEN}{game_state['pot']:.1f} BB{Colors.END} | "
              f"To Call: {Colors.RED if game_state['to_call'] > 0 else Colors.GREEN}{game_state['to_call']:.1f} BB{Colors.END}")
        print(f"Stack: {Colors.CYAN}{self.stack:.1f} BB{Colors.END}")
        
        # Show available actions
        available_actions = []
        if game_state['to_call'] == 0:
            available_actions.extend([f"{Colors.CYAN}check (k){Colors.END}", f"{Colors.GREEN}bet (b){Colors.END}"])
        else:
            available_actions.extend([
                f"{Colors.RED}fold (f){Colors.END}", 
                f"{Colors.YELLOW}call (c){Colors.END}", 
                f"{Colors.GREEN}raise (r){Colors.END}"
            ])
        
        print(f"Available actions: {', '.join(available_actions)}")
        
        action_map = {'f': 'fold', 'c': 'call', 'k': 'check', 'b': 'bet', 'r': 'raise'}
        
        while True:
            user_input = input(f"\n{Colors.BOLD}Your action: {Colors.END}").lower().strip()
            action = action_map.get(user_input)
            if not action: 
                print(f"{Colors.RED}Invalid action. Try again.{Colors.END}")
                continue
            if action in ['bet', 'raise']:
                try: 
                    size = float(input("Enter size in BB: "))
                    return action, size
                except ValueError: 
                    print(f"{Colors.RED}Invalid size. Try again.{Colors.END}")
                    continue
            return action, 0

class AdvancedGame:
    def __init__(self, num_players=6, mode='normal'):
        if num_players < 3 or num_players > 9:
            raise ValueError("Number of players must be between 3 and 9.")
        self.mode = mode
        self.session_id = None
        
        # Load strategy
        try:
            with open('strategy.json', 'r') as f:
                self.strategy = json.load(f)
            print(f"{Colors.GREEN}✅ Strategy file loaded successfully.{Colors.END}")
        except FileNotFoundError:
            print(f"{Colors.RED}❌ FATAL: 'strategy.json' not found.{Colors.END}")
            sys.exit(1)

        # Initialize components
        self.hand_evaluator = AdvancedHandEvaluator(self.strategy)
        
        if SESSION_LOGGING:
            self.session_logger = SessionLogger()
            self.session_analyzer = SessionAnalyzer()
            self.training_manager = TrainingModeManager(self.strategy, self.session_logger)
        else:
            self.session_logger = None
            self.session_analyzer = None
            self.training_manager = None

        # CORRECTED: Create players with FIXED SEATS
        self.num_players = num_players
        self.players = []
        
        # Create players at seats 0 through num_players-1
        for seat_num in range(num_players):
            player = Player(f"P{seat_num}", seat_num, is_user=False)
            self.players.append(player)
        
        # Randomly assign one player to be the user
        user_seat = random.randint(0, num_players - 1)
        self.players[user_seat].is_user = True
        self.players[user_seat].name = "You"
        self.user_player = self.players[user_seat]
        
        # Start with dealer at seat 0
        self.dealer_seat = 0
        self.hand_count = 0
        self.session_stats = defaultdict(lambda: {'correct': 0, 'total': 0})
        
        # Show initial table setup
        print(f"\n{Colors.BOLD}🎰 TABLE SETUP{Colors.END}")
        print(f"Number of players: {num_players}")
        print(f"Your seat: #{self.user_player.seat_number}")
        print("\nSeat assignments:")
        for player in self.players:
            user_marker = " (YOU)" if player.is_user else ""
            print(f"  Seat #{player.seat_number}: {player.name}{user_marker}")

    def _get_position_for_seat(self, seat_number, dealer_seat):
        """Calculate the position name for a given seat based on dealer location."""
        # Positions in clockwise order from dealer
        if self.num_players == 9:
            positions = ['BTN', 'SB', 'BB', 'UTG', 'UTG+1', 'UTG+2', 'MP', 'HJ', 'CO']
        elif self.num_players == 8:
            positions = ['BTN', 'SB', 'BB', 'UTG', 'UTG+1', 'UTG+2', 'HJ', 'CO']  # Drop one MP for 8-max
        elif self.num_players == 7:
            positions = ['BTN', 'SB', 'BB', 'UTG', 'UTG+1', 'MP', 'CO']  # Simplified
        elif self.num_players == 6:
            positions = ['BTN', 'SB', 'BB', 'UTG', 'MP', 'CO']
        elif self.num_players == 5:
            positions = ['BTN', 'SB', 'BB', 'CO', 'BTN']  # In 5-max, CO acts as UTG
        elif self.num_players == 4:
            positions = ['BTN', 'SB', 'BB', 'CO']
        elif self.num_players == 3:
            positions = ['BTN', 'SB', 'BB']
        else:
            positions = ['BTN', 'SB', 'BB'] + [f'P{i}' for i in range(3, self.num_players)]  # Generic fallback
        
        position_index = (seat_number - dealer_seat) % self.num_players
        return positions[position_index]

    def _update_all_positions(self):
        """Update current_position for all players based on dealer location."""
        for player in self.players:
            player.current_position = self._get_position_for_seat(player.seat_number, self.dealer_seat)

    def _get_player_at_position(self, position):
        """Get the player currently at a specific position."""
        for player in self.players:
            if player.current_position == position:
                return player
        return None

    def _get_action_order(self, street):
        """Get the correct action order for the current street."""
        if self.num_players == 9:
            if street == 'preflop':
                order = ['UTG', 'UTG+1', 'UTG+2', 'MP', 'HJ', 'CO', 'BTN', 'SB', 'BB']
            else:
                order = ['SB', 'BB', 'UTG', 'UTG+1', 'UTG+2', 'MP', 'HJ', 'CO', 'BTN']
        elif self.num_players == 8:
            if street == 'preflop':
                order = ['UTG', 'UTG+1', 'UTG+2', 'HJ', 'CO', 'BTN', 'SB', 'BB']
            else:
                order = ['SB', 'BB', 'UTG', 'UTG+1', 'UTG+2', 'HJ', 'CO', 'BTN']
        elif self.num_players == 7:
            if street == 'preflop':
                order = ['UTG', 'UTG+1', 'MP', 'CO', 'BTN', 'SB', 'BB']
            else:
                order = ['SB', 'BB', 'UTG', 'UTG+1', 'MP', 'CO', 'BTN']
        elif self.num_players == 6:
            if street == 'preflop':
                order = ['UTG', 'MP', 'CO', 'BTN', 'SB', 'BB']
            else:
                order = ['SB', 'BB', 'UTG', 'MP', 'CO', 'BTN']
        elif self.num_players == 5:
            if street == 'preflop':
                order = ['CO', 'BTN', 'SB', 'BB']  # CO acts as UTG in 5-max
            else:
                order = ['SB', 'BB', 'CO', 'BTN']
        elif self.num_players == 4:
            if street == 'preflop':
                order = ['CO', 'BTN', 'SB', 'BB']
            else:
                order = ['SB', 'BB', 'CO', 'BTN']
        elif self.num_players == 3:
            if street == 'preflop':
                order = ['BTN', 'SB', 'BB']
            else:
                order = ['SB', 'BB', 'BTN']
        
        # Return only positions that exist at this table
        return [pos for pos in order if self._get_player_at_position(pos) is not None]

    def start_session(self):
        """Start a new training session."""
        if self.session_logger:
            self.session_id = self.session_logger.start_session("8.4")
            print(f"{Colors.GREEN}📊 Session logging started: {self.session_id}{Colors.END}")

    def play_hand(self):
        """Play a single hand with proper position rotation."""
        self.hand_count += 1
        print(f"\n{Colors.BOLD}{'='*20} Hand #{self.hand_count} {'='*20}{Colors.END}")
        
        # Rotate dealer button
        self.dealer_seat = (self.dealer_seat + 1) % self.num_players
        self._update_all_positions()
        
        # Show current positions
        print(f"Dealer button at seat #{self.dealer_seat}")
        print("Current positions:")
        for player in sorted(self.players, key=lambda p: p.seat_number):
            user_marker = " (YOU)" if player.is_user else ""
            print(f"  Seat #{player.seat_number}: {player.current_position}{user_marker}")
        
        deck = get_shuffled_deck()
        self._reset_hand_and_deal(deck)
        
        for street in ['preflop', 'flop', 'turn', 'river']:
            if len([p for p in self.players if p.is_active]) <= 1: 
                break
            print(f"\n{Colors.BOLD}--- {street.upper()} ---{Colors.END}")
            if street == 'flop': 
                self.board.extend([deck.pop() for _ in range(3)])
            elif street != 'preflop': 
                self.board.append(deck.pop())
            if self.board: 
                print(f"Board: {Colors.YELLOW}{' '.join(self.board)}{Colors.END}")
            self._run_betting_round(street)
        self._showdown()

    def _run_betting_round(self, street):
        """Run a betting round with proper action order based on positions."""
        
        # Reset street contributions for postflop
        if street != 'preflop':
            for p in self.players: 
                p.contributed_this_street = 0
            self.to_call = 0
        
        # Get correct action order for this street
        action_order = self._get_action_order(street)
        
        # Build list of players to act in correct order
        players_to_act = []
        for position in action_order:
            player = self._get_player_at_position(position)
            if player and player.is_active:
                players_to_act.append(player)
        
        # Show action order
        positions_str = ' → '.join([p.current_position for p in players_to_act])
        print(f"\n{Colors.CYAN}Action order: {positions_str}{Colors.END}")
        
        last_aggressor = None
        action_complete = False
        
        while players_to_act and not action_complete:
            player = players_to_act.pop(0)
            if not player.is_active or player.stack == 0: 
                continue
            if player == last_aggressor: 
                action_complete = True
                break

            # Check if action is already closed
            remaining_active = [p for p in self.players if p.is_active]
            if len(remaining_active) == 1:
                winner = remaining_active[0]
                if street == 'preflop' and winner.current_position == 'BB' and self.to_call == 1.0:
                    print(f"\n{Colors.GREEN}→ {winner.current_position} wins uncontested pot of {self.pot:.1f} BB (everyone folded to BB){Colors.END}")
                else:
                    print(f"\n{Colors.GREEN}→ {winner.current_position} wins uncontested pot of {self.pot:.1f} BB{Colors.END}")
                winner.stack += self.pot
                return

            # Calculate actual amount to call
            amount_to_call = max(0, self.to_call - player.contributed_this_street)
            
            # Special case: BB option when no one raised preflop
            if (street == 'preflop' and player.current_position == 'BB' and 
                self.to_call == 1.0 and amount_to_call == 0):
                print(f"\n{Colors.BLUE}→ {player.current_position} wins uncontested pot of {self.pot:.1f} BB (everyone folded to BB){Colors.END}")
                player.stack += self.pot
                return

            # Show whose turn it is
            if player.is_user:
                print(f"\n{Colors.BOLD}🎯 YOUR TURN ({player.current_position}){Colors.END}")
            else:
                print(f"\n→ {player.current_position} (Seat #{player.seat_number})'s turn...", end="", flush=True)

            # Calculate hand strength and get action
            preflop_hs = self.hand_evaluator.get_preflop_hs(player.hole)
            
            if street != 'preflop':
                action_history = ['bet'] if amount_to_call > 0 else []
                postflop_eval = self.hand_evaluator.get_postflop_evaluation(
                    player.hole, self.board, player.current_position, action_history
                )
                dynamic_hs = postflop_eval['hs']
                postflop_details = postflop_eval
            else:
                dynamic_hs = preflop_hs
                postflop_details = {}

            # Calculate if player is in position
            is_ip = self._calculate_is_ip(player, players_to_act, street)

            game_state = {
                'preflop_hs': preflop_hs,
                'dynamic_hs': dynamic_hs,
                'postflop_rank': postflop_details.get('rank', 'unknown'),
                'postflop_details': postflop_details,
                'position': player.current_position,  # Use current position!
                'is_ip': is_ip,
                'street': street,
                'history': ['bet'] if amount_to_call > 0 else [],
                'pot': self.pot, 
                'to_call': amount_to_call,
                'hole': player.hole, 
                'board': self.board, 
                'was_aggressor': player.was_aggressor,
            }
            
            # Get action
            decision_start_time = time.time()
            action, size = player.get_action(game_state, self.strategy, self.hand_evaluator)
            decision_time = time.time() - decision_start_time

            # Show action result
            if not player.is_user:
                print()  # New line after "X's turn..."

            if player.is_user:
                self._handle_user_decision(player, game_state, action, size, decision_time)

            # Execute the action
            self._execute_action(player, action, size, game_state)
            
            # Update game state based on action
            if action in ['bet', 'raise']:
                last_aggressor = player
                # Add all remaining active players back to the action queue
                new_players_to_act = []
                for position in action_order:
                    p = self._get_player_at_position(position)
                    if p and p.is_active and p != player:
                        new_players_to_act.append(p)
                players_to_act = new_players_to_act
                print(f"{Colors.YELLOW}   (Action reopened to all players){Colors.END}")
            elif action == 'fold':
                # Check if only one player remains
                remaining_players = [p for p in self.players if p.is_active]
                if len(remaining_players) == 1:
                    winner = remaining_players[0]
                    print(f"\n{Colors.GREEN}→ {winner.current_position} wins uncontested pot of {self.pot:.1f} BB{Colors.END}")
                    winner.stack += self.pot
                    return
            
            # Show current pot and action status
            active_count = len([p for p in self.players if p.is_active])
            if active_count > 1:
                status_msg = f"{Colors.CYAN}   Pot: {self.pot:.1f} BB"
                if self.to_call > 0:
                    status_msg += f" | To call: {self.to_call:.1f} BB"
                status_msg += f" | Active: {active_count} players{Colors.END}"
                print(status_msg)
            
            # Small delay for non-user actions
            if not player.is_user:
                time.sleep(0.8)

    def _calculate_is_ip(self, player, players_remaining, street):
        """Calculate if player is in position."""
        # On the button, always IP
        if player.current_position == 'BTN':
            return True
        
        # If no players left to act after us, we're IP
        if not players_remaining:
            return True
        
        # If button is still to act, we're OOP
        for p in players_remaining:
            if p.current_position == 'BTN':
                return False
        
        return True

    def _handle_user_decision(self, player, game_state, action, size, decision_time):
        """Handle user decision with feedback and logging."""
        opt_action, opt_size = get_optimal_action(game_state, self.strategy)
        is_correct = (action == opt_action)
        
        # Update session stats
        street = game_state['street']
        self.session_stats[street]['total'] += 1
        if is_correct:
            self.session_stats[street]['correct'] += 1
        
        # Provide feedback
        if is_correct: 
            print(f"{Colors.GREEN}✅ Correct!{Colors.END}")
            if decision_time < 3:
                print(f"{Colors.CYAN}⚡ Quick decision! ({decision_time:.1f}s){Colors.END}")
        else: 
            print(f"{Colors.RED}❌ Incorrect! Optimal was {opt_action.upper()}")
            if opt_size > 0:
                print(f"   Suggested sizing: ~{opt_size:.1f} BB{Colors.END}")
            if decision_time > 15:
                print(f"{Colors.YELLOW}⏰ Consider practicing this spot more.{Colors.END}")
        
        # Log to database if available
        if self.session_logger and self.session_id:
            decision_data = {
                'hand_number': self.hand_count,
                'street': street,
                'position': player.current_position,
                'is_ip': game_state['is_ip'],
                'hole_cards': ' '.join(player.hole),
                'board_cards': ' '.join(game_state['board']),
                'pot_size': game_state['pot'],
                'to_call': game_state['to_call'],
                'stack_size': player.stack,
                'preflop_hs': game_state['preflop_hs'],
                'postflop_hs': game_state['dynamic_hs'],
                'hand_rank': game_state['postflop_rank'],
                'action_history': json.dumps(game_state['history']),
                'was_pfa': game_state['was_aggressor'],
                'user_action': action,
                'user_size': size,
                'optimal_action': opt_action,
                'optimal_size': opt_size,
                'is_correct': is_correct,
                'decision_time': decision_time
            }
            self.session_logger.log_decision(self.session_id, decision_data)

    def _execute_action(self, player, action, size, game_state):
        """Execute a player's action with clear messaging."""
        pos_str = f"{player.current_position} (Seat #{player.seat_number})"
        
        if action == 'fold': 
            player.is_active = False
            print(f"   {Colors.RED}{pos_str} folds{Colors.END}")
        elif action == 'check':
            if game_state['to_call'] > 0: 
                player.is_active = False
                print(f"   {Colors.RED}{pos_str} folds (can't check when facing a bet){Colors.END}")
            else: 
                print(f"   {Colors.BLUE}{pos_str} checks{Colors.END}")
        elif action == 'call':
            amount = min(game_state['to_call'], player.stack)
            self.pot += amount
            player.stack -= amount
            player.contributed_this_street += amount
            print(f"   {Colors.YELLOW}{pos_str} calls {amount:.1f} BB{Colors.END}")
        elif action in ['bet', 'raise']:
            amount = min(size, player.stack)
            self.pot += amount
            player.stack -= amount
            player.contributed_this_street += amount
            self.to_call = player.contributed_this_street
            action_word = 'bets' if action == 'bet' else 'raises to'
            print(f"   {Colors.GREEN}{pos_str} {action_word} {self.to_call:.1f} BB{Colors.END}")
            player.was_aggressor = True

    def _reset_hand_and_deal(self, deck):
        """Reset hand state and deal cards, maintaining stack sizes."""
        self.board = []
        self.pot = 0
        self.to_call = 0
        
        # Reset hand-specific state but maintain stack sizes
        for p in self.players: 
            p.hole = []
            p.is_active = True
            p.contributed_this_street = 0
            p.was_aggressor = False
            
            # Ensure minimum stack for blinds
            if p.stack < 1.0:
                print(f"{Colors.YELLOW}Player at seat #{p.seat_number} reloaded to 100 BB{Colors.END}")
                p.stack = 100.0
        
        # Post blinds based on positions
        sb_player = self._get_player_at_position('SB')
        bb_player = self._get_player_at_position('BB')
        
        # Small blind
        sb_amount = min(0.5, sb_player.stack)
        sb_player.stack -= sb_amount
        sb_player.contributed_this_street = sb_amount
        self.pot += sb_amount
        
        # Big blind  
        bb_amount = min(1.0, bb_player.stack)
        bb_player.stack -= bb_amount
        bb_player.contributed_this_street = bb_amount
        self.pot += bb_amount
        self.to_call = bb_amount
        
        # Deal hole cards
        for p in self.players: 
            p.hole = [deck.pop(), deck.pop()]
        
        print(f"\nDealing hands...")
        print(f"Blinds: {sb_player.current_position} posts SB ({sb_amount:.1f}), "
              f"{bb_player.current_position} posts BB ({bb_amount:.1f})")
        
        # Show stack sizes occasionally
        if self.hand_count % 10 == 1:  # Every 10 hands
            print("\nCurrent Stacks:")
            for p in sorted(self.players, key=lambda x: x.seat_number):
                color = Colors.GREEN if p.stack > 90 else Colors.YELLOW if p.stack > 50 else Colors.RED
                user_marker = " (YOU)" if p.is_user else ""
                print(f"  Seat #{p.seat_number}: {color}{p.stack:.1f} BB{Colors.END}{user_marker}")

    def _showdown(self):
        """Handle showdown with proper hand evaluation."""
        print(f"\n{Colors.BOLD}--- SHOWDOWN ---{Colors.END}")
        active = [p for p in self.players if p.is_active]
        if not active: 
            return
        if len(active) == 1: 
            winner = active[0]
            print(f"{winner.current_position} wins uncontested pot of {Colors.GREEN}{self.pot:.1f} BB{Colors.END}.")
        else: 
            # Use proper hand evaluation
            if SESSION_LOGGING and self.hand_evaluator.enhanced_evaluator and len(self.board) == 5:
                # Use enhanced evaluator for accurate showdown
                best_hand = None
                best_player = None
                
                for p in active:
                    try:
                        evaluation = self.hand_evaluator.enhanced_evaluator.evaluate_hand(p.hole, self.board)
                        hand_rank = (evaluation['hand_rank'], evaluation['rank_values'])
                        
                        if best_hand is None or self.hand_evaluator.enhanced_evaluator._compare_hands(hand_rank, best_hand) > 0:
                            best_hand = hand_rank
                            best_player = p
                    except:
                        # Fallback
                        if best_player is None:
                            best_player = p
                
                winner = best_player
            else:
                # Fallback to highest preflop hand strength
                winner = max(active, key=lambda p: self.hand_evaluator.get_preflop_hs(p.hole))
            
            print(f"{winner.current_position} shows {Colors.BOLD}{' '.join(winner.hole)}{Colors.END} "
                  f"and wins {Colors.GREEN}{self.pot:.1f} BB{Colors.END}.")
            
            # Show other hands at showdown
            for p in active:
                if p != winner:
                    print(f"{p.current_position} shows {' '.join(p.hole)}")
        
        winner.stack += self.pot

    def _show_quick_stats(self):
        """Show quick session statistics."""
        total_decisions = sum(stats['total'] for stats in self.session_stats.values())
        if total_decisions > 0:
            total_correct = sum(stats['correct'] for stats in self.session_stats.values())
            accuracy = (total_correct / total_decisions) * 100
            color = Colors.GREEN if accuracy >= 80 else Colors.YELLOW if accuracy >= 60 else Colors.RED
            print(f"\nSession Accuracy: {color}{accuracy:.1f}%{Colors.END} "
                  f"({total_correct}/{total_decisions})")

    def show_main_menu(self):
        """Display the main menu."""
        print(f"\n{Colors.BOLD}🃏 ADVANCED HOLD'EM TRAINER v8.4 🃏{Colors.END}")
        print(f"{Colors.CYAN}{'='*50}{Colors.END}")
        print("1. Normal Training - Standard poker practice")
        print("2. Drill Mode - Focus on specific scenarios")
        print("3. Speed Training - Time-limited decisions")
        print("4. Blind Training - Limited information practice")
        print("5. Mistake Review - Practice previous errors")
        print("6. View Statistics - Analyze your performance")
        print("7. Comprehensive Report - Detailed analysis")
        print("8. Quit")
        
        choice = input(f"\n{Colors.BOLD}Choose an option (1-8): {Colors.END}").strip()
        return choice

    def play_normal_training(self):
        """Run normal training mode."""
        print(f"\n{Colors.BOLD}🎯 NORMAL TRAINING MODE{Colors.END}")
        
        self.start_session()
        
        while True:
            self.play_hand()
            
            # Show quick stats
            self._show_quick_stats()
            
            continue_choice = input("\nContinue? (y/n/stats/menu): ").lower().strip()
            if continue_choice == 'stats':
                self._show_session_stats()
                continue_choice = input("\nContinue training? (y/n/menu): ").lower().strip()
            
            if continue_choice == 'menu':
                break
            elif continue_choice != 'y':
                self._end_session()
                break

    def _show_session_stats(self):
        """Show detailed session statistics."""
        print(f"\n{Colors.BOLD}📊 SESSION STATISTICS{Colors.END}")
        print(f"{Colors.CYAN}{'='*40}{Colors.END}")
        
        total_decisions = sum(stats['total'] for stats in self.session_stats.values())
        if total_decisions == 0:
            print("No decisions made yet.")
            return
        
        total_correct = sum(stats['correct'] for stats in self.session_stats.values())
        overall_accuracy = (total_correct / total_decisions) * 100
        
        print(f"Overall: {total_correct}/{total_decisions} ({overall_accuracy:.1f}%)")
        print("\nBy Street:")
        for street, stats in self.session_stats.items():
            if stats['total'] > 0:
                acc = (stats['correct'] / stats['total']) * 100
                color = Colors.GREEN if acc >= 80 else Colors.YELLOW if acc >= 60 else Colors.RED
                print(f"  {street.title()}: {color}{acc:.1f}%{Colors.END} "
                      f"({stats['correct']}/{stats['total']})")

    def _end_session(self):
        """End the current session."""
        if self.session_logger and self.session_id:
            total_decisions = sum(stats['total'] for stats in self.session_stats.values())
            total_correct = sum(stats['correct'] for stats in self.session_stats.values())
            self.session_logger.end_session(
                self.session_id, self.hand_count, total_decisions, total_correct
            )
            print(f"{Colors.GREEN}📊 Session data saved.{Colors.END}")

    def run(self):
        """Main game loop."""
        while True:
            choice = self.show_main_menu()
            
            if choice == '1':
                self.play_normal_training()
            elif choice in ['2', '3', '4', '5']:
                print(f"{Colors.YELLOW}Advanced training modes require full module installation.{Colors.END}")
            elif choice == '6' or choice == '7':
                if self.session_analyzer:
                    if choice == '6':
                        recent = self.session_analyzer.get_recent_performance(7)
                        if recent:
                            print(f"\n{Colors.BOLD}📈 RECENT PERFORMANCE (7 days){Colors.END}")
                            print(f"Sessions: {recent['sessions_count']}")
                            print(f"Average Accuracy: {recent['avg_accuracy']:.1f}%")
                            print(f"Trend: {recent['accuracy_trend'].title()}")
                        else:
                            print("No recent data available.")
                    else:
                        self.session_analyzer.print_comprehensive_report()
                else:
                    print("Statistics require session logging modules.")
            elif choice == '8':
                print(f"{Colors.CYAN}Thanks for training! Keep improving your game! 🃏{Colors.END}")
                break
            else:
                print(f"{Colors.RED}Invalid choice. Please try again.{Colors.END}")

def main():
    """Main entry point."""
    print(f"{Colors.BOLD}🃏 Welcome to Advanced Hold'em Trainer! 🃏{Colors.END}")
    
    # Check for required files
    try:
        with open('strategy.json', 'r') as f:
            json.load(f)
    except FileNotFoundError:
        print(f"{Colors.RED}Error: strategy.json not found. Please run strategy_manager.py first.{Colors.END}")
        return
    
    # Get number of players
    num_players = 6
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        num_players = int(sys.argv[1])
        if num_players < 3 or num_players > 6:
            print(f"{Colors.YELLOW}Number of players must be between 3 and 6. Using 6 players.{Colors.END}")
            num_players = 6
    
    try:
        game = AdvancedGame(num_players=num_players)
        game.run()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Training interrupted. See you next time!{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.END}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()