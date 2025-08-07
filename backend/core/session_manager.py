"""
Session Manager for Poker State Machine

This module handles session tracking, logging, and statistics collection
for the poker game sessions.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import time
import uuid
import json
import os

# Import shared types
from .session_logger import SessionLogger
from .types import Player, GameState


@dataclass
class SessionMetadata:
    """Complete session information and metadata."""
    session_id: str
    start_time: float
    end_time: Optional[float] = None
    total_hands: int = 0
    total_players: int = 0
    initial_stacks: Dict[str, float] = field(default_factory=dict)
    final_stacks: Dict[str, float] = field(default_factory=dict)
    big_blind_amount: float = 1.0
    strategy_data: Optional[Dict] = None
    session_notes: str = ""


@dataclass
class HandHistoryLog:
    """A snapshot of the game state at a specific action."""
    timestamp: float
    street: str
    player_name: str
    action: str
    amount: float
    pot_size: float
    board: List[str]
    player_states: List[dict]  # Store a simplified dict of each player's state


@dataclass
class HandResult:
    """Complete information about a hand's outcome."""
    hand_number: int
    start_time: float
    end_time: float
    players_at_start: List[Dict[str, Any]]
    players_at_end: List[Dict[str, Any]]
    board_cards: List[str]
    pot_amount: float
    winners: List[Dict[str, Any]]
    side_pots: List[Dict[str, Any]]
    action_history: List[HandHistoryLog]
    showdown_cards: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class SessionState:
    """Complete session state for replay and debugging."""
    session_metadata: SessionMetadata
    current_hand_number: int
    hands_played: List[HandResult]
    current_hand_state: Optional[Dict[str, Any]] = None
    current_hand_history: List[HandHistoryLog] = field(default_factory=list)
    session_log: List[str] = field(default_factory=list)


