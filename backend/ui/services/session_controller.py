from __future__ import annotations

from typing import Any, Callable, Dict
import time


class SessionController:
    """
    Bridges an FPSM-like engine to the UI store by translating snapshots
    to store actions. The controller does not schedule time; GameDirector
    (out of scope here) would drive progression.
    """

    def __init__(self, session_id: str, services, store, fsm: Any):
        self.session_id = session_id
        self.services = services
        self.store = store
        self.fsm = fsm
        self._unsubs: list[Callable[[], None]] = []

    def start(self) -> None:
        # Subscribe to FSM updates if available
        if hasattr(self.fsm, "subscribe"):
            self._unsubs.append(
                self.fsm.subscribe("snapshot", self._on_snapshot)
            )

    def _on_snapshot(self, snapshot: Dict[str, Any]) -> None:
        # Expected snapshot fields: pot, seats, board, dealer
        if "pot" in snapshot:
            amt = int(snapshot.get("pot") or 0)
            self.store.dispatch({"type": "SET_POT", "amount": amt})
        if "seats" in snapshot:
            self.store.dispatch(
                {"type": "SET_SEATS", "seats": snapshot["seats"]}
            )
        if "board" in snapshot:
            self.store.dispatch(
                {"type": "SET_BOARD", "board": snapshot["board"]}
            )
        if "dealer" in snapshot:
            self.store.dispatch(
                {"type": "SET_DEALER", "dealer": snapshot["dealer"]}
            )

    def dispose(self) -> None:
        for u in self._unsubs:
            try:
                u()
            except Exception:
                pass
        self._unsubs.clear()


class EnhancedRPGWController:
    """Controller for Enhanced RPGW actions - maintains architectural compliance."""
    
    def __init__(self, event_bus, store, ppsm):
        self.event_bus = event_bus
        self.store = store
        self.ppsm = ppsm
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """Setup event handlers for Enhanced RPGW actions."""
        self.event_bus.subscribe(
            "enhanced_rpgw:action_executed",
            self._handle_action_execution
        )
        
        self.event_bus.subscribe(
            "enhanced_rpgw:trigger_animation",
            self._handle_animation_trigger
        )
    
    def _handle_action_execution(self, event_data):
        """Handle Enhanced RPGW action execution via PPSM."""
        try:
            action = event_data['action']
            action_index = event_data['action_index']
            
            # Execute action in PPSM (business logic)
            ppsm_result = self._execute_ppsm_action(action)
            
            # Update store with PPSM results
            self.store.dispatch({
                "type": "UPDATE_ENHANCED_RPGW_STATE",
                "updates": {
                    "ppsm_result": ppsm_result,
                    "last_executed_action": action,
                    "execution_timestamp": time.time()
                }
            })
            
            # Trigger appropriate animations/sounds
            self._trigger_action_feedback(action, ppsm_result)
            
            print(f"🎯 Enhanced RPGW: Action {action_index} executed via PPSM")
            
        except Exception as e:
            print(f"⚠️ Enhanced RPGW: Action execution error: {e}")
            # Dispatch error state
            self.store.dispatch({
                "type": "UPDATE_ENHANCED_RPGW_STATE",
                "updates": {
                    "error": str(e),
                    "execution_status": "error"
                }
            })
    
    def _execute_ppsm_action(self, action):
        """Execute action in PPSM - pure business logic."""
        action_type = action['type']
        
        if action_type == 'DEAL_HOLE':
            return {"type": "hole_cards_dealt", "status": "success"}
        
        elif action_type == 'DEAL_BOARD':
            street = action['payload']['street']
            board = action['payload'].get('board', [])
            return {
                "type": "board_dealt",
                "street": street,
                "cards": board,
                "status": "success"
            }
        
        elif action_type in ['POST_BLIND', 'BET', 'RAISE', 'CALL', 'CHECK', 'FOLD']:
            actor_uid = action['payload'].get('actor_uid')
            amount = action['payload'].get('amount', 0)
            return {
                "type": "player_action",
                "action": action_type,
                "actor": actor_uid,
                "amount": amount,
                "status": "success"
            }
        
        elif action_type == 'END_HAND':
            return {"type": "hand_ended", "status": "success"}
        
        return {"type": "unknown", "status": "unknown"}
    
    def _trigger_action_feedback(self, action, ppsm_result):
        """Trigger appropriate feedback (sounds, animations) based on action."""
        action_type = action['type']
        
        # Map action types to feedback events
        feedback_mapping = {
            'DEAL_HOLE': 'card_deal',
            'DEAL_BOARD': 'card_deal',
            'POST_BLIND': 'chip_bet',
            'BET': 'player_bet',
            'RAISE': 'player_bet',
            'CALL': 'player_call',
            'CHECK': 'player_check',
            'FOLD': 'player_fold',
            'END_HAND': 'hand_end'
        }
        
        feedback_type = feedback_mapping.get(action_type, 'default')
        
        # Publish feedback event
        self.event_bus.publish(
            "enhanced_rpgw:feedback",
            {
                "type": feedback_type,
                "action": action,
                "ppsm_result": ppsm_result
            }
        )
    
    def _handle_animation_trigger(self, event_data):
        """Handle animation trigger events."""
        animation_type = event_data.get('type')
        
        if animation_type == 'player_highlight':
            # Schedule highlight clear animation
            self.event_bus.publish(
                "enhanced_rpgw:animation_event",
                {
                    "type": "SCHEDULE_HIGHLIGHT_CLEAR",
                    "delay_ms": 200,
                    "action": "clear_highlight"
                }
            )
        
        print(f"🎬 Enhanced RPGW: Animation triggered: {animation_type}")

