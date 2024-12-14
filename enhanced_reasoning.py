"""
Enhanced reasoning library combining pattern detection, hierarchy analysis, and transformation prediction
"""

import numpy as np
from typing import Dict, List, Optional, Union
from grid_ops import GridOperations
from pattern_testing import PatternTester
from transform_analysis import TransformationAnalyzer
from transform_predictor import TransformationPredictor
from pattern_hierarchy import PatternHierarchy

class EnhancedReasoning:
    def __init__(self):
        self.grid_ops = GridOperations()
        self.pattern_tester = PatternTester()
        self.transform_analyzer = TransformationAnalyzer()
        self.predictor = TransformationPredictor()
        self.hierarchy = PatternHierarchy()
        
    def analyze_grid(self, grid: List[List[int]]) -> Dict:
        """Analyze a single grid with hierarchical pattern analysis"""
        grid = np.array(grid)
        
        # Get basic grid properties
        properties = self.grid_ops.get_grid_properties(grid)
        
        # Find objects and their relationships
        objects = self.grid_ops.get_objects(grid)
        
        # Detect patterns
        patterns = self.pattern_tester.run_all_tests(grid)
        
        # Analyze pattern hierarchy
        hierarchy = self.hierarchy.analyze_pattern_relationships(
            patterns,
            {}  # No transformation data for single grid
        )
        
        return {
            'properties': properties,
            'objects': objects,
            'patterns': patterns,
            'pattern_hierarchy': hierarchy
        }
        
    def analyze_transform(self, input_grid: List[List[int]], 
                         output_grid: List[List[int]]) -> Dict:
        """Analyze transformation between input and output with pattern hierarchy"""
        input_grid = np.array(input_grid)
        output_grid = np.array(output_grid)
        
        # Analyze value mappings
        value_mappings = self.transform_analyzer.analyze_value_mappings(
            input_grid, output_grid
        )
        
        # Analyze object transformations
        object_transforms = self.transform_analyzer.analyze_object_transformations(
            input_grid, output_grid
        )
        
        # Analyze spatial transformations
        spatial_transforms = self.transform_analyzer.analyze_spatial_transformations(
            input_grid, output_grid
        )
        
        # Get input and output patterns
        input_patterns = self.pattern_tester.run_all_tests(input_grid)
        output_patterns = self.pattern_tester.run_all_tests(output_grid)
        
        # Analyze pattern hierarchies
        transform_data = {
            'value_mappings': value_mappings,
            'object_transforms': object_transforms,
            'spatial_transforms': spatial_transforms
        }
        
        input_hierarchy = self.hierarchy.analyze_pattern_relationships(
            input_patterns,
            transform_data
        )
        
        output_hierarchy = self.hierarchy.analyze_pattern_relationships(
            output_patterns,
            transform_data
        )
        
        return {
            'value_mappings': value_mappings,
            'object_transforms': object_transforms,
            'spatial_transforms': spatial_transforms,
            'input_hierarchy': input_hierarchy,
            'output_hierarchy': output_hierarchy,
            'meta_patterns': self._analyze_hierarchy_changes(
                input_hierarchy,
                output_hierarchy,
                transform_data
            )
        }
        
    def _analyze_hierarchy_changes(self,
                                 input_hierarchy: Dict,
                                 output_hierarchy: Dict,
                                 transform_data: Dict) -> Dict:
        """Analyze how pattern hierarchies change during transformation"""
        changes = {
            'preserved_patterns': [],
            'modified_patterns': [],
            'new_patterns': [],
            'lost_patterns': []
        }
        
        # Helper function to compare patterns
        def patterns_match(p1: Dict, p2: Dict) -> bool:
            return (p1['type'] == p2['type'] and 
                   p1['properties'] == p2['properties'])
        
        # Check each level
        for level in ['atomic', 'composite', 'structural', 'meta']:
            input_patterns = input_hierarchy[level]
            output_patterns = output_hierarchy[level]
            
            # Find preserved patterns
            for in_p in input_patterns:
                for out_p in output_patterns:
                    if patterns_match(in_p, out_p):
                        changes['preserved_patterns'].append({
                            'pattern': in_p,
                            'level': level
                        })
                        break
                        
            # Find modified patterns
            for in_p in input_patterns:
                for out_p in output_patterns:
                    if in_p['type'] == out_p['type'] and not patterns_match(in_p, out_p):
                        changes['modified_patterns'].append({
                            'from': in_p,
                            'to': out_p,
                            'level': level,
                            'changes': self._compare_pattern_properties(in_p, out_p)
                        })
                        
            # Find new patterns
            for out_p in output_patterns:
                if not any(p['type'] == out_p['type'] for p in input_patterns):
                    changes['new_patterns'].append({
                        'pattern': out_p,
                        'level': level
                    })
                    
            # Find lost patterns
            for in_p in input_patterns:
                if not any(p['type'] == in_p['type'] for p in output_patterns):
                    changes['lost_patterns'].append({
                        'pattern': in_p,
                        'level': level
                    })
                    
        return changes
        
    def _compare_pattern_properties(self, p1: Dict, p2: Dict) -> Dict:
        """Compare properties of two patterns to identify changes"""
        changes = {}
        
        # Compare all properties
        all_keys = set(p1['properties'].keys()) | set(p2['properties'].keys())
        
        for key in all_keys:
            v1 = p1['properties'].get(key)
            v2 = p2['properties'].get(key)
            
            if v1 != v2:
                changes[key] = {
                    'from': v1,
                    'to': v2
                }
                
        return changes
        
    def predict_output(self, input_grid: List[List[int]], 
                      training_inputs: List[List[List[int]]], 
                      training_outputs: List[List[List[int]]]) -> List[List[int]]:
        """Predict output for new input using pattern hierarchies"""
        training_data = []
        
        # Analyze each training example
        for train_in, train_out in zip(training_inputs, training_outputs):
            analysis = self.analyze_transform(train_in, train_out)
            training_data.append(analysis)
            
        # Analyze input grid
        input_analysis = self.analyze_grid(input_grid)
        
        # Use predictor with hierarchical pattern information
        prediction = self.predictor.predict_output(
            input_grid,
            training_inputs,
            training_outputs,
            {
                'input_analysis': input_analysis,
                'training_data': training_data
            }
        )
        
        return prediction
        
    def explain_prediction(self, input_grid: List[List[int]], 
                         predicted_output: List[List[int]], 
                         training_data: List[Dict]) -> Dict:
        """Explain prediction using pattern hierarchies"""
        # Analyze input and predicted output
        input_analysis = self.analyze_grid(input_grid)
        prediction_analysis = self.analyze_grid(predicted_output)
        
        # Analyze transformation
        transform_analysis = self.analyze_transform(input_grid, predicted_output)
        
        return {
            'input_analysis': input_analysis,
            'prediction_analysis': prediction_analysis,
            'transform_analysis': transform_analysis,
            'training_patterns': training_data
        }