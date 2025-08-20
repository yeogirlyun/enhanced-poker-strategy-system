import json
import random
from typing import List
from backend.core.pure_poker_state_machine import PurePokerStateMachine, GameConfig
from .industry_gto_engine import IndustryGTOEngine
from .gto_decision_engine_adapter import GTODecisionEngineAdapter

class GTOHandsGenerator:
    def __init__(self, player_count: int):
        self.player_count = player_count
        self.gto_engine = IndustryGTOEngine(player_count=player_count)
        self.adapter = GTODecisionEngineAdapter(self.gto_engine)
        config = GameConfig(num_players=player_count, starting_stack=10000.0, small_blind=50.0, big_blind=100.0)
        self.ppsm = PurePokerStateMachine(config=config, decision_engine=self.adapter)

    def generate_hand(self) -> dict:
        self.ppsm.start_hand()
        while not self.ppsm.is_hand_complete():
            self.ppsm.step()
        final_state = self.ppsm.get_game_info()
        return {
            "hand_id": f"gto_generated_{random.randint(1000, 9999)}",
            "player_count": self.player_count, "final_pot": final_state['pot'],
            "board": final_state['board'], "players": final_state['players']
        }

    def generate_hands_batch(self, hands_count: int) -> List[dict]:
        return [self.generate_hand() for _ in range(hands_count)]

    def export_to_json(self, hands: List[dict], filename: str) -> bool:
        try:
            with open(filename, 'w') as f:
                json.dump(hands, f, indent=2)
            return True
        except Exception:
            return False