"""
Task processor with enhanced pattern analysis
"""

import logging
from typing import Dict, List, Any
from operations import (
    rotate_grid, flip_grid, fill_pattern,
    extract_pattern, apply_pattern, get_shape_dimensions,
    find_objects, analyze_grid_changes, detect_symmetry
)

class TaskProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def analyze_task(self, task_data: Dict) -> Dict[str, Any]:
        """Analyze task using operation library"""
        analysis = {
            'patterns': [],
            'objects': [],
            'symmetries': [],
            'transformations': []
        }
        
        try:
            # Analyze each training example
            for train in task_data['train']:
                input_grid = train['input']
                output_grid = train['output']
                
                # Extract basic patterns
                pattern = extract_pattern(input_grid, output_grid)
                if pattern:
                    analysis['patterns'].append(pattern)
                    
                # Find objects
                input_objects = find_objects(input_grid)
                output_objects = find_objects(output_grid)
                analysis['objects'].append({
                    'input': input_objects,
                    'output': output_objects
                })
                
                # Detect symmetries
                input_sym = detect_symmetry(input_grid)
                output_sym = detect_symmetry(output_grid)
                analysis['symmetries'].append({
                    'input': input_sym,
                    'output': output_sym
                })
                
                # Analyze transformations
                changes = analyze_grid_changes(input_grid, output_grid)
                analysis['transformations'].append(changes)
                
            # Log analysis
            self.logger.debug(f"Task analysis: {analysis}")
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Task analysis failed: {str(e)}")
            return analysis
            
    def extract_rules(self, analysis: Dict[str, Any]) -> List[str]:
        """Extract rules from analysis"""
        rules = []
        
        try:
            # Pattern rules
            if analysis['patterns']:
                common_patterns = set.intersection(*map(set, analysis['patterns']))
                for val, transformed in common_patterns:
                    rules.append(f"Value {val} always transforms to {transformed}")
                    
            # Object rules
            obj_counts = [(len(ex['input']), len(ex['output'])) 
                         for ex in analysis['objects']]
            if all(c[0] == c[1] for c in obj_counts):
                rules.append("Object count preserved")
                
            # Symmetry rules
            sym_pairs = [(ex['input'], ex['output']) 
                        for ex in analysis['symmetries']]
            common_sym = set.intersection(*[set(i) & set(o) 
                                         for i, o in sym_pairs])
            if common_sym:
                rules.append(f"Preserves symmetries: {', '.join(common_sym)}")
                
            # Transformation rules
            dim_changes = [t['dimension_change'] 
                         for t in analysis['transformations']]
            if all(d == dim_changes[0] for d in dim_changes):
                dr, dc = dim_changes[0]
                if dr != 0 or dc != 0:
                    rules.append(f"Grid size changes by ({dr}, {dc})")
                    
            return rules
            
        except Exception as e:
            self.logger.error(f"Rule extraction failed: {str(e)}")
            return rules
            
    def apply_rules(self, rules: List[str], input_grid: List[List[int]]) -> List[List[int]]:
        """Apply extracted rules to new input"""
        result = input_grid
        
        try:
            for rule in rules:
                if "Value" in rule:
                    val, new_val = map(int, rule.split())[1:4:2]
                    pattern = {val: new_val}
                    result = apply_pattern(result, pattern)
                    
                elif "Grid size changes" in rule:
                    # Handle dimension changes
                    pass
                    
                elif "Preserves symmetries" in rule:
                    # Maintain symmetries
                    pass
                    
            return result
            
        except Exception as e:
            self.logger.error(f"Rule application failed: {str(e)}")
            return result