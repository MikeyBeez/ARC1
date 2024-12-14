"""
Enhanced pattern analysis for ARC tasks with checkerboard pattern detection.
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

def _is_checkerboard(grid: List[List[int]]) -> bool:
    """Check if grid has checkerboard pattern of 0s and 1s"""
    h, w = len(grid), len(grid[0])
    
    # Check each position against expected value
    for i in range(h):
        for j in range(w):
            expected = (i + j) % 2
            if grid[i][j] == expected:
                continue
            if grid[i][j] == 1 - expected:
                continue
            return False
    return True

def _is_inverted_checkerboard(input_grid: List[List[int]], 
                             output_grid: List[List[int]]) -> bool:
    """Check if output is inverted checkerboard of input"""
    h, w = len(input_grid), len(input_grid[0])
    
    for i in range(h):
        for j in range(w):
            if input_grid[i][j] == output_grid[i][j]:
                return False
    return True

def _get_pattern_type(grid: List[List[int]]) -> str:
    """Identify the type of pattern in the grid"""
    if _is_checkerboard(grid):
        return "checkerboard"
    return "other"

def _analyze_pattern_transformation(input_grid: List[List[int]], 
                                  output_grid: List[List[int]]) -> Dict:
    """Analyze how pattern transforms between input and output"""
    input_type = _get_pattern_type(input_grid)
    output_type = _get_pattern_type(output_grid)
    
    transform = {
        "input_pattern": input_type,
        "output_pattern": output_type,
        "inverted": _is_inverted_checkerboard(input_grid, output_grid),
        "preserves_structure": input_type == output_type
    }
    
    # Add alternation analysis if it's checkerboard
    if input_type == "checkerboard":
        transform["alternation_preserved"] = _check_alternation_preserved(
            input_grid, output_grid)
        
    return transform

def _check_alternation_preserved(input_grid: List[List[int]], 
                               output_grid: List[List[int]]) -> bool:
    """Check if alternating pattern is preserved even if values change"""
    h, w = len(input_grid), len(input_grid[0])
    
    for i in range(h):
        for j in range(w):
            if i > 0 and input_grid[i][j] == input_grid[i-1][j] and \
               output_grid[i][j] == output_grid[i-1][j]:
                return False
            if j > 0 and input_grid[i][j] == input_grid[i][j-1] and \
               output_grid[i][j] == output_grid[i][j-1]:
                return False
    return True

def _find_corner_pattern(grid: List[List[int]]) -> str:
    """Identify pattern in corners"""
    corners = [
        grid[0][0],
        grid[0][-1],
        grid[-1][0],
        grid[-1][-1]
    ]
    if all(c == corners[0] for c in corners):
        return f"all_{corners[0]}"
    if corners[0] == corners[-1] and corners[1] == corners[2]:
        return "diagonal_symmetric"
    return "other"

def extract_meta_patterns(examples: List[Dict]) -> List[GridMetaPattern]:
    """Extract high-level patterns across multiple examples"""
    meta_patterns = []
    
    # Check for checkerboard pattern
    if all(_is_checkerboard(ex['input']) for ex in examples):
        transforms = [_analyze_pattern_transformation(ex['input'], ex['output']) 
                     for ex in examples]
        if all(t["inverted"] for t in transforms):
            meta_patterns.append(GridMetaPattern(
                name="checkerboard_inversion",
                description="Checkerboard pattern inverts while maintaining structure",
                conditions={
                    "input_type": "checkerboard",
                    "output_type": "checkerboard",
                    "preserves_alternation": True,
                    "inverts_values": True
                },
                confidence=1.0,
                size_invariant=True,
                examples=[{
                    "grid_size": (len(ex['input']), len(ex['input'][0])),
                    "corner_pattern": _find_corner_pattern(ex['input']),
                    "inverted_corner_pattern": _find_corner_pattern(ex['output'])
                } for ex in examples]
            ))
    
    # Check for value preservation pattern
    preserved_positions = []
    for ex in examples:
        positions = [(i, j) for i in range(len(ex['input'])) 
                    for j in range(len(ex['input'][0]))
                    if ex['input'][i][j] == ex['output'][i][j]]
        preserved_positions.append(positions)
    
    if preserved_positions and all(preserved_positions):
        meta_patterns.append(GridMetaPattern(
            name="value_preservation",
            description="Certain positions preserve their values",
            conditions={
                "preserved_count": len(preserved_positions[0]),
                "position_dependent": True
            },
            confidence=1.0,
            size_invariant=True,
            examples=[{
                "grid_size": (len(ex['input']), len(ex['input'][0])),
                "preserved_positions": positions
            } for ex, positions in zip(examples, preserved_positions)]
        ))
    
    # Check for alternation preservation
    if all(_check_alternation_preserved(ex['input'], ex['output']) 
           for ex in examples):
        meta_patterns.append(GridMetaPattern(
            name="alternation_preservation",
            description="Adjacent cells maintain different values",
            conditions={
                "horizontal_alternation": True,
                "vertical_alternation": True
            },
            confidence=1.0,
            size_invariant=True,
            examples=[{
                "grid_size": (len(ex['input']), len(ex['input'][0]))
            } for ex in examples]
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