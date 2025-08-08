#!/usr/bin/env python3
"""
PHH (Poker Hand History) Converter for Practice Sessions

This module converts practice session hands from our internal JSON format
to PHH format for integration with the hands review system and legendary
hands framework.

Features:
- Convert SessionLogger hand data to PHH format
- Export individual hands or entire sessions as .phh files
- Integration with hands review panel for seamless practice hand analysis
- Compatible with existing PHH validation framework
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from .session_logger import SessionLog, HandLog, ActionLog


class PHHConverter:
    """Converts practice session data to PHH format."""
    
    def __init__(self):
        self.suits = {'h': '♥', 'd': '♦', 'c': '♣', 's': '♠'}
        self.ranks = {'A': 'A', 'K': 'K', 'Q': 'Q', 'J': 'J', 'T': '10',
                      '9': '9', '8': '8', '7': '7', '6': '6', '5': '5',
                      '4': '4', '3': '3', '2': '2'}
    
    def convert_session_to_phh(self, session_log: SessionLog,
                               output_dir: str = "logs") -> str:
        """Convert an entire session to a PHH file."""
        if not session_log.hands:
            raise ValueError("No hands in session to convert")
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Create PHH filename
        start_time = datetime.fromtimestamp(session_log.start_time)
        timestamp = start_time.strftime("%Y%m%d_%H%M%S")
        session_id_short = session_log.session_id[:8]
        filename = f"practice_session_{timestamp}_{session_id_short}.phh"
        
        file_path = output_path / filename
        
        # Generate PHH content
        phh_content = self._generate_session_phh_header(session_log)
        
        for hand in session_log.hands:
            if hand.hand_complete:  # Only export completed hands
                phh_content += ("\n" +
                               self._convert_hand_to_phh(hand, session_log))
        
        # Write to file
        with open(file_path, 'w') as f:
            f.write(phh_content)
        
        return str(file_path)
    
    def convert_hand_to_phh(self, hand_log: HandLog, session_log: SessionLog) -> str:
        """Convert a single hand to PHH format."""
        return self._convert_hand_to_phh(hand_log, session_log)
    
    def _generate_session_phh_header(self, session_log: SessionLog) -> str:
        """Generate PHH file header for the session."""
        start_time = datetime.fromtimestamp(session_log.start_time)
        formatted_date = start_time.strftime("%Y-%m-%d %H:%M:%S")
        
        header = f"""# Practice Session PHH File
