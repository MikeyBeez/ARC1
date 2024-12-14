"""
Comprehensive library of reasoning functions for ARC challenges
"""

import numpy as np
from typing import List, Dict, Optional, Tuple, Union

class GridReasoning:
    @staticmethod
    def find_objects(grid: List[List[int]]) -> List[Dict]:
        """Find distinct connected objects and their properties"""
        grid = np.array(grid)
        objects = []
        seen = set()
        
        def get_object(r: int, c: int, value: int) -> List[Tuple[int, int]]:
            if (r < 0 or r >= grid.shape[0] or 
                c < 0 or c >= grid.shape[1] or 
                grid[r,c] != value or 
                (r,c) in seen):
                return []
            
            seen.add((r,c))
            coords = [(r,c)]
            # Check 4-connected neighbors
            for nr, nc in [(r+1,c), (r-1,c), (r,c+1), (r,c-1)]:
                coords.extend(get_object(nr, nc, value))
            return coords
        
        # Find all objects
        for r in range(grid.shape[0]):
            for c in range(grid.shape[1]):
                if (r,c) not in seen and grid[r,c] != 0:
                    coords = get_object(r, c, grid[r,c])
                    if coords:
                        coords = np.array(coords)
                        objects.append({
                            'value': int(grid[r,c]),
                            'coords': coords.tolist(),
                            'min_r': int(coords[:,0].min()),
                            'max_r': int(coords[:,0].max()),
                            'min_c': int(coords[:,1].min()),
                            'max_c': int(coords[:,1].max()),
                            'size': len(coords)
                        })
        return objects

    @staticmethod
    def get_object_relations(grid: Union[List[List[int]], List[Dict]]) -> List[Dict]:
        """Analyze spatial relations between objects"""
        # Convert grid to objects if needed
        if isinstance(grid, list) and isinstance(grid[0], list):
            objects = GridReasoning.find_objects(grid)
        else:
            objects = grid
            
        relations = []
        for i, obj1 in enumerate(objects):
            for j, obj2 in enumerate(objects[i+1:], i+1):
                # Calculate relative positions
                vertical_rel = "same_row" if obj1['min_r'] == obj2['min_r'] else (
                    "above" if obj1['max_r'] < obj2['min_r'] else 
                    "below" if obj1['min_r'] > obj2['max_r'] else 
                    "overlaps_vertical"
                )
                
                horizontal_rel = "same_column" if obj1['min_c'] == obj2['min_c'] else (
                    "left" if obj1['max_c'] < obj2['min_c'] else
                    "right" if obj1['min_c'] > obj2['max_c'] else
                    "overlaps_horizontal"
                )
                
                # Calculate distances
                vertical_dist = abs((obj1['min_r'] + obj1['max_r'])//2 - 
                                 (obj2['min_r'] + obj2['max_r'])//2)
                horizontal_dist = abs((obj1['min_c'] + obj1['max_c'])//2 - 
                                   (obj2['min_c'] + obj2['max_c'])//2)
                
                relations.append({
                    'obj1_idx': i,
                    'obj2_idx': j,
                    'vertical_relation': vertical_rel,
                    'horizontal_relation': horizontal_rel,
                    'vertical_distance': vertical_dist,
                    'horizontal_distance': horizontal_dist,
                    'same_color': obj1['value'] == obj2['value'],
                    'size_ratio': obj1['size'] / obj2['size'] if obj2['size'] > 0 else float('inf')
                })
                
        return relations

    @staticmethod 
    def detect_patterns(grid: List[List[int]]) -> Dict:
        """Detect various patterns in the grid"""
        grid = np.array(grid)
        patterns = {
            'repetitions': {},
            'symmetries': [],
            'gradients': [],
            'sequences': []
        }
        
        # Check for value repetitions
        unique, counts = np.unique(grid, return_counts=True)
        patterns['repetitions'] = {int(v): int(c) for v, c in zip(unique, counts)}
        
        # Check for symmetries
        if np.array_equal(grid, np.flip(grid, 0)):
            patterns['symmetries'].append('horizontal')
        if np.array_equal(grid, np.flip(grid, 1)):
            patterns['symmetries'].append('vertical')
        if np.array_equal(grid, np.rot90(grid)):
            patterns['symmetries'].append('90_degree')
        if np.array_equal(grid, np.rot90(grid, 2)):
            patterns['symmetries'].append('180_degree')
            
        # Check for gradients
        for row in grid:
            if len(row) > 1:
                if np.all(row[1:] >= row[:-1]):
                    patterns['gradients'].append('increasing_row')
                if np.all(row[1:] <= row[:-1]):
                    patterns['gradients'].append('decreasing_row')
                
        for col in grid.T:
            if len(col) > 1:
                if np.all(col[1:] >= col[:-1]):
                    patterns['gradients'].append('increasing_column')
                if np.all(col[1:] <= col[:-1]):
                    patterns['gradients'].append('decreasing_column')
                
        # Look for arithmetic/geometric sequences
        for row in grid:
            if len(row) > 1:
                diffs = np.diff(row)
                if len(set(diffs)) == 1:
                    patterns['sequences'].append({
                        'type': 'arithmetic',
                        'difference': int(diffs[0])
                    })
                
                nonzero_mask = row != 0
                if np.any(nonzero_mask):
                    nonzero_values = row[nonzero_mask]
                    if len(nonzero_values) > 1:
                        ratios = nonzero_values[1:] / nonzero_values[:-1]
                        if len(set(ratios)) == 1:
                            patterns['sequences'].append({
                                'type': 'geometric',
                                'ratio': float(ratios[0])
                            })
        return patterns

    @staticmethod
    def analyze_transformations(input_grid: List[List[int]], output_grid: List[List[int]]) -> Dict:
        """Analyze transformations between input and output grids"""
        in_grid = np.array(input_grid)
        out_grid = np.array(output_grid)
        
        transforms = {
            'dimension_change': None,
            'value_mapping': {},
            'operations': [],
            'object_changes': []
        }
        
        # Check dimension changes
        transforms['dimension_change'] = {
            'rows': out_grid.shape[0] - in_grid.shape[0],
            'cols': out_grid.shape[1] - in_grid.shape[1]
        }
        
        # Analyze value mappings
        for val in np.unique(in_grid):
            mask = (in_grid == val)
            if mask.any():
                out_vals, counts = np.unique(out_grid[mask], return_counts=True)
                if len(out_vals) == 1:
                    transforms['value_mapping'][int(val)] = int(out_vals[0])
                    
        # Check for common operations
        # Rotation
        for k in [1, 2, 3]:
            if np.array_equal(out_grid, np.rot90(in_grid, k)):
                transforms['operations'].append(f'rotation_{k*90}')
                
        # Flips
        if np.array_equal(out_grid, np.flip(in_grid, 0)):
            transforms['operations'].append('horizontal_flip')
        if np.array_equal(out_grid, np.flip(in_grid, 1)):
            transforms['operations'].append('vertical_flip')
            
        # Object-level changes
        in_objects = GridReasoning.find_objects(input_grid)
        out_objects = GridReasoning.find_objects(output_grid)
        
        if len(in_objects) == len(out_objects):
            for in_obj, out_obj in zip(in_objects, out_objects):
                change = {
                    'size_change': out_obj['size'] - in_obj['size'],
                    'value_change': out_obj['value'] - in_obj['value'],
                    'position_change': (
                        out_obj['min_r'] - in_obj['min_r'],
                        out_obj['min_c'] - in_obj['min_c']
                    )
                }
                transforms['object_changes'].append(change)
                
        return transforms

    @staticmethod
    def predict_output(training_results: List[Dict], test_result: Dict, test_input: List[List[int]]) -> List[List[int]]:
        """Generate prediction for test input based on analyzed patterns"""
        if not training_results or not test_input:
            return None
            
        # Convert input to numpy array for processing
        test_grid = np.array(test_input)
        prediction = test_grid.copy()
        
        try:
            # Collect consistent transformations across training examples
            transforms = []
            for result in training_results:
                for func_name, func_result in result.items():
                    if func_name == 'analyze_transformations':
                        transforms.append(func_result)
                        
            if not transforms:
                return test_input  # No transformation data available
                
            # Apply consistent transformations
            value_maps = {}
            operations = []
            
            # Extract consistent patterns
            for t in transforms:
                if 'value_mapping' in t:
                    for val, mapped in t['value_mapping'].items():
                        if val not in value_maps:
                            value_maps[val] = mapped
                        elif value_maps[val] != mapped:
                            value_maps.pop(val)
                            
                if 'operations' in t:
                    for op in t['operations']:
                        if op not in operations:
                            operations.append(op)
                            
            # Apply value mappings
            for val, mapped in value_maps.items():
                prediction[test_grid == val] = mapped
                
            # Apply operations in sequence
            for op in operations:
                if 'rotation' in op:
                    k = int(op.split('_')[1]) // 90
                    prediction = np.rot90(prediction, k)
                elif op == 'horizontal_flip':
                    prediction = np.flip(prediction, 0)
                elif op == 'vertical_flip':
                    prediction = np.flip(prediction, 1)
                    
            return prediction.tolist()
            
        except Exception as e:
            print(f"Prediction error: {str(e)}")
            return None