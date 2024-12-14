"""
Enhanced pattern analysis for ARC tasks with better abstraction detection.
"""

import json
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Set, Optional

@dataclass
class GridMetaPattern:
    """Represents a high-level pattern in grid transformation"""
    name: str
    description: str
    conditions: Dict
    confidence: float
    size_invariant: bool
    examples: List[Dict]

def _preserves_symmetry(input_grid: List[List[int]], output_grid: List[List[int]]) -> bool:
    """Check if transformation preserves symmetry properties"""
    return (_has_horizontal_symmetry(input_grid) == _has_horizontal_symmetry(output_grid) and
            _has_vertical_symmetry(input_grid) == _has_vertical_symmetry(output_grid))

def extract_meta_patterns(examples: List[Dict]) -> List[GridMetaPattern]:
    """Extract high-level patterns across multiple examples"""
    meta_patterns = []
    
    # Check for border inversion pattern
    if all(_has_border_inversion(ex['input'], ex['output']) for ex in examples):
        meta_patterns.append(GridMetaPattern(
            name="border_inversion",
            description="Border elements are inverted while preserving uniformity",
            conditions={
                "input_border": {"uniform": True, "value": 0},
                "output_border": {"uniform": True, "value": 1}
            },
            confidence=1.0,
            size_invariant=True,
            examples=[{
                "grid_size": (len(ex['input']), len(ex['input'][0])),
                "preserves_structure": True
            } for ex in examples]
        ))
    
    # Check for center inversion pattern
    if all(_has_center_inversion(ex['input'], ex['output']) for ex in examples):
        meta_patterns.append(GridMetaPattern(
            name="center_preservation_with_inversion",
            description="Center elements are inverted while preserving layout",
            conditions={
                "input_center": {"uniform_regions": True},
                "output_center": {"preserves_regions": True}
            },
            confidence=1.0,
            size_invariant=True,
            examples=[{
                "grid_size": (len(ex['input']), len(ex['input'][0])),
                "region_count": _count_center_regions(ex['input'])
            } for ex in examples]
        ))
    
    # Check for symmetry preservation
    if all(_preserves_symmetry(ex['input'], ex['output']) for ex in examples):
        meta_patterns.append(GridMetaPattern(
            name="symmetry_preservation",
            description="All symmetry properties are preserved in transformation",
            conditions={
                "horizontal_symmetry": all(_has_horizontal_symmetry(ex['input']) == 
                                        _has_horizontal_symmetry(ex['output']) 
                                        for ex in examples),
                "vertical_symmetry": all(_has_vertical_symmetry(ex['input']) == 
                                       _has_vertical_symmetry(ex['output']) 
                                       for ex in examples)
            },
            confidence=1.0,
            size_invariant=True,
            examples=[{
                "grid_size": (len(ex['input']), len(ex['input'][0])),
                "symmetry_type": _get_symmetry_type(ex['input'])
            } for ex in examples]
        ))
    
    # Check for value relationship pattern
    value_patterns = _analyze_value_patterns(examples)
    if value_patterns:
        meta_patterns.append(GridMetaPattern(
            name="consistent_value_mapping",
            description="Values are transformed consistently across all positions",
            conditions=value_patterns,
            confidence=1.0,
            size_invariant=True,
            examples=[{
                "grid_size": (len(ex['input']), len(ex['input'][0])),
                "value_map": _get_value_mapping(ex['input'], ex['output'])
            } for ex in examples]
        ))
    
    return meta_patterns

def _has_border_inversion(input_grid: List[List[int]], 
                         output_grid: List[List[int]]) -> bool:
    """Check if grid has border inversion pattern"""
    h, w = len(input_grid), len(input_grid[0])
    
    # Check borders
    for i in range(h):
        for j in range(w):
            if i in (0, h-1) or j in (0, w-1):  # Border position
                if input_grid[i][j] == output_grid[i][j]:  # Should be inverted
                    return False
    return True

def _has_center_inversion(input_grid: List[List[int]], 
                         output_grid: List[List[int]]) -> bool:
    """Check if grid has center region inversion"""
    h, w = len(input_grid), len(input_grid[0])
    
    for i in range(1, h-1):
        for j in range(1, w-1):
            if input_grid[i][j] == output_grid[i][j]:  # Should be inverted
                return False
    return True

def _count_center_regions(grid: List[List[int]]) -> int:
    """Count distinct regions in grid center"""
    h, w = len(grid), len(grid[0])
    values = set()
    
    for i in range(1, h-1):
        for j in range(1, w-1):
            values.add(grid[i][j])
            
    return len(values)

def _has_horizontal_symmetry(grid: List[List[int]]) -> bool:
    """Check for horizontal symmetry"""
    h = len(grid)
    return all(grid[i] == grid[h-1-i] for i in range(h//2))

def _has_vertical_symmetry(grid: List[List[int]]) -> bool:
    """Check for vertical symmetry"""
    h, w = len(grid), len(grid[0])
    return all(all(grid[i][j] == grid[i][w-1-j] 
                  for j in range(w//2))
              for i in range(h))

def _get_symmetry_type(grid: List[List[int]]) -> str:
    """Get the type of symmetry present"""
    h_sym = _has_horizontal_symmetry(grid)
    v_sym = _has_vertical_symmetry(grid)
    
    if h_sym and v_sym:
        return "full"
    elif h_sym:
        return "horizontal"
    elif v_sym:
        return "vertical"
    return "none"

def _analyze_value_patterns(examples: List[Dict]) -> Optional[Dict]:
    """Analyze patterns in value transformations"""
    patterns = {}
    
    # Check each example for value mappings
    for ex in examples:
        mapping = _get_value_mapping(ex['input'], ex['output'])
        
        for in_val, out_val in mapping.items():
            if in_val not in patterns:
                patterns[in_val] = set()
            patterns[in_val].add(out_val)
    
    # Only return if mappings are consistent
    if all(len(v) == 1 for v in patterns.values()):
        return {
            'consistent_mapping': True,
            'mapping': {k: next(iter(v)) for k, v in patterns.items()},
            'bijective': len(set.union(*patterns.values())) == len(patterns)
        }
    
    return None

def _get_value_mapping(input_grid: List[List[int]], 
                      output_grid: List[List[int]]) -> Dict[int, int]:
    """Get mapping of input values to output values"""
    mapping = {}
    h, w = len(input_grid), len(input_grid[0])
    
    for i in range(h):
        for j in range(w):
            mapping[input_grid[i][j]] = output_grid[i][j]
            
    return mapping

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