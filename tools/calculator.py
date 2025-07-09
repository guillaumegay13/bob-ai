import math
from .base import Tool, ToolParameter

def _calculate_function(**kwargs):
    """Perform calculations with flexible parameters
    
    Arguments:
        expression (str): Mathematical expression to evaluate (required)
                         Can also use 'expr' or 'formula' parameter
        precision (int): Number of decimal places for the result (default: 2)
    
    Returns:
        str: Calculation result or error message
    """
    expression = kwargs.get('expression', kwargs.get('expr', kwargs.get('formula', '')))
    precision = kwargs.get('precision', 2)
    
    if not expression:
        return "Error: expression, expr, or formula parameter is required"
    
    # Create a safe namespace with math functions
    safe_namespace = {
        'abs': abs,
        'round': round,
        'min': min,
        'max': max,
        'sum': sum,
        'pow': pow,
        'sqrt': math.sqrt,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'pi': math.pi,
        'e': math.e,
        'log': math.log,
        'log10': math.log10,
    }
    
    try:
        # Evaluate the expression in a restricted namespace
        result = eval(expression, {"__builtins__": {}}, safe_namespace)
        
        if isinstance(result, float):
            result = round(result, precision)
        
        return f"Result: {result}"
    except Exception as e:
        return f"Calculation error: {str(e)}"

# Create the tool instance with metadata
calculate = Tool(
    name="calculate",
    description="Perform mathematical calculations",
    function=_calculate_function,
    parameters=[
        ToolParameter(
            name="expression",
            type="string",
            description="Mathematical expression to evaluate (e.g., '2 + 2 * 3', 'sqrt(16)', 'sin(pi/2)')",
            required=True
        ),
        ToolParameter(
            name="precision",
            type="integer",
            description="Number of decimal places for the result",
            required=False,
            default=2
        )
    ]
)