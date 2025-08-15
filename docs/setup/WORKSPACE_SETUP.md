# 🎮 Poker Strategy System - Workspace Setup

## 📁 Workspace Files

This project includes workspace files for different IDEs to make development easier:

### **VS Code Workspace**
- **File**: `poker-strategy-system.code-workspace`
- **How to use**: Double-click the file or open it from VS Code
- **Features**:
  - Pre-configured Python interpreter
  - Code formatting with Black
  - Linting with Flake8
  - Built-in tasks for running CLI/GUI
  - Launch configurations for debugging

### **PyCharm Workspace**
- **Directory**: `poker-strategy-system.idea/`
- **How to use**: Open the project folder in PyCharm
- **Features**:
  - Pre-configured run configurations
  - Python interpreter setup
  - Working directory configuration

## 🚀 Quick Start

### **VS Code:**
1. Open `poker-strategy-system.code-workspace`
2. Install recommended extensions
3. Use `Ctrl+Shift+P` → "Tasks: Run Task" to run:
   - **Run CLI Game**
   - **Run GUI Game**
   - **Run Tests**

### **PyCharm:**
1. Open the project folder
2. Configure Python interpreter if needed
3. Use Run configurations:
   - **run_cli** - Launch CLI version
   - **run_gui** - Launch GUI version
   - **test_enhanced_evaluator** - Run tests

## ⚙️ Workspace Features

### **VS Code Settings:**
- **Python Path**: Automatically set to `python3`
- **Extra Paths**: Includes `./backend` and `./backend/shared`
- **Formatting**: Black formatter with 79-character line length
- **Linting**: Flake8 enabled
- **File Exclusions**: Hides cache files and PDFs

### **Pre-configured Tasks:**
- **Run CLI Game**: `python3 backend/cli_poker_game.py`
- **Run GUI Game**: `python3 backend/run_gui.py`
- **Run Tests**: `python3 backend/comprehensive_test_suite.py`
- **Test Enhanced Evaluator**: `python3 backend/test_enhanced_evaluator.py`
- **Test Position Manager**: `python3 backend/dynamic_position_manager.py`

### **Debug Configurations:**
- **Launch CLI Game**: Debug CLI with integrated terminal
- **Launch GUI Game**: Debug GUI with integrated terminal
- **Run Test Suite**: Debug test suite

## 🎯 Benefits

1. **🎯 One-Click Access**: Open workspace file to start coding immediately
2. **⚙️ Pre-configured**: All settings optimized for the project
3. **🚀 Quick Tasks**: Built-in tasks for common operations
4. **🐛 Debug Ready**: Launch configurations for debugging
5. **📝 Code Quality**: Automatic formatting and linting

## 📋 Usage Tips

- **VS Code**: Use `Ctrl+Shift+P` → "Tasks: Run Task" for quick access to tasks
- **PyCharm**: Use the Run toolbar or `Shift+F10` to run configurations
- **Both**: The workspace automatically sets the correct working directory

The workspace files make it easy to jump into development with all the right settings and tools pre-configured! 🎮✨ 