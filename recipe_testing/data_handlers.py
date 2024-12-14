"""Data handling and serialization for recipe testing"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Set

from .errors import TaskError, SerializationError

def validate_task_data(task_data: Dict) -> None:
    """Validate structure and types of task data"""
    if not isinstance(task_data, dict):
        raise TaskError("Task data must be a dictionary")
        
    required = {'task_id', 'train', 'test'}
    missing = required - set(task_data.keys())
    if missing:
        raise TaskError(f"Missing required keys: {missing}")
        
    if not isinstance(task_data['train'], list):
        raise TaskError("Train data must be a list")
        
    if not isinstance(task_data['test'], list):
        raise TaskError("Test data must be a list")
        
    if not task_data['train'] or not task_data['test']:
        raise TaskError("Train and test data must be non-empty")
        
    def validate_example(example: Dict, name: str) -> None:
        """Validate a single training/test example"""
        if not isinstance(example, dict):
            raise TaskError(f"{name} example must be a dictionary")
            
        if 'input' not in example or 'output' not in example:
            raise TaskError(f"{name} example must have input and output")
            
        if not isinstance(example['input'], list):
            raise TaskError(f"{name} input must be a list")
            
        if not isinstance(example['output'], list):
            raise TaskError(f"{name} output must be a list")
            
        if not example['input'] or not example['output']:
            raise TaskError(f"{name} input and output must be non-empty")
            
        def validate_grid(grid: List[List[int]], grid_name: str) -> None:
            """Validate a 2D grid of integers"""
            if not grid:
                raise TaskError(f"{grid_name} must be non-empty")
                
            if not all(isinstance(row, list) for row in grid):
                raise TaskError(f"{grid_name} must be a 2D grid")
                
            width = len(grid[0])
            if not all(len(row) == width for row in grid):
                raise TaskError(f"{grid_name} must be rectangular")
                
            if not all(isinstance(val, (int, float)) for row in grid for val in row):
                raise TaskError(f"{grid_name} values must be numbers")
                
        validate_grid(example['input'], f"{name} input")
        validate_grid(example['output'], f"{name} output")
        
    for i, example in enumerate(task_data['train']):
        validate_example(example, f"Training example {i+1}")
        
    for i, example in enumerate(task_data['test']):
        validate_example(example, f"Test example {i+1}")

def serialize_item(obj: Any) -> Any:
    """Convert sets and tuples to sorted lists for JSON serialization"""
    if isinstance(obj, (set, tuple)):
        return sorted(serialize_item(x) for x in obj)
    elif isinstance(obj, dict):
        return {k: serialize_item(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_item(x) for x in obj]
    elif isinstance(obj, (int, float, str, bool, type(None))):
        return obj
    else:
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def load_recipes(recipes_file: Path, logger: logging.Logger) -> Dict:
    """Load and validate recipe data"""
    try:
        if recipes_file.exists():
            with open(recipes_file) as f:
                try:
                    recipes = json.load(f)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse recipes file: {e}")
                    raise SerializationError("Invalid JSON in recipes file") from e
                    
            recipes.setdefault('task_solutions', {})
            recipes.setdefault('function_stats', {})
            recipes.setdefault('combination_stats', {})
            
            for func, stats in recipes['function_stats'].items():
                stats['tasks_solved'] = set(stats.get('tasks_solved', []))
                
            for combo, stats in recipes['combination_stats'].items():
                stats['tasks_solved'] = set(stats.get('tasks_solved', []))
                
            for task_id, solutions in list(recipes['task_solutions'].items()):
                recipes['task_solutions'][task_id] = {
                    tuple(solution) if isinstance(solution, list) else solution
                    for solution in solutions
                }
        else:
            recipes = {
                'task_solutions': {},
                'function_stats': {},
                'combination_stats': {}
            }
            
        return recipes
        
    except OSError as e:
        logger.error(f"Failed to load recipes file: {e}")
        raise SerializationError("Could not access recipes file") from e

def save_recipes(recipes: Dict, recipes_file: Path, logger: logging.Logger) -> None:
    """Save recipes with atomic file write"""
    try:
        recipes_copy = serialize_item(recipes)
        temp_file = recipes_file.with_suffix('.tmp')
        
        with open(temp_file, 'w') as f:
            json.dump(recipes_copy, f, indent=2)
            
        temp_file.rename(recipes_file)
        
    except Exception as e:
        logger.error(f"Failed to save recipes: {e}", exc_info=True)
        raise SerializationError("Failed to save recipes") from e