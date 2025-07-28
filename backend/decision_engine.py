# filename: decision_engine.py
"""
Decision Engine for the Advanced Hold'em Trainer

REVISION HISTORY:
================
Version 1.0 (2025-07-26) - Initial Refactoring
- Created the `decision_engine.py` module as part of a major OOP refactoring.
- Moved the `get_optimal_action` function from `integrated_trainer.py` into
  a new `DecisionEngine` class.
- This class is now solely responsible for interpreting the strategy file
  and determining the optimal move for a given game state.
- This change separates the "thinking" part of the AI from the game flow
  and orchestration logic, improving modularity.
"""

class DecisionEngine:
    """
    Calculates the optimal poker action based on game state and a strategy profile.
    """
    def get_optimal_action(self, state, strategy):
        """
        Enhanced optimal action calculation with modern blind defense.

        Args:
            state (dict): The current state of the game for the player to act.
                          Includes position, street, history, hs, etc.
            strategy (dict): The loaded strategy configuration from strategy.json.

        Returns:
            tuple: A tuple containing the optimal action (str) and size (float).
        """
        pos, street, actions, pfa, pot, to_call, is_ip = (
            state.get('position'), state.get('street'), state.get('history', []),
            state.get('was_aggressor'), state.get('pot'), state.get('to_call'), state.get('is_ip')
        )

        # Use the correct HS for the current street
        hs = state.get('dynamic_hs') if street != 'preflop' else state.get('preflop_hs', 0)
        pos_type = "IP" if is_ip else "OOP"

        try:
            if street == 'preflop':
                if not actions:
                    # Opening action - Fallback for new positions
                    if pos not in strategy['preflop']['open_rules']:
                        fallback_pos = 'UTG' if 'UTG' in pos else 'MP' if 'HJ' in pos else 'CO'
                        rule = strategy['preflop']['open_rules'][fallback_pos]
                    else:
                        rule = strategy['preflop']['open_rules'][pos]
                    return ('raise', rule['sizing']) if hs >= rule['threshold'] else ('fold', 0)

                elif 'raise' in actions and pos in ['BB', 'SB']:
                    # BLIND DEFENSE logic
                    if 'blind_defense' in strategy['preflop'] and pos in strategy['preflop']['blind_defense']:
                        # Simple heuristic to determine opener's position
                        opener = 'BTN' if pot <= 4.0 else 'CO' if pot <= 4.5 else 'MP' if pot <= 5.0 else 'UTG'
                        
                        vs_opener = f"vs_{opener}"
                        blind_rules = strategy['preflop']['blind_defense'][pos]
                        
                        if vs_opener not in blind_rules:
                            fallback_opener = 'CO' if opener == 'HJ' else 'MP' if 'UTG' in opener else opener
                            rule = blind_rules.get(f"vs_{fallback_opener}", blind_rules['vs_BTN']) # Default to vs_BTN
                        else:
                            rule = blind_rules[vs_opener]
                            
                        if hs >= rule['value_thresh']:
                            sizing = rule.get('sizing', 3.5) * to_call
                            return ('raise', sizing)
                        if rule['call_range'][0] <= hs <= rule['call_range'][1]:
                            return ('call', to_call)
                        return ('fold', 0)

                elif 'raise' in actions:
                    # Non-blind facing a raise
                    if pos not in strategy['preflop']['vs_raise']:
                        fallback_pos = 'UTG' if 'UTG' in pos else 'MP' if 'HJ' in pos else 'CO'
                        rule = strategy['preflop']['vs_raise'][fallback_pos][pos_type]
                    else:
                        rule = strategy['preflop']['vs_raise'][pos][pos_type]
                    if hs >= rule['value_thresh']:
                        return ('raise', rule['sizing'] * 3)
                    if rule['call_range'][0] <= hs <= rule['call_range'][1]:
                        return ('call', to_call)
                    return ('fold', 0)

            else:  # Postflop
                if pfa and not actions: # PFA is checking or betting
                    if pos not in strategy['postflop']['pfa'][street]:
                        fallback_pos = 'UTG' if 'UTG' in pos else 'MP' if 'HJ' in pos else 'BTN'
                        rule = strategy['postflop']['pfa'][street][fallback_pos][pos_type]
                    else:
                        rule = strategy['postflop']['pfa'][street][pos][pos_type]
                    
                    if hs >= rule['val_thresh']:
                        return ('bet', pot * rule['sizing'])
                    if hs >= rule['check_thresh']:
                        return ('check', 0)
                    return ('check', 0) # Check/fold otherwise

                if not pfa and 'bet' in actions: # Caller is facing a bet
                    if pos not in strategy['postflop']['caller'][street]:
                        fallback_pos = 'UTG' if 'UTG' in pos else 'MP' if 'HJ' in pos else 'BTN'
                        rule = strategy['postflop']['caller'][street][fallback_pos][pos_type]
                    else:
                        rule = strategy['postflop']['caller'][street][pos][pos_type]

                    bet_ratio = to_call / pot if pot > 0 else 1
                    bet_category = 'large_bet' if bet_ratio > 1 else 'medium_bet' if bet_ratio >= 0.5 else 'small_bet'
                    
                    val_raise, call_thresh = rule[bet_category]
                    
                    if hs >= val_raise:
                        return ('raise', to_call * 2.5)
                    if hs >= call_thresh:
                        return ('call', to_call)
                    return ('fold', 0)

        except KeyError as e:
            # Safe fallback if a specific strategy rule is missing
            print(f"Warning: Strategy lookup failed for key: {e}. Using default action.")
            return ('check' if to_call == 0 else 'fold', 0)

        # Default action if no other conditions are met
        return ('check' if to_call == 0 else 'fold', 0)
