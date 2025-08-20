#!/usr/bin/env python3
"""
HandsReviewEventController - Architecture compliant event handler for hands review.
Handles business logic triggered by UI actions via Store/Reducer pattern.
"""

from typing import Dict, Any
import time


class HandsReviewEventController:
    """
    Architecture compliant controller for hands review events.
    
    This controller handles business logic triggered by Store actions,
    maintaining clean separation between UI and business logic.
    """
    
    def __init__(self, event_bus, store, services):
        self.event_bus = event_bus
        self.store = store
        self.services = services
        self.session_managers = {}  # session_id -> HandsReviewSessionManager
        
        # Subscribe to hands review events
        self._setup_event_handlers()
        print("🎯 HandsReviewEventController: Architecture compliant controller initialized")
    
    def _setup_event_handlers(self):
        """Setup event handlers for hands review actions."""
        self.event_bus.subscribe(
            "hands_review:next_action_requested",
            self._handle_next_action_request
        )
        
        self.event_bus.subscribe(
            "hands_review:session_created",
            self._handle_session_created
        )
        
        self.event_bus.subscribe(
            "hands_review:session_disposed",
            self._handle_session_disposed
        )
    
    def _handle_next_action_request(self, event_data: Dict[str, Any]):
        """Handle next action request - pure business logic."""
        try:
            session_id = event_data.get('session_id')
            timestamp = event_data.get('timestamp', time.time())
            
            print(f"🎯 HandsReviewEventController: Processing next action for session {session_id}")
            
            # Get session manager
            session_manager = self.session_managers.get(session_id)
            if not session_manager:
                print(f"⚠️ HandsReviewEventController: No session manager for {session_id}")
                self._update_review_status("error", f"Session {session_id} not found")
                return
            
            # Execute business logic via session manager
            try:
                session_state = session_manager.execute_action()
                
                # Update store with results
                if session_state:
                    self.store.dispatch({
                        "type": "UPDATE_HANDS_REVIEW_STATE",
                        "session_id": session_id,
                        "state": session_state,
                        "timestamp": timestamp
                    })
                    
                    # Trigger UI update via event
                    self.event_bus.publish(
                        "hands_review:state_updated",
                        {
                            "session_id": session_id,
                            "state": session_state,
                            "timestamp": timestamp
                        }
                    )
                    
                    print(f"🎯 HandsReviewEventController: Action executed successfully")
                else:
                    self._update_review_status("completed", "Hand complete")
                    
            except Exception as e:
                print(f"❌ HandsReviewEventController: Action execution error: {e}")
                self._update_review_status("error", str(e))
                
        except Exception as e:
            print(f"❌ HandsReviewEventController: Event handling error: {e}")
            self._update_review_status("error", str(e))
    
    def _handle_session_created(self, event_data: Dict[str, Any]):
        """Register a new hands review session."""
        session_id = event_data.get('session_id')
        session_manager = event_data.get('session_manager')
        
        if session_id and session_manager:
            self.session_managers[session_id] = session_manager
            print(f"🎯 HandsReviewEventController: Registered session {session_id}")
    
    def _handle_session_disposed(self, event_data: Dict[str, Any]):
        """Clean up disposed session."""
        session_id = event_data.get('session_id')
        
        if session_id in self.session_managers:
            del self.session_managers[session_id]
            print(f"🎯 HandsReviewEventController: Disposed session {session_id}")
    
    def _update_review_status(self, status: str, message: str = ""):
        """Update review status in store."""
        self.store.dispatch({
            "type": "SET_REVIEW_STATUS",
            "status": status,
            "message": message,
            "timestamp": time.time()
        })
    
    def dispose(self):
        """Clean up controller resources."""
        self.session_managers.clear()
        print("🎯 HandsReviewEventController: Disposed")
