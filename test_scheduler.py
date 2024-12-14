"""
Schedules and runs periodic ARC tests with graph correlation analysis
"""

import os
import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
from batch_tester import BatchTester
from graph_integration import GraphAnalyzer

class TestScheduler:
    def __init__(self):
        self.base_dir = Path('/users/bard/mcp/arc_testing')
        self.schedule_file = self.base_dir / 'test_schedule.json'
        self.log_file = self.base_dir / 'scheduler.log'
        
        # Configure logging
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        self.batch_tester = BatchTester()
        self.graph_analyzer = GraphAnalyzer()
        
        # Load or create schedule
        self.load_schedule()
        
    def load_schedule(self) -> None:
        """Load or initialize test schedule"""
        if self.schedule_file.exists():
            with open(self.schedule_file, 'r') as f:
                self.schedule = json.load(f)
        else:
            self.schedule = {
                'baseline_established': False,
                'last_run': None,
                'test_frequency': 3600,  # Default 1 hour
                'test_history': []
            }
            
    def save_schedule(self) -> None:
        """Save current schedule"""
        with open(self.schedule_file, 'w') as f:
            json.dump(self.schedule, f, indent=2)
            
    async def run_test_cycle(self) -> Dict[str, Any]:
        """Run a complete test cycle with analysis"""
        logging.info("Starting test cycle")
        
        try:
            # Run batch tests
            results = await self.batch_tester.run_batch()
            
            # Analyze correlations
            correlation = self.graph_analyzer.analyze_arc_correlations(results)
            
            # Generate report
            report = self.graph_analyzer.generate_correlation_report()
            
            # Update schedule
            self.schedule['last_run'] = datetime.now().isoformat()
            self.schedule['test_history'].append({
                'timestamp': datetime.now().isoformat(),
                'results': results,
                'correlation': correlation
            })
            
            if not self.schedule['baseline_established']:
                self.schedule['baseline_established'] = True
                
            self.save_schedule()
            
            # Log report
            logging.info("\n" + report)
            
            return {
                'results': results,
                'correlation': correlation,
                'report': report
            }
            
        except Exception as e:
            logging.error(f"Error in test cycle: {str(e)}")
            return {
                'error': str(e)
            }
            
    def should_run_test(self) -> bool:
        """Check if it's time to run another test"""
        if not self.schedule['last_run']:
            return True
            
        last_run = datetime.fromisoformat(self.schedule['last_run'])
        time_since = (datetime.now() - last_run).total_seconds()
        
        return time_since >= self.schedule['test_frequency']
        
    async def monitor_and_test(self):
        """Main monitoring loop"""
        while True:
            try:
                if self.should_run_test():
                    logging.info("Starting scheduled test cycle")
                    await self.run_test_cycle()
                    
                # Wait before next check
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logging.error(f"Error in monitoring loop: {str(e)}")
                await asyncio.sleep(60)

async def main():
    """Run the test scheduler"""
    scheduler = TestScheduler()
    
    print("Starting test scheduler...")
    print(f"Test frequency: {scheduler.schedule['test_frequency']} seconds")
    
    if not scheduler.schedule['baseline_established']:
        print("\nRunning baseline test...")
        result = await scheduler.run_test_cycle()
        if 'error' not in result:
            print("\nBaseline established!")
            print(result['report'])
    
    print("\nEntering monitoring loop...")
    print("Press Ctrl+C to stop")
    
    await scheduler.monitor_and_test()

if __name__ == '__main__':
    asyncio.run(main())