"""
Pure Poker State Machine - Clean Architecture

This is a pure poker rules engine that:
- Manages only poker state transitions
- Has no knowledge of human vs bot players
- Has no application-specific logic
- Uses dependency injection for all external concerns
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Protocol
from enum import Enum
import time

from .poker_types import Player, PokerState, GameState
from .hand_model import ActionType
from .session_logger import get_session_logger


class DeckProvider(Protocol):
    """Protocol for deck management."""
    def get_deck(self) -> List[str]:
        """Get a fresh deck of cards."""
        pass
    
    def replace_deck(self, deck: List[str]) -> None:
        """Replace the current deck."""
        pass


class RulesProvider(Protocol):
    """Protocol for poker rules."""
    def get_first_to_act_preflop(self, dealer_pos: int, num_players: int) -> int:
        """Get first player to act preflop."""
        pass
    
    def get_first_to_act_postflop(self, dealer_pos: int, players: List[Player]) -> int:
        """Get first active player to act postflop."""
        pass


class AdvancementController(Protocol):
    """Protocol for controlling game advancement."""
    def should_advance_automatically(self, current_state: PokerState, players: List[Player]) -> bool:
        """Determine if the game should advance automatically."""
        pass
    
    def on_round_complete(self, street: str, game_state: GameState) -> None:
        """Handle round completion."""
        pass


class DecisionEngineProtocol(Protocol):
    """Protocol for decision engines that can provide actions for players."""
    
    def get_decision(self, player_name: str, game_state: GameState) -> tuple:
        """
        Get the decision for a player in the current game state.
        
        Returns:
            tuple: (ActionType, amount) or None if no decision available
        """
        pass
    
    def has_decision_for_player(self, player_name: str) -> bool:
        """Check if engine has a decision for the specified player."""
        pass
    
    def reset_for_new_hand(self) -> None:
        """Reset engine state for a new hand."""
        pass


@dataclass
class GameConfig:
    """Pure game configuration without application context."""
    num_players: int = 2
    small_blind: float = 1.0
    big_blind: float = 2.0
    starting_stack: float = 200.0


class PurePokerStateMachine:
    """
    Pure poker state machine that only handles poker rules and state transitions.
    
    All application-specific concerns (human vs bot, auto-advance, deck management)
    are handled through injected providers and controllers.
    """
    
    # Valid state transitions (pure poker rules)
    STATE_TRANSITIONS = {
        PokerState.START_HAND: [PokerState.PREFLOP_BETTING],
        PokerState.PREFLOP_BETTING: [PokerState.DEAL_FLOP, PokerState.END_HAND],
        PokerState.DEAL_FLOP: [PokerState.FLOP_BETTING, PokerState.END_HAND],
        PokerState.FLOP_BETTING: [PokerState.DEAL_TURN, PokerState.END_HAND],
        PokerState.DEAL_TURN: [PokerState.TURN_BETTING, PokerState.END_HAND],
        PokerState.TURN_BETTING: [PokerState.DEAL_RIVER, PokerState.END_HAND],
        PokerState.DEAL_RIVER: [PokerState.RIVER_BETTING, PokerState.END_HAND],
        PokerState.RIVER_BETTING: [PokerState.SHOWDOWN, PokerState.END_HAND],
        PokerState.SHOWDOWN: [PokerState.END_HAND],
        PokerState.END_HAND: [PokerState.START_HAND],
    }
    
    def __init__(
        self, 
        config: GameConfig,
        deck_provider: Optional[DeckProvider] = None,
        rules_provider: Optional[RulesProvider] = None,
        advancement_controller: Optional[AdvancementController] = None,
        decision_engine: Optional[DecisionEngineProtocol] = None
    ):
        """Initialize pure poker state machine with injected dependencies."""
        self.config = config
        self.deck_provider = deck_provider
        self.rules_provider = rules_provider
        self.advancement_controller = advancement_controller
        self.decision_engine = decision_engine
        
        # Pure poker state
        self.game_state = GameState(
            players=[],
            board=[],
            committed_pot=0.0,
            current_bet=0.0,
            street="preflop",
            big_blind=config.big_blind
        )
        self.current_state = PokerState.START_HAND
        self.hand_number = 0
        self.action_player_index = 0
        self.dealer_position = 0
        self.small_blind_position = 0
        self.big_blind_position = 1
        
        # Round tracking - FIXED: Better tracking
        self.actions_this_round = 0
        self.players_acted_this_round: set = set()
        self.last_raiser_name: Optional[str] = None  # Track who made the last raise
        self.last_bet_size = 0.0  # Track last bet/raise size for min raise
        
        # Logging
        self.session_logger = get_session_logger()
        
        # Initialize players
        self._initialize_players()
        
        print(f"🔧 FIXED_PPSM: Initialized with {config.num_players} players")
    
    def _initialize_players(self):
        """Initialize players with pure poker data (no human/bot distinction)."""
        self.game_state.players = []
        for i in range(self.config.num_players):
            player = Player(
                name=f"Seat{i + 1}",
                stack=self.config.starting_stack,
                position="",
                is_human=False,  # Pure FPSM doesn't care about this
                is_active=True,
                cards=[],
            )
            self.game_state.players.append(player)
        
        # Assign positions
        self._assign_positions()
    
    def _assign_positions(self):
        """Assign poker positions relative to dealer."""
        num_players = len(self.game_state.players)
        if num_players == 2:
            # Heads-up: dealer is small blind
            positions = ["SB", "BB"]
        else:
            # Multi-way: standard positions
            positions = self._get_standard_positions(num_players)
        
        for i, player in enumerate(self.game_state.players):
            position_offset = (i - self.dealer_position) % num_players
            if position_offset < len(positions):
                player.position = positions[position_offset]
            else:
                player.position = f"Seat{i + 1}"
    
    def _get_standard_positions(self, num_players: int) -> List[str]:
        """Get standard poker position names."""
        if num_players <= 2:
            return ["SB", "BB"]
        elif num_players <= 6:
            return ["SB", "BB", "UTG", "MP", "CO", "BTN"][:num_players]
        else:
            # For larger games, add MP positions
            positions = ["SB", "BB", "UTG"]
            mp_count = num_players - 5  # Subtract SB, BB, UTG, CO, BTN
            for i in range(1, mp_count + 1):
                positions.append(f"MP{i}")
            positions.extend(["CO", "BTN"])
            return positions
    
    def start_hand(self, existing_players: Optional[List[Player]] = None):
        """Start a new hand with pure poker logic."""
        self.hand_number += 1
        self.current_state = PokerState.START_HAND
        
        # --- NEW: rotate dealer starting on the 2nd hand ---
        if self.hand_number > 1:
            self.dealer_position = (self.dealer_position + 1) % self.config.num_players

        # Reset game state for the new hand
        self.game_state.board = []
        self.game_state.committed_pot = 0.0
        self.game_state.current_bet = 0.0
        self.game_state.street = "preflop"
        # Reset round state for new hand
        from .poker_types import RoundState
        self.game_state.round_state = RoundState()
        
        # Use existing players if provided, otherwise the initialized ones
        if existing_players:
            self.game_state.players = existing_players
            if len(self.game_state.players) != self.config.num_players:
                raise ValueError(
                    f"Expected {self.config.num_players} players, got {len(self.game_state.players)}"
                )
        
        # Reset per-player state
        for player in self.game_state.players:
            player.current_bet = 0.0
            player.has_folded = False
            player.is_active = True
            player.cards = []
        
        # --- NEW: compute blind seats from current dealer ---
        if self.config.num_players == 2:
            # Heads-up: dealer is SB
            self.small_blind_position = self.dealer_position
            self.big_blind_position = (self.dealer_position + 1) % self.config.num_players
        else:
            # 3+ players: SB is next seat; BB is the one after
            self.small_blind_position = (self.dealer_position + 1) % self.config.num_players
            self.big_blind_position = (self.dealer_position + 2) % self.config.num_players

        # --- NEW: update human-readable positions relative to dealer each hand ---
        self._assign_positions()

        # Initialize/refresh deck
        if self.deck_provider:
            self.game_state.deck = self.deck_provider.get_deck()
        else:
            self.game_state.deck = self._create_standard_deck()
        
        # Deal hole cards, post blinds, and set first to act (your existing logic)
        self._deal_hole_cards()
        self._post_blinds()
        
        if self.rules_provider:
            self.action_player_index = self.rules_provider.get_first_to_act_preflop(
                self.dealer_position, self.config.num_players
            )
        else:
            if self.config.num_players == 2:
                self.action_player_index = self.small_blind_position
            else:
                self.action_player_index = (self.big_blind_position + 1) % self.config.num_players
        
        self.transition_to(PokerState.PREFLOP_BETTING)
        print(f"🃏 FIXED_PPSM: Hand {self.hand_number} started, action on {self.game_state.players[self.action_player_index].name}")
    
    def replay_hand_model(self, hand_model) -> Dict[str, Any]:
        """
        Replay a Hand Model object through PPSM using HandModelDecisionEngine.
        
        This is the ultimate interface for external hand compatibility.
        Creates a HandModelDecisionEngine and uses the DecisionEngine interface.
        
        Args:
            hand_model: Hand model object with standardized format
            
        Returns:
            Dict with replay results and validation metrics
        """
        print(f"🎯 PPSM: Replaying Hand Model {hand_model.metadata.hand_id}")
        
        # Setup PPSM to match hand model
        self._setup_for_hand_model(hand_model)
        
        # Create HandModelDecisionEngine adapter for this replay
        hand_decision_engine = HandModelDecisionEngineAdapter(hand_model)
        
        # Use the decision engine interface
        return self.play_hand_with_decision_engine(hand_decision_engine, hand_model)
    
    def play_hand_with_decision_engine(self, decision_engine: DecisionEngineProtocol, hand_model=None) -> Dict[str, Any]:
        """
        Play a hand using any DecisionEngine implementation.
        
        This is the core interface for bot play, hand replay, etc.
        
        Args:
            decision_engine: Any decision engine implementing DecisionEngineProtocol
            hand_model: Optional hand model for result comparison
            
        Returns:
            Dict with play results and validation metrics
        """
        # Set the decision engine
        self.decision_engine = decision_engine
        
        # Reset decision engine for new hand
        if self.decision_engine:
            self.decision_engine.reset_for_new_hand()
        
        # Start the hand
        self.start_hand()
        
        # Play results tracking
        play_results = {
            'hand_id': hand_model.metadata.hand_id if hand_model else f"hand_{self.hand_number}",
            'total_actions': 0,
            'successful_actions': 0,
            'failed_actions': 0,
            'final_pot': 0.0,
            'expected_pot': 0.0,
            'pot_match': True,  # Default true for non-replay scenarios
            'errors': []
        }
        
        # Calculate expected pot if we have a hand model
        if hand_model:
            play_results['expected_pot'] = self._calculate_expected_pot_from_hand_model(hand_model)
        
        # Game loop: continue until hand ends
        max_actions = 200  # Safety limit
        action_count = 0
        
        while (self.current_state not in [PokerState.END_HAND, PokerState.SHOWDOWN] and 
               action_count < max_actions):
            
            # Check if we need a player action
            if self.action_player_index >= 0 and self.action_player_index < len(self.game_state.players):
                current_player = self.game_state.players[self.action_player_index]
                
                # Get decision from engine
                if self.decision_engine and self.decision_engine.has_decision_for_player(current_player.name):
                    try:
                        decision = self.decision_engine.get_decision(current_player.name, self.game_state)
                        if decision:
                            ppsm_action_type, ppsm_amount = decision
                            
                            # Convert and execute the action
                            if self._is_valid_action(current_player, ppsm_action_type, ppsm_amount):
                                success = self.execute_action(current_player, ppsm_action_type, ppsm_amount)
                                if success:
                                    play_results['successful_actions'] += 1
                                else:
                                    play_results['failed_actions'] += 1
                                    play_results['errors'].append(f"Failed to execute {ppsm_action_type.value}")
                            else:
                                play_results['failed_actions'] += 1
                                play_results['errors'].append(f"Invalid action: {ppsm_action_type.value} {ppsm_amount}")
                            
                            play_results['total_actions'] += 1
                            action_count += 1
                        else:
                            # No decision available, break to avoid infinite loop
                            break
                    except Exception as e:
                        play_results['failed_actions'] += 1
                        play_results['errors'].append(f"Exception getting decision: {str(e)}")
                        action_count += 1
                else:
                    # No decision engine or no decision available
                    break
            else:
                # Auto-advance for non-action states (deal cards, etc.)
                if self.current_state in [PokerState.DEAL_FLOP, PokerState.DEAL_TURN, PokerState.DEAL_RIVER]:
                    # Always auto-advance card dealing states
                    self._advance_to_betting_round()
                elif (self.advancement_controller and 
                      self.advancement_controller.should_advance_automatically(self.current_state, self.game_state.players)):
                    self._advance_to_betting_round()
                else:
                    # No more automatic advancement, but check if more decisions available
                    if (self.decision_engine and 
                        hasattr(self.decision_engine, 'current_action_index') and
                        hasattr(self.decision_engine, 'actions_for_replay')):
                        # Check if more actions available from decision engine
                        if self.decision_engine.current_action_index < len(self.decision_engine.actions_for_replay):
                            # Force advance to next betting state to continue action sequence
                            if self.current_state == PokerState.DEAL_FLOP:
                                self.transition_to(PokerState.FLOP_BETTING)
                                self._set_first_to_act_postflop()
                            elif self.current_state == PokerState.DEAL_TURN:
                                self.transition_to(PokerState.TURN_BETTING)
                                self._set_first_to_act_postflop()
                            elif self.current_state == PokerState.DEAL_RIVER:
                                self.transition_to(PokerState.RIVER_BETTING)
                                self._set_first_to_act_postflop()
                        else:
                            break
                    else:
                        break
        
        # Calculate final pot
        final_pot = self.game_state.displayed_pot()
        
        play_results['final_pot'] = final_pot
        if hand_model:
            play_results['pot_match'] = abs(final_pot - play_results['expected_pot']) < 0.01
        
        print(f"🎯 PPSM: Hand complete - {play_results['successful_actions']}/{play_results['total_actions']} actions successful")
        if hand_model:
            print(f"🎯 PPSM: Pot: ${final_pot:.2f} (expected: ${play_results['expected_pot']:.2f})")
        else:
            print(f"🎯 PPSM: Final Pot: ${final_pot:.2f}")
        
        return play_results
    
    def _setup_for_hand_model(self, hand_model):
        """Setup PPSM to match hand model configuration."""
        # Update config to match hand model
        self.config.num_players = len(hand_model.seats)
        self.config.small_blind = hand_model.metadata.small_blind
        self.config.big_blind = hand_model.metadata.big_blind
        
        # Clear and recreate players from hand model seats
        self.game_state.players = []
        
        # Find button position
        button_seat_no = getattr(hand_model.metadata, 'button_seat_no', 1)
        button_pos = 0
        for i, seat in enumerate(hand_model.seats):
            if seat.seat_no == button_seat_no:
                button_pos = i
                break
        
        # Set dealer position  
        self.dealer_position = button_pos
        
        # Reset hand number for independent hand validation
        # This prevents dealer rotation between different hand validations
        self.hand_number = 0
        
        # Create players from hand model seats
        hole_cards = getattr(hand_model.metadata, 'hole_cards', {})
        for seat in hand_model.seats:
            player_cards = hole_cards.get(seat.player_uid, [])
            player = Player(
                name=seat.player_uid,
                stack=seat.starting_stack,
                position=f"seat_{seat.seat_no}",
                is_human=False,
                current_bet=0.0,
                has_folded=False,
                is_active=True,
                cards=player_cards
            )
            self.game_state.players.append(player)
        
        # CRITICAL: Create deterministic deck from hand model
        self._setup_deterministic_deck(hand_model)
    
    def _setup_deterministic_deck(self, hand_model):
        """Setup deterministic deck with exact cards from hand model."""
        from core.hand_model import Street
        
        # Extract all cards that will be dealt
        dealt_cards = []
        
        # 1. Hole cards from metadata (in correct deal order)
        hole_cards = getattr(hand_model.metadata, 'hole_cards', {})
        for seat in hand_model.seats:
            player_cards = hole_cards.get(seat.player_uid, [])
            if player_cards:
                dealt_cards.extend(player_cards)
        
        # 2. Board cards from final street (most complete board)
        board_cards = []
        if Street.RIVER in hand_model.streets and hand_model.streets[Street.RIVER].board:
            board_cards = hand_model.streets[Street.RIVER].board
        elif Street.TURN in hand_model.streets and hand_model.streets[Street.TURN].board:
            board_cards = hand_model.streets[Street.TURN].board
        elif Street.FLOP in hand_model.streets and hand_model.streets[Street.FLOP].board:
            board_cards = hand_model.streets[Street.FLOP].board
        
        dealt_cards.extend(board_cards)
        
        # Create deterministic deck
        suits = ["C", "D", "H", "S"]
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
        full_deck = [rank + suit for suit in suits for rank in ranks]
        
        # Remove dealt cards from deck
        remaining_cards = [card for card in full_deck if card not in dealt_cards]
        
        # Create deck: dealt cards first (will be dealt in order), then remaining
        deterministic_deck = dealt_cards + remaining_cards
        self.game_state.deck = deterministic_deck
        
        print(f"🎯 PPSM: Deterministic deck created with {len(dealt_cards)} predetermined cards: {dealt_cards}")
    
    def _find_player_by_name(self, name: str) -> Optional[Player]:
        """Find player by name in current game state."""
        for player in self.game_state.players:
            if player.name == name:
                return player
        return None
    
    def _calculate_expected_pot_from_hand_model(self, hand_model) -> float:
        """Calculate expected final pot from hand model actions."""
        from core.hand_model import ActionType as HandModelActionType
        
        total_pot = 0.0
        all_actions = hand_model.get_all_actions()
        
        # Sum all betting action amounts (these are total contribution amounts)
        betting_actions = {
            HandModelActionType.POST_BLIND, HandModelActionType.BET, 
            HandModelActionType.CALL, HandModelActionType.RAISE
        }
        
        for action in all_actions:
            if action.action in betting_actions:
                total_pot += action.amount
        
        return total_pot
    
    def _convert_hand_model_action_with_translation(self, action, actor: Player, street_contributions: Dict[str, float]) -> tuple:
        """
        Convert hand model action to PPSM action with bet amount translation.
        
        CRITICAL CONCEPT:
        - Hand Model: amount = "total chips contributed in this specific action"
        - PPSM: amount = "player's total bet amount for the street"
        
        Example: Player with $5 SB does RAISE $30 in hand model
        - Hand Model: Player contributes $30 MORE chips (total street contribution becomes $35)
        - PPSM: Player's total bet should become $35
        """
        from core.hand_model import ActionType as HandModelActionType
        
        action_type = action.action
        amount = action.amount
        
        if action_type == HandModelActionType.CHECK:
            return ActionType.CHECK, 0.0
            
        elif action_type == HandModelActionType.FOLD:
            return ActionType.FOLD, 0.0
            
        elif action_type == HandModelActionType.CALL:
            # CALL: Player contributes enough to match current_bet
            # PPSM handles the calculation internally
            return ActionType.CALL, 0.0
            
        elif action_type == HandModelActionType.BET:
            # BET: First wager on a street
            # Hand Model amount = total contribution = PPSM target
            return ActionType.BET, amount
            
        elif action_type == HandModelActionType.RAISE:
            # RAISE: Player already has some money in the pot this street
            # Hand Model amount = additional contribution in this action
            # PPSM needs: current_bet + additional_amount = new total bet
            current_bet_amount = actor.current_bet
            new_total_bet = current_bet_amount + amount
            return ActionType.RAISE, new_total_bet
        
        # Default fallback
        return None, 0.0
    
    def _create_standard_deck(self) -> List[str]:
        """Create a standard 52-card deck."""
        suits = ["C", "D", "H", "S"]
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
        return [rank + suit for suit in suits for rank in ranks]
    
    def _deal_hole_cards(self):
        """Deal 2 hole cards to each player."""
        for player in self.game_state.players:
            player.cards = self._deal_cards(2)
    
    def _deal_cards(self, num_cards: int) -> List[str]:
        """Deal cards from the deck."""
        if len(self.game_state.deck) < num_cards:
            raise ValueError(f"Not enough cards in deck: need {num_cards}, have {len(self.game_state.deck)}")
        
        cards = self.game_state.deck[:num_cards]
        self.game_state.deck = self.game_state.deck[num_cards:]
        return cards
    
    def _post_blinds(self):
        """Post small and big blinds."""
        # Small blind
        sb_player = self.game_state.players[self.small_blind_position]
        sb_amount = min(self.config.small_blind, sb_player.stack)
        sb_player.stack -= sb_amount
        sb_player.current_bet = sb_amount
        # Note: Blind amounts stay in current_bet until round completes
        
        # Big blind
        bb_player = self.game_state.players[self.big_blind_position]
        bb_amount = min(self.config.big_blind, bb_player.stack)
        bb_player.stack -= bb_amount
        bb_player.current_bet = bb_amount
        # Note: Blind amounts stay in current_bet until round completes
        self.game_state.current_bet = bb_amount
        
        print(f"🃏 PURE_FPSM: Posted blinds - SB: ${sb_amount}, BB: ${bb_amount}")
    
    def execute_action(self, player: Player, action_type: ActionType, to_amount: Optional[float] = None) -> bool:
        """Execute a poker action with pure poker logic."""
        try:
            # Validate action
            if not self._is_valid_action(player, action_type, to_amount):
                print(f"❌ PURE_FPSM: Invalid action {action_type.value} ${to_amount} for {player.name}")
                return False
            
            # Execute the action
            success = self._apply_action(player, action_type, to_amount)
            if not success:
                return False
            
            # Track that this player acted
            self.actions_this_round += 1
            self.players_acted_this_round.add(player.name)
            
            # If this was a raise, reset who has acted (except the raiser)
            if action_type == ActionType.RAISE:
                # Everyone needs to respond to the raise
                self.players_acted_this_round = {player.name}
            
            # Check if round is complete
            if self._is_round_complete():
                self._handle_round_complete()
            else:
                self._advance_to_next_player()
            
            return True
            
        except Exception as e:
            print(f"❌ PURE_FPSM: Error executing action: {e}")
            return False
    
    def _end_street(self):
        """Commit this street's bets into the pot and reset per-street state."""
        # Commit all current bets to the pot
        self.game_state.committed_pot += sum(p.current_bet for p in self.game_state.players)
        
        # Reset per-player street state
        for p in self.game_state.players:
            p.current_bet = 0.0
        
        # Reset per-street game state
        self.game_state.current_bet = 0.0
        from .poker_types import RoundState
        self.game_state.round_state = RoundState()
        
        print(f"🃏 FIXED_PPSM: Street ended, pot now: ${self.game_state.displayed_pot()}")
    
    def _is_valid_action(self, player: Player, action_type: ActionType, to_amount: Optional[float] = None) -> bool:
        """Validate if an action is legal using to-amount semantics."""
        
        if player.has_folded or not player.is_active:
            return False
        
        # All-in players cannot act
        if player.stack == 0:
            return False
        
        # CHECK: only if already matched
        if action_type == ActionType.CHECK:
            return player.current_bet == self.game_state.current_bet
        
        # FOLD: always allowed when facing action
        if action_type == ActionType.FOLD:
            return True
        
        # CALL: only if behind and can afford (all-in calls allowed)
        if action_type == ActionType.CALL:
            return player.current_bet < self.game_state.current_bet
        
        # All wager actions use "to-amount" = total chips committed on THIS street after action
        if to_amount is None or to_amount <= player.current_bet:
            return False
        
        addl = to_amount - player.current_bet
        if addl > player.stack + 1e-9:  # allow for tiny float noise
            return False
        
        bb = self.config.big_blind
        rs = self.game_state.round_state
        
        if action_type == ActionType.BET:
            # First wager of street only
            if self.game_state.current_bet != 0:
                return False
            min_bet = bb if self.rules_provider is None else getattr(self.rules_provider, "min_bet", lambda b: b)(bb)
            return to_amount >= min_bet
        
        if action_type == ActionType.RAISE:
            # Must be raising an existing bet
            if self.game_state.current_bet == 0:
                return False
            # Must exceed current_bet
            if to_amount <= self.game_state.current_bet + 1e-9:
                return False
            # Check if raising is allowed based on reopen status
            if not rs.reopen_available:
                return False
            # Full-raise size check (unless all-in short raise — allowed but won't reopen)
            # Legal even if < min_full (short all-in), but we'll handle reopen in _apply_action
            return True
        
        return False
    
    def _apply_action(self, player: Player, action_type: ActionType, to_amount: Optional[float] = None) -> bool:
        """Apply the action to game state using to-amount semantics."""
        rs = self.game_state.round_state
        prev_current_bet = self.game_state.current_bet
        bb = self.config.big_blind
        
        def _pay_to(to_amt: float):
            pay = max(0.0, to_amt - player.current_bet)
            pay = min(pay, player.stack)  # all-in if insufficient
            player.stack -= pay
            player.current_bet += pay
            return pay
        
        if action_type == ActionType.CHECK:
            # nothing to pay
            pass
        
        elif action_type == ActionType.FOLD:
            player.has_folded = True
            player.is_active = False
        
        elif action_type == ActionType.CALL:
            _pay_to(self.game_state.current_bet)
        
        elif action_type == ActionType.BET:
            _pay_to(to_amount)
            self.game_state.current_bet = to_amount
            # First wager defines full-raise size base
            rs.last_full_raise_size = to_amount
            rs.last_aggressor_idx = self._get_player_index(player)
            rs.reopen_available = True
        
        elif action_type == ActionType.RAISE:
            _pay_to(to_amount)
            self.game_state.current_bet = to_amount
            raise_size = to_amount - prev_current_bet
            min_full = rs.last_full_raise_size if rs.last_full_raise_size > 0 else bb
            rs.last_aggressor_idx = self._get_player_index(player)
            # Short all-in allowed but doesn't reopen
            rs.reopen_available = raise_size + 1e-9 >= min_full
            if rs.reopen_available:
                rs.last_full_raise_size = raise_size
        
        print(f"🃏 FIXED_PPSM: {player.name} {action_type.value} ${to_amount or 0} (pot: ${self.game_state.displayed_pot()})")
        return True
    
    def _get_player_index(self, player: Player) -> int:
        """Get the index of a player in the players list."""
        for i, p in enumerate(self.game_state.players):
            if p.name == player.name:
                return i
        return -1
    
    def _is_round_complete(self) -> bool:
        """Check if the current betting round is complete - FIXED version."""
        active_players = [p for p in self.game_state.players if not p.has_folded and p.is_active]
        
        # If only one player left, round is complete
        if len(active_players) <= 1:
            return True
        
        # Get players who can still act (not all-in)
        actionable_players = [p for p in active_players if p.stack > 0]
        
        # If no one can act (all players all-in or folded), round is complete
        if len(actionable_players) == 0:
            return True
        
        # Check if all active players have matched the current bet
        for player in active_players:
            # Skip all-in players (they've contributed all they can)
            if player.stack == 0:
                continue
            # If someone hasn't matched the bet, round continues
            if player.current_bet < self.game_state.current_bet:
                return False
        
        # Special case: if there was a raise, everyone needs to act after it
        if self.last_raiser_name:
            # Everyone after the raiser must have acted
            for player in actionable_players:
                if player.name == self.last_raiser_name:
                    continue
                if player.name not in self.players_acted_this_round:
                    return False
        else:
            # No raises - just check everyone has acted at least once
            for player in actionable_players:
                if player.name not in self.players_acted_this_round:
                    # Exception: BB preflop gets option even if no raise
                    if (self.game_state.street == "preflop" and 
                        player == self.game_state.players[self.big_blind_position] and
                        self.game_state.current_bet == self.config.big_blind):
                        # BB hasn't acted yet but needs option
                        return False
                    # Otherwise, if they match current bet, they don't need to act
                    if player.current_bet != self.game_state.current_bet:
                        return False
        
        return True
    
    def _handle_round_complete(self):
        """Handle completion of a betting round - FIXED version."""
        print(f"🃏 FIXED_PPSM: Round complete on {self.game_state.street}")
        
        # Reset round tracking
        self.actions_this_round = 0
        self.players_acted_this_round.clear()
        self.last_raiser_name = None
        self.last_bet_size = 0.0
        
        # Notify advancement controller
        if self.advancement_controller:
            self.advancement_controller.on_round_complete(self.game_state.street, self.game_state)
        
        # Determine next state
        if self.current_state == PokerState.PREFLOP_BETTING:
            self.transition_to(PokerState.DEAL_FLOP)
            # Reset action player for dealing state
            self.action_player_index = -1
        elif self.current_state == PokerState.FLOP_BETTING:
            self.transition_to(PokerState.DEAL_TURN)
            # Reset action player for dealing state
            self.action_player_index = -1
        elif self.current_state == PokerState.TURN_BETTING:
            self.transition_to(PokerState.DEAL_RIVER)
            # Reset action player for dealing state
            self.action_player_index = -1
        elif self.current_state == PokerState.RIVER_BETTING:
            self.transition_to(PokerState.SHOWDOWN)
        else:
            self.transition_to(PokerState.END_HAND)
    
    def _advance_to_next_player(self):
        """Advance to the next active player - FIXED version."""
        original_index = self.action_player_index
        
        for _ in range(len(self.game_state.players)):
            self.action_player_index = (self.action_player_index + 1) % len(self.game_state.players)
            next_player = self.game_state.players[self.action_player_index]
            
            # Skip folded players
            if next_player.has_folded:
                continue
            
            # Skip inactive players
            if not next_player.is_active:
                continue
            
            # Skip all-in players (stack == 0)
            if next_player.stack == 0:
                continue
            
            # Found valid next player
            print(f"🃏 FIXED_PPSM: Action advances to {next_player.name}")
            return
        
        # No actionable players found, round should be complete
        print(f"🃏 FIXED_PPSM: No actionable players found, completing round")
        self._handle_round_complete()
    
    def transition_to(self, new_state: PokerState):
        """Transition to a new poker state."""
        if new_state not in self.STATE_TRANSITIONS.get(self.current_state, []):
            raise ValueError(f"Invalid transition from {self.current_state} to {new_state}")
        
        old_state = self.current_state
        self.current_state = new_state
        
        print(f"🃏 PURE_FPSM: {old_state} → {new_state}")
        
        # Handle state-specific logic
        if new_state == PokerState.DEAL_FLOP:
            self.game_state.board.extend(self._deal_cards(3))
            self.game_state.street = "flop"
            self._reset_bets_for_new_round()
            self._set_first_to_act_postflop()
            
        elif new_state == PokerState.DEAL_TURN:
            self.game_state.board.extend(self._deal_cards(1))
            self.game_state.street = "turn"
            self._reset_bets_for_new_round()
            self._set_first_to_act_postflop()
            
        elif new_state == PokerState.DEAL_RIVER:
            self.game_state.board.extend(self._deal_cards(1))
            self.game_state.street = "river"
            self._reset_bets_for_new_round()
            self._set_first_to_act_postflop()
        
        # Check if advancement controller wants to auto-advance
        if (self.advancement_controller and 
            self.advancement_controller.should_advance_automatically(new_state, self.game_state.players)):
            
            if new_state in [PokerState.DEAL_FLOP, PokerState.DEAL_TURN, PokerState.DEAL_RIVER]:
                # Auto-advance to betting round with proper setup
                self._advance_to_betting_round()
    
    def _reset_bets_for_new_round(self):
        """Reset bets for a new betting round."""
        # First, collect all current bets into the pot
        for player in self.game_state.players:
            self.game_state.committed_pot += player.current_bet
            player.current_bet = 0.0
        self.game_state.current_bet = 0.0
    
    def _set_first_to_act_postflop(self):
        """Set first to act for postflop rounds."""
        if self.rules_provider:
            self.action_player_index = self.rules_provider.get_first_to_act_postflop(
                self.dealer_position, self.game_state.players
            )
        else:
            # Default: first active player after dealer
            self.action_player_index = self._find_first_active_after_dealer()
    
    def _find_first_active_after_dealer(self) -> int:
        """Find first active player after dealer."""
        for i in range(1, len(self.game_state.players) + 1):
            idx = (self.dealer_position + i) % len(self.game_state.players)
            player = self.game_state.players[idx]
            if not player.has_folded and player.is_active:
                return idx
        return -1  # No active players
    
    def get_game_info(self) -> Dict[str, Any]:
        """Get current game information with proper pot accounting."""
        return {
            "players": [
                {
                    "name": p.name,
                    "stack": p.stack,
                    "current_bet": p.current_bet,
                    "is_active": p.is_active,
                    "has_folded": p.has_folded,
                    "position": p.position,
                    "cards": p.cards,
                }
                for p in self.game_state.players
            ],
            "committed_pot": self.game_state.committed_pot,
            "street_commit_sum": sum(p.current_bet for p in self.game_state.players),
            "pot": self.game_state.displayed_pot(),
            "current_bet": self.game_state.current_bet,
            "board": self.game_state.board,
            "street": self.game_state.street,
            "current_state": self.current_state.value,
            "action_player_index": self.action_player_index,
            "hand_number": self.hand_number,
            "dealer_position": self.dealer_position,
        }
    
    def _advance_to_betting_round(self):
        """Advance from dealing states to betting states."""
        if self.current_state == PokerState.DEAL_FLOP:
            # Deal flop cards
            flop_cards = self._deal_cards(3)
            self.game_state.board.extend(flop_cards)
            self.game_state.street = "flop"
            # Transition to flop betting
            self.transition_to(PokerState.FLOP_BETTING)
            self._set_first_to_act_postflop()
            print(f"🃏 PPSM: Dealing flop: {flop_cards}, transitioning to FLOP_BETTING")
            
        elif self.current_state == PokerState.DEAL_TURN:
            # Deal turn card
            turn_card = self._deal_cards(1)
            self.game_state.board.extend(turn_card)
            self.game_state.street = "turn"
            # Transition to turn betting
            self.transition_to(PokerState.TURN_BETTING)
            self._set_first_to_act_postflop()
            print(f"🃏 PPSM: Dealing turn: {turn_card}, transitioning to TURN_BETTING")
            
        elif self.current_state == PokerState.DEAL_RIVER:
            # Deal river card
            river_card = self._deal_cards(1)
            self.game_state.board.extend(river_card)
            self.game_state.street = "river"
            # Transition to river betting
            self.transition_to(PokerState.RIVER_BETTING)
            self._set_first_to_act_postflop()
            print(f"🃏 PPSM: Dealing river: {river_card}, transitioning to RIVER_BETTING")


