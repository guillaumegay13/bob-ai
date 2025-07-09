# Import all tools for easy access
from .weather import get_weather
from .time_tool import get_time
from .calculator import calculate
from .brave_search import brave_search
from .base import Tool, ToolParameter

# Export all available tools
__all__ = ['get_weather', 'get_time', 'calculate', 'brave_search', 'Tool', 'ToolParameter']

# Tools registry - now contains Tool instances
tools_registry = {
    "get_weather": get_weather,
    "get_time": get_time,
    "calculate": calculate,
    "brave_search": brave_search
}

def generate_tools_description():
    """Generate a formatted description of all available tools for the LLM"""
    descriptions = []
    
    for tool_name, tool in tools_registry.items():
        desc = f"{tool.name} - {tool.description}\n   Arguments:"
        
        for param in tool.parameters:
            param_desc = f"\n   - {param.name} ({'required' if param.required else 'optional'}): {param.description}"
            if not param.required and param.default is not None:
                param_desc += f" (default: {param.default})"
            desc += param_desc
        
        descriptions.append(desc)
    
    return "\n\n".join(descriptions)