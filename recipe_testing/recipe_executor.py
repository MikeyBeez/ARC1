"""Execution logic for recipe testing"""

import logging
from typing import Dict, List, Any
from datetime import datetime

from .errors import ExecutionError
from .function_registry import FunctionRegistry

class RecipeExecutor:
    def __init__(self, registry: FunctionRegistry, logger: logging.Logger):
        self.registry = registry
        self.logger = logger
        
    def execute_training(self, train_example: Dict, functions: List[str], example_idx: int) -> Dict:
        """Execute recipe on a single training example"""
        example_results = {}
        
        # Apply analysis functions
        for func_name in functions:
            if self.registry.is_analyzer(func_name):
                try:
                    result = self.registry.get_analyzer(func_name)(
                        train_example['input']
                    )
                    example_results[func_name] = result
                except Exception as e:
                    raise ExecutionError(
                        f"Analysis function '{func_name}' failed on "
                        f"training example {example_idx+1}: {e}"
                    )
                    
        # Apply transformation functions
        for func_name in functions:
            if func_name == 'analyze_transformations':
                try:
                    result = self.registry.get_transformer(func_name)(
                        train_example['input'],
                        train_example['output']
                    )
                    example_results[func_name] = result
                except Exception as e:
                    raise ExecutionError(
                        f"Transformation function failed on "
                        f"training example {example_idx+1}: {e}"
                    )
                    
        return example_results
        
    def execute_test(self, test_input: List[List[int]], functions: List[str]) -> Dict:
        """Execute recipe on test input"""
        test_results = {}
        
        for func_name in functions:
            if self.registry.is_analyzer(func_name):
                try:
                    result = self.registry.get_analyzer(func_name)(test_input)
                    test_results[func_name] = result
                except Exception as e:
                    raise ExecutionError(f"Analysis failed on test input: {e}")
                    
        return test_results