from datetime import datetime, timezone
import pytz
from .base import Tool, ToolParameter

def _get_time_function(**kwargs):
    """Get current time with flexible parameters
    
    Arguments:
        timezone (str): Timezone like 'Europe/Paris', 'America/New_York' (default: UTC)
                       Can also use 'tz' parameter
        format (str): Time format string (default: '%Y-%m-%d %H:%M:%S')
    
    Returns:
        str: Formatted time string or error message
    """
    timezone_str = kwargs.get('timezone', kwargs.get('tz', 'UTC'))
    format_str = kwargs.get('format', '%Y-%m-%d %H:%M:%S')
    
    try:
        if timezone_str == 'UTC':
            current_time = datetime.now(timezone.utc)
        else:
            tz = pytz.timezone(timezone_str)
            current_time = datetime.now(tz)
        
        return f"Current time in {timezone_str}: {current_time.strftime(format_str)}"
    except Exception as e:
        # Fallback to UTC if timezone is invalid
        current_time = datetime.now(timezone.utc)
        return f"Invalid timezone: {timezone_str}. Using UTC instead: {current_time.strftime(format_str)}"

# Create the tool instance with metadata
get_time = Tool(
    name="get_time",
    description="Get current time in a specific timezone",
    function=_get_time_function,
    parameters=[
        ToolParameter(
            name="timezone",
            type="string",
            description="Timezone like 'Europe/Paris', 'America/New_York', 'Asia/Tokyo'",
            required=False,
            default="UTC"
        ),
        ToolParameter(
            name="format",
            type="string",
            description="Time format string (e.g., '%Y-%m-%d %H:%M:%S', '%H:%M', '%d/%m/%Y')",
            required=False,
            default="%Y-%m-%d %H:%M:%S"
        )
    ]
)