#!/usr/bin/env python3
"""
Comprehensive Session Logger for Poker Training System

This module provides detailed JSON logging for:
- Complete session tracking
- Hand-by-hand analysis  
- Player action logging
- System debugging
- Performance analytics
- Research data collection

All data is stored in structured JSON format for easy analysis.
"""

import json
import time
import uuid
import signal
import atexit
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field

# Define debug_print locally to avoid circular import
def debug_print(*args, **kwargs):
    """Debug print function that flushes immediately."""
    print(*args, **kwargs, flush=True)


@dataclass
class ActionLog:
    """Single player action within a hand."""
    timestamp: float
    hand_id: str
    player_name: str
    player_index: int
    action: str  # FOLD, CALL, BET, RAISE, CHECK
    amount: float
    stack_before: float
    stack_after: float
    pot_before: float
    pot_after: float
    current_bet: float
    street: str  # preflop, flop, turn, river
    position: str
    is_human: bool
    decision_time_ms: Optional[int] = None
    pot_odds: Optional[float] = None
    stack_pot_ratio: Optional[float] = None


@dataclass
class HandLog:
    """Complete data for a single hand."""
    hand_id: str
    session_id: str
    timestamp: float
    hand_number: int
    
    # Pre-hand setup
    dealer_button: int
    small_blind: int
    big_blind: int
    sb_amount: float
    bb_amount: float
    
    # Player data at hand start
    players: List[Dict[str, Any]]
    
    # Cards
    hole_cards: Dict[str, List[str]]  # player_name -> [card1, card2]
    board_cards: List[str]
    
    # Actions by street
    preflop_actions: List[ActionLog] = field(default_factory=list)
    flop_actions: List[ActionLog] = field(default_factory=list)
    turn_actions: List[ActionLog] = field(default_factory=list)
    river_actions: List[ActionLog] = field(default_factory=list)
    
    # Hand results
    winner: Optional[str] = None
    winning_hand: Optional[str] = None
    pot_size: float = 0.0
    showdown: bool = False
    hand_complete: bool = False
    
    # Timing
    hand_duration_ms: Optional[int] = None
    streets_reached: List[str] = field(default_factory=list)


@dataclass
class SystemLog:
    """System-level debug and performance data."""
    timestamp: float
    session_id: str
    level: str  # DEBUG, INFO, WARNING, ERROR
    category: str  # UI, STATE_MACHINE, SOUND, ANIMATION, etc.
    message: str
    data: Optional[Dict[str, Any]] = None


@dataclass
class SessionLog:
    """Complete session data."""
    session_id: str
    start_time: float
    end_time: Optional[float] = None
    
    # Session setup
    num_players: int = 6
    starting_stack: float = 100.0
    blinds: Dict[str, float] = field(default_factory=lambda: {"small": 0.5, "big": 1.0})
    
    # Player information
    human_player: str = "Player 1"
    bot_players: List[str] = field(default_factory=list)
    
    # Session results
    hands_played: int = 0
    session_duration_ms: Optional[int] = None
    
    # Data collections
    hands: List[HandLog] = field(default_factory=list)
    system_logs: List[SystemLog] = field(default_factory=list)
    
    # Statistics
    human_stats: Dict[str, Any] = field(default_factory=dict)
    bot_stats: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)


