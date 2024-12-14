"""
Real-time monitoring of test progress and system performance
"""

import os
import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class TestMonitor:
    def __init__(self):
        self.base_dir = Path('/users/bard/mcp/arc_testing')
        self.monitor_log = self.base_dir / 'monitor.log'
        self.status_file = self.base_dir / 'current_status.json'
        
        logging.basicConfig(
            filename=self.monitor_log,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    async def watch_progress(self):
        """Monitor test progress in real time"""
        current_status = {
            'phase': 'initializing',
            'tasks_completed': 0,
            'success_count': 0,
            'current_task': None,
            'start_time': datetime.now().isoformat()
        }
        
        while True:
            try:
                # Update status
                self.update_status_file(current_status)
                
                # Check results directory for new completions
                results_dir = self.base_dir / 'results'
                if results_dir.exists():
                    result_files = list(results_dir.glob('*.json'))
                    current_status['tasks_completed'] = len(result_files)
                    
                    # Analyze latest result
                    if result_files:
                        latest = max(result_files, key=lambda x: x.stat().st_mtime)
                        with open(latest, 'r') as f:
                            latest_result = json.load(f)
                            if latest_result.get('success', False):
                                current_status['success_count'] += 1
                
                # Log progress
                self.log_progress(current_status)
                
                # Check if testing is complete
                if current_status.get('phase') == 'complete':
                    break
                    
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logging.error(f"Error in progress monitoring: {str(e)}")
                await asyncio.sleep(5)
                
    def update_status_file(self, status: Dict[str, Any]) -> None:
        """Update the current status file"""
        with open(self.status_file, 'w') as f:
            json.dump(status, f, indent=2)
            
    def log_progress(self, status: Dict[str, Any]) -> None:
        """Log current progress"""
        elapsed = (datetime.now() - datetime.fromisoformat(status['start_time'])).total_seconds()
        success_rate = (
            status['success_count'] / status['tasks_completed'] 
            if status['tasks_completed'] > 0 else 0
        )
        
        logging.info(
            f"Progress: {status['tasks_completed']} tasks completed, "
            f"Success rate: {success_rate:.2%}, "
            f"Elapsed time: {elapsed:.1f}s"
        )
        
    def print_status(self) -> None:
        """Print current status to console"""
        if self.status_file.exists():
            with open(self.status_file, 'r') as f:
                status = json.load(f)
                
            elapsed = (datetime.now() - datetime.fromisoformat(status['start_time'])).total_seconds()
            print(f"\nCurrent Status:")
            print(f"Phase: {status['phase']}")
            print(f"Tasks Completed: {status['tasks_completed']}")
            print(f"Successful Solutions: {status['success_count']}")
            print(f"Time Elapsed: {elapsed:.1f} seconds")
            if status['tasks_completed'] > 0:
                success_rate = status['success_count'] / status['tasks_completed']
                print(f"Current Success Rate: {success_rate:.2%}")

async def main():
    """Run the test monitor"""
    monitor = TestMonitor()
    print("Starting test monitor...")
    print("Press Ctrl+C to stop monitoring")
    
    try:
        await monitor.watch_progress()
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
    finally:
        monitor.print_status()

if __name__ == '__main__':
    asyncio.run(main())