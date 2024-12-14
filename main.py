"""Main entry point for ARC recipe testing"""

import asyncio
import logging
from pathlib import Path
from recipe_testing import RecipeTester
from recipe_testing.logging_setup import setup_logging
from batch_tester import load_arc_tasks

async def main():
    """Initialize and run recipe testing"""
    base_dir = Path('/users/bard/mcp/arc_testing')
    logger, run_id_filter = setup_logging(base_dir)
    
    # Load all ARC tasks
    tasks = load_arc_tasks(base_dir)
    logger.info(f"Loaded {len(tasks)} tasks")
    
    try:
        tester = RecipeTester(base_dir, logger, run_id_filter)
        
        for task in tasks:
            logger.info(f"Testing task: {task['task_id']}")
            await tester.test_task(task)
            
        print("Testing complete")
        
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        
    except Exception as e:
        print(f"Fatal error: {e}")
        logger.error("Fatal error in main process", exc_info=True)

if __name__ == '__main__':
    asyncio.run(main())