"""Statistics tracking for recipe testing"""

import json
import logging
from typing import Dict, List, Set
from pathlib import Path

from .errors import SerializationError
from .data_handlers import serialize_item

class StatsTracker:
    def __init__(self, recipes: Dict, recipes_file: Path, logger: logging.Logger):
        self.recipes_file = recipes_file
        self.logger = logger
        
        # Initialize stats from recipes
        self.function_stats = {}
        self.combination_stats = {}
        self.task_solutions = {}
        
        # Convert tasks_solved strings to sets
        for func, stats in recipes.get('function_stats', {}).items():
            self.function_stats[func] = {
                'successes': stats.get('successes', 0),
                'attempts': stats.get('attempts', 0),
                'success_rate': stats.get('success_rate', 0.0),
                'tasks_solved': set(stats.get('tasks_solved', []))
            }
            
        for combo, stats in recipes.get('combination_stats', {}).items():
            self.combination_stats[combo] = {
                'successes': stats.get('successes', 0),
                'attempts': stats.get('attempts', 0),
                'success_rate': stats.get('success_rate', 0.0),
                'tasks_solved': set(stats.get('tasks_solved', []))
            }
            
        self.task_solutions = recipes.get('task_solutions', {})
        
    def update_stats(self, functions: List[str], success: bool, task_id: str) -> None:
        """Update statistics for functions and combinations"""
        # Update individual function stats
        for func in functions:
            if func not in self.function_stats:
                self.function_stats[func] = {
                    'successes': 0,
                    'attempts': 0,
                    'success_rate': 0.0,
                    'tasks_solved': set()
                }
                
            stats = self.function_stats[func]
            stats['attempts'] += 1
            
            if success:
                stats['successes'] += 1
                stats['tasks_solved'].add(task_id)
                
            stats['success_rate'] = stats['successes'] / stats['attempts']
            
        # Update combination stats
        combo_key = ','.join(sorted(functions))
        if combo_key not in self.combination_stats:
            self.combination_stats[combo_key] = {
                'successes': 0,
                'attempts': 0,
                'success_rate': 0.0,
                'tasks_solved': set()
            }
            
        combo_stats = self.combination_stats[combo_key]
        combo_stats['attempts'] += 1
        
        if success:
            combo_stats['successes'] += 1
            combo_stats['tasks_solved'].add(task_id)
            
        combo_stats['success_rate'] = combo_stats['successes'] / combo_stats['attempts']
        
        # Update task solutions
        if success:
            if task_id not in self.task_solutions:
                self.task_solutions[task_id] = set()
            self.task_solutions[task_id].add(tuple(sorted(functions)))
            
        # Save updated stats
        try:
            recipes = {
                'function_stats': self.function_stats,
                'combination_stats': self.combination_stats,
                'task_solutions': self.task_solutions
            }
            
            # Create a serializable copy
            recipes_copy = serialize_item(recipes)
            
            # Write to file
            with open(self.recipes_file, 'w') as f:
                json.dump(recipes_copy, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save recipes: {e}", exc_info=True)
            raise SerializationError("Failed to save recipes") from e
            
    def get_best_recipes(self) -> Dict:
        """Get current best performing functions and combinations"""
        # Get function stats sorted by success rate
        best_functions = []
        for func, stats in sorted(
            self.function_stats.items(),
            key=lambda x: (-x[1]['success_rate'], -len(x[1]['tasks_solved']))
        ):
            best_functions.append({
                'name': func,
                'successes': stats['successes'],
                'attempts': stats['attempts'],
                'success_rate': stats['success_rate'],
                'tasks_solved': len(stats['tasks_solved'])
            })
            
        # Get combination stats sorted by success rate
        best_combinations = []
        for combo, stats in sorted(
            self.combination_stats.items(),
            key=lambda x: (-x[1]['success_rate'], -len(x[1]['tasks_solved']))
        ):
            best_combinations.append({
                'name': combo,
                'successes': stats['successes'],
                'attempts': stats['attempts'],
                'success_rate': stats['success_rate'],
                'tasks_solved': len(stats['tasks_solved'])
            })
            
        return {
            'best_functions': best_functions[:10],
            'best_combinations': best_combinations[:10],
            'solved_tasks': len(self.task_solutions)
        }