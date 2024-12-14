"""
Basic grid operations for ARC tasks
"""

import numpy as np
from typing import List, Dict, Optional, Tuple, Union

class GridOperations:
    @staticmethod
    def get_objects(grid: np.ndarray) -> List[Dict]:
        """Extract distinct objects from grid based on connected components"""
        objects = []
        seen = set()
        
        def flood_fill(r: int, c: int, value: int) -> List[Tuple[int, int]]:
            if (r < 0 or r >= grid.shape[0] or 
                c < 0 or c >= grid.shape[1] or 
                grid[r,c] != value or 
                (r,c) in seen):
                return []
                
            seen.add((r,c))
            coords = [(r,c)]
            
            # Check 4-connected neighbors
            for nr, nc in [(r+1,c), (r-1,c), (r,c+1), (r,c-1)]:
                coords.extend(flood_fill(nr, nc, value))
                
            return coords
        
        # Find all objects
        for r in range(grid.shape[0]):
            for c in range(grid.shape[1]):
                if (r,c) not in seen and grid[r,c] != 0:
                    coords = flood_fill(r, c, grid[r,c])
                    if coords:
                        coords = np.array(coords)
                        objects.append({
                            'value': int(grid[r,c]),
                            'coords': coords.tolist(),
                            'min_r': int(coords[:,0].min()),
                            'max_r': int(coords[:,0].max()),
                            'min_c': int(coords[:,1].min()),
                            'max_c': int(coords[:,1].max()),
                            'size': len(coords),
                            'dimensions': [
                                int(coords[:,0].max() - coords[:,0].min() + 1),
                                int(coords[:,1].max() - coords[:,1].min() + 1)
                            ],
                            'center': [
                                float((coords[:,0].max() + coords[:,0].min()) / 2),
                                float((coords[:,1].max() + coords[:,1].min()) / 2)
                            ]
                        })
        return objects
    
    @staticmethod
    def get_object_grid(grid: np.ndarray, obj: Dict) -> np.ndarray:
        """Extract a rectangular grid containing just the object"""
        r1, r2 = obj['min_r'], obj['max_r'] + 1
        c1, c2 = obj['min_c'], obj['max_c'] + 1
        obj_grid = grid[r1:r2, c1:c2].copy()
        
        # Mask everything that's not part of the object
        mask = np.ones_like(obj_grid, dtype=bool)
        local_coords = [(r-r1, c-c1) for r,c in obj['coords']]
        for r,c in local_coords:
            mask[r,c] = False
        obj_grid[mask] = 0
        
        return obj_grid
    
    @staticmethod
    def rotate_grid(grid: np.ndarray, k: int = 1) -> np.ndarray:
        """Rotate grid k*90 degrees counterclockwise"""
        return np.rot90(grid, k=k)
    
    @staticmethod
    def flip_grid(grid: np.ndarray, axis: int = 0) -> np.ndarray:
        """Flip grid along specified axis (0=horizontal, 1=vertical)"""
        return np.flip(grid, axis=axis)
    
    @staticmethod
    def count_values(grid: np.ndarray) -> Dict[int, int]:
        """Count occurrences of each value in grid"""
        unique, counts = np.unique(grid, return_counts=True)
        return {int(v): int(c) for v,c in zip(unique, counts)}
    
    @staticmethod
    def extract_subgrids(grid: np.ndarray, size: Tuple[int, int]) -> List[np.ndarray]:
        """Extract all possible subgrids of given size"""
        h, w = size
        if h > grid.shape[0] or w > grid.shape[1]:
            return []
        
        subgrids = []
        for i in range(grid.shape[0] - h + 1):
            for j in range(grid.shape[1] - w + 1):
                subgrids.append(grid[i:i+h, j:j+w].copy())
                
        return subgrids
    
    @staticmethod
    def find_subgrid(grid: np.ndarray, subgrid: np.ndarray) -> List[Tuple[int, int]]:
        """Find all occurrences of subgrid in grid"""
        locations = []
        h, w = subgrid.shape
        
        for i in range(grid.shape[0] - h + 1):
            for j in range(grid.shape[1] - w + 1):
                if np.array_equal(grid[i:i+h, j:j+w], subgrid):
                    locations.append((i,j))
                    
        return locations
    
    @staticmethod
    def get_grid_properties(grid: np.ndarray) -> Dict:
        """Get basic properties of the grid"""
        height, width = grid.shape
        values = GridOperations.count_values(grid)
        center = (height // 2, width // 2)
        
        # Check if grid is square
        is_square = height == width
        
        # Calculate density
        total_cells = height * width
        filled_cells = sum(v for k,v in values.items() if k != 0)
        density = filled_cells / total_cells
        
        return {
            'height': int(height),
            'width': int(width),
            'values': values,
            'center': center,
            'is_square': is_square,
            'density': float(density),
            'total_cells': int(total_cells),
            'filled_cells': int(filled_cells)
        }