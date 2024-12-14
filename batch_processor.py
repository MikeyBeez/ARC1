"""
Resource-conscious batch processor with checkpointing
"""
import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from typing import List, Dict
from enhanced_reasoning import EnhancedReasoning

def ensure_dirs():
    """Ensure all required directories exist"""
    dirs = [
        '/users/bard/mcp/arc_testing/logs',
        '/users/bard/mcp/arc_testing/checkpoints',
        '/users/bard/mcp/arc_testing/results'
    ]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)

def setup_logging():
    """Configure logging"""
    ensure_dirs()
    log_file = '/users/bard/mcp/arc_testing/logs/batch_processing.log'
    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    # Also log to console
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger('').addHandler(console)

class CheckpointedBatchProcessor:
    def __init__(self):
        self.batch_size = 1  # Process one task at a time
        self.task_timeout = 60  # 1 minute per task
        self.reasoning = None
        self.checkpoint_file = Path('/users/bard/mcp/arc_testing/checkpoints/processor_state.json')
        
    def load_checkpoint(self) -> Dict:
        """Load previous state"""
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file) as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Error loading checkpoint: {e}")
        return {'processed_tasks': [], 'results': []}
        
    def save_checkpoint(self, state: Dict):
        """Save current state"""
        try:
            with open(self.checkpoint_file, 'w') as f:
                json.dump(state, f)
        except Exception as e:
            logging.error(f"Error saving checkpoint: {e}")
            
    def initialize_reasoning(self):
        """Initialize reasoning system"""
        try:
            self.reasoning = EnhancedReasoning()
            logging.info("Reasoning system initialized")
        except Exception as e:
            logging.error(f"Failed to initialize reasoning: {e}")
            raise
            
    async def process_task(self, task_file: Path) -> Dict:
        """Process a single task"""
        logging.info(f"Processing {task_file}")
        try:
            if self.reasoning is None:
                self.initialize_reasoning()
                
            with open(task_file) as f:
                task_data = json.load(f)
                
            result = await asyncio.wait_for(
                self._analyze_task(task_data),
                timeout=self.task_timeout
            )
            return result
            
        except asyncio.TimeoutError:
            logging.error(f"Task {task_file} timed out")
            return {'status': 'timeout', 'task': str(task_file)}
        except Exception as e:
            logging.error(f"Error processing {task_file}: {e}")
            return {'status': 'error', 'task': str(task_file), 'error': str(e)}
            
    async def _analyze_task(self, task_data: Dict) -> Dict:
        """Analyze a single task"""
        task_id = task_data.get('task_id', 'unknown')
        try:
            train_examples = task_data.get('train', [])
            test_case = task_data.get('test', [{}])[0]
            
            train_inputs = [ex['input'] for ex in train_examples]
            train_outputs = [ex['output'] for ex in train_examples]
            
            prediction = self.reasoning.predict_output(
                test_case['input'],
                train_inputs,
                train_outputs
            )
            
            success = prediction == test_case['output']
            explanation = self.reasoning.explain_prediction(
                test_case['input'],
                prediction,
                train_examples
            )
            
            return {
                'task_id': task_id,
                'success': success,
                'prediction': prediction,
                'expected': test_case['output'],
                'explanation': explanation
            }
        except Exception as e:
            logging.error(f"Error analyzing task {task_id}: {e}")
            return {'task_id': task_id, 'success': False, 'error': str(e)}
            
    async def process_all(self):
        """Process all tasks with checkpointing"""
        state = self.load_checkpoint()
        processed = set(state['processed_tasks'])
        results = state['results']
        
        data_dir = Path('/users/bard/mcp/arc_testing/data')
        task_files = [f for f in data_dir.glob('*.json') 
                     if f.name not in processed]
        
        for task_file in task_files:
            result = await self.process_task(task_file)
            results.append(result)
            processed.add(task_file.name)
            
            # Save state after each task
            state = {
                'processed_tasks': list(processed),
                'results': results
            }
            self.save_checkpoint(state)
            
            # Save individual result
            self.save_result(task_file.stem, result)
            
            # Brief pause between tasks
            await asyncio.sleep(1)
            
        return results
        
    def save_result(self, task_name: str, result: Dict):
        """Save individual task result"""
        result_dir = Path('/users/bard/mcp/arc_testing/results')
        result_file = result_dir / f"{task_name}_result.json"
        try:
            with open(result_file, 'w') as f:
                json.dump(result, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving result: {e}")

async def main():
    setup_logging()
    logging.info("Starting batch processor")
    
    processor = CheckpointedBatchProcessor()
    results = await processor.process_all()
    
    successes = sum(1 for r in results if r.get('success', False))
    total = len(results)
    
    if total > 0:
        logging.info(f"Processing complete: {successes}/{total} tasks solved "
                    f"({successes/total*100:.2f}%)")
    else:
        logging.warning("No tasks processed")

if __name__ == '__main__':
    asyncio.run(main())