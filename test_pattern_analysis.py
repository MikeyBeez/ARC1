"""
Test script for enhanced pattern analysis capabilities
"""

import sys
from pathlib import Path
sys.path.append(str(Path('/users/bard/mcp/arc_testing')))

import json
import logging
from enhanced_pattern_analysis import EnhancedPatternAnalyzer

logging.basicConfig(
    filename='pattern_analysis_test.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def load_task(file_path: str) -> dict:
    """Load a task file"""
    with open(file_path) as f:
        return json.load(f)

def test_pattern_analysis(train_input, train_output):
    """Test pattern analysis on a single training example"""
    analyzer = EnhancedPatternAnalyzer()
    
    logging.info("Analyzing input grid patterns")
    input_analysis = analyzer.analyze_grid(train_input)
    logging.info(f"Input patterns: {json.dumps(input_analysis['patterns'], indent=2)}")
    
    logging.info("Analyzing output grid patterns")
    output_analysis = analyzer.analyze_grid(train_output)
    logging.info(f"Output patterns: {json.dumps(output_analysis['patterns'], indent=2)}")
    
    logging.info("Finding transformation rules")
    transform_rules = analyzer.find_transformation_rules(train_input, train_output)
    logging.info(f"Transformation rules: {json.dumps(transform_rules, indent=2)}")
    
    return input_analysis, output_analysis, transform_rules

def main():
    task_path = Path('/users/bard/mcp/arc_testing/data/pattern_test.json')
    
    logging.info(f"Loading test task from {task_path}")
    task = load_task(task_path)
    
    # Test each training example
    for i, example in enumerate(task['train']):
        logging.info(f"\nTesting training example {i+1}")
        input_analysis, output_analysis, rules = test_pattern_analysis(
            example['input'],
            example['output']
        )
        
        logging.info("\nVisualization paths:")
        logging.info(f"Input visualizations: {input_analysis['visualizations']}")
        logging.info(f"Output visualizations: {output_analysis['visualizations']}")

if __name__ == '__main__':
    main()