"""
Enhanced recipe tester using improved pattern detection and prediction
"""

import os
import json
import time
import logging
import asyncio
import itertools
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from enhanced_reasoning import EnhancedReasoning

class EnhancedRecipeTester:
    def __init__(self):
        self.base_dir = Path('/users/bard/mcp/arc_testing')
        self.recipes_file = self.base_dir / 'enhanced_recipes.json'
        self.load_recipes()
        
        # Configure logging
        logging.basicConfig(
            filename=self.base_dir / 'enhanced_recipe_testing.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        self.reasoning = EnhancedReasoning()
        
    def load_recipes(self):
        """Load successful recipes"""
        if self.recipes_file.exists():
            with open(self.recipes_file) as f:
                self.recipes = json.load(f)
        else:
            self.recipes = {
                'task_solutions': {},
                'analysis_stats': {},
                'training_examples': {}
            }
            
    def save_recipes(self):
        """Save recipes and statistics"""
        with open(self.recipes_file, 'w') as f:
            json.dump(self.recipes, f, indent=2)
            
    async def test_task(self, task_data: Dict) -> bool:
        """Test enhanced reasoning on a task"""
        try:
            # Extract training examples
            train_examples = task_data['train']
            test_case = task_data['test'][0]
            
            # Analyze training examples
            training_data = []
            training_inputs = []
            training_outputs = []
            
            for example in train_examples:
                train_analysis = {
                    'input': example['input'],
                    'output': example['output'],
                    'input_analysis': self.reasoning.analyze_grid(example['input']),
                    'output_analysis': self.reasoning.analyze_grid(example['output']),
                    'transform_analysis': self.reasoning.analyze_transform(
                        example['input'], example['output']
                    )
                }
                training_data.append(train_analysis)
                training_inputs.append(example['input'])
                training_outputs.append(example['output'])
                
            # Generate prediction for test input
            prediction = self.reasoning.predict_output(
                test_case['input'],
                training_inputs,
                training_outputs
            )
            
            # Get explanation for prediction
            explanation = self.reasoning.explain_prediction(
                test_case['input'],
                prediction,
                training_data
            )
            
            # Check if prediction matches expected output
            success = prediction == test_case['output']
            
            # Save results
            task_id = task_data['task_id']
            if success:
                if task_id not in self.recipes['task_solutions']:
                    self.recipes['task_solutions'][task_id] = []
                    
                solution = {
                    'timestamp': datetime.now().isoformat(),
                    'training_data': training_data,
                    'prediction': prediction,
                    'explanation': explanation
                }
                self.recipes['task_solutions'][task_id].append(solution)
                
                # Update statistics
                self._update_analysis_stats(task_id, explanation, success=True)
                
                logging.info(f"Successfully solved task {task_id}")
                
            else:
                # Save failed attempt for analysis
                self._update_analysis_stats(task_id, explanation, success=False)
                logging.warning(f"Failed to solve task {task_id}")
                
            self.save_recipes()
            return success
            
        except Exception as e:
            logging.error(f"Error testing task: {str(e)}")
            return False
            
    def _update_analysis_stats(self, task_id: str, explanation: Dict, success: bool):
        """Update statistics about what kinds of analysis lead to success"""
        if task_id not in self.recipes['analysis_stats']:
            self.recipes['analysis_stats'][task_id] = {
                'attempts': 0,
                'successes': 0,
                'pattern_types': {},
                'transform_types': {}
            }
            
        stats = self.recipes['analysis_stats'][task_id]
        stats['attempts'] += 1
        if success:
            stats['successes'] += 1
            
        # Track which patterns were found
        for pattern_type, pattern_results in explanation['input_analysis']['patterns'].items():
            if pattern_type not in stats['pattern_types']:
                stats['pattern_types'][pattern_type] = {
                    'found': 0,
                    'led_to_success': 0
                }
            stats['pattern_types'][pattern_type]['found'] += 1
            if success:
                stats['pattern_types'][pattern_type]['led_to_success'] += 1
                
        # Track which transforms were found
        transform_analysis = explanation['transform_analysis']
        for transform_type in ['value_mappings', 'object_transforms', 'spatial_transforms']:
            if transform_type not in stats['transform_types']:
                stats['transform_types'][transform_type] = {
                    'found': 0,
                    'led_to_success': 0
                }
            if transform_analysis[transform_type]:  # If any transforms of this type were found
                stats['transform_types'][transform_type]['found'] += 1
                if success:
                    stats['transform_types'][transform_type]['led_to_success'] += 1
                    
    def get_success_stats(self) -> Dict:
        """Get statistics about successful solutions"""
        stats = {
            'total_tasks': len(self.recipes['analysis_stats']),
            'solved_tasks': len(self.recipes['task_solutions']),
            'success_rate': None,
            'most_useful_patterns': [],
            'most_useful_transforms': []
        }
        
        # Calculate overall success rate
        total_attempts = sum(s['attempts'] for s in self.recipes['analysis_stats'].values())
        total_successes = sum(s['successes'] for s in self.recipes['analysis_stats'].values())
        if total_attempts > 0:
            stats['success_rate'] = total_successes / total_attempts
            
        # Find most useful patterns
        pattern_stats = {}
        for task_stats in self.recipes['analysis_stats'].values():
            for pattern_type, pattern_data in task_stats['pattern_types'].items():
                if pattern_type not in pattern_stats:
                    pattern_stats[pattern_type] = {
                        'total_found': 0,
                        'total_successes': 0
                    }
                pattern_stats[pattern_type]['total_found'] += pattern_data['found']
                pattern_stats[pattern_type]['total_successes'] += pattern_data['led_to_success']
                
        stats['most_useful_patterns'] = sorted(
            [
                {
                    'type': p_type,
                    'success_rate': p_data['total_successes'] / p_data['total_found']
                    if p_data['total_found'] > 0 else 0
                }
                for p_type, p_data in pattern_stats.items()
            ],
            key=lambda x: x['success_rate'],
            reverse=True
        )
        
        # Find most useful transforms
        transform_stats = {}
        for task_stats in self.recipes['analysis_stats'].values():
            for transform_type, transform_data in task_stats['transform_types'].items():
                if transform_type not in transform_stats:
                    transform_stats[transform_type] = {
                        'total_found': 0,
                        'total_successes': 0
                    }
                transform_stats[transform_type]['total_found'] += transform_data['found']
                transform_stats[transform_type]['total_successes'] += transform_data['led_to_success']
                
        stats['most_useful_transforms'] = sorted(
            [
                {
                    'type': t_type,
                    'success_rate': t_data['total_successes'] / t_data['total_found']
                    if t_data['total_found'] > 0 else 0
                }
                for t_type, t_data in transform_stats.items()
            ],
            key=lambda x: x['success_rate'],
            reverse=True
        )
        
        return stats
        
    async def run_continuous(self):
        """Run continuous testing"""
        while True:
            try:
                # Load tasks
                tasks_dir = self.base_dir / 'data'
                for task_file in tasks_dir.glob('*.json'):
                    try:
                        with open(task_file) as f:
                            task_data = json.load(f)
                            task_id = task_data['task_id']
                            
                        logging.info(f"Testing task {task_id}")
                        success = await self.test_task(task_data)
                        
                        # Log current stats
                        stats = self.get_success_stats()
                        logging.info(f"Current stats: {json.dumps(stats, indent=2)}")
                        
                    except Exception as e:
                        logging.error(f"Error processing task {task_file}: {str(e)}")
                        continue
                        
                # Brief pause between cycles
                await asyncio.sleep(60)
                
            except Exception as e:
                logging.error(f"Error in continuous testing: {str(e)}")
                await asyncio.sleep(60)
                
    def cleanup_logs(self):
        """Cleanup old log files if they get too large"""
        log_file = self.base_dir / 'enhanced_recipe_testing.log'
        max_size = 50 * 1024 * 1024  # 50MB
        
        if log_file.exists() and log_file.stat().st_size > max_size:
            backup = log_file.with_suffix('.log.old')
            if backup.exists():
                backup.unlink()
            log_file.rename(backup)

async def main():
    tester = EnhancedRecipeTester()
    print("Starting enhanced recipe testing...")
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