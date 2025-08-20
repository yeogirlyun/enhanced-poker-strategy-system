import tkinter as tk
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from ui.app_shell import AppShell

def main() -> None:
    root = tk.Tk()
    root.title("Poker Trainer — MVU UI")
    root.geometry("1200x800")
    
    app = AppShell(root)
    root.mainloop()

if __name__ == "__main__":
    main()