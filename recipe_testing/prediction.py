"""Prediction generation and validation"""

from typing import List, Dict, Any
import logging

from .errors import ExecutionError
from .function_registry import FunctionRegistry

class PredictionHandler:
    def __init__(self, registry: FunctionRegistry, logger: logging.Logger):
        self.registry = registry
        self.logger = logger
        
    def generate_prediction(
        self,
        training_results: List[Dict],
        test_results: Dict,
        test_input: List[List[int]],
        expected_output: List[List[int]]
    ) -> tuple[List[List[int]], bool]:
        """Generate and validate prediction"""
        try:
            prediction = self.registry.get_transformer('predict_output')(
                training_results,
                test_results,
                test_input
            )
            
            if prediction is None:
                raise ExecutionError("Prediction function returned None")
                
            self._validate_prediction(prediction, expected_output)
            
            # Check if prediction matches expected output
            success = (prediction == expected_output)
            return prediction, success
            
        except Exception as e:
            self.logger.error(f"Prediction failed: {str(e)}", exc_info=True)
            raise ExecutionError("Failed to generate prediction") from e
            
    def _validate_prediction(
        self,
        prediction: List[List[int]],
        expected_output: List[List[int]]
    ) -> None:
        """Validate prediction structure and dimensions"""
        if not isinstance(prediction, list):
            raise ExecutionError("Invalid prediction type - must be a list")
            
        if not all(isinstance(row, list) for row in prediction):
            raise ExecutionError("Invalid prediction format - must be 2D grid")
            
        if not all(isinstance(val, int) for row in prediction for val in row):
            raise ExecutionError("Invalid prediction values - must be integers")
            
        # Check dimensions match
        if (len(prediction) != len(expected_output) or 
            any(len(pred_row) != len(out_row) 
                for pred_row, out_row in zip(prediction, expected_output))):
            raise ExecutionError("Prediction dimensions don't match expected output")