def _create_chip_with_label(self, canvas, start_x, start_y, denom, tokens, chip_size=58, tags=None):
    """Create a chip with label at the specified position.
    
    Args:
        canvas: The canvas to draw on
        start_x: X coordinate for chip
        start_y: Y coordinate for chip
        denom: Denomination value 
        tokens: Token style info
        chip_size: Size of chip graphic (default 58px)
        tags: Optional canvas tags
    """
    if tags is None:
        tags = ["chip"]
    
    # Create the chip shape
    chip_radius = chip_size // 2
    chip_id = canvas.create_oval(
        start_x - chip_radius,
        start_y - chip_radius,
        start_x + chip_radius, 
        start_y + chip_radius,
        fill=tokens.chip_colors[denom],
        outline=tokens.chip_border_colors[denom],
        width=2,
        tags=tags
    )
    
    # Add denomination text
    text_id = canvas.create_text(
        start_x,
        start_y,
        text=str(denom),
        fill=tokens.chip_text_colors[denom],
        font=("Arial", int(chip_size/3), "bold"),
        tags=tags
    )
    
    return chip_id, text_id
