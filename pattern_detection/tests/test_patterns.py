"""Test pattern detection functionality"""
import sys
import os
import logging
from pathlib import Path

print("Python path:", sys.path)
print("Current directory:", os.getcwd())

try:
    # Add parent directory to path for imports
    sys.path.append(str(Path(__file__).parent.parent))

    print("Attempting imports...")
    from pattern_base import Pattern, PatternLevel, BaseDetector
    from core_pattern_manager import CorePatternManager
    print("Imports successful")

    # Configure logging
    log_dir = Path('/users/bard/mcp/arc_testing/pattern_detection/logs')
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=log_dir / 'pattern_test.log',
        filemode='w'
    )

    def main():
        logging.info("Starting pattern detection test")
        print("Test started")
        try:
            manager = CorePatternManager()
            logging.info("Pattern manager initialized")
            print("Manager initialized")
            
        except Exception as e:
            print(f"Test failed with error: {str(e)}")
            logging.error(f"Test failed: {str(e)}")
            sys.exit(1)
            
        print("Test completed successfully")
        sys.exit(0)
            
except Exception as e:
    print(f"Setup failed with error: {str(e)}")
    sys.exit(1)

if __name__ == '__main__':
    main()