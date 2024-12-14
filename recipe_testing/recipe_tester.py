"""Main recipe testing class"""

import json
import time
import asyncio
import logging
import itertools
from pathlib import Path
from typing import List, Dict, Set
from datetime import datetime

from .errors import ExecutionError
from .data_handlers import load_recipes, validate_task_data
from .function_registry import FunctionRegistry
from .recipe_executor import RecipeExecutor
from .prediction import PredictionHandler
from .stats_tracker import StatsTracker

class RecipeTester:
    def __init__(self, base_dir: Path, logger: logging.Logger, run_id_filter=None):
        self.base_dir = base_dir
        self.recipes_file = base_dir / 'successful_recipes.json'
        self.logger = logger
        self.run_id_filter = run_id_filter
        
        self.recipes = load_recipes(self.recipes_file, self.logger)
        
        self.registry = FunctionRegistry()
        self.executor = RecipeExecutor(self.registry, self.logger)
        self.predictor = PredictionHandler(self.registry, self.logger)
        self.stats = StatsTracker(self.recipes, self.recipes_file, self.logger)
        
        self.categories = self._load_categories()
        
    def _load_categories(self) -> Dict:
        """Load task categories from metadata"""
        try:
            categories_file = self.base_dir / 'data/arc_tasks/task_categories.json'
            if categories_file.exists():
                with open(categories_file) as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Failed to load categories: {e}")
        return {}
        
    def generate_combinations(self, min_funcs: int = 1, max_funcs: int = 4) -> List[List[str]]:
        """Generate combinations of reasoning functions to try"""
        func_names = list(self.registry.reasoning_functions.keys())
        combinations = []
        
        for i in range(min_funcs, max_funcs + 1):
            combinations.extend(itertools.combinations(func_names, i))
            
        return [list(c) for c in combinations]
        
    async def test_recipe(self, task_data: Dict, functions: List[str]) -> bool:
        """Test a specific combination of reasoning functions"""
        test_id = f"test_{int(time.time())}_{hash(tuple(functions))}"
        start_time = datetime.now()
        
        if self.run_id_filter:
            self.run_id_filter.run_id = test_id
        
        self.logger.info(
            f"Starting test {test_id} for task {task_data['task_id']} "
            f"with functions: {functions}"
        )
        
        try:
            validate_task_data(task_data)
            
            if not functions:
                raise ExecutionError("No functions provided for testing")
                
            unknown = set(functions) - set(self.registry.reasoning_functions)
            if unknown:
                raise ExecutionError(f"Unknown functions: {unknown}")
                
            train_examples = task_data['train']
            test_case = task_data['test'][0]
            
            training_results = []
            for i, train_example in enumerate(train_examples):
                example_results = self.executor.execute_training(
                    train_example, functions, i
                )
                training_results.append(example_results)
                
            test_results = self.executor.execute_test(
                test_case['input'], functions
            )
            
            success = False
            if 'predict_output' in functions:
                _, success = self.predictor.generate_prediction(
                    training_results,
                    test_results,
                    test_case['input'],
                    test_case['output']
                )
                
            duration = (datetime.now() - start_time).total_seconds()
            if success:
                self.logger.info(
                    f"Test {test_id} succeeded after {duration:.2f}s"
                )
            else:
                self.logger.warning(
                    f"Test {test_id} failed after {duration:.2f}s"
                )
                
            return success
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.error(
                f"Test {test_id} failed after {duration:.2f}s: {str(e)}",
                exc_info=True
            )
            return False
            
    async def test_task(self, task_data: Dict) -> None:
        """Test all function combinations on a single task"""
        combinations = self.generate_combinations()
        
        for functions in combinations:
            try:
                success = await self.test_recipe(task_data, functions)
                self.stats.update_stats(functions, success, task_data['task_id'])
                
                if success:
                    self.logger.info(
                        f"Found successful recipe for task {task_data['task_id']}: "
                        f"{functions}"
                    )
                    
            except Exception as e:
                self.logger.error(
                    f"Failed testing recipe {functions} for task {task_data['task_id']}: {e}",
                    exc_info=True
                )
                continue
                
        stats = self.stats.get_best_recipes()
        self.logger.info(
            f"Current stats for task {task_data['task_id']}: "
            f"{json.dumps(stats, indent=2)}"
        )
            
    async def run_continuous(self):
        """Run continuous testing of different recipes"""
        while True:
            run_id = f"run_{int(time.time())}"
            if self.run_id_filter:
                self.run_id_filter.run_id = run_id
            start_time = datetime.now()
            
            try:
                self.logger.info(f"Starting test run {run_id}")
                
                combinations = self.generate_combinations()
                self.logger.info(
                    f"Generated {len(combinations)} function combinations to test"
                )
                
                tasks_dir = self.base_dir / 'data/arc_tasks'
                task_files = [f for f in tasks_dir.glob('*.json') 
                            if f.name != 'task_categories.json']
                self.logger.info(f"Found {len(task_files)} tasks to process")
                
                for task_file in task_files:
                    try:
                        with open(task_file) as f:
                            task_data = json.load(f)
                        await self.test_task(task_data)
                        
                    except Exception as e:
                        self.logger.error(
                            f"Failed processing task {task_file}: {e}",
                            exc_info=True
                        )
                        continue
                        
                duration = (datetime.now() - start_time).total_seconds()
                self.logger.info(
                    f"Completed test run {run_id} in {duration:.2f}s. "
                    f"Processed {len(task_files)} tasks with "
                    f"{len(combinations)} function combinations"
                )
                
                await asyncio.sleep(60)
                
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                self.logger.error(
                    f"Test run {run_id} failed after {duration:.2f}s: {e}",
                    exc_info=True
                )
                await asyncio.sleep(60)