class HandModelDecisionEngineAdapter:
    """
    Adapter that wraps HandModelDecisionEngine to implement DecisionEngineProtocol.
    
    This bridges the existing HandModelDecisionEngine to the new DecisionEngine interface,
    allowing PPSM to use any decision engine polymorphically.
    """
    
    def __init__(self, hand_model):
        from core.hand_model_decision_engine import HandModelDecisionEngine
        self.hand_engine = HandModelDecisionEngine(hand_model)
        self.actions_for_replay = self.hand_engine.actions_for_replay
        self.current_action_index = 0
        
    def get_decision(self, player_name: str, game_state) -> tuple:
        """
        Get the decision for a player from the hand model sequence.
        
        Returns:
            tuple: (ActionType, amount) or None if no decision available
        """
        if self.current_action_index >= len(self.actions_for_replay):
            return None
            
        # Get the next action from the sequence
        current_action = self.actions_for_replay[self.current_action_index]
        
        # Check if this action is for the requested player
        if current_action.actor_uid == player_name:
            self.current_action_index += 1
            
            # Convert hand model action to PPSM action format
            from core.hand_model import ActionType as HandModelActionType
            
            if current_action.action == HandModelActionType.CHECK:
                return ActionType.CHECK, 0.0
            elif current_action.action == HandModelActionType.FOLD:
                return ActionType.FOLD, 0.0
            elif current_action.action == HandModelActionType.CALL:
                return ActionType.CALL, 0.0
            elif current_action.action == HandModelActionType.BET:
                return ActionType.BET, current_action.amount
            elif current_action.action == HandModelActionType.RAISE:
                # For RAISE, we need to convert from "additional amount" to "total bet"
                # This will need the current bet info from game_state
                # For now, use the raw amount and let PPSM handle the translation
                return ActionType.RAISE, current_action.amount
            else:
                return None
        else:
            # This action is not for the current player - skip ahead or return None
            return None
    
    def has_decision_for_player(self, player_name: str) -> bool:
        """Check if engine has a decision for the specified player."""
        if self.current_action_index >= len(self.actions_for_replay):
            return False
            
        # Look at the next action to see if it's for this player
        current_action = self.actions_for_replay[self.current_action_index]
        return current_action.actor_uid == player_name
    
    def reset_for_new_hand(self) -> None:
        """Reset engine state for a new hand."""
        self.current_action_index = 0
        
        
# Factory functions for creating different decision engines

def create_hand_replay_engine(hand_model):
    """Create a decision engine for replaying a specific hand."""
    return HandModelDecisionEngineAdapter(hand_model)

def create_gto_decision_engine(config):
    """Create a GTO decision engine (placeholder for future implementation)."""
    # TODO: Implement GTO decision engine
    raise NotImplementedError("GTO decision engine not yet implemented")

def create_custom_decision_engine(strategy_function):
    """Create a custom decision engine from a strategy function (placeholder)."""
    # TODO: Implement custom decision engine wrapper
    raise NotImplementedError("Custom decision engine not yet implemented")
