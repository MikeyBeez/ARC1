"""
Pattern analysis for ARC tasks using enhanced pattern detection.
"""

import json
import numpy as np
import argparse
from typing import Dict, List
from enhanced_meta_patterns import EnhancedMetaPatterns
from pattern_hierarchy import Pattern, PatternHierarchy, PatternLevel

def load_task(filename: str) -> Dict:
    """Load task from JSON file"""
    with open(f"data/{filename}", 'r') as f:
        return json.load(f)

def extract_patterns_from_grid(grid: List[List[int]], 
                             is_output: bool = False) -> Dict:
    """Extract patterns from a grid"""
    patterns = {
        'border': analyze_border_pattern(grid),
        'center': analyze_center_pattern(grid),
        'symmetry': analyze_symmetry(grid),
        'distribution': analyze_value_distribution(grid)
    }
    return patterns

def analyze_border_pattern(grid: List[List[int]]) -> Dict:
    """Analyze the border pattern of a grid"""
    height, width = len(grid), len(grid[0])
    border_values = set()
    
    # Top and bottom rows
    border_values.update(grid[0])
    border_values.update(grid[-1])
    
    # Left and right columns (excluding corners)
    for i in range(1, height-1):
        border_values.add(grid[i][0])
        border_values.add(grid[i][-1])
    
    return {
        'type': 'border',
        'values': list(border_values),
        'uniform': len(border_values) == 1,
        'border_value': next(iter(border_values)) if len(border_values) == 1 else None
    }

def analyze_center_pattern(grid: List[List[int]]) -> Dict:
    """Analyze the center pattern of a grid"""
    height, width = len(grid), len(grid[0])
    center_values = set()
    
    # Get all non-border values
    for i in range(1, height-1):
        for j in range(1, width-1):
            center_values.add(grid[i][j])
    
    return {
        'type': 'center',
        'values': list(center_values),
        'uniform': len(center_values) == 1,
        'center_value': next(iter(center_values)) if len(center_values) == 1 else None
    }

