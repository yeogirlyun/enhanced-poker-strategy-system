"""
Menu integration for Theme Manager.
Simple hook to open Theme Manager from Settings → Appearance menu.
"""

from typing import Optional, Callable
import tkinter as tk

from .theme_manager import ThemeManager


def open_theme_manager(parent: tk.Tk, on_theme_change: Optional[Callable] = None):
    """
    Open Theme Manager dialog.
    
    Args:
        parent: Parent window
        on_theme_change: Callback when theme is saved/changed
    """
    def on_close():
        """Handle theme manager close - trigger theme refresh if needed."""
        if on_theme_change:
            on_theme_change()
    
    # Create and show theme manager
    theme_manager = ThemeManager(parent, on_theme_change=on_close)
    
    # The dialog is modal and will block until closed
    parent.wait_window(theme_manager)


def add_theme_manager_to_menu(menu_bar: tk.Menu, parent: tk.Tk, on_theme_change: Optional[Callable] = None):
    """
    Add Theme Manager to an existing menu bar.
    
    Args:
        menu_bar: Menu bar to add to
        parent: Parent window
        on_theme_change: Callback when theme is changed
    """
    # Look for existing Settings menu
    settings_menu = None
    try:
        menu_end = menu_bar.index("end")
        if menu_end is not None:
            for i in range(menu_end + 1):
                try:
                    menu_label = menu_bar.entrycget(i, "label")
                    if "Settings" in menu_label or "Preferences" in menu_label:
                        settings_menu = menu_bar.nametowidget(menu_bar.entrycget(i, "menu"))
                        break
                except:
                    continue
    except:
        # Menu is empty or doesn't support index("end")
        pass
    
    # Create Settings menu if it doesn't exist
    if settings_menu is None:
        settings_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Settings", menu=settings_menu)
    
    # Look for existing Appearance submenu
    appearance_menu = None
    if settings_menu:
        try:
            submenu_end = settings_menu.index("end")
            if submenu_end is not None:
                for i in range(submenu_end + 1):
                    try:
                        submenu_label = settings_menu.entrycget(i, "label")
                        if "Appearance" in submenu_label:
                            appearance_menu = settings_menu.nametowidget(settings_menu.entrycget(i, "menu"))
                            break
                    except:
                        continue
        except:
            pass
    
    # Create Appearance submenu if it doesn't exist
    if appearance_menu is None:
        appearance_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label="Appearance", menu=appearance_menu)
    
    # Add Theme Manager option
    appearance_menu.add_command(
        label="🎨 Theme Manager...",
        command=lambda: open_theme_manager(parent, on_theme_change)
    )


# Example usage for integrating into existing app:
def example_integration():
    """Example of how to integrate Theme Manager into an existing app."""
    
    root = tk.Tk()
    root.title("Poker Pro Trainer")
    
    # Create menu bar
    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)
    
    # Your existing menus...
    file_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="New Game")
    file_menu.add_command(label="Exit", command=root.quit)
    
    # Theme change callback
    def on_theme_changed():
        """Called when user saves theme changes."""
        print("🎨 Theme changed - refreshing UI...")
        # Here you would refresh your UI with new theme
        # For example:
        # your_theme_manager.reload()
        # your_ui.refresh_colors()
        # your_poker_table.re_render()
    
    # Add Theme Manager to menu
    add_theme_manager_to_menu(menu_bar, root, on_theme_changed)
    
    # Your app content...
    tk.Label(root, text="Your poker app content here").pack(pady=20)
    
    root.mainloop()


if __name__ == "__main__":
    example_integration()
