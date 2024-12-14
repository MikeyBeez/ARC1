"""Test ARC reasoning functions in batches"""

import asyncio
import json
from pathlib import Path

def load_arc_tasks(base_dir: Path) -> list:
    """Load all ARC tasks from arc_tasks directory"""
    tasks_dir = base_dir / 'data/arc_tasks'
    tasks = []
    
    for task_file in tasks_dir.glob('*.json'):
        if task_file.name != 'task_categories.json':
            with open(task_file) as f:
                tasks.append(json.load(f))
                
    return tasks

async def main():
    """Run batch testing of ARC tasks"""
    base_dir = Path('/users/bard/mcp/arc_testing')
    tasks = load_arc_tasks(base_dir)
    
    print(f"Loaded {len(tasks)} tasks")
    print("Running tests...")
    
    # Initialize testing components
    # Test each task with various function combinations
    
if __name__ == '__main__':
    asyncio.run(main())