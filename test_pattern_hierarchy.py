"""
Tests for pattern hierarchy analysis
"""

import unittest
import numpy as np
from pattern_hierarchy import PatternHierarchy, Pattern, PatternLevel

class TestPatternHierarchy(unittest.TestCase):
    def setUp(self):
        self.hierarchy = PatternHierarchy()
        
        # Sample grid patterns
        self.grid_patterns = {
            'symmetry': {
                'symmetry_found': True,
                'symmetry_types': [
                    {'type': 'horizontal_reflection', 'position': 2},
                    {'type': 'rotational_90', 'order': 4}
                ]
            },
            'progression': {
                'progression_found': True,
                'progression_types': [
                    {'type': 'arithmetic', 'difference': 1, 'location': 'row_0'},
                    {'type': 'geometric', 'ratio': 2.0, 'location': 'col_1'}
                ]
            },
            'repetition': {
                'repetition_found': True,
                'patterns': [
                    {'type': 'horizontal_repeat', 'block_size': [2, 2], 'count': 3},
                    {'type': 'vertical_repeat', 'block_size': [1, 2], 'count': 2}
                ]
            },
            'spatial': {
                'spatial_patterns_found': True,
                'patterns': [
                    {'type': 'linear_arrangement', 'direction': [1, 0], 'value': 1},
                    {'type': 'diagonal_pattern', 'direction': 'positive', 'value': 2}
                ]
            }
        }
        
        # Sample transformation data
        self.transform_data = {
            'value_mappings': {
                1: {'type': 'conditional', 'conditions': {'corner': 2, 'edge': 3}},
                2: {'type': 'direct', 'to': 4}
            },
            'object_transforms': {
                'object_mappings': [
                    {'input_object': {'value': 1}, 'transform': {'type': 'scale', 'factor': 2}},
                    {'input_object': {'value': 2}, 'transform': {'type': 'rotation', 'degrees': 90}}
                ]
            }
        }
        
    def test_atomic_pattern_extraction(self):
        """Test extraction of atomic patterns"""
        result = self.hierarchy.analyze_pattern_relationships(
            self.grid_patterns, self.transform_data
        )
        
        # Check atomic patterns
        atomic = result['atomic']
        self.assertTrue(any(p['type'].startswith('symmetry_') for p in atomic))
        self.assertTrue(any(p['type'].startswith('progression_') for p in atomic))
        self.assertTrue(any(p['type'].startswith('repetition_') for p in atomic))
        self.assertTrue(any(p['type'].startswith('spatial_') for p in atomic))
        
    def test_composite_pattern_formation(self):
        """Test formation of composite patterns"""
        result = self.hierarchy.analyze_pattern_relationships(
            self.grid_patterns, self.transform_data
        )
        
        # Check composite patterns
        composites = result['composite']
        self.assertTrue(len(composites) > 0)
        self.assertTrue(all(p['level'] == 'COMPOSITE' for p in composites))
        
    def test_structural_pattern_identification(self):
        """Test identification of structural patterns"""
        result = self.hierarchy.analyze_pattern_relationships(
            self.grid_patterns, self.transform_data
        )
        
        # Check structural patterns
        structural = result['structural']
        self.assertTrue(all(p['level'] == 'STRUCTURAL' for p in structural))
        
    def test_meta_pattern_discovery(self):
        """Test discovery of meta patterns"""
        result = self.hierarchy.analyze_pattern_relationships(
            self.grid_patterns, self.transform_data
        )
        
        # Check meta patterns
        meta = result['meta']
        self.assertTrue(any(p['type'] == 'meta_conditional_mapping' for p in meta))
        self.assertTrue(any(p['type'] == 'meta_object_transform' for p in meta))
        
    def test_pattern_confidence(self):
        """Test pattern confidence calculation"""
        result = self.hierarchy.analyze_pattern_relationships(
            self.grid_patterns, self.transform_data
        )
        
        # Check all patterns have confidence scores
        all_patterns = (result['atomic'] + result['composite'] + 
                       result['structural'] + result['meta'])
        
        self.assertTrue(all('confidence' in p for p in all_patterns))
        self.assertTrue(all(0 <= p['confidence'] <= 1 for p in all_patterns))
        
    def test_pattern_relationships(self):
        """Test pattern relationship analysis"""
        result = self.hierarchy.analyze_pattern_relationships(
            self.grid_patterns, self.transform_data
        )
        
        # Check composite patterns have relationship info
        composites = result['composite']
        for comp in composites:
            self.assertIn('relationship', comp['properties'])
            rel = comp['properties']['relationship']
            self.assertIn('type', rel)
            self.assertIn('interaction', rel)
            self.assertIn('dependency', rel)

if __name__ == '__main__':
    unittest.main()