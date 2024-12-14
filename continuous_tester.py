"""
Continuous ARC testing with resource management
"""

import os
import json
import time
import psutil
import logging
import asyncio
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from arc_tester import ARCTester
from operations import *

class ResourceManager:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.log_max_size = 50 * 1024 * 1024  # 50MB
        self.results_max_count = 100
        self.disk_warning_threshold = 85  # percentage
        self.memory_warning_threshold = 80  # percentage
        
    def check_resources(self) -> bool:
        """Check system resources, return True if okay to continue"""
        try:
            # Check disk space
            disk_usage = psutil.disk_usage(self.base_dir).percent
            if disk_usage > self.disk_warning_threshold:
                logging.warning(f"Disk usage high: {disk_usage}%")
                self.clean_old_results()
                
            # Check memory
            memory_usage = psutil.virtual_memory().percent
            if memory_usage > self.memory_warning_threshold:
                logging.warning(f"Memory usage high: {memory_usage}%")
                return False
                
            # Rotate logs if needed
            self.rotate_logs()
            
            return True
            
        except Exception as e:
            logging.error(f"Resource check failed: {str(e)}")
            return False
            
    def rotate_logs(self):
        """Rotate log files if too large"""
        log_file = self.base_dir / 'arc_testing.log'
        if log_file.exists() and log_file.stat().st_size > self.log_max_size:
            backup = log_file.with_suffix('.log.1')
            if backup.exists():
                backup.unlink()
            log_file.rename(backup)
            
    def clean_old_results(self):
        """Clean old result files"""
        results_dir = self.base_dir / 'results'
        result_files = sorted(
            results_dir.glob('results_*.json'),
            key=lambda x: x.stat().st_mtime
        )
        
        while len(result_files) > self.results_max_count:
            old_file = result_files.pop(0)
            old_file.unlink()
            logging.info(f"Cleaned old result file: {old_file}")

class ContinuousTester:
    def __init__(self):
        self.base_dir = Path('/users/bard/mcp/arc_testing')
        self.resource_mgr = ResourceManager(self.base_dir)
        self.tester = ARCTester()
        self.experiment_count = 0
        
        # Setup logging
        logging.basicConfig(
            filename=self.base_dir / 'arc_testing.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Load configuration history
        self.history_file = self.base_dir / 'experiment_history.json'
        self.load_history()
        
    def load_history(self):
        """Load experiment history"""
        if self.history_file.exists():
            with open(self.history_file) as f:
                self.history = json.load(f)
        else:
            self.history = {
                'tried_configs': [],
                'best_score': 0,
                'best_config': None
            }
            
    def save_history(self):
        """Save experiment history"""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
            
    def generate_experiment_config(self) -> Dict[str, Any]:
        """Generate new experiment configuration"""
        # Example parameters to vary
        config = {
            'prompt_style': np.random.choice([
                'step_by_step',
                'pattern_focused',
                'transformation_focused'
            ]),
            'max_retries': np.random.randint(2, 5),
            'model_timeout': np.random.randint(20, 40),
            'pattern_analysis_depth': np.random.randint(1, 4)
        }
        
        # Avoid repeating exact configurations
        config_str = json.dumps(config, sort_keys=True)
        if config_str in self.history['tried_configs']:
            return self.generate_experiment_config()
            
        self.history['tried_configs'].append(config_str)
        return config
        
    async def run_experiment(self, config: Dict[str, Any]) -> float:
        """Run experiment with given configuration"""
        try:
            self.tester.timeout = config['model_timeout']
            self.tester.max_retries = config['max_retries']
            
            results = {
                'timestamp': datetime.now().isoformat(),
                'config': config,
                'tasks': {},
                'summary': {
                    'total': 0,
                    'attempted': 0,
                    'solved': 0
                }
            }
            
            # Run tests with current configuration
            for task_id, task in self.tester.task_cache.items():
                if not self.resource_mgr.check_resources():
                    logging.warning("Resources low, pausing testing")
                    await asyncio.sleep(60)
                    continue
                    
                success, response, solution = await self.tester.solve_task(task)
                results['tasks'][task_id] = {
                    'success': success,
                    'response': response[:500],  # Truncate response
                    'solution': solution
                }
                
                results['summary']['total'] += 1
                if solution is not None:
                    results['summary']['attempted'] += 1
                if success:
                    results['summary']['solved'] += 1
                    
            # Calculate score
            score = results['summary']['solved'] / results['summary']['total']
            
            # Save results if better than previous
            if score > self.history['best_score']:
                self.history['best_score'] = score
                self.history['best_config'] = config
                self.save_history()
                
            # Save detailed results
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            result_file = self.base_dir / 'results' / f'results_{timestamp}.json'
            with open(result_file, 'w') as f:
                json.dump(results, f, indent=2)
                
            return score
            
        except Exception as e:
            logging.error(f"Experiment failed: {str(e)}")
            return 0.0
            
    async def run_continuous(self):
        """Run continuous testing"""
        while True:
            try:
                # Check resources
                if not self.resource_mgr.check_resources():
                    logging.warning("Resources low, waiting...")
                    await asyncio.sleep(300)  # Wait 5 minutes
                    continue
                    
                # Generate new configuration
                config = self.generate_experiment_config()
                self.experiment_count += 1
                
                logging.info(f"Starting experiment {self.experiment_count}")
                logging.info(f"Configuration: {config}")
                
                # Run experiment
                score = await self.run_experiment(config)
                
                logging.info(f"Experiment {self.experiment_count} score: {score}")
                logging.info(f"Best score so far: {self.history['best_score']}")
                
                # Brief pause between experiments
                await asyncio.sleep(30)
                
            except Exception as e:
                logging.error(f"Continuous testing error: {str(e)}")
                await asyncio.sleep(60)
                
async def main():
    """Run continuous testing"""
    tester = ContinuousTester()
    
    print("Starting continuous testing...")
    print("Press Ctrl+C to stop")
    
    await tester.run_continuous()

if __name__ == '__main__':
    asyncio.run(main())