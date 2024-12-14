"""
Enhanced pattern analysis for ARC tasks with spatial motion detection.
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

def _find_line_patterns(grid: List[List[int]]) -> List[Dict]:
    """Find horizontal and vertical lines in the grid"""
    h, w = len(grid), len(grid[0])
    lines = []
    
    # Find horizontal lines
    for i in range(h):
        line_vals = grid[i]
        if all(v == line_vals[0] for v in line_vals):
            lines.append({
                'type': 'horizontal',
                'value': line_vals[0],
                'row': i,
                'length': w,
                'complete': True,
                'position': 'top' if i == 0 else 'middle' if i < h-1 else 'bottom'
            })
    
    # Find vertical lines
    for j in range(w):
        col_vals = [grid[i][j] for i in range(h)]
        if all(v == col_vals[0] for v in col_vals):
            lines.append({
                'type': 'vertical',
                'value': col_vals[0],
                'column': j,
                'length': h,
                'complete': True,
                'position': 'left' if j == 0 else 'middle' if j < w-1 else 'right'
            })
    
    return lines

def _analyze_spatial_movement(input_grid: List[List[int]], 
                            output_grid: List[List[int]]) -> List[Dict]:
    """Analyze how patterns move in the grid"""
    input_lines = _find_line_patterns(input_grid)
    output_lines = _find_line_patterns(output_grid)
    movements = []
    
    for in_line in input_lines:
        # Find matching lines in output (same type, value, length)
        matches = [
            out_line for out_line in output_lines
            if (out_line['type'] == in_line['type'] and
                out_line['value'] == in_line['value'] and
                out_line['length'] == in_line['length'])
        ]
        
        if matches:
            for match in matches:
                movement = {
                    'pattern_type': in_line['type'],
                    'value': in_line['value'],
                    'length': in_line['length'],
                    'from_position': in_line['position'],
                    'to_position': match['position']
                }
                
                if in_line['type'] == 'horizontal':
                    movement['from_row'] = in_line['row']
                    movement['to_row'] = match['row']
                    movement['movement'] = 'vertical'
                    movement['direction'] = 'down' if match['row'] > in_line['row'] else 'up'
                else:  # vertical
                    movement['from_col'] = in_line['column']
                    movement['to_col'] = match['column']
                    movement['movement'] = 'horizontal'
                    movement['direction'] = 'right' if match['column'] > in_line['column'] else 'left'
                    
                movements.append(movement)
    
    return movements

def _find_region_movements(input_grid: List[List[int]], 
                         output_grid: List[List[int]]) -> List[Dict]:
    """Find how regions of similar values move"""
    h, w = len(input_grid), len(input_grid[0])
    movements = []
    
    # Find regions in input
    input_regions = _find_connected_regions(input_grid)
    output_regions = _find_connected_regions(output_grid)
    
    # Match regions by size and value
    for in_region in input_regions:
        matches = [
            out_region for out_region in output_regions
            if (out_region['value'] == in_region['value'] and
                len(out_region['positions']) == len(in_region['positions']))
        ]
        
        if matches:
            for match in matches:
                # Calculate movement vector
                in_center = _calculate_region_center(in_region['positions'])
                out_center = _calculate_region_center(match['positions'])
                
                movements.append({
                    'value': in_region['value'],
                    'size': len(in_region['positions']),
                    'from_center': in_center,
                    'to_center': out_center,
                    'displacement': (
                        out_center[0] - in_center[0],
                        out_center[1] - in_center[1]
                    ),
                    'preserves_shape': _same_shape(
                        in_region['positions'], 
                        match['positions']
                    )
                })
    
    return movements

def _find_connected_regions(grid: List[List[int]]) -> List[Dict]:
    """Find connected regions of the same value"""
    h, w = len(grid), len(grid[0])
    visited = set()
    regions = []
    
    def dfs(i: int, j: int, value: int) -> Set[Tuple[int, int]]:
        if (i < 0 or i >= h or j < 0 or j >= w or
            (i,j) in visited or grid[i][j] != value):
            return set()
            
        positions = {(i,j)}
        visited.add((i,j))
        
        # Check all 4 directions
        for ni, nj in [(i+1,j), (i-1,j), (i,j+1), (i,j-1)]:
            positions.update(dfs(ni, nj, value))
            
        return positions
    
    # Find all regions
    for i in range(h):
        for j in range(w):
            if (i,j) not in visited:
                positions = dfs(i, j, grid[i][j])
                if positions:
                    regions.append({
                        'value': grid[i][j],
                        'positions': positions
                    })
    
    return regions

def _calculate_region_center(positions: Set[Tuple[int, int]]) -> Tuple[float, float]:
    """Calculate center of mass for a region"""
    if not positions:
        return (0, 0)
    return (
        sum(i for i,j in positions) / len(positions),
        sum(j for i,j in positions) / len(positions)
    )

def _same_shape(pos1: Set[Tuple[int, int]], 
                pos2: Set[Tuple[int, int]]) -> bool:
    """Check if two sets of positions form the same shape"""
    if len(pos1) != len(pos2):
        return False
        
    # Normalize positions to origin
    min_i1 = min(i for i,j in pos1)
    min_j1 = min(j for i,j in pos1)
    shape1 = {(i-min_i1, j-min_j1) for i,j in pos1}
    
    min_i2 = min(i for i,j in pos2)
    min_j2 = min(j for i,j in pos2)
    shape2 = {(i-min_i2, j-min_j2) for i,j in pos2}
    
    return shape1 == shape2

def extract_meta_patterns(examples: List[Dict]) -> List[GridMetaPattern]:
    """Extract high-level patterns across multiple examples"""
    meta_patterns = []
    
    # Analyze spatial movements in each example
    all_movements = [
        _analyze_spatial_movement(ex['input'], ex['output'])
        for ex in examples
    ]
    
    # Analyze region movements
    all_region_movements = [
        _find_region_movements(ex['input'], ex['output'])
        for ex in examples
    ]
    
    # Look for consistent movement patterns
    if all_movements and all(movements for movements in all_movements):
        common_features = {
            'pattern_types': set(),
            'directions': set(),
            'movements': set()
        }
        
        for movements in all_movements:
            for m in movements:
                common_features['pattern_types'].add(m['pattern_type'])
                common_features['directions'].add(m['direction'])
                common_features['movements'].add(m['movement'])
        
        meta_patterns.append(GridMetaPattern(
            name="spatial_movement_pattern",
            description="Patterns move in consistent directions",
            conditions={
                'pattern_types': list(common_features['pattern_types']),
                'directions': list(common_features['directions']),
                'movements': list(common_features['movements'])
            },
            confidence=1.0,
            size_invariant=True,
            examples=[{
                'grid_size': (len(ex['input']), len(ex['input'][0])),
                'movements': movs
            } for ex, movs in zip(examples, all_movements)]
        ))
    
    # Look for region movement patterns
    if all_region_movements and all(movements for movements in all_region_movements):
        meta_patterns.append(GridMetaPattern(
            name="region_movement_pattern",
            description="Connected regions move while preserving their shape",
            conditions={
                'preserves_shape': all(
                    m['preserves_shape']
                    for movements in all_region_movements
                    for m in movements
                ),
                'consistent_displacement': len(set(
                    m['displacement']
                    for movements in all_region_movements
                    for m in movements
                )) == 1
            },
            confidence=1.0,
            size_invariant=True,
            examples=[{
                'grid_size': (len(ex['input']), len(ex['input'][0])),
                'movements': movs
            } for ex, movs in zip(examples, all_region_movements)]
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