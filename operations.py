"""
Basic grid operations library for ARC testing
"""

import numpy as np
from typing import List, Tuple, Optional

def rotate_grid(grid: List[List[int]], k: int = 1) -> List[List[int]]:
    """Rotate grid k times 90 degrees clockwise"""
    return np.rot90(np.array(grid), k=(-k)).tolist()

def flip_grid(grid: List[List[int]], axis: int = 0) -> List[List[int]]:
    """Flip grid along axis (0=horizontal, 1=vertical)"""
    return np.flip(np.array(grid), axis=axis).tolist()

def fill_pattern(grid: List[List[int]], pattern: int) -> List[List[int]]:
    """Fill grid with pattern value where non-zero"""
    result = np.array(grid)
    result[result != 0] = pattern
    return result.tolist()

def extract_pattern(input_grid: List[List[int]], output_grid: List[List[int]]) -> Optional[dict]:
    """Extract transformation pattern between input and output"""
    input_arr = np.array(input_grid)
    output_arr = np.array(output_grid)
    
    patterns = {}
    for val in np.unique(input_arr):
        mask = (input_arr == val)
        if mask.any():
            corresponding_vals = output_arr[mask]
            if len(np.unique(corresponding_vals)) == 1:
                patterns[val] = corresponding_vals[0]
                
    return patterns if patterns else None

def apply_pattern(grid: List[List[int]], pattern: dict) -> List[List[int]]:
    """Apply transformation pattern to grid"""
    result = np.array(grid)
    for in_val, out_val in pattern.items():
        result[result == in_val] = out_val
    return result.tolist()

def get_shape_dimensions(grid: List[List[int]], target_val: int = 1) -> Tuple[int, int]:
    """Get dimensions of shape marked by target value"""
    arr = np.array(grid)
    if not (arr == target_val).any():
        return (0, 0)
    rows = np.any(arr == target_val, axis=1)
    cols = np.any(arr == target_val, axis=0)
    return (np.sum(rows), np.sum(cols))

def find_objects(grid: List[List[int]]) -> List[Tuple[int, List[Tuple[int, int]]]]:
    """Find distinct objects (connected components) in grid"""
    arr = np.array(grid)
    objects = []
    seen = set()
    
    def flood_fill(i: int, j: int, val: int) -> List[Tuple[int, int]]:
        if (i < 0 or i >= arr.shape[0] or 
            j < 0 or j >= arr.shape[1] or 
            arr[i,j] != val or 
            (i,j) in seen):
            return []
            
        seen.add((i,j))
        points = [(i,j)]
        
        # Check neighbors
        for ni, nj in [(i+1,j), (i-1,j), (i,j+1), (i,j-1)]:
            points.extend(flood_fill(ni, nj, val))
            
        return points
        
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            if (i,j) not in seen and arr[i,j] != 0:
                obj_points = flood_fill(i, j, arr[i,j])
                if obj_points:
                    objects.append((arr[i,j], obj_points))
                    
    return objects

def analyze_grid_changes(before: List[List[int]], after: List[List[int]]) -> dict:
    """Analyze changes between two grids"""
    before_arr = np.array(before)
    after_arr = np.array(after)
    
    changes = {
        'dimension_change': (
            after_arr.shape[0] - before_arr.shape[0],
            after_arr.shape[1] - before_arr.shape[1]
        ),
        'value_changes': {},
        'object_count_before': len(find_objects(before)),
        'object_count_after': len(find_objects(after))
    }
    
    # Analyze value changes
    for val in np.unique(before_arr):
        mask = (before_arr == val)
        if mask.any():
            after_vals, counts = np.unique(
                after_arr[mask] if mask.shape == after_arr.shape else [],
                return_counts=True
            )
            if len(after_vals) == 1:
                changes['value_changes'][int(val)] = int(after_vals[0])
                
    return changes

def detect_symmetry(grid: List[List[int]]) -> List[str]:
    """Detect symmetries in grid"""
    arr = np.array(grid)
    symmetries = []
    
    # Horizontal symmetry
    if np.array_equal(arr, np.flip(arr, axis=0)):
        symmetries.append('horizontal')
        
    # Vertical symmetry
    if np.array_equal(arr, np.flip(arr, axis=1)):
        symmetries.append('vertical')
        
    # Rotational symmetry
    if np.array_equal(arr, np.rot90(arr)):
        symmetries.append('rotational_90')
    elif np.array_equal(arr, np.rot90(arr, k=2)):
        symmetries.append('rotational_180')
        
    return symmetries