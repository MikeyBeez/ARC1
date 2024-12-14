"""
Analyze and predict transformations between input and output grids
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from grid_ops import GridOperations

class TransformationAnalyzer:
    def __init__(self):
        self.grid_ops = GridOperations()
        
    def analyze_value_mappings(self, input_grid: np.ndarray, output_grid: np.ndarray) -> Dict:
        """Analyze how values map between input and output"""
        mappings = {}
        input_values = self.grid_ops.count_values(input_grid)
        output_values = self.grid_ops.count_values(output_grid)
        
        # Look for consistent value transformations
        for in_val in input_values:
            if in_val == 0:  # Skip background
                continue
                
            mask = input_grid == in_val
            out_vals = output_grid[mask]
            unique_out, counts = np.unique(out_vals, return_counts=True)
            
            if len(unique_out) == 1:
                # Direct mapping found
                mappings[int(in_val)] = {
                    'type': 'direct',
                    'to': int(unique_out[0])
                }
            elif len(unique_out) > 1:
                # Check for conditional mapping
                positions = np.argwhere(input_grid == in_val)
                position_based = {}
                
                for pos, out_val in zip(positions, out_vals):
                    key = self._get_position_type(pos, input_grid.shape)
                    if key not in position_based:
                        position_based[key] = []
                    position_based[key].append(int(out_val))
                    
                # Check if position determines output value
                conditional = {}
                for pos_type, values in position_based.items():
                    if len(set(values)) == 1:
                        conditional[pos_type] = values[0]
                        
                if conditional:
                    mappings[int(in_val)] = {
                        'type': 'conditional',
                        'conditions': conditional
                    }
                else:
                    mappings[int(in_val)] = {
                        'type': 'complex',
                        'position_values': position_based
                    }
                    
        return mappings
        
    def analyze_object_transformations(self, input_grid: np.ndarray, output_grid: np.ndarray) -> Dict:
        """Analyze how objects transform between input and output"""
        input_objects = self.grid_ops.get_objects(input_grid)
        output_objects = self.grid_ops.get_objects(output_grid)
        
        transforms = {
            'object_count_change': len(output_objects) - len(input_objects),
            'object_mappings': []
        }
        
        # Try to match objects between input and output
        for in_obj in input_objects:
            matches = []
            in_grid = self.grid_ops.get_object_grid(input_grid, in_obj)
            
            for out_obj in output_objects:
                out_grid = self.grid_ops.get_object_grid(output_grid, out_obj)
                
                # Check different transformations
                transform = self._find_object_transform(in_grid, out_grid)
                if transform['type'] != 'none':
                    matches.append({
                        'output_object': out_obj,
                        'transform': transform
                    })
                    
            if matches:
                transforms['object_mappings'].append({
                    'input_object': in_obj,
                    'matches': matches
                })
                
        return transforms
        
    def analyze_spatial_transformations(self, input_grid: np.ndarray, output_grid: np.ndarray) -> Dict:
        """Analyze spatial relationships and transformations"""
        input_objects = self.grid_ops.get_objects(input_grid)
        output_objects = self.grid_ops.get_objects(output_grid)
        
        transforms = {
            'global_transform': self._find_global_transform(input_grid, output_grid),
            'relative_positions': []
        }
        
        # Analyze relative position changes between objects
        if len(input_objects) > 1 and len(input_objects) == len(output_objects):
            for i, in_obj1 in enumerate(input_objects[:-1]):
                for in_obj2 in input_objects[i+1:]:
                    in_rel = self._get_relative_position(in_obj1, in_obj2)
                    
                    # Find corresponding objects in output
                    out_obj1 = self._find_matching_object(in_obj1, output_objects)
                    out_obj2 = self._find_matching_object(in_obj2, output_objects)
                    
                    if out_obj1 and out_obj2:
                        out_rel = self._get_relative_position(out_obj1, out_obj2)
                        
                        if in_rel != out_rel:
                            transforms['relative_positions'].append({
                                'objects': [in_obj1['value'], in_obj2['value']],
                                'from': in_rel,
                                'to': out_rel
                            })
                            
        return transforms
        
    def _get_position_type(self, pos: Tuple[int, int], shape: Tuple[int, int]) -> str:
        """Get position type (corner, edge, interior) for a coordinate"""
        r, c = pos
        h, w = shape
        
        if (r in (0, h-1)) and (c in (0, w-1)):
            return 'corner'
        elif r in (0, h-1) or c in (0, w-1):
            return 'edge'
        else:
            return 'interior'
            
    def _find_object_transform(self, obj1: np.ndarray, obj2: np.ndarray) -> Dict:
        """Find transformation between two object grids"""
        # Check for size change
        h1, w1 = obj1.shape
        h2, w2 = obj2.shape
        
        if h1 == h2 and w1 == w2:
            # Check for value change
            if np.array_equal(obj1, obj2):
                return {'type': 'none'}
            else:
                unique1 = np.unique(obj1[obj1 != 0])
                unique2 = np.unique(obj2[obj2 != 0])
                if len(unique1) == 1 and len(unique2) == 1:
                    return {
                        'type': 'value_change',
                        'from': int(unique1[0]),
                        'to': int(unique2[0])
                    }
                    
        # Check for scaling
        if h2 % h1 == 0 and w2 % w1 == 0:
            scale_h = h2 // h1
            scale_w = w2 // w1
            if scale_h == scale_w:
                return {
                    'type': 'scale',
                    'factor': int(scale_h)
                }
                
        # Check for rotation
        for k in range(1, 4):
            rotated = np.rot90(obj1, k=k)
            if rotated.shape == obj2.shape and np.array_equal(rotated != 0, obj2 != 0):
                return {
                    'type': 'rotation',
                    'degrees': int(k * 90)
                }
                
        # Check for flip
        flipped_h = np.flip(obj1, axis=0)
        flipped_v = np.flip(obj1, axis=1)
        
        if np.array_equal(flipped_h != 0, obj2 != 0):
            return {'type': 'flip', 'axis': 'horizontal'}
        elif np.array_equal(flipped_v != 0, obj2 != 0):
            return {'type': 'flip', 'axis': 'vertical'}
            
        return {'type': 'complex'}
        
    def _find_global_transform(self, grid1: np.ndarray, grid2: np.ndarray) -> Dict:
        """Find global transformation between grids"""
        h1, w1 = grid1.shape
        h2, w2 = grid2.shape
        
        if h1 == h2 and w1 == w2:
            # Check for rotation
            for k in range(1, 4):
                if np.array_equal(np.rot90(grid1, k=k), grid2):
                    return {'type': 'rotation', 'degrees': int(k * 90)}
                    
            # Check for flip
            if np.array_equal(np.flip(grid1, axis=0), grid2):
                return {'type': 'flip', 'axis': 'horizontal'}
            elif np.array_equal(np.flip(grid1, axis=1), grid2):
                return {'type': 'flip', 'axis': 'vertical'}
                
        # Check for scaling
        if h2 % h1 == 0 and w2 % w1 == 0:
            scale_h = h2 // h1
            scale_w = w2 // w1
            if scale_h == scale_w:
                return {'type': 'scale', 'factor': int(scale_h)}
                
        return {'type': 'none'}
        
    def _get_relative_position(self, obj1: Dict, obj2: Dict) -> Dict:
        """Get relative position between two objects"""
        center1 = obj1['center']
        center2 = obj2['center']
        
        dx = center2[1] - center1[1]
        dy = center2[0] - center1[0]
        
        return {
            'dx': float(dx),
            'dy': float(dy),
            'distance': float(np.sqrt(dx*dx + dy*dy)),
            'angle': float(np.arctan2(dy, dx))
        }
        
    def _find_matching_object(self, obj: Dict, objects: List[Dict]) -> Optional[Dict]:
        """Find matching object based on properties"""
        best_match = None
        best_score = 0
        
        for other in objects:
            score = 0
            # Match by value
            if obj['value'] == other['value']:
                score += 1
            # Match by size
            if obj['size'] == other['size']:
                score += 1
            # Match by dimensions
            if obj['dimensions'] == other['dimensions']:
                score += 1
                
            if score > best_score:
                best_score = score
                best_match = other
                
        return best_match if best_score > 0 else None