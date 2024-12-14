"""
Enhanced pattern analysis capabilities for ARC challenge
"""

import numpy as np
from typing import Dict, List, Optional
from pattern_testing import PatternTester
from pattern_visualizer import PatternVisualizer

class EnhancedPatternAnalyzer:
    def __init__(self):
        self.pattern_tester = PatternTester()
        self.visualizer = PatternVisualizer()
        
    def analyze_grid(self, grid: List[List[int]]) -> Dict:
        """Analyze a grid for patterns"""
        grid = np.array(grid)
        results = {
            'patterns': {},
            'visualizations': {}
        }
        
        # Run all pattern tests
        pattern_results = self.pattern_tester.run_all_tests(grid)
        results['patterns'] = pattern_results
        
        # Generate visualizations
        for pattern_type in pattern_results.keys():
            viz_path = self.visualizer.visualize_pattern(
                grid, 
                pattern_results[pattern_type],
                pattern_type
            )
            results['visualizations'][pattern_type] = viz_path
            
        return results
        
    def compare_patterns(self, grid1: List[List[int]], grid2: List[List[int]]) -> Dict:
        """Compare patterns between two grids"""
        results1 = self.analyze_grid(grid1)
        results2 = self.analyze_grid(grid2)
        
        comparison = {
            'consistent_patterns': [],
            'changed_patterns': [],
            'new_patterns': [],
            'lost_patterns': []
        }
        
        # Helper function to get all detected patterns of a specific type
        def get_patterns(results: Dict, pattern_type: str) -> List:
            return results['patterns'].get(pattern_type, {}).get('patterns', [])
        
        # Compare each pattern type
        pattern_types = ['symmetry', 'progression', 'repetition', 'spatial']
        for p_type in pattern_types:
            patterns1 = get_patterns(results1, p_type)
            patterns2 = get_patterns(results2, p_type)
            
            # Find consistent patterns
            for p1 in patterns1:
                for p2 in patterns2:
                    if self._compare_pattern_attributes(p1, p2):
                        comparison['consistent_patterns'].append({
                            'type': p_type,
                            'pattern': p1
                        })
                        
            # Find changed patterns
            for p1 in patterns1:
                found_similar = False
                for p2 in patterns2:
                    if self._compare_pattern_structure(p1, p2):
                        found_similar = True
                        comparison['changed_patterns'].append({
                            'type': p_type,
                            'from': p1,
                            'to': p2
                        })
                if not found_similar:
                    comparison['lost_patterns'].append({
                        'type': p_type,
                        'pattern': p1
                    })
                    
            # Find new patterns
            for p2 in patterns2:
                if not any(self._compare_pattern_structure(p1, p2) for p1 in patterns1):
                    comparison['new_patterns'].append({
                        'type': p_type,
                        'pattern': p2
                    })
                    
        return comparison
        
    def _compare_pattern_attributes(self, p1: Dict, p2: Dict) -> bool:
        """Compare if two patterns have identical attributes"""
        # Remove position-specific attributes for comparison
        p1_clean = {k: v for k, v in p1.items() 
                   if k not in ['position', 'location']}
        p2_clean = {k: v for k, v in p2.items() 
                   if k not in ['position', 'location']}
        return p1_clean == p2_clean
        
    def _compare_pattern_structure(self, p1: Dict, p2: Dict) -> bool:
        """Compare if two patterns have the same structure but different attributes"""
        return (p1['type'] == p2['type'] and 
                set(p1.keys()) == set(p2.keys()))
        
    def find_transformation_rules(self, input_grid: List[List[int]], 
                                output_grid: List[List[int]]) -> Dict:
        """Find transformation rules between input and output grids"""
        comparison = self.compare_patterns(input_grid, output_grid)
        
        rules = []
        
        # Analyze consistent patterns
        if comparison['consistent_patterns']:
            rules.append({
                'type': 'preserve',
                'patterns': comparison['consistent_patterns']
            })
            
        # Analyze changed patterns
        for change in comparison['changed_patterns']:
            from_pattern = change['from']
            to_pattern = change['to']
            
            if from_pattern['type'] == to_pattern['type']:
                # Look for specific transformations
                if 'value' in from_pattern and 'value' in to_pattern:
                    rules.append({
                        'type': 'value_transform',
                        'from': from_pattern['value'],
                        'to': to_pattern['value']
                    })
                    
                if 'dimensions' in from_pattern and 'dimensions' in to_pattern:
                    rules.append({
                        'type': 'size_transform',
                        'from': from_pattern['dimensions'],
                        'to': to_pattern['dimensions']
                    })
                    
                if ('direction' in from_pattern and 'direction' in to_pattern and
                    from_pattern['direction'] != to_pattern['direction']):
                    rules.append({
                        'type': 'direction_change',
                        'from': from_pattern['direction'],
                        'to': to_pattern['direction']
                    })
                    
        # Analyze pattern additions/removals
        if comparison['new_patterns']:
            rules.append({
                'type': 'add_patterns',
                'patterns': comparison['new_patterns']
            })
            
        if comparison['lost_patterns']:
            rules.append({
                'type': 'remove_patterns',
                'patterns': comparison['lost_patterns']
            })
            
        return {
            'rules': rules,
            'comparison': comparison
        }