"""
Automated testing of reasoning function combinations with ARC agent integration
"""

[Previous content remains the same until the prediction section...]

            # Generate prediction if we have the necessary function
            if 'predict_output' in functions:
                prediction = GridReasoning.predict_output(
                    training_results,
                    test_results,
                    test_case['input']
                )
                
                # Get ARC agent validation of prediction
                validation = self.arc_agent.validate_recipe(
                    functions,
                    {
                        'input': test_case['input'],
                        'predicted_output': prediction,
                        'expected_output': test_case['output'],
                        'training_results': training_results,
                        'test_results': test_results
                    }
                )
                
                # If agent confidence is high enough and prediction matches
                if (validation['confidence'] > 0.8 and 
                    validation['is_valid'] and 
                    prediction == test_case['output']):
                    
                    # Log successful pattern
                    analysis = self.arc_agent.analyze_grid_transformation(
                        test_case['input'],
                        prediction
                    )
                    logging.info(f"Successful transformation pattern: {analysis}")
                    
                    return True
                    
                return False
            else:
                # If we don't have predict_output, we're just testing analysis functions
                return False
            
        except Exception as e:
            logging.error(f"Recipe test failed: {str(e)}")
            return False
            
    def update_stats(self, functions: List[str], success: bool, task_id: str):
        """Update statistics with knowledge graph integration"""
        try:
            # Update individual function stats
            for func in functions:
                if func not in self.recipes['function_stats']:
                    self.recipes['function_stats'][func] = {
                        'successes': 0,
                        'attempts': 0,
                        'tasks_solved': set()
                    }
                
                self.recipes['function_stats'][func]['attempts'] += 1
                if success:
                    self.recipes['function_stats'][func]['successes'] += 1
                    self.recipes['function_stats'][func]['tasks_solved'].add(task_id)
                    
            # Update combination stats
            combo_key = ','.join(sorted(functions))
            if combo_key not in self.recipes['combination_stats']:
                self.recipes['combination_stats'][combo_key] = {
                    'successes': 0,
                    'attempts': 0,
                    'tasks_solved': set()
                }
                
            self.recipes['combination_stats'][combo_key]['attempts'] += 1
            if success:
                self.recipes['combination_stats'][combo_key]['successes'] += 1
                self.recipes['combination_stats'][combo_key]['tasks_solved'].add(task_id)
                
            # Update task solutions
            if success:
                if task_id not in self.recipes['task_solutions']:
                    self.recipes['task_solutions'][task_id] = set()
                self.recipes['task_solutions'][task_id].add(tuple(functions))
                
            # Update knowledge graph with success/failure pattern
            self.arc_agent.grid_patterns.update_knowledge_graph(
                ['recipe_pattern', combo_key],
                {
                    'functions': functions,
                    'success': success,
                    'task_id': task_id,
                    'timestamp': datetime.now().isoformat()
                }
            )
                
            self.save_recipes()
            
        except Exception as e:
            logging.error(f"Error updating stats: {str(e)}")
            # Create backup before retry
            self.save_recipes()
            raise
            
    async def run_continuous(self):
        """Run continuous testing with improved error handling and progress tracking"""
        while True:
            try:
                # Generate new combinations with agent assistance
                combinations = self.generate_combinations()
                
                # Load tasks
                tasks_dir = self.base_dir / 'data' / 'arc_tasks'
                if not tasks_dir.exists():
                    tasks_dir = self.base_dir / 'data'
                
                for task_file in tasks_dir.glob('*.json'):
                    try:
                        with open(task_file) as f:
                            task_data = json.load(f)
                            task_id = task_data['task_id']
                            
                        logging.info(f"Testing recipes for task {task_id}")
                        
                        # Get agent's analysis of the task
                        for example in task_data['train']:
                            analysis = self.arc_agent.analyze_grid_transformation(
                                example['input'],
                                example['output']
                            )
                            logging.info(f"Task {task_id} training example analysis: {analysis}")
                        
                        # Try each combination
                        for functions in combinations:
                            # Get agent's validation before testing
                            validation = self.arc_agent.validate_recipe(
                                functions,
                                {'task': task_data}
                            )
                            
                            # Only test if agent thinks it's promising
                            if validation['confidence'] > 0.6:
                                success = await self.test_recipe(task_data, functions)
                                self.update_stats(functions, success, task_id)
                                
                                if success:
                                    logging.info(f"Found successful recipe for task {task_id}: {functions}")
                                    
                        # Log progress after each task
                        stats = self.get_best_recipes()
                        logging.info(f"Current stats: {json.dumps(stats, indent=2)}")
                        
                    except Exception as e:
                        logging.error(f"Error processing task {task_file}: {str(e)}")
                        continue
                    
                # Brief pause between cycles
                await asyncio.sleep(60)
                
            except Exception as e:
                logging.error(f"Continuous testing error: {str(e)}")
                await asyncio.sleep(60)
                
    def cleanup_logs(self):
        """Cleanup old log files if they get too large"""
        log_file = self.base_dir / 'recipe_testing.log'
        max_size = 50 * 1024 * 1024  # 50MB
        
        if log_file.exists() and log_file.stat().st_size > max_size:
            backup = log_file.with_suffix('.log.old')
            if backup.exists():
                backup.unlink()
            log_file.rename(backup)

async def main():
    tester = RecipeTester()
    print("Starting continuous recipe testing...")
    print("Press Ctrl+C to stop")
    
    while True:
        try:
            # Clean up logs before starting new cycle
            tester.cleanup_logs()
            
            # Run test cycle
            await tester.run_continuous()
        except Exception as e:
            logging.error(f"Main loop error: {str(e)}")
            await asyncio.sleep(60)

if __name__ == '__main__':
    asyncio.run(main())