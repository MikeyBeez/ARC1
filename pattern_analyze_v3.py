"""
Enhanced pattern analysis for ARC tasks with spatial propagation detection.
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

def _find_ones_positions(grid: List[List[int]]) -> List[Tuple[int, int]]:
    """Find positions of all 1s in the grid"""
    return [(i, j) for i in range(len(grid)) for j in range(len(grid[0]))
            if grid[i][j] == 1]

def _has_vertical_propagation(input_grid: List[List[int]], 
                            output_grid: List[List[int]]) -> bool:
    """Check if 1s in top row propagate downward"""
    top_ones = [(0, j) for j in range(len(input_grid[0])) 
                if input_grid[0][j] == 1]
    
    for i, j in top_ones:
        # Check if there's a vertical line of 1s below this position
        if not all(output_grid[row][j] == 1 
                  for row in range(len(output_grid))):
            return False
    return bool(top_ones)  # True if we found any top ones

def _has_bottom_row_fill(output_grid: List[List[int]]) -> bool:
    """Check if bottom row is all 1s"""
    return all(val == 1 for val in output_grid[-1])

def _preserves_top_row(input_grid: List[List[int]], 
                      output_grid: List[List[int]]) -> bool:
    """Check if top row pattern is preserved"""
    return input_grid[0] == output_grid[0]

def _find_source_positions(input_grid: List[List[int]]) -> List[Tuple[int, int]]:
    """Find positions that act as sources for pattern propagation"""
    return [(i, j) for i in range(len(input_grid)) 
            for j in range(len(input_grid[0]))
            if input_grid[i][j] == 1]

def extract_meta_patterns(examples: List[Dict]) -> List[GridMetaPattern]:
    """Extract high-level patterns across multiple examples"""
    meta_patterns = []
    
    # Check for vertical propagation pattern
    if all(_has_vertical_propagation(ex['input'], ex['output']) 
           for ex in examples):
        meta_patterns.append(GridMetaPattern(
            name="vertical_line_propagation",
            description="Ones in the top row create vertical lines of ones",
            conditions={
                "requires_top_position": True,
                "propagation_type": "vertical",
                "value": 1
            },
            confidence=1.0,
            size_invariant=True,
            examples=[{
                "grid_size": (len(ex['input']), len(ex['input'][0])),
                "source_positions": _find_source_positions(ex['input']),
                "preserved_source": True
            } for ex in examples]
        ))
    
    # Check for bottom row fill pattern
    if all(_has_bottom_row_fill(ex['output']) for ex in examples):
        meta_patterns.append(GridMetaPattern(
            name="bottom_row_fill",
            description="Bottom row is filled with ones",
            conditions={
                "required_value": 1,
                "position": "bottom_row",
                "complete_fill": True
            },
            confidence=1.0,
            size_invariant=True,
            examples=[{
                "grid_size": (len(ex['input']), len(ex['input'][0])),
                "row_index": len(ex['input']) - 1
            } for ex in examples]
        ))
    
    # Check for top row preservation
    if all(_preserves_top_row(ex['input'], ex['output']) 
           for ex in examples):
        meta_patterns.append(GridMetaPattern(
            name="top_row_preservation",
            description="Top row pattern remains unchanged",
            conditions={
                "preserved_region": "top_row",
                "exact_match": True
            },
            confidence=1.0,
            size_invariant=True,
            examples=[{
                "grid_size": (len(ex['input']), len(ex['input'][0])),
                "pattern": ex['input'][0]
            } for ex in examples]
        ))
    
    # Check for source preservation
    if all(_find_source_positions(ex['input']) == 
           [(i,j) for i,j in _find_ones_positions(ex['output']) 
            if i == 0] for ex in examples):
        meta_patterns.append(GridMetaPattern(
            name="source_pattern_preservation",
            description="Original ones act as sources and remain in position",
            conditions={
                "preserves_positions": True,
                "source_value": 1
            },
            confidence=1.0,
            size_invariant=True,
            examples=[{
                "grid_size": (len(ex['input']), len(ex['input'][0])),
                "source_positions": _find_source_positions(ex['input'])
            } for ex in examples]
        ))
    
    # Add path analysis
    paths = _analyze_paths(examples)
    if paths:
        meta_patterns.append(GridMetaPattern(
            name="value_propagation_paths",
            description="Values propagate along specific paths",
            conditions=paths,
            confidence=1.0,
            size_invariant=True,
            examples=[{
                "grid_size": (len(ex['input']), len(ex['input'][0])),
                "paths": _find_propagation_paths(ex['input'], ex['output'])
            } for ex in examples]
        ))
    
    return meta_patterns

def _analyze_paths(examples: List[Dict]) -> Optional[Dict]:
    """Analyze how values propagate through the grid"""
    paths = {}
    
    for ex in examples:
        input_grid, output_grid = ex['input'], ex['output']
        source_positions = _find_source_positions(input_grid)
        
        for pos in source_positions:
            path = _find_propagation_paths(input_grid, output_grid)
            path_type = _categorize_path_type(path)
            
            if path_type not in paths:
                paths[path_type] = []
            paths[path_type].append(path)
    
    if paths:
        return {
            'path_types': list(paths.keys()),
            'consistent': len(paths) == 1,
            'source_dependent': _is_source_dependent(paths)
        }
    return None

def _find_propagation_paths(input_grid: List[List[int]], 
                          output_grid: List[List[int]]) -> List[List[Tuple[int, int]]]:
    """Find paths along which values propagate"""
    paths = []
    source_positions = _find_source_positions(input_grid)
    
    for pos in source_positions:
        path = _trace_path(pos, output_grid)
        if path:
            paths.append(path)
    
    return paths

def _trace_path(start: Tuple[int, int], 
                grid: List[List[int]]) -> List[Tuple[int, int]]:
    """Trace a path of 1s starting from a position"""
    path = [start]
    current = start
    h, w = len(grid), len(grid[0])
    
    while current[0] < h - 1:  # Until we reach bottom
        next_pos = (current[0] + 1, current[1])  # Go down
        if grid[next_pos[0]][next_pos[1]] == 1:
            path.append(next_pos)
            current = next_pos
        else:
            break
            
    return path

def _categorize_path_type(path: List[Tuple[int, int]]) -> str:
    """Categorize the type of propagation path"""
    if not path:
        return "none"
    
    # Check if it's a straight vertical line
    if all(x[1] == path[0][1] for x in path):
        return "vertical"
    
    # Check if it's a diagonal
    if all(abs(path[i+1][1] - path[i][1]) == 1 
           for i in range(len(path)-1)):
        return "diagonal"
        
    return "complex"

def _is_source_dependent(paths: Dict[str, List]) -> bool:
    """Check if path behavior depends on source position"""
    if len(paths) == 1:
        path_type = next(iter(paths))
        if path_type == "vertical":
            return False  # Same behavior regardless of source
    return True

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