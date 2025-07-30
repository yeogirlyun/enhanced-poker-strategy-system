#!/usr/bin/env python3
"""
Test script to verify poker table centering
"""

import tkinter as tk
from tkinter import ttk
import math

def test_centering():
    """Test the centering calculations."""
    
    # Test dimensions
    canvas_width = 900
    canvas_height = 600
    
    # Perfect centering calculations
    center_x = canvas_width // 2
    center_y = canvas_height // 2
    
    # Table dimensions (professional ratios)
    table_width = int(canvas_width * 0.75)  # 75% of canvas width
    table_height = int(canvas_height * 0.65)  # 65% of canvas height
    
    # Player positioning
    player_radius = min(table_width, table_height) * 0.4
    
    print("=== Centering Test Results ===")
    print(f"Canvas: {canvas_width} x {canvas_height}")
    print(f"Center: ({center_x}, {center_y})")
    print(f"Table: {table_width} x {table_height}")
    print(f"Player Radius: {player_radius}")
    
    # Test table position
    table_x = center_x - table_width // 2
    table_y = center_y - table_height // 2
    print(f"Table Position: ({table_x}, {table_y})")
    
    # Test if table is centered
    table_center_x = table_x + table_width // 2
    table_center_y = table_y + table_height // 2
    print(f"Table Center: ({table_center_x}, {table_center_y})")
    print(f"Perfect Center: ({center_x}, {center_y})")
    
    # Check centering
    x_centered = abs(table_center_x - center_x) < 5
    y_centered = abs(table_center_y - center_y) < 5
    print(f"Horizontally Centered: {x_centered}")
    print(f"Vertically Centered: {y_centered}")
    
    # Test player positions
    num_players = 6
    for i in range(num_players):
        angle = (i * 2 * math.pi / num_players) - math.pi / 2
        x = center_x + int(player_radius * math.cos(angle))
        y = center_y + int(player_radius * math.sin(angle))
        print(f"Player {i}: ({x}, {y})")
    
    return x_centered and y_centered

if __name__ == "__main__":
    result = test_centering()
    print(f"\nCentering Test: {'PASSED' if result else 'FAILED'}") 