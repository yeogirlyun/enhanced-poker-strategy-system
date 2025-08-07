#!/usr/bin/env python3
"""
Test script for the FastAPI backend
"""
import requests
import json
import time

def test_api():
    """Test the FastAPI backend endpoints."""
    base_url = "http://127.0.0.1:8000"
    
    try:
        # Test 1: Create a new game
        print("🧪 Testing new game creation...")
        response = requests.post(f"{base_url}/api/game/new")
        if response.status_code == 200:
            data = response.json()
            session_id = data['session_id']
            game_state = data['game_state']
            print(f"✅ New game created: {session_id}")
            print(f"📊 Game state: {len(game_state['players'])} players, pot: ${game_state['pot']:.2f}")
        else:
            print(f"❌ Failed to create game: {response.status_code}")
            return
        
        # Test 2: Get current state
        print("\n🧪 Testing state retrieval...")
        response = requests.get(f"{base_url}/api/game/{session_id}/state")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ State retrieved successfully")
            print(f"📊 Current action player: {data['game_state']['action_player']}")
        else:
            print(f"❌ Failed to get state: {response.status_code}")
            return
        
        # Test 3: Perform an action (if it's human's turn)
        print("\n🧪 Testing action submission...")
        game_state = data['game_state']
        if game_state.get('is_users_turn', False):
            action_data = {"action": "call", "size": 0.0}
            response = requests.post(f"{base_url}/api/game/{session_id}/action", json=action_data)
            if response.status_code == 200:
                print("✅ Action submitted successfully")
            else:
                print(f"❌ Failed to submit action: {response.status_code}")
        else:
            print("ℹ️ Not human's turn, skipping action test")
        
        print("\n🎉 All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API server")
        print("Make sure to run: cd backend && uvicorn main:app --reload")
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    print("🚀 Testing FastAPI Backend...")
    test_api() 