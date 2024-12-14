"""
Visualization tools for pattern detection results
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json

class PatternVisualizer:
    def __init__(self):
        self.output_dir = Path('/users/bard/mcp/arc_testing/visualizations')
        self.output_dir.mkdir(exist_ok=True)
        
    def visualize_pattern(self, grid: np.ndarray, pattern_results: Dict, pattern_type: str) -> str:
        """Save pattern analysis results in JSON format for visualization"""
        result = {
            'grid': grid.tolist(),
            'pattern_type': pattern_type,
            'analysis': pattern_results
        }
        
        output_file = self.output_dir / f'{pattern_type}_analysis.json'
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
            
        return str(output_file)