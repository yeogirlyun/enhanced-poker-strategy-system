import tkinter as tk
import sys
import os

def check_terminal_compatibility():
    """Check if we're running in VS Code integrated terminal and warn user."""
    if os.environ.get('TERM_PROGRAM') == 'vscode':
        print("⚠️  WARNING: Running GUI in VS Code integrated terminal may cause crashes!")
        print("💡 RECOMMENDED: Run this from macOS Terminal app instead:")
        print(f"   cd {os.getcwd()}")
        print(f"   python3 {os.path.basename(__file__)}")
        print()
        
        response = input("Continue anyway? (y/N): ").lower().strip()
        if response not in ['y', 'yes']:
            print("Exiting safely. Run from external terminal for best experience.")
            sys.exit(0)

try:  # Prefer package-relative import (python -m backend.run_new_ui)
    from .ui.app_shell import AppShell  # type: ignore
except Exception:
    try:  # Running as a script from backend/ (python backend/run_new_ui.py)
        from ui.app_shell import AppShell  # type: ignore
    except Exception:
        # Last resort: ensure repo root is on sys.path then import absolute
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from backend.ui.app_shell import AppShell  # type: ignore


def main() -> None:
    # Check terminal compatibility before creating GUI
    check_terminal_compatibility()
    
    root = tk.Tk()
    root.title("Poker Trainer — New UI Preview")
    
    # Configure window size and position (70% of screen, centered)
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Calculate 70% size
    window_width = int(screen_width * 0.7)
    window_height = int(screen_height * 0.7)
    
    # Calculate center position
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    
    # Set window geometry (width x height + x_offset + y_offset)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # Set minimum size (50% of calculated size)
    root.minsize(int(window_width * 0.5), int(window_height * 0.5))
    
    AppShell(root)
    root.mainloop()


if __name__ == "__main__":
    main()

