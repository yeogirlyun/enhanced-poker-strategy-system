# Hybrid HS Score Approach

## Overview

The Hybrid HS Score approach combines two complementary ways of displaying Hand Strength (HS) scores in the poker strategy development application:

1. **Grid Display**: HS scores visible directly on hand buttons for larger font sizes
2. **Tier Panel Details**: Comprehensive HS breakdown with ranges and individual hand scores

## Implementation Details

### 1. Grid HS Scores

**Location**: `hand_grid.py`

**Features**:
- HS scores appear in the bottom-right corner of hand buttons
- Only visible on larger font sizes (font size > 10)
- Uses smaller font size for HS scores to avoid clutter
- Maintains clean appearance on smaller font sizes

**Code Implementation**:
```python
def _create_button_with_hs(self, hand: str, size_config: Dict, bg_color: str, fg_color: str, border_color: str, border_width: int):
    """Create a button with hand name and HS score in a more sophisticated layout."""
    hs_score = self._get_hand_strength(hand)
    
    # Create a frame to hold the button content
    button_frame = tk.Frame(self.hand_frame, bg=bg_color, relief=tk.RAISED, bd=border_width)
    
    # Main hand label
    main_label = tk.Label(button_frame, text=hand, 
                         font=self.base_font,
                         bg=bg_color, fg=fg_color,
                         anchor=tk.CENTER)
    main_label.pack(expand=True, fill=tk.BOTH)
    
    # HS score label (smaller font, positioned in corner)
    if hs_score is not None and size_config['font'][1] > 10:
        hs_font = tkFont.Font(family=THEME["font_family"], size=max(6, size_config['font'][1] - 4))
        hs_label = tk.Label(button_frame, text=str(hs_score),
                           font=hs_font,
                           bg=bg_color, fg=fg_color,
                           anchor=tk.SE)
        hs_label.pack(side=tk.BOTTOM, anchor=tk.SE, padx=2, pady=1)
    
    return button_frame
```

### 2. Tier Panel HS Details

**Location**: `tier_panel.py`

**Features**:
- Shows HS ranges for each tier (e.g., "Elite (40-50)")
- Displays individual hand HS scores when a single tier is selected
- Shows HS ranges for multiple selected tiers
- Provides comprehensive HS breakdown

**Code Implementation**:
```python
def _update_tier_details(self):
    """Updates the tier details display with HS score information."""
    if len(self.selected_tiers) == 1:
        tier = self.selected_tiers[0]
        
        # Get HS scores for hands in this tier
        hand_hs_info = []
        for hand in sorted(tier.hands):
            hs_score = self._get_hand_strength(hand)
            if hs_score is not None:
                hand_hs_info.append(f"{hand}({hs_score})")
            else:
                hand_hs_info.append(hand)
        
        details_text = f"{tier.name} Tier Details:\n"
        details_text += f"HS Range: {tier.min_hs}-{tier.max_hs}\n"
        details_text += f"Total Hands: {len(tier.hands)}\n"
        details_text += f"Hands with HS: {', '.join(hand_hs_info)}"
        
    elif len(self.selected_tiers) > 1:
        # Get HS ranges for all selected tiers
        hs_ranges = []
        for tier in self.selected_tiers:
            hs_ranges.append(f"{tier.name}({tier.min_hs}-{tier.max_hs})")
        
        details_text = f"Multiple Tiers Selected:\n"
        details_text += f"HS Ranges: {', '.join(hs_ranges)}\n"
        details_text += f"Total Hands: {total_hands}"
```

### 3. HS Data Source

**Location**: `gui_models.py` - `StrategyData` class

**Features**:
- HS scores stored in `strategy_dict["hand_strength_tables"]["preflop"]`
- Supports loading from JSON strategy files
- Automatic HS assignment based on tier ranges
- Fallback to default tiers if no HS data available

**Example HS Data Structure**:
```python
strategy_data.strategy_dict = {
    "hand_strength_tables": {
        "preflop": {
            "AA": 50, "KK": 48, "QQ": 46, "JJ": 44,
            "AKs": 42, "AKo": 40, "AQs": 38,
            "TT": 39, "99": 37, "AJo": 35,
            # ... more hands
        }
    }
}
```

## User Experience

### Grid View
- **Small Fonts**: Clean hand names only
- **Large Fonts**: Hand names with HS scores in corner
- **Visual Hierarchy**: HS scores are smaller and positioned to not interfere with readability

### Tier Panel View
- **Single Tier Selected**: Shows detailed breakdown with individual HS scores
- **Multiple Tiers Selected**: Shows HS ranges for all selected tiers
- **No Selection**: Shows instruction to select a tier

### Benefits of Hybrid Approach

1. **Flexibility**: Users can choose their preferred level of detail
2. **Scalability**: Works well across different font sizes
3. **Completeness**: Provides both quick reference (grid) and detailed analysis (tier panel)
4. **Performance**: HS scores only calculated when needed
5. **Consistency**: Same HS data source used across both displays

## Testing

Use the test script `test_hybrid_hs_approach.py` to verify:
- Grid HS scores appear on larger fonts
- Tier panel shows detailed HS breakdown
- Both components work together seamlessly
- HS data is correctly loaded and displayed

## Future Enhancements

1. **HS Score Formatting**: Add color coding for different HS ranges
2. **HS Score Tooltips**: Show detailed HS information on hover
3. **HS Score Filtering**: Filter hands by HS range
4. **HS Score Export**: Export HS data to external formats
5. **HS Score Validation**: Validate HS scores against poker theory

## Usage Instructions

1. **To see grid HS scores**: Increase font size using the "+" button in the top control area
2. **To see tier HS details**: Select a tier in the tier panel
3. **To see multiple tier HS ranges**: Select multiple tiers
4. **To load custom HS data**: Use the "Open" button to load a strategy file with HS data 