class SessionManager:
    """Manages session tracking, logging, and statistics."""

    def __init__(self, num_players: int, big_blind: float = 1.0, 
                 logger: Optional[SessionLogger] = None):
        self.logger = logger or SessionLogger()
        self.session_state: Optional[SessionState] = None
        self.num_players = num_players
        self.big_blind = big_blind
        self.session_id: Optional[str] = None

    def start_session(self) -> str:
        """Start a new session and return session ID."""
        session_id = str(uuid.uuid4())
        self.session_id = session_id
        
        self.session_state = SessionState(
            session_metadata=SessionMetadata(
                session_id=session_id,
                start_time=time.time(),
                total_players=self.num_players,
                big_blind_amount=self.big_blind
            ),
            current_hand_number=0,
            hands_played=[]
        )
        
        self._log_session_event("Session started")
        return session_id

    def end_session(self) -> Dict[str, Any]:
        """End the current session and return final statistics."""
        if not self.session_state:
            return {}
        
        self.session_state.session_metadata.end_time = time.time()
        self.session_state.session_metadata.total_hands = len(self.session_state.hands_played)
        
        self._log_session_event("Session ended")
        
        return self.get_session_info()

    def _log_session_event(self, event: str) -> None:
        """Log a session event."""
        if self.logger:
            try:
                self.logger.log_system("INFO", "SESSION", event)
            except Exception as e:
                print(f"Warning: Could not log session event: {e}")

    def capture_hand_start(self, hand_number: int, players: List[Dict[str, Any]], 
                          dealer_button: int, blinds: Dict[str, float]) -> None:
        """Capture the start of a new hand."""
        if not self.session_state:
            return
        
        self.session_state.current_hand_number = hand_number
        self.session_state.current_hand_history.clear()
        
        # Log hand start
        if self.logger:
            try:
                self.logger.log_system("INFO", "HAND", "Started hand", {
                    "hand_number": hand_number,
                    "dealer_button": dealer_button,
                    "blinds": blinds
                })
            except Exception as e:
                print(f"Warning: Could not log hand start: {e}")

    def capture_hand_end(self, hand_result: HandResult) -> None:
        """Capture the end of a hand."""
        if not self.session_state:
            return
        
        self.session_state.hands_played.append(hand_result)
        
        # Log hand completion
        if self.logger:
            try:
                self.logger.log_system("INFO", "HAND", "Hand completed", {
                    "hand_number": hand_result.hand_number,
                    "winner": hand_result.winners[0]["name"] if hand_result.winners else "None",
                    "pot_size": hand_result.pot_amount,
                    "duration_ms": int((hand_result.end_time - hand_result.start_time) * 1000)
                })
            except Exception as e:
                print(f"Warning: Could not log hand completion: {e}")

    def log_player_action(self, player_name: str, action: str, amount: float, 
                         pot_before: float, pot_after: float, street: str, 
                         board: List[str], player_states: List[Dict[str, Any]]) -> None:
        """Log a player action."""
        if not self.session_state:
            return
        
        action_log = HandHistoryLog(
            timestamp=time.time(),
            street=street,
            player_name=player_name,
            action=action,
            amount=amount,
            pot_size=pot_after,
            board=board.copy(),
            player_states=player_states
        )
        
        self.session_state.current_hand_history.append(action_log)
        
        # Log to system logger
        if self.logger:
            try:
                self.logger.log_system("INFO", "ACTION", f"{player_name} {action}", {
                    "amount": amount,
                    "pot_before": pot_before,
                    "pot_after": pot_after,
                    "street": street
                })
            except Exception as e:
                print(f"Warning: Could not log player action: {e}")

    def get_session_info(self) -> Dict[str, Any]:
        """Get comprehensive session information."""
        if not self.session_state:
            return {}
        
        metadata = self.session_state.session_metadata
        duration = (metadata.end_time or time.time()) - metadata.start_time
        
        return {
            "session_id": metadata.session_id,
            "start_time": metadata.start_time,
            "end_time": metadata.end_time,
            "duration_seconds": duration,
            "total_hands": metadata.total_hands,
            "total_players": metadata.total_players,
            "big_blind_amount": metadata.big_blind_amount,
            "hands_played": len(self.session_state.hands_played),
            "current_hand": self.session_state.current_hand_number
        }

    def get_session_statistics(self) -> Dict[str, Any]:
        """Get detailed session statistics."""
        if not self.session_state or not self.session_state.hands_played:
            return {}
        
        hands = self.session_state.hands_played
        total_duration = sum(h.end_time - h.start_time for h in hands)
        avg_hand_duration = total_duration / len(hands) if hands else 0
        
        # Calculate pot statistics
        pot_sizes = [h.pot_amount for h in hands]
        avg_pot_size = sum(pot_sizes) / len(pot_sizes) if pot_sizes else 0
        max_pot_size = max(pot_sizes) if pot_sizes else 0
        
        # Calculate winner statistics
        winner_counts = {}
        for hand in hands:
            for winner in hand.winners:
                winner_name = winner["name"]
                winner_counts[winner_name] = winner_counts.get(winner_name, 0) + 1
        
        return {
            "total_hands": len(hands),
            "avg_hand_duration_seconds": avg_hand_duration,
            "total_session_duration_seconds": total_duration,
            "avg_pot_size": avg_pot_size,
            "max_pot_size": max_pot_size,
            "winner_distribution": winner_counts,
            "hands_per_hour": len(hands) / (total_duration / 3600) if total_duration > 0 else 0
        }

    def export_session(self, filepath: str) -> bool:
        """Export session data to JSON file."""
        if not self.session_state:
            return False
        
        try:
            session_data = {
                "session_info": self.get_session_info(),
                "statistics": self.get_session_statistics(),
                "hands": [
                    {
                        "hand_number": h.hand_number,
                        "start_time": h.start_time,
                        "end_time": h.end_time,
                        "board_cards": h.board_cards,
                        "pot_amount": h.pot_amount,
                        "winners": h.winners,
                        "action_history": [
                            {
                                "timestamp": a.timestamp,
                                "street": a.street,
                                "player_name": a.player_name,
                                "action": a.action,
                                "amount": a.amount,
                                "pot_size": a.pot_size,
                                "board": a.board
                            }
                            for a in h.action_history
                        ]
                    }
                    for h in self.session_state.hands_played
                ]
            }
            
            with open(filepath, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error exporting session: {e}")
            return False

    def import_session(self, filepath: str) -> bool:
        """Import session data from JSON file."""
        try:
            with open(filepath, 'r') as f:
                session_data = json.load(f)
            
            # Reconstruct session state from imported data
            # This is a simplified import - you might want to add more validation
            metadata = SessionMetadata(
                session_id=session_data["session_info"]["session_id"],
                start_time=session_data["session_info"]["start_time"],
                end_time=session_data["session_info"]["end_time"],
                total_hands=session_data["session_info"]["total_hands"],
                total_players=session_data["session_info"]["total_players"],
                big_blind_amount=session_data["session_info"]["big_blind_amount"]
            )
            
            # Reconstruct hands (simplified)
            hands = []
            for hand_data in session_data["hands"]:
                hand = HandResult(
                    hand_number=hand_data["hand_number"],
                    start_time=hand_data["start_time"],
                    end_time=hand_data["end_time"],
                    players_at_start=[],  # Would need to reconstruct
                    players_at_end=[],    # Would need to reconstruct
                    board_cards=hand_data["board_cards"],
                    pot_amount=hand_data["pot_amount"],
                    winners=hand_data["winners"],
                    side_pots=[],  # Would need to reconstruct
                    action_history=[]  # Would need to reconstruct
                )
                hands.append(hand)
            
            self.session_state = SessionState(
                session_metadata=metadata,
                current_hand_number=0,
                hands_played=hands
            )
            
            return True
        except Exception as e:
            print(f"Error importing session: {e}")
            return False

    def get_hand_history(self) -> List[HandHistoryLog]:
        """Get the current hand's action history."""
        if not self.session_state:
            return []
        return self.session_state.current_hand_history.copy()

    def get_comprehensive_session_data(self) -> Dict[str, Any]:
        """Get all session data for analysis."""
        if not self.session_state:
            return {}
        
        return {
            "session_info": self.get_session_info(),
            "statistics": self.get_session_statistics(),
            "current_hand_history": [
                {
                    "timestamp": a.timestamp,
                    "street": a.street,
                    "player_name": a.player_name,
                    "action": a.action,
                    "amount": a.amount,
                    "pot_size": a.pot_size,
                    "board": a.board
                }
                for a in self.session_state.current_hand_history
            ],
            "hands_played": [
                {
                    "hand_number": h.hand_number,
                    "start_time": h.start_time,
                    "end_time": h.end_time,
                    "board_cards": h.board_cards,
                    "pot_amount": h.pot_amount,
                    "winners": h.winners
                }
                for h in self.session_state.hands_played
            ]
        }
