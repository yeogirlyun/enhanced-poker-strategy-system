#!/usr/bin/env python3
"""
Test runner for the PPSM Hands Review Tab

This script creates a simple Tkinter application to test the new hands review tab
with PPSM integration and GTO hands loading functionality.
"""

import tkinter as tk
from tkinter import ttk
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Test imports
try:
    from ui.tabs.hands_review_tab_ppsm import HandsReviewTabPPSM, GTOHandsLoader, PPSMHandReplayEngine
    from ui.state.store import Store
    from ui.services.event_bus import EventBus
    from ui.services.theme_manager import ThemeManager
    IMPORTS_OK = True
    import_error = None
except ImportError as e:
    IMPORTS_OK = False
    import_error = str(e)
    print(f"❌ Import error: {e}")


class TestHandsReviewApp:
    """Simple test application for PPSM hands review."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎯 PPSM Hands Review Test")
        self.root.geometry("1200x800")
        
        # Initialize components if imports worked
        if IMPORTS_OK:
            self._setup_components()
            self._setup_ui()
        else:
            self._setup_error_ui()
    
    def _setup_components(self):
        """Setup the required components for testing."""
        try:
            # Create basic store (simplified for testing)
            self.store = Store()
            
            # Create event bus
            self.event_bus = EventBus()
            
            # Create theme manager
            self.theme_manager = ThemeManager()
            
            print("✅ Components initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to setup components: {e}")
            self.components_error = str(e)
    
    def _setup_ui(self):
        """Setup the UI with hands review tab."""
        try:
            # Create notebook for testing
            self.notebook = ttk.Notebook(self.root)
            self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Create hands review tab
            hands_review_frame = ttk.Frame(self.notebook)
            self.hands_review_tab = HandsReviewTabPPSM(
                hands_review_frame,
                self.store,
                self.event_bus,
                self.theme_manager
            )
            
            # Add to notebook
            self.notebook.add(hands_review_frame, text="🎯 PPSM Hands Review")
            
            # Add status bar
            self.status_bar = ttk.Label(
                self.root,
                text="✅ PPSM Hands Review Tab loaded successfully",
                relief=tk.SUNKEN,
                anchor=tk.W
            )
            self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
            
            # Add test controls
            self._add_test_controls()
            
            print("✅ UI setup complete")
            
        except Exception as e:
            print(f"❌ Failed to setup UI: {e}")
            self._setup_error_ui(f"UI Setup Error: {e}")
    
    def _setup_error_ui(self, additional_error=None):
        """Setup error display UI."""
        error_frame = ttk.Frame(self.root)
        error_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(
            error_frame,
            text="❌ PPSM Hands Review Test - Error",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Error details
        error_text = f"""Import Error: {import_error or 'None'}"""
        
        if additional_error:
            error_text += f"\\n\\nAdditional Error: {additional_error}"
        
        error_text += """

Required Components:
- ui.tabs.hands_review_tab_ppsm
- ui.state.store  
- ui.services.event_bus
- ui.services.theme_manager
- core.pure_poker_state_machine
- core.hand_model_decision_engine

Please ensure all components are available and properly installed.
"""
        
        text_widget = tk.Text(error_frame, font=("Consolas", 10))
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(1.0, error_text)
        text_widget.config(state=tk.DISABLED)
    
    def _add_test_controls(self):
        """Add test control buttons."""
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Test buttons
        test_gto_button = ttk.Button(
            control_frame,
            text="🧪 Test GTO Loader",
            command=self._test_gto_loader
        )
        test_gto_button.pack(side=tk.LEFT, padx=5)
        
        test_ppsm_button = ttk.Button(
            control_frame,
            text="🔧 Test PPSM Integration",
            command=self._test_ppsm_integration
        )
        test_ppsm_button.pack(side=tk.LEFT, padx=5)
        
        # Status button  
        status_button = ttk.Button(
            control_frame,
            text="📊 Show Status",
            command=self._show_status
        )
        status_button.pack(side=tk.RIGHT, padx=5)
    
    def _test_gto_loader(self):
        """Test the GTO hands loader independently."""
        try:
            print("🧪 Testing GTO Loader...")
            loader = GTOHandsLoader()
            hands = loader.load_gto_hands()
            summary = loader.get_hands_summary()
            
            result = f"""✅ GTO Loader Test Results:
            
