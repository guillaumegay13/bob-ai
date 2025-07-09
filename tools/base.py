from typing import Dict, List, Any, Callable
from dataclasses import dataclass

@dataclass
class ToolParameter:
    """Define a tool parameter"""
    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None

@dataclass
class Tool:
    """Define a tool with its metadata"""
    name: str
    description: str
    function: Callable
    parameters: List[ToolParameter]
    
    def get_signature(self) -> Dict[str, Any]:
        """Get tool signature for LLM"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": [
                {
                    "name": param.name,
                    "type": param.type,
                    "description": param.description,
                    "required": param.required,
                    "default": param.default
                }
                for param in self.parameters
            ]
        }
    
    def __call__(self, **kwargs):
        """Execute the tool"""
        return self.function(**kwargs)