"""
Example: How to create a new tool

To add this tool to the system:
1. Uncomment the import in tools/__init__.py
2. Add it to the tools_registry
"""

import random
from .base import Tool, ToolParameter

def _dice_roll_function(**kwargs):
    """Roll dice based on parameters"""
    sides = kwargs.get('sides', 6)
    count = kwargs.get('count', 1)
    
    if sides < 2:
        return "Error: Dice must have at least 2 sides"
    
    if count < 1 or count > 100:
        return "Error: Count must be between 1 and 100"
    
    rolls = [random.randint(1, sides) for _ in range(count)]
    total = sum(rolls)
    
    if count == 1:
        return f"Rolled a d{sides}: {rolls[0]}"
    else:
        return f"Rolled {count}d{sides}: {rolls} (Total: {total})"

# Create the tool instance
dice_roll = Tool(
    name="dice_roll",
    description="Roll dice for games or random number generation",
    function=_dice_roll_function,
    parameters=[
        ToolParameter(
            name="sides",
            type="integer",
            description="Number of sides on the dice (e.g., 6 for d6, 20 for d20)",
            required=False,
            default=6
        ),
        ToolParameter(
            name="count",
            type="integer",
            description="Number of dice to roll",
            required=False,
            default=1
        )
    ]
)