Poker Trainer Web Application - Setup GuideThis guide will walk you through setting up and running the full-stack poker trainer application, which includes a Python/FastAPI backend and a React frontend.Project StructureFirst, organize your project files into the following structure. This is crucial for the application to work correctly./poker_trainer_project/
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
Action Required:Create a main folder named poker_trainer_project.Inside it, create a backend folder and a frontend folder.Move all your existing .py files, strategy.json, and holdem_sessions.db into the backend folder.I will provide the content for main.py, requirements.txt, and poker_trainer_ui.html in the next steps.Step 1: Set Up the Python BackendThe backend runs the game logic.A. Create requirements.txtIn your backend folder, create a file named requirements.txt and add the following lines. This file lists the Python libraries needed.fastapi
uvicorn[standard]
python-cors
B. Install DependenciesOpen your terminal, navigate into the backend folder, and run this command:pip install -r requirements.txt
C. Run the Backend ServerWhile still in the backend folder, run the following command to start the game server:uvicorn main:app --reload
You should see output indicating that the server is running, typically on http://127.0.0.1:8000. Keep this terminal window open.Step 2: Set Up the React FrontendThe frontend is the visual interface you'll interact with in your browser.A. Save the Frontend FileSave the poker_trainer_ui.html file (which I will provide) inside your frontend folder.B. Open in BrowserSimply open the poker_trainer_ui.html file with your web browser (e.g., Google Chrome, Firefox). You can usually do this by double-clicking the file.The web page will load, and it will automatically connect to the backend server you started in the previous step. You can now start training!