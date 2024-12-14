"""
ARC Testing Framework with enhanced logging and reasoning
"""

import os
import json
import time
import logging
import asyncio
import http.client
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

@dataclass
class ARCTask:
    """Represents a single ARC task"""
    task_id: str
    train_inputs: List[List[List[int]]]
    train_outputs: List[List[List[int]]]
    test_inputs: List[List[List[int]]]
    test_outputs: List[List[List[int]]]
    
    @classmethod
    def from_json(cls, json_data: Dict) -> 'ARCTask':
        return cls(
            task_id=json_data['task_id'],
            train_inputs=[t['input'] for t in json_data['train']],
            train_outputs=[t['output'] for t in json_data['train']],
            test_inputs=[t['input'] for t in json_data['test']],
            test_outputs=[t['output'] for t in json_data['test']]
        )

    def analyze_patterns(self) -> List[str]:
        """Analyze common patterns in the training examples"""
        patterns = []
        
        # Compare dimensions
        for i, (input_grid, output_grid) in enumerate(zip(self.train_inputs, self.train_outputs)):
            in_dims = (len(input_grid), len(input_grid[0]))
            out_dims = (len(output_grid), len(output_grid[0]))
            patterns.append(f"Example {i+1} transforms {in_dims} grid to {out_dims} grid")
            
        # Analyze value transformations
        for i, (input_grid, output_grid) in enumerate(zip(self.train_inputs, self.train_outputs)):
            unique_in = set(x for row in input_grid for x in row)
            unique_out = set(x for row in output_grid for x in row)
            patterns.append(f"Example {i+1} maps values {unique_in} to {unique_out}")
            
        return patterns

