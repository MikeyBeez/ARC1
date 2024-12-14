"""
Dedicated testing module for pattern detection capabilities
"""

import numpy as np
from typing import Dict, List, Optional
import json
import logging
from pathlib import Path

logging.basicConfig(
    filename='pattern_testing.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class PatternTester:
    def __init__(self):
        self.base_dir = Path('/users/bard/mcp/arc_testing')
        
    def test_pattern(self, grid: List[List[int]], pattern_type: str) -> Dict:
        """Test a specific type of pattern detection"""
        grid = np.array(grid)
        results = {}
        
        if pattern_type == 'symmetry':
            results.update(self.test_symmetry(grid))
        elif pattern_type == 'progression':
            results.update(self.test_progression(grid))
        elif pattern_type == 'repetition':
            results.update(self.test_repetition(grid))
        elif pattern_type == 'spatial':
            results.update(self.test_spatial_relations(grid))
            
        return results
        
    def test_symmetry(self, grid: np.ndarray) -> Dict:
        """Test for different types of symmetry"""
        results = {
            'symmetry_found': False,
            'symmetry_types': []
        }
        
        # Horizontal reflection
        for i in range(1, grid.shape[0]):
            top = grid[:i]
            bottom = grid[i:]
            if len(top) == len(bottom):
                if np.array_equal(top, np.flip(bottom, 0)):
                    results['symmetry_found'] = True
                    results['symmetry_types'].append({
                        'type': 'horizontal_reflection',
                        'position': i
                    })
                    
        # Vertical reflection
        for i in range(1, grid.shape[1]):
            left = grid[:, :i]
            right = grid[:, i:]
            if left.shape[1] == right.shape[1]:
                if np.array_equal(left, np.flip(right, 1)):
                    results['symmetry_found'] = True
                    results['symmetry_types'].append({
                        'type': 'vertical_reflection',
                        'position': i
                    })
                    
        # Rotational symmetry
        for k in [2, 4]:  # Test for 180 and 90 degree rotational symmetry
            if np.array_equal(grid, np.rot90(grid, k=k)):
                results['symmetry_found'] = True
                results['symmetry_types'].append({
                    'type': f'rotational_{360//k}',
                    'order': k
                })
                
        return results
        
    def test_progression(self, grid: np.ndarray) -> Dict:
        """Test for numeric progressions and patterns"""
        results = {
            'progression_found': False,
            'progression_types': []
        }
        
        # Test rows
        for i, row in enumerate(grid):
            # Arithmetic progression
            diffs = np.diff(row)
            if len(set(diffs)) == 1:
                results['progression_found'] = True
                results['progression_types'].append({
                    'type': 'arithmetic',
                    'location': f'row_{i}',
                    'difference': int(diffs[0])
                })
                
            # Geometric progression
            ratios = row[1:] / row[:-1]
            if len(row[row != 0]) > 1 and len(set(ratios[~np.isnan(ratios)])) == 1:
                results['progression_found'] = True
                results['progression_types'].append({
                    'type': 'geometric',
                    'location': f'row_{i}',
                    'ratio': float(ratios[0])
                })
                
        # Test columns
        for i, col in enumerate(grid.T):
            diffs = np.diff(col)
            if len(set(diffs)) == 1:
                results['progression_found'] = True
                results['progression_types'].append({
                    'type': 'arithmetic',
                    'location': f'col_{i}',
                    'difference': int(diffs[0])
                })
                
            ratios = col[1:] / col[:-1]
            if len(col[col != 0]) > 1 and len(set(ratios[~np.isnan(ratios)])) == 1:
                results['progression_found'] = True
                results['progression_types'].append({
                    'type': 'geometric',
                    'location': f'col_{i}',
                    'ratio': float(ratios[0])
                })
                
        return results
        
    def test_repetition(self, grid: np.ndarray) -> Dict:
        """Test for repeating patterns"""
        results = {
            'repetition_found': False,
            'patterns': []
        }
        
        # Test for repeating blocks
        for h in range(1, grid.shape[0] // 2 + 1):
            for w in range(1, grid.shape[1] // 2 + 1):
                block = grid[:h, :w]
                
                # Test if this block repeats horizontally
                if grid.shape[1] % w == 0:
                    horizontal_blocks = [
                        grid[:h, i:i+w] 
                        for i in range(0, grid.shape[1], w)
                    ]
                    if all(np.array_equal(block, b) for b in horizontal_blocks):
                        results['repetition_found'] = True
                        results['patterns'].append({
                            'type': 'horizontal_repeat',
                            'block': block.tolist(),
                            'block_size': [h, w],
                            'repetitions': len(horizontal_blocks)
                        })
                        
                # Test if this block repeats vertically
                if grid.shape[0] % h == 0:
                    vertical_blocks = [
                        grid[i:i+h, :w]
                        for i in range(0, grid.shape[0], h)
                    ]
                    if all(np.array_equal(block, b) for b in vertical_blocks):
                        results['repetition_found'] = True
                        results['patterns'].append({
                            'type': 'vertical_repeat',
                            'block': block.tolist(),
                            'block_size': [h, w],
                            'repetitions': len(vertical_blocks)
                        })
                        
        return results
        
    def test_spatial_relations(self, grid: np.ndarray) -> Dict:
        """Test for spatial relationships and patterns"""
        results = {
            'spatial_patterns_found': False,
            'patterns': []
        }
        
        # Find unique values
        unique_values = np.unique(grid[grid != 0])
        
        # For each value, analyze its distribution
        for val in unique_values:
            mask = (grid == val)
            coords = np.argwhere(mask)
            
            if len(coords) > 1:
                # Check for linear arrangements
                diffs = np.diff(coords, axis=0)
                if len(set(map(tuple, diffs))) == 1:
                    results['spatial_patterns_found'] = True
                    results['patterns'].append({
                        'type': 'linear_arrangement',
                        'value': int(val),
                        'direction': tuple(map(int, diffs[0])),
                        'count': len(coords)
                    })
                    
                # Check for diagonal patterns
                diag_diffs = np.abs(diffs)
                if len(set(map(tuple, diag_diffs))) == 1 and \
                   all(d[0] == d[1] for d in diag_diffs):
                    results['spatial_patterns_found'] = True
                    results['patterns'].append({
                        'type': 'diagonal_pattern',
                        'value': int(val),
                        'direction': 'positive' if diffs[0][0] * diffs[0][1] > 0 else 'negative',
                        'count': len(coords)
                    })
                    
                # Check for rectangular arrangements
                if len(coords) >= 4:
                    min_r, min_c = coords.min(axis=0)
                    max_r, max_c = coords.max(axis=0)
                    rect = grid[min_r:max_r+1, min_c:max_c+1]
                    if np.all(rect[rect != 0] == val):
                        results['spatial_patterns_found'] = True
                        results['patterns'].append({
                            'type': 'rectangular_arrangement',
                            'value': int(val),
                            'dimensions': [int(max_r - min_r + 1), int(max_c - min_c + 1)],
                            'position': [int(min_r), int(min_c)]
                        })
                        
        return results
        
    def run_all_tests(self, grid: List[List[int]]) -> Dict:
        """Run all pattern detection tests"""
        results = {}
        
        for pattern_type in ['symmetry', 'progression', 'repetition', 'spatial']:
            logging.info(f"Testing {pattern_type} patterns")
            test_results = self.test_pattern(grid, pattern_type)
            results[pattern_type] = test_results
            logging.info(f"{pattern_type} results: {json.dumps(test_results, indent=2)}")
            
        return results

def main():
    # Example usage
    tester = PatternTester()
    
    test_grid = [
        [0, 1, 0],
        [1, 2, 1],
        [0, 1, 0]
    ]
    
    results = tester.run_all_tests(test_grid)
    print(json.dumps(results, indent=2))

if __name__ == '__main__':
    main()