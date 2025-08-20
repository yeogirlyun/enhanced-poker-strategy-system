from typing import Optional, Tuple
from backend.core.pure_poker_state_machine import DecisionEngineProtocol
from backend.core.poker_types import ActionType as PPSMActionType, GameState as PPSMGameState
from .unified_types import ActionType, StandardGameState, PlayerState, UnifiedDecisionEngineProtocol

class GTODecisionEngineAdapter(DecisionEngineProtocol):
    def __init__(self, gto_engine: UnifiedDecisionEngineProtocol):
        self.gto_engine = gto_engine

    def get_decision(self, player_name: str, game_state: PPSMGameState) -> Optional[Tuple[PPSMActionType, Optional[float]]]:
        try:
            standard_game_state = self._convert_to_standard_game_state(game_state)
            action, amount = self.gto_engine.get_decision(player_name, standard_game_state)
            ppsm_action = PPSMActionType[action.name]
            return ppsm_action, amount
        except Exception as e:
            print(f"❌ GTODecisionEngineAdapter Error: {e}")
            return PPSMActionType.FOLD, None

    def _convert_to_standard_game_state(self, ppsm_game_state: PPSMGameState) -> StandardGameState:
        players = tuple(
            PlayerState(
                name=p.name, stack=int(p.stack), position=p.position, cards=tuple(p.cards),
                current_bet=int(p.current_bet), is_active=p.is_active, has_acted=p.has_acted_this_round
            ) for p in ppsm_game_state.players
        )
        legal_actions = frozenset(ActionType[a.name] for a in ppsm_game_state.get_legal_actions())
        return StandardGameState(
            pot=int(ppsm_game_state.displayed_pot()), street=ppsm_game_state.street, board=tuple(ppsm_game_state.board),
            players=players, current_bet_to_call=int(ppsm_game_state.current_bet - ppsm_game_state.players[ppsm_game_state.action_player].current_bet),
            to_act_player_index=ppsm_game_state.action_player, legal_actions=legal_actions
        )

    def has_decision_for_player(self, player_name: str) -> bool:
        return self.gto_engine.has_decision_for_player(player_name)

    def reset_for_new_hand(self) -> None:
        self.gto_engine.reset_for_new_hand()