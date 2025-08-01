# Poker Trainer Web Application - Setup Guide

This guide will walk you through setting up and running the full-stack poker trainer application, which includes a Python/FastAPI backend and a React frontend.

## Project Structure

Your project is now organized into a clean full-stack architecture:

```
/Poker/
|
|--- backend/
|    |--- main.py                  # <-- The new FastAPI backend server
|    |--- player.py
|    |--- table.py
|    |--- decision_engine.py
|    |--- enhanced_hand_evaluation.py
|    |--- session_logger.py
|    |--- strategy.json            # Your existing strategy file
|    |--- holdem_sessions.db       # Your existing database file
|    |--- requirements.txt         # Python dependencies
|
|--- frontend/
|    |--- poker_trainer_ui.html    # <-- The new React frontend UI
|
|--- README.md                      # This file
```

## Step 1: Set Up the Python Backend

The backend runs the game logic and provides REST API endpoints.

#### A. Install Dependencies

Open your terminal, navigate into the `backend` folder, and run this command:

```bash
cd backend
pip install -r requirements.txt
```

#### B. Run the Backend Server

While still in the `backend` folder, run the following command to start the game server:

```bash
uvicorn main:app --reload
```

You should see output indicating that the server is running, typically on `http://127.0.0.1:8000`. Keep this terminal window open.

## Step 2: Set Up the React Frontend

The frontend is the visual interface you'll interact with in your browser.

#### A. Open in Browser

Simply open the `frontend/poker_trainer_ui.html` file with your web browser (e.g., Google Chrome, Firefox). You can usually do this by double-clicking the file.

The web page will load, and it will automatically connect to the backend server you started in the previous step. You can now start training!

## Step 3: Start Playing

1. **Backend**: Make sure the FastAPI server is running (`uvicorn main:app --reload`)
2. **Frontend**: Open `frontend/poker_trainer_ui.html` in your browser
3. **Play**: The game will automatically start and you can begin playing!

## Architecture Benefits

This new architecture provides several key advantages:

### **1. Clean Separation of Concerns**
- **Backend**: Handles all game logic, state management, and bot AI
- **Frontend**: Only responsible for rendering the UI and user interactions
- **No State Synchronization Issues**: The backend is the single source of truth

### **2. Scalability**
- Easy to add new features to either frontend or backend independently
- Can support multiple frontends (web, mobile, desktop)
- Backend can handle multiple concurrent games

### **3. Debugging & Maintenance**
- Clear separation makes bugs easier to isolate
- Can test backend logic independently
- Frontend can be developed and tested separately

### **4. Modern Web Standards**
- RESTful API design
- JSON data exchange
- CORS support for cross-origin requests
- Real-time updates via polling

## Troubleshooting

### **Connection Error**
If you see a "Connection Error" message:
1. Make sure the backend server is running (`uvicorn main:app --reload`)
2. Check that the server is running on `http://127.0.0.1:8000`
3. Try refreshing the browser page

### **Action Not Working**
If actions aren't being processed:
1. Check the browser's developer console for errors
2. Verify the backend server is still running
3. Check the backend terminal for error messages

### **Sound Issues**
If sound isn't working:
1. Click the sound toggle button (🔊/🔇) in the top-right corner
2. Make sure your browser allows audio playback
3. Try clicking anywhere on the page to initialize audio

## API Endpoints

The backend provides these REST API endpoints:

- `POST /api/game/new` - Creates a new game session
- `POST /api/game/{session_id}/action` - Performs a player action
- `GET /api/game/{session_id}/state` - Gets current game state

## Next Steps

With this architecture in place, you can now:

1. **Add New Features**: Easily add new game modes, statistics, or UI improvements
2. **Scale Up**: Support multiple concurrent games or players
3. **Deploy**: Deploy the backend to a cloud service and frontend to a web server
4. **Extend**: Add mobile apps, desktop clients, or other frontends

The application is now much more robust and maintainable! 