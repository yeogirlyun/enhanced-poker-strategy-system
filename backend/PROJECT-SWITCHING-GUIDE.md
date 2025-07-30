# 🚀 Project Switching Guide

This guide shows you how to efficiently switch between your **Poker** and **Janggi** projects while preserving all your work context, chat history, and open files.

## 📁 Workspace Files Created

I've created three VS Code workspace files for you:

1. **`Poker.code-workspace`** - Poker project only
2. **`Janggi.code-workspace`** - Janggi project only  
3. **`Python-Projects.code-workspace`** - Both projects together

## 🎯 How to Switch Between Projects

### **Option 1: Individual Project Workspaces (Recommended)**

**To open Poker project:**
```bash
code Poker.code-workspace
```

**To open Janggi project:**
```bash
code Janggi.code-workspace
```

### **Option 2: Master Workspace (Both Projects)**

**To open both projects together:**
```bash
code Python-Projects.code-workspace
```

### **Option 3: Direct Folder Opening**

**Poker:**
```bash
code Poker/
```

**Janggi:**
```bash
code Janggi/
```

## 🔄 Preserving Context Between Switches

### **✅ What Gets Preserved:**
- **Open files** - All your open tabs and their content
- **Cursor positions** - Where you were editing in each file
- **Chat history** - Previous conversations with AI assistants
- **Terminal sessions** - Running processes and command history
- **Git status** - Current branch and uncommitted changes
- **VS Code settings** - Project-specific configurations
- **Extensions** - Recommended extensions for each project

### **🎯 Quick Switch Commands:**

Create these aliases in your shell profile (`~/.zshrc`):

```bash
# Add to ~/.zshrc
alias poker="cd ~/Python/Poker && code ."
alias janggi="cd ~/Python/Janggi && code ."
alias both="cd ~/Python && code Python-Projects.code-workspace"
```

Then reload your shell:
```bash
source ~/.zshrc
```

Now you can simply type:
- `poker` - Switch to Poker project
- `janggi` - Switch to Janggi project  
- `both` - Open both projects together

## 🛠️ Workspace Features

### **🎰 Poker Workspace Features:**
- **Tasks**: Run Poker GUI, Poker Game, Tests
- **Settings**: Python linting, formatting, file exclusions
- **Extensions**: Python, Git, Markdown support

### **♟️ Janggi Workspace Features:**
- **Tasks**: Run Janggi Game, Tests, Install Dependencies
- **Settings**: Same Python configuration
- **Extensions**: Same development tools

### **🎯 Master Workspace Features:**
- **Both projects** in one window
- **Unified tasks** for both projects
- **Easy switching** between project folders
- **Shared settings** across both projects

## 📋 Best Practices

### **1. Use Workspace Files**
- Always open projects via workspace files
- This ensures consistent settings and tasks
- Preserves project-specific configurations

### **2. Save Before Switching**
- Save all files before switching projects
- Commit or stash git changes
- Close running processes if needed

### **3. Use Terminal Integration**
- Each workspace has integrated terminals
- Run project-specific commands easily
- Keep terminal history per project

### **4. Leverage VS Code Features**
- **Split editors** for comparing files
- **Git integration** for version control
- **Extensions** for enhanced development
- **Tasks** for common operations

## 🚀 Quick Start Commands

### **For Poker Development:**
```bash
# Open Poker workspace
code Poker.code-workspace

# Or use alias
poker

# Run from terminal
cd ~/Python/Poker
python3 main_gui.py
```

### **For Janggi Development:**
```bash
# Open Janggi workspace  
code Janggi.code-workspace

# Or use alias
janggi

# Run from terminal
cd ~/Python/Janggi
python3 src/main.py
```

### **For Both Projects:**
```bash
# Open master workspace
code Python-Projects.code-workspace

# Or use alias
both
```

## 🔧 Troubleshooting

### **If workspaces don't open correctly:**
1. Check file paths are correct
2. Ensure VS Code is installed
3. Verify Python interpreter path

### **If context is lost:**
1. Use workspace files instead of direct folder opening
2. Save files before switching
3. Check VS Code settings are preserved

### **If tasks don't work:**
1. Verify Python is in PATH
2. Check working directory settings
3. Install required extensions

## 📈 Advanced Tips

### **1. Custom Tasks**
Add project-specific tasks to workspace files:
```json
{
    "label": "Custom Task",
    "type": "shell",
    "command": "python3",
    "args": ["your_script.py"]
}
```

### **2. Project-Specific Settings**
Each workspace can have different settings:
- Different Python interpreters
- Project-specific linting rules
- Custom file exclusions

### **3. Extension Management**
- Install extensions per workspace
- Use recommended extensions
- Keep extensions updated

---

**🎉 You're all set!** Now you can seamlessly switch between your Poker and Janggi projects while preserving all your work context and chat history. 