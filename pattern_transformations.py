"""
Analysis of pattern transformations and relationships.
"""

import numpy as np
from typing import Dict, List, Optional, Set, Any
from pattern_core import PatternTransformation, Pattern

class PatternTransformationAnalyzer:
    def __init__(self):
        self.transformations: List[PatternTransformation] = []
    
    def analyze_pattern_transformations(self, 
                                      before_patterns: List[Pattern],
                                      after_patterns: List[Pattern]) -> List[PatternTransformation]:
        """Analyze how patterns transform between states"""
        transformations = []
        
        for before in before_patterns:
            for after in after_patterns:
                if self._patterns_related_by_transformation(before, after):
                    transform = self._extract_transformation(before, after)
                    if transform:
                        transformations.append(transform)
                        self.transformations.append(transform)
        
        return transformations
    
    def _patterns_related_by_transformation(self, p1: Pattern, p2: Pattern) -> bool:
        """Determine if two patterns are related by a transformation"""
        # Check for type similarity
        if p1.type.split('_')[0] == p2.type.split('_')[0]:
            return True
            
        # Check for property overlap
        shared_props = set(p1.properties.keys()) & set(p2.properties.keys())
        if len(shared_props) > 0:
            return True
            
        # Check for spatial relationship
        if ('position' in p1.properties and 'position' in p2.properties and
            self._positions_related(p1.properties['position'], p2.properties['position'])):
            return True
            
        return False
    
    def _extract_transformation(self, 
                              source: Pattern, 
                              target: Pattern) -> Optional[PatternTransformation]:
        """Extract the transformation between two patterns"""
        # Analyze property changes
        changes = {}
        for key in set(source.properties.keys()) | set(target.properties.keys()):
            source_val = source.properties.get(key)
            target_val = target.properties.get(key)
            if source_val != target_val:
                changes[key] = {
                    'from': source_val,
                    'to': target_val
                }
        
        if not changes:
            return None
            
        # Determine transformation type
        transform_type = self._categorize_transformation(changes)
        
        # Extract conditions
        conditions = self._extract_conditions(source, target, changes)
        
        # Calculate confidence
        confidence = self._calculate_transform_confidence(
            source, target, transform_type, conditions)
        
        return PatternTransformation(
            source_pattern=source,
            target_pattern=target,
            transform_type=transform_type,
            conditions=conditions,
            confidence=confidence
        )
    
    def _positions_related(self, pos1: tuple, pos2: tuple) -> bool:
        """Check if positions are related (e.g., adjacent, symmetric)"""
        dx = abs(pos1[0] - pos2[0])
        dy = abs(pos1[1] - pos2[1])
        return dx <= 1 and dy <= 1  # Adjacent or same position
    
    def _categorize_transformation(self, changes: Dict) -> str:
        """Categorize the type of transformation based on changes"""
        if 'position' in changes:
            return 'spatial_transform'
        elif 'color' in changes or 'value' in changes:
            return 'value_transform'
        elif 'size' in changes:
            return 'size_transform'
        else:
            return 'property_transform'
    
    def _extract_conditions(self, 
                          source: Pattern, 
                          target: Pattern, 
                          changes: Dict) -> Dict:
        """Extract conditions under which the transformation applies"""
        conditions = {}
        
        # Look for preserved properties
        preserved = set(source.properties.keys()) & set(target.properties.keys())
        preserved = {k: source.properties[k] for k in preserved 
                    if source.properties[k] == target.properties[k]}
        if preserved:
            conditions['preserved'] = preserved
        
        # Look for relative changes
        if 'position' in changes:
            src_pos = source.properties['position']
            tgt_pos = target.properties['position']
            conditions['relative_movement'] = {
                'dx': tgt_pos[0] - src_pos[0],
                'dy': tgt_pos[1] - src_pos[1]
            }
        
        return conditions
    
    def _calculate_transform_confidence(self,
                                      source: Pattern,
                                      target: Pattern,
                                      transform_type: str,
                                      conditions: Dict) -> float:
        """Calculate confidence in transformation identification"""
        confidence = 0.5  # Base confidence
        
        # Higher confidence for simpler transformations
        if transform_type == 'spatial_transform':
            confidence += 0.2
        elif transform_type == 'value_transform':
            confidence += 0.15
            
        # Higher confidence with more preserved properties
        if 'preserved' in conditions:
            confidence += len(conditions['preserved']) * 0.05
            
        # Higher confidence with clear relative changes
        if 'relative_movement' in conditions:
            mv = conditions['relative_movement']
            if abs(mv['dx']) <= 1 and abs(mv['dy']) <= 1:
                confidence += 0.1
                
        return min(confidence, 1.0)