def analyze_symmetry(grid: List[List[int]]) -> Dict:
    """Analyze symmetry in the grid"""
    height, width = len(grid), len(grid[0])
    
    # Check horizontal symmetry
    h_symmetric = all(grid[i] == grid[height-1-i] 
                     for i in range(height//2))
    
    # Check vertical symmetry
    v_symmetric = all(all(grid[i][j] == grid[i][width-1-j] 
                         for j in range(width//2))
                     for i in range(height))
    
    return {
        'type': 'symmetry',
        'horizontal': h_symmetric,
        'vertical': v_symmetric,
        'full': h_symmetric and v_symmetric
    }

def analyze_value_distribution(grid: List[List[int]]) -> Dict:
    """Analyze distribution of values in the grid"""
    flat = [val for row in grid for val in row]
    unique_vals = set(flat)
    counts = {val: flat.count(val) for val in unique_vals}
    total = len(flat)
    
    return {
        'type': 'distribution',
        'values': list(unique_vals),
        'counts': counts,
        'proportions': {val: count/total 
                       for val, count in counts.items()}
    }

def analyze_transformation(input_grid: List[List[int]], 
                         output_grid: List[List[int]]) -> Dict:
    """Analyze transformation between input and output"""
    in_patterns = extract_patterns_from_grid(input_grid)
    out_patterns = extract_patterns_from_grid(output_grid)
    
    transforms = {
        'border': analyze_border_transform(in_patterns['border'], 
                                         out_patterns['border']),
        'center': analyze_center_transform(in_patterns['center'], 
                                         out_patterns['center']),
        'value_mapping': analyze_value_mapping(input_grid, output_grid)
    }
    
    return transforms

def analyze_border_transform(in_border: Dict, out_border: Dict) -> Dict:
    """Analyze how border pattern transforms"""
    return {
        'type': 'border_transform',
        'input_values': in_border['values'],
        'output_values': out_border['values'],
        'preserves_uniformity': in_border['uniform'] == out_border['uniform'],
        'value_mapping': {
            in_val: find_mapping_value(in_val, in_border['values'], 
                                     out_border['values'])
            for in_val in in_border['values']
        }
    }

def analyze_center_transform(in_center: Dict, out_center: Dict) -> Dict:
    """Analyze how center pattern transforms"""
    return {
        'type': 'center_transform',
        'input_values': in_center['values'],
        'output_values': out_center['values'],
        'preserves_uniformity': in_center['uniform'] == out_center['uniform'],
        'value_mapping': {
            in_val: find_mapping_value(in_val, in_center['values'], 
                                     out_center['values'])
            for in_val in in_center['values']
        }
    }

def analyze_value_mapping(input_grid: List[List[int]], 
                         output_grid: List[List[int]]) -> Dict:
    """Analyze overall value mapping between grids"""
    height, width = len(input_grid), len(input_grid[0])
    mappings = {}
    
    for i in range(height):
        for j in range(width):
            in_val = input_grid[i][j]
            out_val = output_grid[i][j]
            
            if in_val not in mappings:
                mappings[in_val] = set()
            mappings[in_val].add(out_val)
    
    return {
        'type': 'value_mapping',
        'mappings': {k: list(v) for k, v in mappings.items()},
        'consistent': all(len(v) == 1 for v in mappings.values()),
        'bijective': len(set.union(*mappings.values())) == len(mappings)
    }

def find_mapping_value(in_val: int, 
                      in_values: List[int], 
                      out_values: List[int]) -> List[int]:
    """Find corresponding output value(s) for an input value"""
    # For now, just map to values at same indices
    # This is a simplification - real mapping might be more complex
    indices = [i for i, v in enumerate(in_values) if v == in_val]
    return [out_values[i] for i in indices if i < len(out_values)]

def main():
    parser = argparse.ArgumentParser(description='Analyze ARC task patterns')
    parser.add_argument('--task', required=True, help='Task JSON file')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    args = parser.parse_args()
    
    # Load and analyze task
    task = load_task(args.task)
    
    print(f"\nAnalyzing task {task['task_id']}...")
    
    # Analyze each training example
    for i, example in enumerate(task['train']):
        print(f"\nTraining example {i+1}:")
        
        # Extract patterns
        input_patterns = extract_patterns_from_grid(example['input'])
        output_patterns = extract_patterns_from_grid(example['output'])
        
        # Analyze transformation
        transforms = analyze_transformation(example['input'], 
                                         example['output'])
        
        # Create enhanced pattern analysis
        hierarchy = PatternHierarchy()
        meta_patterns = EnhancedMetaPatterns(hierarchy)
        
        # Convert patterns to Pattern objects
        input_pattern_objs = [
            Pattern(
                type=f"input_{p['type']}", 
                level=PatternLevel.ATOMIC,
                properties=p,
                confidence=1.0
            )
            for name, p in input_patterns.items()
        ]
        
        output_pattern_objs = [
            Pattern(
                type=f"output_{p['type']}", 
                level=PatternLevel.ATOMIC,
                properties=p,
                confidence=1.0
            )
            for name, p in output_patterns.items()
        ]
        
        # Analyze with enhanced system
        pattern_transforms = meta_patterns.analyze_transformation(
            input_pattern_objs, output_pattern_objs)
        
        abstractions = meta_patterns.find_abstractions()
        
        # Print results
        if args.verbose:
            print("\nInput patterns:")
            for name, pattern in input_patterns.items():
                print(f"  {name}: {pattern}")
                
            print("\nOutput patterns:")
            for name, pattern in output_patterns.items():
                print(f"  {name}: {pattern}")
                
            print("\nTransformations:")
            for name, transform in transforms.items():
                print(f"  {name}: {transform}")
                
            print("\nPattern transformations:")
            for t in pattern_transforms:
                print(f"  {t.transform_type}: {t.conditions}")
                
            print("\nAbstractions found:")
            for a in abstractions:
                print(f"  {a.template_type}: {a.abstraction_level}")
        else:
            print(f"Found {len(pattern_transforms)} transformations")
            print(f"Found {len(abstractions)} abstractions")

if __name__ == '__main__':
    main()