# Generated from Poker Trainer Practice Session
# Session ID: {session_log.session_id}
# Start Time: {formatted_date}
# Players: {session_log.num_players}
# Hands Played: {session_log.hands_played}
# Starting Stack: ${session_log.starting_stack:.2f}
# Blinds: ${session_log.blinds.get('small', 0.5):.2f}/${session_log.blinds.get('big', 1.0):.2f}
# Human Player: {session_log.human_player}
#
# This file contains practice hands that can be reviewed and analyzed
# using the hands review panel and legendary hands framework.
"""
        return header
    
    def _convert_hand_to_phh(self, hand: HandLog, session: SessionLog) -> str:
        """Convert a single HandLog to PHH format."""
        # Start hand entry
        hand_time = datetime.fromtimestamp(hand.timestamp)
        formatted_time = hand_time.strftime("%Y-%m-%d %H:%M:%S")
        
        phh_lines = [
            f"",
            f"# Hand {hand.hand_number} - {formatted_time}",
            f"# Dealer: Position {hand.dealer_button}",
            f"# Duration: {hand.hand_duration_ms}ms" if hand.hand_duration_ms else "# Duration: Unknown",
            f"# Winner: {hand.winner}" if hand.winner else "# Winner: Unknown",
            f"# Pot: ${hand.pot_size:.2f}",
            f"",
            f"variant = \"NLHE\"",
            f"ante = 0",
            f"blinds = [{hand.sb_amount}, {hand.bb_amount}]",
            f"min_bet = {hand.bb_amount}",
            f"starting_stacks = [{', '.join([str(p['stack']) for p in hand.players])}]",
            f"actions = ["
        ]
        
        # Add hole cards
        if hand.hole_cards:
            hole_cards_line = "  # Hole cards: "
            for player_name, cards in hand.hole_cards.items():
                formatted_cards = self._format_cards(cards)
                hole_cards_line += f"{player_name}: {formatted_cards} "
            phh_lines.append(hole_cards_line)
        
        # Add board cards if available
        if hand.board_cards:
            formatted_board = self._format_cards(hand.board_cards)
            phh_lines.append(f"  # Board: {formatted_board}")
        
        # Convert all actions by street
        all_actions = []
        
        # Collect actions from all streets
        for actions_list in [hand.preflop_actions, hand.flop_actions, 
                           hand.turn_actions, hand.river_actions]:
            all_actions.extend(actions_list)
        
        # Sort actions by timestamp to ensure correct order
        all_actions.sort(key=lambda x: x.timestamp)
        
        # Convert actions to PHH format
        for action in all_actions:
            phh_action = self._convert_action_to_phh(action)
            if phh_action:
                phh_lines.append(f"  {phh_action},")
        
        # Close actions array
        phh_lines.append("]")
        
        return "\n".join(phh_lines)
    
    def _convert_action_to_phh(self, action: ActionLog) -> Optional[str]:
        """Convert an ActionLog to PHH action format."""
        player_idx = action.player_index
        action_type = action.action.upper()
        amount = action.amount
        
        # Map our action types to PHH format
        if action_type == "FOLD":
            return f"\"p{player_idx}f\""
        elif action_type == "CHECK":
            return f"\"p{player_idx}x\""
        elif action_type == "CALL":
            if amount > 0:
                return f"\"p{player_idx}c{amount:.0f}\""
            else:
                return f"\"p{player_idx}x\""  # Call 0 is check
        elif action_type == "BET":
            return f"\"p{player_idx}b{amount:.0f}\""
        elif action_type == "RAISE":
            return f"\"p{player_idx}r{amount:.0f}\""
        elif action_type == "ALL_IN":
            return f"\"p{player_idx}A{amount:.0f}\""
        else:
            # Unknown action type, add as comment
            return f"# Unknown action: {action_type} {amount}"
    
    def _format_cards(self, cards: List[str]) -> str:
        """Format cards for PHH display."""
        if not cards:
            return "[]"
        
        formatted = []
        for card in cards:
            if len(card) >= 2:
                rank = card[0]
                suit = card[1].lower()
                # Convert to readable format
                rank_display = self.ranks.get(rank, rank)
                suit_display = self.suits.get(suit, suit)
                formatted.append(f"{rank_display}{suit_display}")
            else:
                formatted.append(card)
        
        return f"[{', '.join(formatted)}]"
    
    def export_practice_hand_metadata(self, hand: HandLog, session: SessionLog) -> Dict[str, Any]:
        """Export metadata for a practice hand for the review system."""
        return {
            "id": f"practice_{session.session_id[:8]}_{hand.hand_number}",
            "name": f"Practice Hand {hand.hand_number}",
            "category": "Practice Hands",
            "event": f"Practice Session {datetime.fromtimestamp(session.start_time).strftime('%Y-%m-%d')}",
            "description": f"Practice hand from training session. Winner: {hand.winner or 'Unknown'}",
            "players_involved": [p['name'] for p in hand.players],
            "source": "practice_session",
            "session_id": session.session_id,
            "hand_number": hand.hand_number,
            "timestamp": hand.timestamp,
            "pot_size": hand.pot_size,
            "duration_ms": hand.hand_duration_ms,
            "streets_reached": hand.streets_reached,
            "hand_complete": hand.hand_complete,
            "study_value": "Analyze your decision-making process and compare with GTO strategy",
            "why_notable": f"Practice hand with ${hand.pot_size:.2f} pot, {len(hand.streets_reached)} streets"
        }


class PracticeHandsPHHManager:
    """Manager for practice hands in PHH format."""
    
    def __init__(self, practice_hands_dir: str = "logs/practice_hands"):
        self.practice_hands_dir = Path(practice_hands_dir)
        self.practice_hands_dir.mkdir(exist_ok=True)
        self.converter = PHHConverter()
    
    def export_session_hands(self, session_log: SessionLog) -> List[str]:
        """Export all hands from a session to PHH format."""
        exported_files = []
        
        if not session_log.hands:
            return exported_files
        
        # Export entire session as one PHH file
        session_file = self.converter.convert_session_to_phh(
            session_log, str(self.practice_hands_dir)
        )
        exported_files.append(session_file)
        
        # Also export individual hand metadata for the review system
        metadata_file = self._export_session_metadata(session_log)
        if metadata_file:
            exported_files.append(metadata_file)
        
        return exported_files
    
    def _export_session_metadata(self, session_log: SessionLog) -> Optional[str]:
        """Export session metadata for the hands review system."""
        if not session_log.hands:
            return None
        
        # Create metadata for each completed hand
        hands_metadata = []
        for hand in session_log.hands:
            if hand.hand_complete:
                metadata = self.converter.export_practice_hand_metadata(hand, session_log)
                hands_metadata.append(metadata)
        
        if not hands_metadata:
            return None
        
        # Create metadata file
        start_time = datetime.fromtimestamp(session_log.start_time)
        timestamp = start_time.strftime("%Y%m%d_%H%M%S")
        session_id_short = session_log.session_id[:8]
        filename = f"practice_metadata_{timestamp}_{session_id_short}.json"
        
        metadata_path = self.practice_hands_dir / filename
        
        metadata_content = {
            "session_info": {
                "session_id": session_log.session_id,
                "start_time": session_log.start_time,
                "end_time": session_log.end_time,
                "num_players": session_log.num_players,
                "starting_stack": session_log.starting_stack,
                "blinds": session_log.blinds,
                "hands_played": session_log.hands_played
            },
            "hands": hands_metadata
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata_content, f, indent=2)
        
        return str(metadata_path)
    
    def get_practice_hands_files(self) -> List[Dict[str, str]]:
        """Get list of available practice hands files."""
        files = []
        
        for file_path in self.practice_hands_dir.glob("*.phh"):
            metadata_file = file_path.with_suffix('.json').name.replace('practice_session_', 'practice_metadata_')
            metadata_path = self.practice_hands_dir / metadata_file
            
            files.append({
                "phh_file": str(file_path),
                "metadata_file": str(metadata_path) if metadata_path.exists() else None,
                "session_date": self._extract_date_from_filename(file_path.name),
                "file_size": file_path.stat().st_size
            })
        
        return sorted(files, key=lambda x: x["session_date"], reverse=True)
    
    def _extract_date_from_filename(self, filename: str) -> str:
        """Extract readable date from PHH filename."""
        try:
            # Extract timestamp from filename like "practice_session_20231201_143022_abc12345.phh"
            parts = filename.split('_')
            if len(parts) >= 4:
                date_part = parts[2]  # "20231201"
                time_part = parts[3]  # "143022"
                
                year = date_part[:4]
                month = date_part[4:6]
                day = date_part[6:8]
                hour = time_part[:2]
                minute = time_part[2:4]
                
                return f"{year}-{month}-{day} {hour}:{minute}"
        except:
            pass
        
        return "Unknown Date"


def integrate_with_session_manager():
    """Helper function to show how to integrate with existing session manager."""
    pass  # Implementation example below


# Example integration with SessionManager and SessionLogger
class EnhancedSessionLogger:
    """Extended SessionLogger with PHH export capabilities."""
    
    def __init__(self, *args, **kwargs):
        # This would extend the existing SessionLogger
        self.phh_manager = PracticeHandsPHHManager()
        # Initialize parent class...
    
    def end_session_with_phh_export(self):
        """End session and automatically export to PHH format."""
        # End session normally first
        # self.end_session()
        
        # Then export to PHH
        if hasattr(self, 'session') and self.session:
            try:
                exported_files = self.phh_manager.export_session_hands(self.session)
                print(f"✅ Exported {len(exported_files)} PHH files: {exported_files}")
                return exported_files
            except Exception as e:
                print(f"❌ Error exporting to PHH: {e}")
                return []
        
        return []
