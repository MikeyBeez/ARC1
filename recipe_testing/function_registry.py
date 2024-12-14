"""Function registry for recipe testing"""

from typing import Dict, Any, Callable
from reasoning_library import GridReasoning

class FunctionRegistry:
    def __init__(self):
        # Analysis functions
        self.analyzing_functions = {
            'find_objects': GridReasoning.find_objects,
            'get_object_relations': GridReasoning.get_object_relations,
            'detect_patterns': GridReasoning.detect_patterns
        }
        
        # Transformation functions
        self.transforming_functions = {
            'analyze_transformations': GridReasoning.analyze_transformations,
            'predict_output': GridReasoning.predict_output
        }
        
        # Combined registry
        self.reasoning_functions = {
            **self.analyzing_functions,
            **self.transforming_functions
        }
        
    def get_analyzer(self, name: str) -> Callable:
        """Get analysis function by name"""
        return self.analyzing_functions[name]
        
    def get_transformer(self, name: str) -> Callable:
        """Get transformation function by name"""
        return self.transforming_functions[name]
        
    def is_analyzer(self, name: str) -> bool:
        """Check if function is an analyzer"""
        return name in self.analyzing_functions
        
    def is_transformer(self, name: str) -> bool:
        """Check if function is a transformer"""
        return name in self.transforming_functions
        
    def list_functions(self) -> Dict[str, str]:
        """List all registered functions and their types"""
        return {
            name: ("analyzer" if name in self.analyzing_functions else "transformer")
            for name in self.reasoning_functions
        }