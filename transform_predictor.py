"""
Predict output grids based on transformation analysis
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from transform_analysis import TransformationAnalyzer
from grid_ops import GridOperations

class TransformationPredictor:
    def __init__(self):
        self.analyzer = TransformationAnalyzer()
        self.grid_ops = GridOperations()
        
    def predict_output(self, input_grid: np.ndarray, 
                      training_inputs: List[np.ndarray],
                      training_outputs: List[np.ndarray]) -> np.ndarray:
        """Predict output for new input based on training examples"""
        # Analyze all training pairs
        transforms = []
        for train_in, train_out in zip(training_inputs, training_outputs):
            analysis = {
                'value_mappings': self.analyzer.analyze_value_mappings(train_in, train_out),
                'object_transforms': self.analyzer.analyze_object_transformations(train_in, train_out),
                'spatial_transforms': self.analyzer.analyze_spatial_transformations(train_in, train_out)
            }
            transforms.append(analysis)
            
        # Find consistent transformations
        consistent = self._find_consistent_transforms(transforms)
        
        # Create predicted output grid
        prediction = self._apply_transforms(input_grid, consistent)
        
        return prediction
        
    def _find_consistent_transforms(self, transforms: List[Dict]) -> Dict:
        """Find transformations that are consistent across all training examples"""
        if not transforms:
            return {}
            
        consistent = {
            'value_mappings': {},
            'object_transforms': {},
            'spatial_transforms': {}
        }
        
        # Check value mappings
        first_mappings = transforms[0]['value_mappings']
        for val, mapping in first_mappings.items():
            consistent_mapping = True
            for t in transforms[1:]:
                if val not in t['value_mappings'] or t['value_mappings'][val] != mapping:
                    consistent_mapping = False
                    break
            if consistent_mapping:
                consistent['value_mappings'][val] = mapping
                
        # Check object transformations
        first_obj_trans = transforms[0]['object_transforms']
        if all(t['object_transforms']['object_count_change'] == 
              first_obj_trans['object_count_change'] for t in transforms[1:]):
            consistent['object_transforms']['object_count_change'] = \
                first_obj_trans['object_count_change']
                
        # Check for consistent object mapping types
        obj_mappings = []
        for mapping in first_obj_trans['object_mappings']:
            if len(mapping['matches']) == 1:
                transform = mapping['matches'][0]['transform']
                if transform['type'] != 'complex':
                    consistent_transform = True
                    for t in transforms[1:]:
                        found_match = False
                        for m in t['object_transforms']['object_mappings']:
                            if len(m['matches']) == 1 and \
                               m['matches'][0]['transform'] == transform:
                                found_match = True
                                break
                        if not found_match:
                            consistent_transform = False
                            break
                    if consistent_transform:
                        obj_mappings.append({
                            'input_value': mapping['input_object']['value'],
                            'transform': transform
                        })
        consistent['object_transforms']['mappings'] = obj_mappings
        
        # Check spatial transformations
        first_spatial = transforms[0]['spatial_transforms']
        if all(t['spatial_transforms']['global_transform'] == 
              first_spatial['global_transform'] for t in transforms[1:]):
            consistent['spatial_transforms']['global_transform'] = \
                first_spatial['global_transform']
                
        # Check relative position changes
        rel_pos_changes = []
        for rel_change in first_spatial['relative_positions']:
            consistent_change = True
            for t in transforms[1:]:
                found_match = False
                for other_change in t['spatial_transforms']['relative_positions']:
                    if (rel_change['objects'] == other_change['objects'] and
                        rel_change['from'] == other_change['from'] and
                        rel_change['to'] == other_change['to']):
                        found_match = True
                        break
                if not found_match:
                    consistent_change = False
                    break
            if consistent_change:
                rel_pos_changes.append(rel_change)
        consistent['spatial_transforms']['relative_positions'] = rel_pos_changes
        
        return consistent
        
    def _apply_transforms(self, input_grid: np.ndarray, transforms: Dict) -> np.ndarray:
        """Apply transformations to create predicted output"""
        prediction = input_grid.copy()
        
        # Apply global transform first
        global_trans = transforms['spatial_transforms'].get('global_transform', {'type': 'none'})
        if global_trans['type'] == 'rotation':
            prediction = np.rot90(prediction, k=global_trans['degrees'] // 90)
        elif global_trans['type'] == 'flip':
            prediction = np.flip(prediction, axis=0 if global_trans['axis'] == 'horizontal' else 1)
        elif global_trans['type'] == 'scale':
            prediction = np.kron(prediction, np.ones((global_trans['factor'],) * 2))
            
        # Apply value mappings
        for val, mapping in transforms['value_mappings'].items():
            mask = prediction == val
            if mapping['type'] == 'direct':
                prediction[mask] = mapping['to']
            elif mapping['type'] == 'conditional':
                for pos_type, new_val in mapping['conditions'].items():
                    type_mask = mask & np.array([
                        [self.analyzer._get_position_type((r,c), prediction.shape) == pos_type
                         for c in range(prediction.shape[1])]
                        for r in range(prediction.shape[0])
                    ])
                    prediction[type_mask] = new_val
                    
        # Apply object transformations
        objects = self.grid_ops.get_objects(prediction)
        for obj in objects:
            # Find matching transformation
            for mapping in transforms['object_transforms'].get('mappings', []):
                if mapping['input_value'] == obj['value']:
                    transform = mapping['transform']
                    obj_grid = self.grid_ops.get_object_grid(prediction, obj)
                    
                    if transform['type'] == 'value_change':
                        mask = obj_grid != 0
                        obj_grid[mask] = transform['to']
                    elif transform['type'] == 'scale':
                        obj_grid = np.kron(obj_grid, np.ones((transform['factor'],) * 2))
                    elif transform['type'] == 'rotation':
                        obj_grid = np.rot90(obj_grid, k=transform['degrees'] // 90)
                    elif transform['type'] == 'flip':
                        obj_grid = np.flip(obj_grid, 
                                         axis=0 if transform['axis'] == 'horizontal' else 1)
                                         
                    # Update region in prediction
                    r1, r2 = obj['min_r'], obj['max_r'] + 1
                    c1, c2 = obj['min_c'], obj['max_c'] + 1
                    if obj_grid.shape == (r2-r1, c2-c1):
                        prediction[r1:r2, c1:c2] = obj_grid
                        
        # Apply relative position changes
        for rel_change in transforms['spatial_transforms'].get('relative_positions', []):
            obj1_val, obj2_val = rel_change['objects']
            obj1_mask = prediction == obj1_val
            obj2_mask = prediction == obj2_val
            
            if np.any(obj1_mask) and np.any(obj2_mask):
                obj1_pos = np.mean(np.argwhere(obj1_mask), axis=0)
                obj2_pos = np.mean(np.argwhere(obj2_mask), axis=0)
                
                current_rel = {
                    'dx': obj2_pos[1] - obj1_pos[1],
                    'dy': obj2_pos[0] - obj1_pos[0]
                }
                
                if (current_rel['dx'] != rel_change['to']['dx'] or
                    current_rel['dy'] != rel_change['to']['dy']):
                    # Move obj2 to satisfy relationship
                    dx = rel_change['to']['dx'] - current_rel['dx']
                    dy = rel_change['to']['dy'] - current_rel['dy']
                    
                    new_prediction = prediction.copy()
                    new_prediction[obj2_mask] = 0
                    
                    # Calculate new positions
                    old_positions = np.argwhere(obj2_mask)
                    new_positions = old_positions + np.array([dy, dx])
                    
                    # Filter valid positions
                    valid = (new_positions >= 0).all(axis=1) & \
                           (new_positions < prediction.shape).all(axis=1)
                    
                    if valid.any():
                        new_positions = new_positions[valid]
                        new_prediction[new_positions[:,0], new_positions[:,1]] = obj2_val
                        prediction = new_prediction
                        
        return prediction