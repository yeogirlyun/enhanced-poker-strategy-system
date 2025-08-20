"""
Pure Poker State Machine - Clean Architecture

This is a pure poker rules engine that:
- Manages only poker state transitions
- Has no knowledge of human vs bot players
- Has no application-specific logic
- Uses dependency injection for all external concerns
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Protocol, Set
from enum import Enum
import time

from .poker_types import Player, PokerState, GameState
from .hand_model import ActionType
from .session_logger import get_session_logger
from .deuces_hand_evaluator import DeucesHandEvaluator


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
        
        # Hand evaluation using proven deuces library
        self.hand_evaluator = DeucesHandEvaluator()
        
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
    
    def _active_indices(self) -> List[int]:
        """Get indices of active (not folded) players."""
        return [i for i, p in enumerate(self.game_state.players) if p.is_active and not p.has_folded]

    def _seed_round_state_for_street(self, street: str):
        """Seed the round state for a new street with proper need_action_from tracking."""
        from .poker_types import RoundState
        rs = RoundState()
        active = set(self._active_indices())
        
        if street == "preflop":
            # BB is the implicit aggressor from posting blinds.
            rs.last_full_raise_size = self.config.big_blind
            rs.last_aggressor_idx = self.big_blind_position
            rs.reopen_available = True
            rs.need_action_from = active - {self.big_blind_position}
            self.game_state.current_bet = self.config.big_blind
        else:
            # No wager yet; everyone must act at least once (check/bet).
            rs.last_full_raise_size = 0.0
            rs.last_aggressor_idx = None
            rs.reopen_available = True
            rs.need_action_from = active
            self.game_state.current_bet = 0.0
        
        self.game_state.round_state = rs
    
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
        
        # Seed preflop round state based on blinds
        self._seed_round_state_for_street("preflop")
        
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
        MAX_STEPS_PER_STREET = 200
        MAX_STEPS_PER_HAND = 800
        
        steps_this_street = 0
        steps_this_hand = 0
        last_street = self.game_state.street
        action_count = 0
        
        while (self.current_state not in [PokerState.END_HAND, PokerState.SHOWDOWN] and 
               action_count < MAX_STEPS_PER_HAND):
            
            # Track street changes and reset counters
            if self.game_state.street != last_street:
                last_street = self.game_state.street
                steps_this_street = 0
            
            steps_this_street += 1
            steps_this_hand += 1
            
            # Loop guard: break with detailed state if exceeded
            if steps_this_street > MAX_STEPS_PER_STREET or steps_this_hand > MAX_STEPS_PER_HAND:
                info = self.get_game_info()
                error_msg = (
                    f"Loop guard tripped.\n"
                    f"street={info['street']} state={info['current_state']} pot={info['pot']}\n"
                    f"dealer={info['dealer_position']} action_idx={info['action_player_index']}\n"
                    f"need_action_from={info.get('need_action_from', 'N/A')}\n"
                    f"steps_this_street={steps_this_street} steps_this_hand={steps_this_hand}\n"
                    f"players={info['players']}"
                )
                play_results['errors'].append(f"INFINITE_LOOP_DETECTED: {error_msg}")
                break
            
            # Check if we need a player action
            if self.action_player_index >= 0 and self.action_player_index < len(self.game_state.players):
                current_player = self.game_state.players[self.action_player_index]
                
                # Always ask the adapter; let it return None if it has nothing.
                if self.decision_engine:
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
                            self._advance_to_next_player()
                            continue
                    except Exception as e:
                        play_results['failed_actions'] += 1
                        play_results['errors'].append(f"Exception getting decision: {str(e)}")
                        action_count += 1
                else:
                    self._advance_to_next_player()
                    continue
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
    
    def _deal_flop(self):
        """Deal the flop (3 cards)."""
        flop_cards = self._deal_cards(3)
        self.game_state.board.extend(flop_cards)
        return flop_cards
    
    def _deal_turn(self):
        """Deal the turn (1 card)."""
        turn_card = self._deal_cards(1)
        self.game_state.board.extend(turn_card)
        return turn_card
    
    def _deal_river(self):
        """Deal the river (1 card)."""
        river_card = self._deal_cards(1)
        self.game_state.board.extend(river_card)
        return river_card
    
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
        """Execute a poker action with new need_action_from tracking."""
        actor_idx = self._get_player_index(player)
        if actor_idx == -1:
            return False
            
        if not self._is_valid_action(player, action_type, to_amount):
            return False
        
        rs = self.game_state.round_state
        prev_current_bet = self.game_state.current_bet
        bb = self.config.big_blind
        
        def _pay_to(to_amt: float):
            pay = max(0.0, to_amt - player.current_bet)
            pay = min(pay, player.stack)
            player.stack -= pay
            player.current_bet += pay
            return pay
        
        if action_type == ActionType.CHECK:
            # At current_bet == 0, a check consumes this player's turn.
            rs.need_action_from.discard(actor_idx)
        
        elif action_type == ActionType.FOLD:
            player.has_folded = True
            player.is_active = False
            rs.need_action_from.discard(actor_idx)
            # If only one active player remains, the hand ends
            if len(self._active_indices()) <= 1:
                self.current_state = PokerState.SHOWDOWN
                self._resolve_showdown()
                return True
        
        elif action_type == ActionType.CALL:
            _pay_to(self.game_state.current_bet)
            # Caller has now matched; they no longer need to act this street
            rs.need_action_from.discard(actor_idx)
        
        elif action_type == ActionType.BET:
            _pay_to(to_amount)
            self.game_state.current_bet = to_amount
            rs.last_full_raise_size = to_amount            # first wager sets "full raise" base
            rs.last_aggressor_idx = actor_idx
            rs.reopen_available = True
            # All *other* active players now must respond
            rs.need_action_from = set(self._active_indices()) - {actor_idx}
        
        elif action_type == ActionType.RAISE:
            _pay_to(to_amount)
            self.game_state.current_bet = to_amount
            raise_size = to_amount - prev_current_bet
            min_full = rs.last_full_raise_size if rs.last_full_raise_size > 0 else bb
            rs.last_aggressor_idx = actor_idx
            rs.reopen_available = (raise_size + 1e-9 >= min_full)
            if rs.reopen_available:
                rs.last_full_raise_size = raise_size
            # After a (full or short) raise, everyone else must act again
            rs.need_action_from = set(self._active_indices()) - {actor_idx}
        
        print(f"🃏 FIXED_PPSM: {player.name} {action_type.value} ${to_amount or 0} (pot: ${self.game_state.displayed_pot()})")
        
        # If no one needs to act anymore, close the street
        if len(rs.need_action_from) == 0:
            self._end_street()
            self._advance_street()
        else:
            self._advance_to_next_player()
        return True
    
    def _end_street(self):
        """Commit this street's bets into the pot and reset per-street state."""
        # Commit all current bets to the pot
        self.game_state.committed_pot += sum(p.current_bet for p in self.game_state.players)
        
        # Reset per-player street state
        for p in self.game_state.players:
            p.current_bet = 0.0
        
        # Reset per-street game state
        self.game_state.current_bet = 0.0
        # Next street will re-seed round_state via _seed_round_state_for_street()
        
        print(f"🃏 FIXED_PPSM: Street ended, pot now: ${self.game_state.displayed_pot()}")
    
    def _advance_street(self):
        """Advance to the next street after a betting round has completed."""
        if self.game_state.street == "preflop":
            self.game_state.street = "flop"
            self._deal_flop()
            self._seed_round_state_for_street("flop")
            self.current_state = PokerState.FLOP_BETTING
            self._set_first_to_act_postflop()
        elif self.game_state.street == "flop":
            self.game_state.street = "turn"
            self._deal_turn()
            self._seed_round_state_for_street("turn")
            self.current_state = PokerState.TURN_BETTING
            self._set_first_to_act_postflop()
        elif self.game_state.street == "turn":
            self.game_state.street = "river"
            self._deal_river()
            self._seed_round_state_for_street("river")
            self.current_state = PokerState.RIVER_BETTING
            self._set_first_to_act_postflop()
        else:
            self.current_state = PokerState.SHOWDOWN
            self._resolve_showdown()
    
    def _is_valid_action(self, player: Player, action_type: ActionType, to_amount: Optional[float] = None) -> bool:
        """Validate if an action is legal using to-amount semantics."""
        
        if player.has_folded or not player.is_active:
            return False
        
        # All-in players cannot act
        if player.stack == 0:
            return False
        
        # CHECK: only if already matched (with defensive None handling)
        if action_type == ActionType.CHECK:
            current_bet = player.current_bet if player.current_bet is not None else 0.0
            game_current_bet = self.game_state.current_bet if self.game_state.current_bet is not None else 0.0
            return current_bet == game_current_bet
        
        # FOLD: always allowed when facing action
        if action_type == ActionType.FOLD:
            return True

        # CALL: ignore to_amount; legal if player is behind the current_bet (with defensive None handling)
        if action_type == ActionType.CALL:
            # Allow all-in calls (engine will clamp payment to stack)
            current_bet = player.current_bet if player.current_bet is not None else 0.0
            game_current_bet = self.game_state.current_bet if self.game_state.current_bet is not None else 0.0
            return current_bet < game_current_bet
        
        # For BET/RAISE only: require a to-amount (CALL is handled above)
        if action_type in (ActionType.BET, ActionType.RAISE):
            if to_amount is None:
                return False
            # Defensive None handling for player.current_bet
            current_bet = player.current_bet if player.current_bet is not None else 0.0
            if to_amount <= current_bet:
                return False
            addl = to_amount - current_bet
        else:
            # For other action types, addl is not used
            addl = 0.0
            current_bet = player.current_bet if player.current_bet is not None else 0.0
        
        # Defensive None handling for player.stack
        stack = player.stack if player.stack is not None else 0.0
        if addl > stack + 1e-9:  # allow for tiny float noise
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
            # Enforce minimum raise UNLESS this action is all-in.
            min_full = rs.last_full_raise_size if rs.last_full_raise_size > 0 else bb
            additional_needed = to_amount - player.current_bet
            is_all_in = abs(additional_needed - player.stack) <= 1e-9
            raise_size = to_amount - self.game_state.current_bet
            if not is_all_in and (raise_size + 1e-9) < min_full:
                return False
            # If table is "not reopened" (e.g., previous short all-in), disallow further raises
            if not rs.reopen_available and not is_all_in:
                return False
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
        """Advance to the next player who still needs to act."""
        rs = self.game_state.round_state
        if not rs.need_action_from:
            return
        n = self.config.num_players
        i = self.action_player_index
        for _ in range(n):
            i = (i + 1) % n
            if i in rs.need_action_from:
                self.action_player_index = i
                print(f"🃏 FIXED_PPSM: Action advances to {self.game_state.players[i].name}")
                return
        # If we somehow didn't find one, fail safe by closing street
        self._end_street()
        self._advance_street()
    
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
            "need_action_from": list(self.game_state.round_state.need_action_from),
        }
    
    def _advance_to_betting_round(self):
        """Advance from dealing states to betting states."""
        if self.current_state == PokerState.DEAL_FLOP:
            # Deal flop cards
            flop_cards = self._deal_cards(3)
            self.game_state.board.extend(flop_cards)
            self.game_state.street = "flop"
            self._seed_round_state_for_street("flop")
            # Transition to flop betting
            self.transition_to(PokerState.FLOP_BETTING)
            self._set_first_to_act_postflop()
            print(f"🃏 PPSM: Dealing flop: {flop_cards}, transitioning to FLOP_BETTING")
            
        elif self.current_state == PokerState.DEAL_TURN:
            # Deal turn card
            turn_card = self._deal_cards(1)
            self.game_state.board.extend(turn_card)
            self.game_state.street = "turn"
            self._seed_round_state_for_street("turn")
            # Transition to turn betting
            self.transition_to(PokerState.TURN_BETTING)
            self._set_first_to_act_postflop()
            print(f"🃏 PPSM: Dealing turn: {turn_card}, transitioning to TURN_BETTING")
            
        elif self.current_state == PokerState.DEAL_RIVER:
            # Deal river card
            river_card = self._deal_cards(1)
            self.game_state.board.extend(river_card)
            self.game_state.street = "river"
            self._seed_round_state_for_street("river")
            # Transition to river betting
            self.transition_to(PokerState.RIVER_BETTING)
            self._set_first_to_act_postflop()
            print(f"🃏 PPSM: Dealing river: {river_card}, transitioning to RIVER_BETTING")
    
    def _resolve_showdown(self):
        """Resolve the showdown and determine winners using deuces library."""
        # Before finalizing, roll any outstanding street bets into the pot
        residual = sum(p.current_bet for p in self.game_state.players)
        if residual:
            self.game_state.committed_pot += residual
            for p in self.game_state.players:
                p.current_bet = 0.0

        print(f"🃏 PPSM: Resolving showdown, final pot: ${self.game_state.displayed_pot()}")
        self.current_state = PokerState.SHOWDOWN
        
        # Determine active players (not folded)
        active_players = [p for p in self.game_state.players if not p.has_folded and p.is_active]
        
        if len(active_players) == 0:
            # No active players - shouldn't happen but handle gracefully
            print("🃏 PPSM: No active players at showdown")
            self.current_state = PokerState.END_HAND
            return
        elif len(active_players) == 1:
            # Single winner (all others folded)
            winner = active_players[0]
            pot_amount = self.game_state.displayed_pot()
            winner.stack += pot_amount
            print(f"🏆 PPSM: {winner.name} wins ${pot_amount:.2f} (all others folded)")
            self.current_state = PokerState.END_HAND
            return
        
        # Multiple players - evaluate hands using deuces
        winners = self._determine_winners(active_players)
        
        if winners:
            pot_amount = self.game_state.displayed_pot()
            pot_per_winner = pot_amount / len(winners)
            
            for winner in winners:
                winner.stack += pot_per_winner
            
            if len(winners) == 1:
                print(f"🏆 PPSM: {winners[0].name} wins ${pot_amount:.2f}")
            else:
                winner_names = [w.name for w in winners]
                print(f"🏆 PPSM: Split pot - {', '.join(winner_names)} each win ${pot_per_winner:.2f}")
        
        self.current_state = PokerState.END_HAND
    
    def _determine_winners(self, active_players: List[Player]) -> List[Player]:
        """Determine winners using deuces hand evaluation."""
        if not active_players:
            return []
        
        if len(active_players) == 1:
            return active_players
        
        # Evaluate hands for all active players
        player_evaluations = []
        for player in active_players:
            if hasattr(player, 'hole_cards') and len(player.hole_cards) == 2:
                # Use hole_cards if available
                hole_cards = player.hole_cards
            elif hasattr(player, 'cards') and len(player.cards) == 2:
                # Fallback to cards attribute
                hole_cards = player.cards
            else:
                # Skip players without valid hole cards
                print(f"🃏 PPSM: Skipping {player.name} - no valid hole cards")
                continue
            
            if len(self.game_state.board) >= 3:
                # Evaluate hand using deuces
                hand_eval = self.hand_evaluator.evaluate_hand(hole_cards, self.game_state.board)
                player_evaluations.append((player, hand_eval))
                
                # Log hand evaluation for transparency
                score = hand_eval.get("hand_score", 9999)
                description = hand_eval.get("hand_description", "Unknown")
                strength = hand_eval.get("strength_score", 0)
                print(f"🃏 PPSM: {player.name} ({hole_cards}) + {self.game_state.board} = {description} (score={score}, strength={strength:.1f}%)")
            else:
                print(f"🃏 PPSM: Insufficient board cards ({len(self.game_state.board)}) for evaluation")
                return active_players  # Return all players if can't evaluate
        
        # Handle case where no hands could be evaluated
        if not player_evaluations:
            print("🃏 PPSM: No hands could be evaluated - returning all active players")
            return active_players
        
        # Use deuces evaluator to determine winners
        winners_with_evals = self.hand_evaluator.determine_winners(player_evaluations)
        winners = [player for player, eval_data in winners_with_evals]
        
        # Log winner determination
        if len(winners) == 1:
            winner_eval = winners_with_evals[0][1]
            description = winner_eval.get("hand_description", "Unknown")
            best_five = winner_eval.get("best_five_cards", [])
            cards_str = f" [{', '.join(best_five)}]" if best_five else ""
            print(f"🏆 PPSM: Winner {winners[0].name} with {description}{cards_str}")
        else:
            winner_names = [w.name for w in winners]
            winner_eval = winners_with_evals[0][1]
            description = winner_eval.get("hand_description", "Unknown")
            print(f"🏆 PPSM: Tie between {', '.join(winner_names)} with {description}")
        
        return winners


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
    
    def has_decision_for_player(self, player_name: str) -> bool:
        """
        Return True while there are hand-model actions remaining. We may also
        inject implicit checks (without consuming the model pointer), so this
        must be True as long as we haven't exhausted actions.
        """
        return self.current_action_index < len(self.actions_for_replay)

    def _to_float(self, x, default=0.0) -> float:
        """Defensive float conversion that handles None/empty strings."""
        try:
            if x is None or x == "":
                return float(default)
            return float(x)
        except Exception:
            return float(default)

    def _need_set(self, game_state):
        """Get the set of seats that need to act."""
        rs = getattr(game_state, "round_state", None)
        return set(getattr(rs, "need_action_from", set()) or set())

    def _seat_index(self, game_state, player_name):
        for i, pl in enumerate(game_state.players):
            if pl.name == player_name:
                return i
        return None

    def _can_inject_check(self, player_name, game_state) -> bool:
        """True iff it's legal/needed to inject a CHECK for player_name now."""
        street = (str(getattr(game_state, "street", "")) or "").lower()
        idx = self._seat_index(game_state, player_name)
        if idx is None:
            return False
        need = self._need_set(game_state)
        curr = self._to_float(getattr(game_state, "current_bet", 0.0))
        # Postflop: if no wager yet, any seat that owes action may CHECK
        if street in ("flop", "turn", "river"):
            return curr == 0.0 and idx in need
        # Preflop "BB option" when limped: BB can CHECK if still owes action and no raise
        if street == "preflop":
            bb_amt = self._to_float(getattr(game_state, "big_blind", 0.0))
            pos = getattr(game_state.players[idx], "position", "")
            return pos == "BB" and idx in need and abs(curr - bb_amt) < 1e-9
        return False

    def _should_inject_fold(self, player_name, game_state) -> bool:
        """True iff player_name faces a bet and still owes action (omitted FOLD)."""
        idx = self._seat_index(game_state, player_name)
        if idx is None:
            return False
        pl = game_state.players[idx]
        if not pl.is_active or pl.has_folded:
            return False
        curr = self._to_float(getattr(game_state, "current_bet", 0.0))
        if curr <= self._to_float(pl.current_bet):
            return False  # not facing a wager
        return idx in self._need_set(game_state)

    def _is_noise(self, act) -> bool:
        """True for non-betting noise lines that should be skipped."""
        n = str(getattr(act, "action", "")).upper()
        return n in {"SHOW", "SHOWHAND", "MUCK", "COLLECT", "WIN", "RESULT", "SUMMARY"}
        
    def get_decision(self, player_name: str, game_state):
        """
        BULLETPROOF Hand-Model adapter for PPSM integration.
        Return (ActionType, to_amount_or_None) for the engine seat to act.
        Uses to-amount semantics, never consumes wrong player's log, injects implied CHECK/FOLD.
        """
        # Import HM with a local alias to avoid enum name collisions
        from core.hand_model import ActionType as HM
        from core.poker_types import ActionType

        # If we're out of logged actions, we might still need to close the street.
        if self.current_action_index >= len(self.actions_for_replay):
            if self._can_inject_check(player_name, game_state):
                return ActionType.CHECK, None
            if self._should_inject_fold(player_name, game_state):
                return ActionType.FOLD, None
            return None

        act = self.actions_for_replay[self.current_action_index]

        # Skip any non-betting "noise" lines by consuming them and re-evaluating
        if self._is_noise(act):
            self.current_action_index += 1
            return self.get_decision(player_name, game_state)

        # If the next logged action is for a different player,
        # inject the implied action for THIS actor (do NOT consume the log).
        if act.actor_uid != player_name:
            if self._can_inject_check(player_name, game_state):
                return ActionType.CHECK, None
            if self._should_inject_fold(player_name, game_state):
                return ActionType.FOLD, None
            return None

        # From here, the log line IS for this player — consume it.
        self.current_action_index += 1

        curr = self._to_float(getattr(game_state, "current_bet", 0.0))
        bb   = self._to_float(getattr(game_state, "big_blind", 10.0))
        p    = next((pl for pl in game_state.players if pl.name == player_name), None)
        p_cb = self._to_float(getattr(p, "current_bet", 0.0)) if p else 0.0
        p_st = self._to_float(getattr(p, "stack", 0.0)) if p else float("inf")
        stack_room = p_cb + p_st

        a = self._to_float(getattr(act, "amount", 0.0))

        # Normalize HM → PPSM with "to-amount" semantics
        if act.action == HM.CHECK:
            return ActionType.CHECK, None
        if act.action == HM.FOLD:
            return ActionType.FOLD, None

        if act.action == HM.CALL:
            # Some logs encode CALL 0 when curr==0 → treat as CHECK
            if curr == 0.0 and a == 0.0:
                return ActionType.CHECK, None
            return ActionType.CALL, None  # engine computes pay-to

        if act.action == HM.BET:
            if a <= 1e-9 and curr == 0.0:
                return ActionType.CHECK, None  # "BET 0" → CHECK
            if curr == 0.0:
                return ActionType.BET, a
            # Mislabelled raise: accept either delta or total
            to_total = max(a, curr + a)
            if to_total > curr and to_total <= stack_room:
                return ActionType.RAISE, to_total
            return None  # let the validator print a snapshot

        if act.action == HM.RAISE:
            candidates = []
            t1 = curr + a   # as delta
            t2 = a          # as total
            if t1 > curr and t1 <= stack_room:
                candidates.append(('delta', t1))
            if t2 > curr and t2 <= stack_room:
                candidates.append(('total', t2))
            
            # Prefer 'total' interpretation over 'delta' when both are valid
            # This handles most hand-log formats better
            chosen = None
            for interpretation, t in candidates:
                if (t - curr) + 1e-9 >= bb:  # meets minimum raise
                    if interpretation == 'total':  # prefer total over delta
                        chosen = t
                        break
                    elif chosen is None:  # accept delta only if no total found
                        chosen = t
            
            if chosen is None and candidates:
                # Fallback: prefer total, then largest
                for interpretation, t in candidates:
                    if interpretation == 'total':
                        chosen = t
                        break
                if chosen is None:
                    chosen = max(candidates, key=lambda x: x[1])[1]
            
            return (ActionType.RAISE, chosen) if chosen else None

        # Optional explicit ALL_IN in some logs
        if getattr(HM, "ALL_IN", None) and act.action == HM.ALL_IN:
            to_allin = stack_room  # current_bet + stack
            if curr == 0.0:
                return ActionType.BET, to_allin
            return ActionType.RAISE, to_allin

        # Unknown action — return None and let the engine move on
        return None
    

    
    def reset_for_new_hand(self) -> None:
        """Reset engine state for a new hand."""
        self.current_action_index = 0
        
        
# Factory functions for creating different decision engines

def create_hand_replay_engine(hand_model):
    """Create a decision engine for replaying a specific hand."""
    return HandModelDecisionEngineAdapter(hand_model)

def create_gto_decision_engine(config):
    """Create a GTO decision engine using the new adapter."""
    try:
        from .gto_decision_engine_adapter import create_gto_decision_engine as create_gto_adapter
        num_players = getattr(config, 'num_players', 6)
        return create_gto_adapter(num_players)
    except ImportError as e:
        print(f"⚠️ GTO decision engine not available: {e}")
        raise NotImplementedError("GTO decision engine not yet implemented")

def create_custom_decision_engine(strategy_function):
    """Create a custom decision engine from a strategy function (placeholder)."""
    # TODO: Implement custom decision engine wrapper
    raise NotImplementedError("Custom decision engine not yet implemented")