class ARCTester:
    def __init__(self, model_name: str = "mistral"):
        # Setup paths
        self.base_dir = Path('/users/bard/mcp')
        self.arc_dir = self.base_dir / 'arc_testing'
        self.data_dir = self.arc_dir / 'data'
        self.results_dir = self.arc_dir / 'results'
        self.log_dir = self.arc_dir
        self.log_file = self.log_dir / 'arc_testing.log'
        
        # Verify directories
        if not self.verify_directories():
            raise RuntimeError("Directory verification failed")
            
        # Model configuration
        self.model_name = model_name
        self.host = os.getenv('OLLAMA_HOST', 'localhost')
        self.port = int(os.getenv('OLLAMA_PORT', '11434'))
        self.timeout = int(os.getenv('MODEL_TIMEOUT', '30'))
        self.max_retries = int(os.getenv('MAX_RETRIES', '3'))
        
        # Setup enhanced logging
        logging.basicConfig(
            filename=self.log_file,
            level=logging.DEBUG if os.getenv('DEBUG') else logging.INFO,
            format='%(asctime)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s'
        )
        
        self.task_cache = {}
        
    def format_prompt(self, task: ARCTask) -> str:
        """Format task with enhanced reasoning guidance"""
        # Analyze patterns first
        patterns = task.analyze_patterns()
        
        prompt = "You are an expert at solving abstract reasoning puzzles. "
        prompt += "Analyze this task step by step:\n\n"
        prompt += "1. First, observe the training examples carefully:\n"
        
        for i, (input_grid, output_grid) in enumerate(zip(task.train_inputs, task.train_outputs)):
            prompt += f"\nExample {i+1}:\n"
            prompt += "Input:\n"
            prompt += '\n'.join(' '.join(str(x) for x in row) for row in input_grid)
            prompt += "\nOutput:\n"
            prompt += '\n'.join(' '.join(str(x) for x in row) for row in output_grid)
            prompt += f"\nPattern observed: {patterns[i]}\n"
            
        prompt += "\n2. Look for these transformations:"
        prompt += "\n- Changes in grid dimensions"
        prompt += "\n- Patterns in value changes (0s to 1s, etc.)"
        prompt += "\n- Row and column operations"
        prompt += "\n- Symmetry or rotations"
        prompt += "\n- Local vs global transformations"
        
        prompt += "\n\n3. Now solve this new input:\n"
        prompt += '\n'.join(' '.join(str(x) for x in row) for row in task.test_inputs[0])
        
        prompt += "\n\n4. First explain your reasoning step by step."
        prompt += "\n5. Then provide ONLY the numeric solution grid with spaces between numbers."
        
        logging.debug(f"Generated prompt for task {task.task_id}:\n{prompt}")
        return prompt
        
    def validate_solution(self, solution: List[List[int]], task: ARCTask) -> Tuple[bool, str]:
        """Validate a solution with detailed checks"""
        try:
            if not solution:
                return False, "Empty solution"
                
            expected = task.test_outputs[0]
            
            # Check dimensions
            if len(solution) != len(expected) or len(solution[0]) != len(expected[0]):
                return False, f"Dimension mismatch: got {len(solution)}x{len(solution[0])}, expected {len(expected)}x{len(expected[0])}"
            
            # Check values
            mismatches = []
            for i in range(len(expected)):
                for j in range(len(expected[0])):
                    if solution[i][j] != expected[i][j]:
                        mismatches.append(f"[{i},{j}]: {solution[i][j]} != {expected[i][j]}")
                        
            if mismatches:
                return False, f"Value mismatches at: {', '.join(mismatches)}"
                
            return True, "Solution matches expected output"
            
        except Exception as e:
            logging.error(f"Validation error: {str(e)}")
            return False, f"Validation error: {str(e)}"
            
    async def query_model(self, prompt: str) -> Optional[str]:
        """Query the model with enhanced error handling"""
        for attempt in range(self.max_retries):
            try:
                start_time = time.time()
                logging.debug(f"Attempt {attempt + 1} to query model")
                
                conn = http.client.HTTPConnection(
                    self.host, 
                    self.port,
                    timeout=self.timeout
                )
                
                data = {
                    'model': self.model_name,
                    'prompt': prompt,
                    'stream': False
                }
                
                conn.request(
                    "POST",
                    "/api/generate",
                    json.dumps(data),
                    {'Content-Type': 'application/json'}
                )
                
                response = conn.getresponse()
                elapsed = time.time() - start_time
                
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}: {response.read().decode()}")
                    
                result = json.loads(response.read().decode())
                logging.debug(f"Model response received in {elapsed:.2f}s")
                logging.debug(f"Raw response: {result['response']}")
                
                return result['response']
                
            except Exception as e:
                logging.error(f"Model query attempt {attempt + 1} failed: {str(e)}\n{traceback.format_exc()}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(1)
            finally:
                conn.close()
                
        return None
        
    def parse_grid(self, text: str) -> Optional[List[List[int]]]:
        """Extract grid with enhanced parsing and validation"""
        try:
            # Log the text being parsed
            logging.debug(f"Attempting to parse grid from:\n{text}")
            
            # Find grid-like pattern
            lines = text.split('\n')
            grid = []
            in_grid = False
            
            for i, line in enumerate(lines):
                # Skip empty lines
                if not line.strip():
                    continue
                    
                # Try to parse numbers
                try:
                    row = [int(x) for x in line.split()]
                    if row:
                        logging.debug(f"Found valid row: {row}")
                        grid.append(row)
                        in_grid = True
                except ValueError:
                    if in_grid:
                        break
                    logging.debug(f"Skipping non-grid line: {line}")
                        
            # Validate grid
            if not grid:
                logging.error("No valid grid found in text")
                return None
                
            # Check all rows same length
            width = len(grid[0])
            if not all(len(row) == width for row in grid):
                logging.error(f"Inconsistent row lengths: {[len(row) for row in grid]}")
                return None
                
            logging.debug(f"Successfully parsed grid: {grid}")
            return grid
            
        except Exception as e:
            logging.error(f"Grid parsing failed: {str(e)}\n{traceback.format_exc()}")
            return None
            
    async def solve_task(self, task: ARCTask) -> Tuple[bool, str, Optional[List[List[int]]]]:
        """Solve a task with enhanced logging and validation"""
        try:
            logging.info(f"Starting task {task.task_id}")
            
            # Generate and log prompt
            prompt = self.format_prompt(task)
            
            # Get model response
            response = await self.query_model(prompt)
            if not response:
                logging.error(f"Task {task.task_id}: Model query failed")
                return False, "Model query failed", None
                
            # Extract grid
            solution = self.parse_grid(response)
            if not solution:
                logging.error(f"Task {task.task_id}: Could not parse solution grid")
                return False, response, None
                
            # Validate solution
            success, validation_msg = self.validate_solution(solution, task)
            logging.info(f"Task {task.task_id} validation: {validation_msg}")
            
            return success, response, solution
            
        except Exception as e:
            logging.error(f"Task {task.task_id} solution failed: {str(e)}\n{traceback.format_exc()}")
            return False, str(e), None
            
    def load_tasks(self) -> None:
        """Load all tasks with validation"""
        for file_path in self.data_dir.glob('*.json'):
            try:
                logging.info(f"Loading task file: {file_path}")
                with open(file_path) as f:
                    data = json.load(f)
                    task = ARCTask.from_json(data)
                    self.task_cache[task.task_id] = task
                    logging.info(f"Loaded task: {task.task_id}")
            except Exception as e:
                logging.error(f"Failed to load {file_path}: {str(e)}\n{traceback.format_exc()}")
                
async def main():
    """Run the ARC tester with result analysis"""
    tester = ARCTester()
    
    print("Loading tasks...")
    tester.load_tasks()
    print(f"Loaded {len(tester.task_cache)} tasks")
    
    print("\nRunning tests...")
    results = {}
    
    for task_id, task in tester.task_cache.items():
        print(f"\nTesting task {task_id}...")
        success, response, solution = await tester.solve_task(task)
        
        results[task_id] = {
            'success': success,
            'response': response,
            'solution': solution
        }
        
        print(f"Success: {success}")
        if not success:
            print("Response excerpt:")
            print(response[:200] + "..." if len(response) > 200 else response)
    
    # Save detailed results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    result_file = tester.results_dir / f'results_{timestamp}.json'
    with open(result_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'model': tester.model_name,
            'tasks': results,
            'summary': {
                'total': len(results),
                'attempted': sum(1 for r in results.values() if r['solution'] is not None),
                'solved': sum(1 for r in results.values() if r['success'])
            }
        }, f, indent=2)
        
    print("\nResults saved to:", result_file)

if __name__ == '__main__':
    asyncio.run(main())