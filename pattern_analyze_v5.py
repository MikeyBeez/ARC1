"""
Enhanced pattern analysis for ARC tasks with conditional transformation detection.
"""

import json
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Set, Optional, Tuple

@dataclass
class GridMetaPattern:
    name: str
    description: str
    conditions: Dict
    confidence: float
    size_invariant: bool
    examples: List[Dict]

def _get_row_position_name(row: int, total_rows: int) -> str:
    """Convert row index to position name"""
    if row == 0:
        return 'top'
    if row == total_rows - 1:
        return 'bottom'
    return 'middle'

def _analyze_position_rule(positions: List[Tuple[int, int]], 
                         grid_size: Tuple[int, int]) -> Dict:
    """Analyze the positional pattern of a group of positions"""
    if not positions:
        return {}
        
    rows = set(pos[0] for pos in positions)
    cols = set(pos[1] for pos in positions)
    
    rule = {}
    if len(rows) == 1:
        row = next(iter(rows))
        rule['row'] = {
            'index': row,
            'position': _get_row_position_name(row, grid_size[0])
        }
    if len(cols) == 1:
        col = next(iter(cols))
        rule['column'] = col
        
    return rule

def _find_value_transformations(input_grid: List[List[int]], 
                              output_grid: List[List[int]]) -> List[Dict]:
    """Find how values transform based on position"""
    h, w = len(input_grid), len(input_grid[0])
    transformations = []
    
    # Group by input value
    input_positions = {}
    for i in range(h):
        for j in range(w):
            val = input_grid[i][j]
            if val not in input_positions:
                input_positions[val] = []
            input_positions[val].append((i, j))
    
    # Analyze each value group
    for input_val, positions in input_positions.items():
        output_vals = set(output_grid[i][j] for i, j in positions)
        
        if len(output_vals) == 1:  # Consistent transformation
            output_val = next(iter(output_vals))
            position_rule = _analyze_position_rule(positions, (h, w))
            
            transformations.append({
                'input_value': input_val,
                'output_value': output_val,
                'positions': positions,
                'position_rule': position_rule
            })
            
    return transformations

def extract_meta_patterns(examples: List[Dict]) -> List[GridMetaPattern]:
    """Extract high-level patterns across multiple examples"""
    meta_patterns = []
    
    # Analyze transformations for each example
    all_transformations = [
        _find_value_transformations(ex['input'], ex['output'])
        for ex in examples
    ]
    
    # Look for consistent transformation rules
    if all_transformations:
        # Group by input value
        value_rules = {}
        for transforms in all_transformations:
            for t in transforms:
                in_val = t['input_value']
                if in_val not in value_rules:
                    value_rules[in_val] = []
                value_rules[in_val].append(t)
        
        # Check if transformations are position-dependent
        position_dependent = False
        for rules in value_rules.values():
            if any(rule['position_rule'] for rule in rules):
                position_dependent = True
                break
        
        if position_dependent:
            meta_patterns.append(GridMetaPattern(
                name="position_dependent_transformation",
                description="Values transform differently based on their position",
                conditions={
                    'input_values': list(value_rules.keys()),
                    'rules': [
                        {
                            'input_value': in_val,
                            'transformations': [
                                {
                                    'output_value': r['output_value'],
                                    'position': r['position_rule']
                                }
                                for r in rules
                            ]
                        }
                        for in_val, rules in value_rules.items()
                    ]
                },
                confidence=1.0,
                size_invariant=True,
                examples=[{
                    'grid_size': (len(ex['input']), len(ex['input'][0])),
                    'transformations': trans
                } for ex, trans in zip(examples, all_transformations)]
            ))
        
        # Check for value preservation
        preserved = []
        for ex in examples:
            preserved.extend([
                (i, j) for i in range(len(ex['input']))
                for j in range(len(ex['input'][0]))
                if ex['input'][i][j] == ex['output'][i][j]
            ])
        
        if preserved:
            meta_patterns.append(GridMetaPattern(
                name="value_preservation",
                description="Some values remain unchanged",
                conditions={
                    'preserved_values': sorted(set(
                        ex['input'][i][j] 
                        for i, j in preserved
                    ))
                },
                confidence=1.0,
                size_invariant=True,
                examples=[{
                    'grid_size': (len(ex['input']), len(ex['input'][0])),
                    'preserved_positions': [
                        (i, j) for i in range(len(ex['input']))
                        for j in range(len(ex['input'][0]))
                        if ex['input'][i][j] == ex['output'][i][j]
                    ]
                } for ex in examples]
            ))
        
        # Check for conditional value mapping
        if value_rules:
            meta_patterns.append(GridMetaPattern(
                name="conditional_value_mapping",
                description="Values transform based on their position in the grid",
                conditions={
                    'mappings': {
                        in_val: sorted(set(
                            r['output_value'] for r in rules
                        ))
                        for in_val, rules in value_rules.items()
                    },
                    'position_dependent': position_dependent
                },
                confidence=1.0,
                size_invariant=True,
                examples=[{
                    'grid_size': (len(ex['input']), len(ex['input'][0])),
                    'transformations': [
                        {
                            'from': t['input_value'],
                            'to': t['output_value'],
                            'at': t['position_rule']
                        }
                        for t in trans
                    ]
                } for ex, trans in zip(examples, all_transformations)]
            ))
    
    return meta_patterns

def analyze_task(task_data: Dict) -> List[GridMetaPattern]:
    """Analyze an ARC task to find high-level patterns"""
    # Extract meta patterns from training examples
    meta_patterns = extract_meta_patterns(task_data['train'])
    
    # Verify patterns against test examples if available
    if 'test' in task_data:
        test_patterns = extract_meta_patterns(task_data['test'])
        # Keep only patterns that appear in both train and test
        meta_patterns = [p for p in meta_patterns 
                        if any(tp.name == p.name for tp in test_patterns)]
    
    return meta_patterns

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze ARC task patterns')
    parser.add_argument('--task', required=True, help='Task JSON file')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    args = parser.parse_args()
    
    # Load task
    with open(f"data/{args.task}", 'r') as f:
        task_data = json.load(f)
    
    print(f"\nAnalyzing task {task_data['task_id']}...")
    
    # Find meta patterns
    patterns = analyze_task(task_data)
    
    print("\nMeta-patterns found:")
    for pattern in patterns:
        print(f"\n{pattern.name}:")
        print(f"  Description: {pattern.description}")
        print(f"  Confidence: {pattern.confidence}")
        print(f"  Size Invariant: {pattern.size_invariant}")
        print("  Conditions:")
        for k, v in pattern.conditions.items():
            print(f"    {k}: {v}")
        print("  Examples:")
        for ex in pattern.examples:
            print(f"    Grid size: {ex['grid_size']}")
            for k, v in ex.items():
                if k != 'grid_size':
                    print(f"    {k}: {v}")

if __name__ == '__main__':
    main()