class SessionLogger:
    """
    Comprehensive logging system for poker training sessions.
    
    Features:
    - Real-time JSON logging
    - Structured data capture
    - Performance tracking
    - Debug message logging
    - Analysis-ready output
    """
    
    def __init__(self, log_directory: str = "logs"):
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(exist_ok=True)
        
        # Current session
        self.session: Optional[SessionLog] = None
        self.current_hand: Optional[HandLog] = None
        self.hand_start_time: Optional[float] = None
        
        # Timing tracking
        self.action_start_times: Dict[str, float] = {}
        
        # File paths
        self.session_file: Optional[Path] = None
        self.system_log_file: Optional[Path] = None
        
        # PHH export functionality
        self._setup_phh_export()
        
        # Graceful shutdown setup
        self._shutdown_handlers_registered = False
        self._register_shutdown_handlers()
    
    def _setup_phh_export(self):
        """Setup PHH export functionality."""
        try:
            from .phh_converter import PracticeHandsPHHManager
            self.phh_manager = PracticeHandsPHHManager()
        except ImportError as e:
            print(f"Warning: PHH export not available: {e}")
            self.phh_manager = None
    
    def start_session(self, num_players: int = 6, starting_stack: float = 100.0) -> str:
        """Start a new logging session."""
        session_id = str(uuid.uuid4())
        timestamp = time.time()
        
        self.session = SessionLog(
            session_id=session_id,
            start_time=timestamp,
            num_players=num_players,
            starting_stack=starting_stack,
            bot_players=[f"Player {i+2}" for i in range(num_players-1)]
        )
        
        # Create session files
        session_datetime = datetime.fromtimestamp(timestamp).strftime("%Y%m%d_%H%M%S")
        self.session_file = self.log_directory / f"session_{session_datetime}_{session_id[:8]}.json"
        self.system_log_file = self.log_directory / f"system_{session_datetime}_{session_id[:8]}.json"
        
        self.log_system("INFO", "SESSION", f"Started new session {session_id}", {
            "num_players": num_players,
            "starting_stack": starting_stack
        })
        
        return session_id
    
    def end_session(self):
        """End the current session and save final data."""
        if not self.session:
            return
            
        self.session.end_time = time.time()
        if self.session.start_time:
            self.session.session_duration_ms = int((self.session.end_time - self.session.start_time) * 1000)
        
        self.log_system("INFO", "SESSION", "Session ended", {
            "hands_played": self.session.hands_played,
            "duration_ms": self.session.session_duration_ms
        })
        
        # Export to PHH format before saving
        self._export_session_to_phh()
        
        self._save_session()
    
    def _export_session_to_phh(self) -> List[str]:
        """Export current session to PHH format."""
        exported_files = []
        
        if not self.session or not self.phh_manager:
            return exported_files
        
        try:
            # Only export if we have completed hands
            completed_hands = [h for h in self.session.hands if h.hand_complete]
            
            if completed_hands:
                exported_files = self.phh_manager.export_session_hands(self.session)
                
                self.log_system("INFO", "PHH_EXPORT", f"Exported {len(exported_files)} PHH files", {
                    "exported_files": exported_files,
                    "hands_exported": len(completed_hands)
                })
            else:
                self.log_system("INFO", "PHH_EXPORT", "No completed hands to export", {})
        
        except Exception as e:
            self.log_system("ERROR", "PHH_EXPORT", f"Error exporting to PHH: {str(e)}", {
                "error": str(e)
            })
        
        return exported_files
    
    def start_hand(self, hand_number: int, players: List[Dict], dealer_button: int, 
                   small_blind: int, big_blind: int, sb_amount: float = 0.5, bb_amount: float = 1.0) -> str:
        """Start logging a new hand."""
        import sys
        print(f"🐛 DEBUG: start_hand called for hand {hand_number}")
        sys.stdout.flush()
        print(f"🐛 DEBUG: session = {self.session}")
        sys.stdout.flush()
        
        if not self.session:
            print("❌ DEBUG: No active session!")
            sys.stdout.flush()
            raise ValueError("No active session")
            
        hand_id = f"{self.session.session_id}_{hand_number}"
        self.hand_start_time = time.time()
        
        print(f"🐛 DEBUG: Creating new HandLog with hand_id = {hand_id}")
        sys.stdout.flush()
        
        self.current_hand = HandLog(
            hand_id=hand_id,
            session_id=self.session.session_id,
            timestamp=self.hand_start_time,
            hand_number=hand_number,
            dealer_button=dealer_button,
            small_blind=small_blind,
            big_blind=big_blind,
            sb_amount=sb_amount,
            bb_amount=bb_amount,
            players=[dict(p) for p in players],  # Deep copy
            hole_cards={},  # Initialize empty, will be populated by log_hole_cards
            board_cards=[]  # Initialize empty, will be populated by log_board_cards
        )
        
        print(f"✅ DEBUG: current_hand created: {self.current_hand}")
        sys.stdout.flush()
        
        self.log_system("INFO", "HAND", f"Started hand {hand_number}", {
            "hand_id": hand_id,
            "dealer_button": dealer_button,
            "blinds": {"sb": sb_amount, "bb": bb_amount}
        })
        
        print(f"✅ DEBUG: Hand {hand_number} logging started successfully")
        sys.stdout.flush()
        return hand_id
    
    def log_hole_cards(self, player_cards: Dict[str, List[str]]):
        """Log hole cards for all players."""
        import sys
        print(f"🐛 DEBUG: log_hole_cards called with {len(player_cards)} players")
        sys.stdout.flush()
        print(f"🐛 DEBUG: current_hand = {self.current_hand}")
        sys.stdout.flush()
        print(f"🐛 DEBUG: session = {self.session}")
        sys.stdout.flush()
        
        if not self.current_hand:
            print("❌ DEBUG: No current_hand, cannot log hole cards!")
            sys.stdout.flush()
            return
            
        self.current_hand.hole_cards = dict(player_cards)
        print(f"✅ DEBUG: Hole cards stored in current_hand")
        sys.stdout.flush()
        
        self.log_system("INFO", "CARDS", "Hole cards dealt", {
            "hand_id": self.current_hand.hand_id,
            "cards_dealt": len(player_cards)
        })
        print(f"✅ DEBUG: Hole cards system log completed")
        sys.stdout.flush()
    
    def log_board_cards(self, board: List[str], street: str):
        """Log community cards for current street."""
        if not self.current_hand:
            return
            
        self.current_hand.board_cards = list(board)
        if street not in self.current_hand.streets_reached:
            self.current_hand.streets_reached.append(street)
        
        self.log_system("INFO", "CARDS", f"Board cards - {street}", {
            "hand_id": self.current_hand.hand_id,
            "board": board,
            "street": street
        })
    
    def start_player_action(self, player_name: str):
        """Mark the start of a player's decision time."""
        self.action_start_times[player_name] = time.time()
    
    def log_action(self, player_name: str, player_index: int, action: str, amount: float,
                   stack_before: float, stack_after: float, pot_before: float, pot_after: float,
                   current_bet: float, street: str, position: str, is_human: bool):
        """Log a player action."""
        if not self.current_hand:
            return
        
        # Calculate decision time
        decision_time_ms = None
        if player_name in self.action_start_times:
            decision_time_ms = int((time.time() - self.action_start_times[player_name]) * 1000)
            del self.action_start_times[player_name]
        
        # Calculate pot odds and ratios
        pot_odds = None
        stack_pot_ratio = None
        if amount > 0 and pot_before > 0:
            pot_odds = amount / (pot_before + amount)
            stack_pot_ratio = stack_before / pot_before
        
        action_log = ActionLog(
            timestamp=time.time(),
            hand_id=self.current_hand.hand_id,
            player_name=player_name,
            player_index=player_index,
            action=action,
            amount=amount,
            stack_before=stack_before,
            stack_after=stack_after,
            pot_before=pot_before,
            pot_after=pot_after,
            current_bet=current_bet,
            street=street,
            position=position,
            is_human=is_human,
            decision_time_ms=decision_time_ms,
            pot_odds=pot_odds,
            stack_pot_ratio=stack_pot_ratio
        )
        
        # Add to appropriate street
        if street == "preflop":
            self.current_hand.preflop_actions.append(action_log)
        elif street == "flop":
            self.current_hand.flop_actions.append(action_log)
        elif street == "turn":
            self.current_hand.turn_actions.append(action_log)
        elif street == "river":
            self.current_hand.river_actions.append(action_log)
        
        self.log_system("INFO", "ACTION", f"{player_name} {action}", {
            "hand_id": self.current_hand.hand_id,
            "action": action,
            "amount": amount,
            "street": street,
            "decision_time_ms": decision_time_ms
        })
    
    def end_hand(self, winner: str, winning_hand: str, pot_size: float, showdown: bool = False):
        """Complete the current hand logging."""
        if not self.current_hand:
            debug_print(f"❌ DEBUG: No current hand to end")
            return
            
        debug_print(f"🔄 DEBUG: Ending hand with winner={winner}, hand={winning_hand}, pot=${pot_size:.2f}")
        
        self.current_hand.winner = winner
        self.current_hand.winning_hand = winning_hand
        self.current_hand.pot_size = pot_size
        self.current_hand.showdown = showdown
        self.current_hand.hand_complete = True
        
        if self.hand_start_time:
            self.current_hand.hand_duration_ms = int((time.time() - self.hand_start_time) * 1000)
        
        # Add to session
        if self.session:
            self.session.hands.append(self.current_hand)
            self.session.hands_played += 1
            debug_print(f"✅ DEBUG: Hand added to session, total hands = {self.session.hands_played}")
        else:
            debug_print(f"❌ ERROR: No session available for hand completion")
        
        self.log_system("INFO", "HAND", f"Hand completed", {
            "hand_id": self.current_hand.hand_id,
            "winner": winner,
            "pot_size": pot_size,
            "showdown": showdown,
            "duration_ms": self.current_hand.hand_duration_ms,
            "hand_complete": True
        })
        
        # Save session data incrementally
        self._save_session()
        
        self.current_hand = None
        self.hand_start_time = None
        debug_print(f"✅ DEBUG: Hand completion successful")
    
    def end_session_with_termination(self, termination_reason: str = "User quit"):
        """End session with termination note for incomplete hands."""
        debug_print(f"🔄 DEBUG: Ending session with termination: {termination_reason}")
        
        # Complete current hand if it exists
        if self.current_hand:
            debug_print(f"🔄 DEBUG: Completing incomplete hand due to termination")
            
            # Mark hand as incomplete
            self.current_hand.winner = "Session terminated"
            self.current_hand.winning_hand = f"Session terminated - {termination_reason}"
            self.current_hand.hand_complete = False  # Mark as incomplete
            self.current_hand.showdown = False
            
            if self.hand_start_time:
                self.current_hand.hand_duration_ms = int((time.time() - self.hand_start_time) * 1000)
            
            # Add to session
            if self.session:
                self.session.hands.append(self.current_hand)
                self.session.hands_played += 1
                debug_print(f"✅ DEBUG: Incomplete hand added to session")
            
            # Log the termination
            self.log_system("WARNING", "SESSION", f"Session terminated: {termination_reason}", {
                "hand_id": self.current_hand.hand_id,
                "termination_reason": termination_reason,
                "hand_complete": False,
                "pot_size": self.current_hand.pot_size
            })
            
            self.current_hand = None
            self.hand_start_time = None
        
        # End the session
        self.end_session()
        
        # Add final termination note
        self.log_system("INFO", "SESSION", f"Session ended by user: {termination_reason}", {
            "hands_played": self.session.hands_played if self.session else 0,
            "session_duration": time.time() - self.session.start_time if self.session else 0,
            "termination_reason": termination_reason
        })
        
        debug_print(f"✅ DEBUG: Session terminated successfully")
    
    def log_system(self, level: str, category: str, message: str, data: Optional[Dict] = None):
        """Log system-level messages with immediate flush."""
        if not self.session:
            return
            
        system_log = SystemLog(
            timestamp=time.time(),
            session_id=self.session.session_id,
            level=level,
            category=category,
            message=message,
            data=data
        )
        
        self.session.system_logs.append(system_log)
        
        # IMMEDIATE FLUSH - critical for debugging
        self._save_system_logs()
        self._force_flush_all()
    
    def _save_session(self):
        """Save session data to JSON file."""
        if not self.session or not self.session_file:
            return
            
        try:
            with open(self.session_file, 'w') as f:
                json.dump(asdict(self.session), f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving session: {e}")
    
    def _save_system_logs(self):
        """Save system logs to separate JSON file."""
        if not self.session or not self.system_log_file:
            return
            
        try:
            system_data = {
                "session_id": self.session.session_id,
                "logs": [asdict(log) for log in self.session.system_logs]
            }
            with open(self.system_log_file, 'w') as f:
                json.dump(system_data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving system logs: {e}")
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get a summary of the current session."""
        if not self.session:
            return {}
            
        return {
            "session_id": self.session.session_id,
            "hands_played": self.session.hands_played,
            "duration_ms": self.session.session_duration_ms,
            "players": self.session.num_players,
            "log_files": {
                "session": str(self.session_file) if self.session_file else None,
                "system": str(self.system_log_file) if self.system_log_file else None
            }
        }
    
    def _register_shutdown_handlers(self):
        """Register signal handlers for graceful shutdown."""
        if self._shutdown_handlers_registered:
            return
            
        try:
            # Register signal handlers for Ctrl+C and other termination signals
            signal.signal(signal.SIGINT, self._signal_handler)  # Ctrl+C
            signal.signal(signal.SIGTERM, self._signal_handler)  # Termination
            
            # Register atexit handler for normal program exit
            atexit.register(self._cleanup_on_exit)
            
            self._shutdown_handlers_registered = True
            print("DEBUG: Shutdown handlers registered successfully")
            
        except Exception as e:
            print(f"Warning: Could not register shutdown handlers: {e}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals (Ctrl+C, etc.)."""
        signal_names = {
            signal.SIGINT: "SIGINT (Ctrl+C)",
            signal.SIGTERM: "SIGTERM"
        }
        signal_name = signal_names.get(signum, f"Signal {signum}")
        
        print(f"\n🔄 Received {signal_name} - Gracefully shutting down...")
        print("💾 Saving session data...")
        
        # Save all pending data
        self._emergency_save()
        
        print("✅ Session data saved successfully!")
        print("👋 Goodbye!")
        
        # Exit cleanly
        exit(0)
    
    def _cleanup_on_exit(self):
        """Cleanup function called on normal program exit."""
        try:
            if self.session:
                print("🔄 Normal exit detected - saving final session data...")
                self.end_session()
                print("✅ Final session data saved!")
        except Exception as e:
            print(f"Warning: Error during exit cleanup: {e}")
    
    def _force_flush_all(self):
        """Force immediate flush of all log files."""
        try:
            import sys
            # Flush stdout/stderr for debug messages
            sys.stdout.flush()
            sys.stderr.flush()
            
            # Force save session and system logs
            self._save_session()
            self._save_system_logs()
            
        except Exception as e:
            print(f"Warning: Could not force flush: {e}")
    
    def _emergency_save(self):
        """Emergency save of all session data."""
        try:
            # Complete current hand if it's in progress
            if self.current_hand and not self.current_hand.hand_complete:
                self.current_hand.hand_complete = True
                self.current_hand.winner = "Unknown (Emergency Exit)"
                self.current_hand.winning_hand = "Session terminated"
                
                if self.hand_start_time:
                    self.current_hand.hand_duration_ms = int((time.time() - self.hand_start_time) * 1000)
                
                # Add to session if not already added
                if self.session and self.current_hand not in self.session.hands:
                    self.session.hands.append(self.current_hand)
                    self.session.hands_played += 1
            
            # End session properly
            if self.session:
                self.session.end_time = time.time()
                if self.session.start_time:
                    self.session.session_duration_ms = int((self.session.end_time - self.session.start_time) * 1000)
                
                # Log emergency shutdown
                self.log_system("WARNING", "SESSION", "Emergency shutdown - session terminated by user", {
                    "hands_completed": self.session.hands_played,
                    "session_duration_ms": self.session.session_duration_ms,
                    "shutdown_reason": "SIGINT/Ctrl+C"
                })
                
                # Force save
                self._save_session()
                self._save_system_logs()
                self._force_flush_all()
                
        except Exception as e:
            print(f"Error during emergency save: {e}")
            # Try to at least save what we can
            try:
                if self.session:
                    self._save_session()
                    self._force_flush_all()
            except:
                print("Failed to save session data")


# Global logger instance
_session_logger: Optional[SessionLogger] = None


def get_session_logger() -> SessionLogger:
    """Get the global session logger instance."""
    global _session_logger
    if _session_logger is None:
        _session_logger = SessionLogger()
    return _session_logger


def initialize_logging(log_directory: str = "logs") -> SessionLogger:
    """Initialize the global logging system."""
    global _session_logger
    _session_logger = SessionLogger(log_directory)
    return _session_logger