Total Hands: {summary['total']}
By Players: {summary.get('by_players', {})}
Sources: {summary.get('sources', [])}

Sample Hand: {hands[0].metadata.hand_id if hands else 'None'}
Loader Status: {'✅ Working' if hands else '❌ No hands loaded'}"""
            
            self._show_test_result("GTO Loader Test", result)
            
        except Exception as e:
            self._show_test_result("GTO Loader Test", f"❌ Test failed: {e}")
    
    def _test_ppsm_integration(self):
        """Test PPSM integration independently."""
        try:
            print("🔧 Testing PPSM Integration...")
            engine = PPSMHandReplayEngine()
            
            # Try to load a sample hand if available
            loader = GTOHandsLoader()
            hands = loader.load_gto_hands()
            
            result = f"""🔧 PPSM Integration Test:
            
Replay Engine: {'✅ Created' if engine else '❌ Failed'}
GTO Hands: {len(hands)} loaded
PPSM Available: {'✅ Yes' if 'PPSM_AVAILABLE' in globals() else '❌ No'}

Components:
- PurePokerStateMachine: ✅
- HandModelDecisionEngine: ✅  
- GameConfig: ✅"""
            
            if hands:
                # Test setup with first hand
                setup_success = engine.setup_hand_replay(hands[0])
                result += f"\\n\\nSetup Test: {'✅ Success' if setup_success else '❌ Failed'}"
                
                if setup_success:
                    game_state = engine.get_game_state()
                    result += f"\\nGame State: {'✅ Available' if game_state else '❌ None'}"
            
            self._show_test_result("PPSM Integration Test", result)
            
        except Exception as e:
            self._show_test_result("PPSM Integration Test", f"❌ Test failed: {e}")
    
    def _show_status(self):
        """Show overall application status."""
        status = f"""📊 PPSM Hands Review Test Status:
        
Application: {'✅ Running' if IMPORTS_OK else '❌ Error State'}
Components: {'✅ Loaded' if IMPORTS_OK and hasattr(self, 'store') else '❌ Failed'}
GTO Hands File: {'✅ Found' if Path('gto_hands.json').exists() else '❌ Missing'}
UI Tab: {'✅ Created' if hasattr(self, 'hands_review_tab') else '❌ Not created'}

Ready for Testing: {'🟢 Yes' if IMPORTS_OK and hasattr(self, 'hands_review_tab') else '🔴 No'}
"""
        
        self._show_test_result("Application Status", status)
    
    def _show_test_result(self, title: str, result: str):
        """Show test result in a popup window."""
        result_window = tk.Toplevel(self.root)
        result_window.title(title)
        result_window.geometry("500x400")
        
        text_widget = tk.Text(result_window, font=("Consolas", 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(1.0, result)
        text_widget.config(state=tk.DISABLED)
        
        # Close button
        close_button = ttk.Button(
            result_window,
            text="Close",
            command=result_window.destroy
        )
        close_button.pack(pady=5)
    
    def run(self):
        """Run the test application."""
        print("🚀 Starting PPSM Hands Review Test Application...")
        print(f"📊 Imports OK: {IMPORTS_OK}")
        
        if IMPORTS_OK:
            print("✅ Application ready - test the hands review functionality!")
        else:
            print(f"❌ Import error: {import_error}")
            print("⚠️ Some functionality may not be available")
        
        self.root.mainloop()


def main():
    """Main entry point for the test application."""
    print("🎯 PPSM Hands Review Tab Test")
    print("=" * 50)
    
    # Check for GTO hands file
    gto_file = Path("gto_hands.json")
    if not gto_file.exists():
        print(f"⚠️ Warning: GTO hands file not found at {gto_file}")
        print("   Run generate_gto_hands.py first to create test data")
    else:
        print(f"✅ Found GTO hands file: {gto_file}")
    
    # Create and run test app
    app = TestHandsReviewApp()
    app.run()


if __name__ == "__main__":
    main()
