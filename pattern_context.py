"""
Analysis of pattern context sensitivity and applicability.
"""

import numpy as np
from typing import Dict, List, Optional, Any
from pattern_core import Pattern

class PatternContextAnalyzer:
    def __init__(self):
        self.pattern_contexts: Dict[str, Dict] = {}
        
    def analyze_context_sensitivity(self, pattern: Pattern, context: Dict) -> Dict:
        """Analyze when a pattern appears based on context"""
        context_data = {
            'position_sensitivity': self._analyze_position_sensitivity(pattern, context),
            'size_sensitivity': self._analyze_size_sensitivity(pattern, context),
            'neighbor_sensitivity': self._analyze_neighbor_sensitivity(pattern, context),
            'global_sensitivity': self._analyze_global_sensitivity(pattern, context)
        }
        
        self.pattern_contexts[pattern.type] = context_data
        return context_data
    
    def _analyze_position_sensitivity(self, pattern: Pattern, context: Dict) -> Dict:
        """Analyze how pattern depends on position"""
        if 'position' not in pattern.properties:
            return {'sensitive': False}
            
        pos = pattern.properties['position']
        grid_size = context.get('grid_size', (0, 0))
        
        edge_relative = {
            'top': pos[0] < 2,
            'bottom': pos[0] > grid_size[0] - 3,
            'left': pos[1] < 2,
            'right': pos[1] > grid_size[1] - 3
        }
        
        center_relative = {
            'distance': np.sqrt(
                (pos[0] - grid_size[0]/2)**2 + 
                (pos[1] - grid_size[1]/2)**2
            ),
            'angle': np.arctan2(
                pos[1] - grid_size[1]/2,
                pos[0] - grid_size[0]/2
            )
        }
        
        return {
            'sensitive': True,
            'edge_relative': edge_relative,
            'center_relative': center_relative
        }
    
    def _analyze_size_sensitivity(self, pattern: Pattern, context: Dict) -> Dict:
        """Analyze how pattern depends on grid size"""
        if 'size' not in pattern.properties:
            return {'sensitive': False}
            
        size = pattern.properties['size']
        grid_size = context.get('grid_size', (0, 0))
        
        relative_size = {
            'width_ratio': size[0] / grid_size[0] if grid_size[0] > 0 else 0,
            'height_ratio': size[1] / grid_size[1] if grid_size[1] > 0 else 0
        }
        
        return {
            'sensitive': True,
            'relative_size': relative_size,
            'fixed_size': size == pattern.properties.get('original_size', size)
        }
    
    def _analyze_neighbor_sensitivity(self, pattern: Pattern, context: Dict) -> Dict:
        """Analyze how pattern depends on neighboring elements"""
        if 'neighbors' not in context:
            return {'sensitive': False}
            
        neighbors = context['neighbors']
        important_neighbors = []
        
        for n in neighbors:
            if self._neighbor_important(pattern, n):
                important_neighbors.append({
                    'type': n.type,
                    'relative_position': self._get_relative_position(pattern, n),
                    'importance': self._calculate_neighbor_importance(pattern, n)
                })
        
        return {
            'sensitive': len(important_neighbors) > 0,
            'important_neighbors': important_neighbors
        }
    
    def _analyze_global_sensitivity(self, pattern: Pattern, context: Dict) -> Dict:
        """Analyze how pattern depends on global grid properties"""
        sensitivities = {}
        
        if 'color_distribution' in context:
            sensitivities['color'] = {
                'sensitive': self._color_sensitive(pattern, context),
                'distribution': context['color_distribution']
            }
            
        if 'global_symmetry' in context:
            sensitivities['symmetry'] = {
                'sensitive': self._symmetry_sensitive(pattern, context),
                'type': context['global_symmetry']
            }
            
        if 'grid_density' in context:
            sensitivities['density'] = {
                'sensitive': self._density_sensitive(pattern, context),
                'threshold': self._find_density_threshold(pattern, context)
            }
        
        return {
            'sensitive': any(s.get('sensitive', False) for s in sensitivities.values()),
            'sensitivities': sensitivities
        }
    
    def _neighbor_important(self, p1: Pattern, p2: Pattern) -> bool:
        """Check if a neighbor is important for the pattern"""
        # Type relationships
        if p1.type.split('_')[0] == p2.type.split('_')[0]:
            return True
            
        # Property relationships    
        shared_props = set(p1.properties.keys()) & set(p2.properties.keys())
        return len(shared_props) > 0
    
    def _get_relative_position(self, p1: Pattern, p2: Pattern) -> Dict:
        """Get relative position between two patterns"""
        if 'position' not in p1.properties or 'position' not in p2.properties:
            return {}
            
        pos1 = p1.properties['position']
        pos2 = p2.properties['position']
        
        return {
            'dx': pos2[0] - pos1[0],
            'dy': pos2[1] - pos1[1],
            'distance': np.sqrt((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2),
            'angle': np.arctan2(pos2[1] - pos1[1], pos2[0] - pos1[0])
        }
    
    def _calculate_neighbor_importance(self, p1: Pattern, p2: Pattern) -> float:
        """Calculate importance score for neighboring pattern"""
        score = 0.0
        
        # Type similarity adds importance
        if p1.type.split('_')[0] == p2.type.split('_')[0]:
            score += 0.3
            
        # Property overlap adds importance
        shared_props = set(p1.properties.keys()) & set(p2.properties.keys())
        score += len(shared_props) * 0.1
        
        return min(score, 1.0)
    
    def predict_pattern_applicability(self, pattern: Pattern, context: Dict) -> float:
        """Predict how likely a pattern is to apply in a new context"""
        if pattern.type not in self.pattern_contexts:
            return 0.0
            
        context_data = self.pattern_contexts[pattern.type]
        score = 1.0
        
        # Position compatibility
        if context_data.get('position_sensitivity', {}).get('sensitive'):
            pos_score = self._evaluate_position_compatibility(
                context_data['position_sensitivity'], context)
            score *= pos_score
            
        # Size compatibility    
        if context_data.get('size_sensitivity', {}).get('sensitive'):
            size_score = self._evaluate_size_compatibility(
                context_data['size_sensitivity'], context)
            score *= size_score
            
        # Neighbor compatibility
        if context_data.get('neighbor_sensitivity', {}).get('sensitive'):
            neighbor_score = self._evaluate_neighbor_compatibility(
                context_data['neighbor_sensitivity'], context)
            score *= neighbor_score
        
        return score
    
    def _evaluate_position_compatibility(self, sensitivity: Dict, context: Dict) -> float:
        """Evaluate position compatibility score"""
        if 'grid_size' not in context:
            return 0.5
            
        score = 1.0
        grid_size = context['grid_size']
        pos = context.get('position', (0, 0))
        
        edge_relative = sensitivity.get('edge_relative', {})
        if edge_relative:
            edge_scores = []
            if edge_relative.get('top') and pos[0] >= 2:
                edge_scores.append(0.0)
            if edge_relative.get('bottom') and pos[0] <= grid_size[0] - 3:
                edge_scores.append(0.0)
            if edge_relative.get('left') and pos[1] >= 2:
                edge_scores.append(0.0)
            if edge_relative.get('right') and pos[1] <= grid_size[1] - 3:
                edge_scores.append(0.0)
                
            if edge_scores:
                score *= (1 - np.mean(edge_scores))
        
        return score
    
    def _evaluate_size_compatibility(self, sensitivity: Dict, context: Dict) -> float:
        """Evaluate size compatibility score"""
        if 'grid_size' not in context:
            return 0.5
            
        score = 1.0
        grid_size = context['grid_size']
        size = context.get('size', (1, 1))
        
        relative_size = sensitivity.get('relative_size', {})
        if relative_size:
            width_ratio = size[0] / grid_size[0] if grid_size[0] > 0 else 0
            height_ratio = size[1] / grid_size[1] if grid_size[1] > 0 else 0
            
            target_width = relative_size.get('width_ratio', 0)
            target_height = relative_size.get('height_ratio', 0)
            
            ratio_score = 1 - (
                abs(width_ratio - target_width) + 
                abs(height_ratio - target_height)
            ) / 2
            
            score *= ratio_score
            
        return score
    
    def _evaluate_neighbor_compatibility(self, sensitivity: Dict, context: Dict) -> float:
        """Evaluate neighbor compatibility score"""
        if 'neighbors' not in context:
            return 0.5
            
        important_neighbors = sensitivity.get('important_neighbors', [])
        if not important_neighbors:
            return 1.0
            
        actual_neighbors = context['neighbors']
        scores = []
        
        for important in important_neighbors:
            matches = [n for n in actual_neighbors if n.type == important['type']]
            if matches:
                best_score = max(self._evaluate_neighbor_match(important, n)
                               for n in matches)
                scores.append(best_score)
            else:
                scores.append(0.0)
                
        return np.mean(scores) if scores else 0.5
    
    def _evaluate_neighbor_match(self, important: Dict, neighbor: Pattern) -> float:
        """Evaluate how well a neighbor matches requirements"""
        score = 1.0
        
        if 'relative_position' in important:
            target_pos = important['relative_position']
            actual_pos = self._get_relative_position(neighbor, neighbor)
            
            distance_diff = abs(actual_pos['distance'] - target_pos['distance'])
            angle_diff = min(
                abs(actual_pos['angle'] - target_pos['angle']),
                2*np.pi - abs(actual_pos['angle'] - target_pos['angle'])
            )
            
            position_score = 1 - (
                distance_diff / max(target_pos['distance'], 1) * 0.5 +
                angle_diff / np.pi * 0.5
            )
            
            score *= position_score
            
        return score
