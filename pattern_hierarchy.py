"""
Pattern hierarchy analysis for ARC challenge.
Analyzes relationships between detected patterns to understand transformation rules.
"""

import numpy as np
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum

class PatternLevel(Enum):
    """Hierarchy levels for patterns"""
    ATOMIC = 1      # Basic patterns like symmetry, color changes
    COMPOSITE = 2   # Combinations of atomic patterns
    STRUCTURAL = 3  # High-level organization patterns
    META = 4        # Patterns about how patterns change

@dataclass
class Pattern:
    """Representation of a detected pattern"""
    type: str
    level: PatternLevel
    properties: Dict
    confidence: float
    sub_patterns: List['Pattern'] = None
    
    def __post_init__(self):
        if self.sub_patterns is None:
            self.sub_patterns = []

class PatternHierarchy:
    """Analyzes and organizes patterns into hierarchical structures"""
    
    def __init__(self):
        self.atomic_patterns: List[Pattern] = []
        self.composite_patterns: List[Pattern] = []
        self.structural_patterns: List[Pattern] = []
        self.meta_patterns: List[Pattern] = []
        
    def analyze_pattern_relationships(self, 
                                   grid_patterns: Dict,
                                   transformation_data: Dict) -> Dict:
        """Analyze relationships between patterns to understand hierarchy"""
        patterns = self._extract_patterns(grid_patterns)
        
        # Analyze atomic patterns first
        atomic = self._identify_atomic_patterns(patterns)
        self.atomic_patterns.extend(atomic)
        
        # Find composite patterns
        composites = self._identify_composite_patterns(atomic)
        self.composite_patterns.extend(composites)
        
        # Identify structural patterns
        structural = self._identify_structural_patterns(composites)
        self.structural_patterns.extend(structural)
        
        # Look for meta-patterns in transformations
        meta = self._identify_meta_patterns(transformation_data)
        self.meta_patterns.extend(meta)
        
        return {
            'atomic': [self._pattern_to_dict(p) for p in atomic],
            'composite': [self._pattern_to_dict(p) for p in composites],
            'structural': [self._pattern_to_dict(p) for p in structural],
            'meta': [self._pattern_to_dict(p) for p in meta]
        }
        
    def _extract_patterns(self, grid_patterns: Dict) -> List[Dict]:
        """Extract pattern information from grid analysis"""
        patterns = []
        
        # Extract symmetry patterns
        if 'symmetry' in grid_patterns:
            sym_data = grid_patterns['symmetry']
            if sym_data.get('symmetry_found', False):
                for sym in sym_data.get('symmetry_types', []):
                    patterns.append({
                        'type': 'symmetry',
                        'subtype': sym['type'],
                        'properties': sym
                    })
                    
        # Extract progression patterns
        if 'progression' in grid_patterns:
            prog_data = grid_patterns['progression']
            if prog_data.get('progression_found', False):
                for prog in prog_data.get('progression_types', []):
                    patterns.append({
                        'type': 'progression',
                        'subtype': prog['type'],
                        'properties': prog
                    })
                    
        # Extract repetition patterns
        if 'repetition' in grid_patterns:
            rep_data = grid_patterns['repetition']
            if rep_data.get('repetition_found', False):
                for rep in rep_data.get('patterns', []):
                    patterns.append({
                        'type': 'repetition',
                        'subtype': rep['type'],
                        'properties': rep
                    })
                    
        # Extract spatial patterns
        if 'spatial' in grid_patterns:
            spatial_data = grid_patterns['spatial']
            if spatial_data.get('spatial_patterns_found', False):
                for spatial in spatial_data.get('patterns', []):
                    patterns.append({
                        'type': 'spatial',
                        'subtype': spatial['type'],
                        'properties': spatial
                    })
                    
        return patterns
        
    def _identify_atomic_patterns(self, patterns: List[Dict]) -> List[Pattern]:
        """Identify atomic (basic) patterns"""
        atomic = []
        
        for p in patterns:
            # Calculate confidence based on pattern properties
            confidence = self._calculate_pattern_confidence(p)
            
            # Create atomic pattern
            atomic.append(Pattern(
                type=f"{p['type']}_{p['subtype']}",
                level=PatternLevel.ATOMIC,
                properties=p['properties'],
                confidence=confidence
            ))
            
        return atomic
        
    def _identify_composite_patterns(self, 
                                   atomic_patterns: List[Pattern]) -> List[Pattern]:
        """Identify patterns that combine multiple atomic patterns"""
        composites = []
        
        # Look for co-occurring patterns
        for i, p1 in enumerate(atomic_patterns):
            for p2 in atomic_patterns[i+1:]:
                if self._patterns_compatible(p1, p2):
                    # Create composite pattern
                    composite = Pattern(
                        type=f"composite_{p1.type}_{p2.type}",
                        level=PatternLevel.COMPOSITE,
                        properties={
                            'components': [p1.type, p2.type],
                            'relationship': self._analyze_pattern_relationship(p1, p2)
                        },
                        confidence=min(p1.confidence, p2.confidence) * 0.9,
                        sub_patterns=[p1, p2]
                    )
                    composites.append(composite)
                    
        return composites
        
    def _identify_structural_patterns(self, 
                                    composite_patterns: List[Pattern]) -> List[Pattern]:
        """Identify high-level structural patterns"""
        structural = []
        
        # Look for patterns in how composites are arranged
        pattern_groups = self._group_related_patterns(composite_patterns)
        
        for group in pattern_groups:
            if len(group) > 1:
                relationship = self._analyze_group_relationship(group)
                structural.append(Pattern(
                    type=f"structural_{relationship['type']}",
                    level=PatternLevel.STRUCTURAL,
                    properties=relationship,
                    confidence=self._calculate_group_confidence(group),
                    sub_patterns=list(group)
                ))
                
        return structural
        
    def _identify_meta_patterns(self, 
                              transformation_data: Dict) -> List[Pattern]:
        """Identify patterns in how patterns transform"""
        meta = []
        
        if 'value_mappings' in transformation_data:
            for val, mapping in transformation_data['value_mappings'].items():
                if mapping['type'] == 'conditional':
                    meta.append(Pattern(
                        type='meta_conditional_mapping',
                        level=PatternLevel.META,
                        properties={
                            'value': val,
                            'conditions': mapping['conditions']
                        },
                        confidence=0.8
                    ))
                    
        if 'object_transforms' in transformation_data:
            for transform in transformation_data['object_transforms'].get('object_mappings', []):
                meta.append(Pattern(
                    type='meta_object_transform',
                    level=PatternLevel.META,
                    properties=transform,
                    confidence=0.7
                ))
                
        return meta
        
    def _calculate_pattern_confidence(self, pattern: Dict) -> float:
        """Calculate confidence score for a pattern"""
        # Base confidence on pattern properties
        confidence = 0.5  # Base confidence
        
        if pattern['type'] == 'symmetry':
            confidence += 0.3  # Symmetry patterns are usually reliable
        elif pattern['type'] == 'progression':
            # Higher confidence for consistent progressions
            props = pattern['properties']
            if 'sequence' in props and len(set(np.diff(props['sequence']))) == 1:
                confidence += 0.3
        elif pattern['type'] == 'repetition':
            # Higher confidence for clear repetitions
            props = pattern['properties']
            if props.get('count', 0) > 2:
                confidence += 0.2
        elif pattern['type'] == 'spatial':
            # Higher confidence for regular spatial arrangements
            props = pattern['properties']
            if 'regularity' in props:
                confidence += props['regularity'] * 0.3
                
        return min(confidence, 1.0)
        
    def _patterns_compatible(self, p1: Pattern, p2: Pattern) -> bool:
        """Check if two patterns can form a meaningful composite"""
        # Patterns of same type usually don't combine
        if p1.type.split('_')[0] == p2.type.split('_')[0]:
            return False
            
        # Check for conflicting properties
        props1 = set(p1.properties.keys())
        props2 = set(p2.properties.keys())
        
        conflicting_props = props1.intersection(props2)
        for prop in conflicting_props:
            if p1.properties[prop] != p2.properties[prop]:
                return False
                
        return True
        
    def _analyze_pattern_relationship(self, p1: Pattern, p2: Pattern) -> Dict:
        """Analyze how two patterns relate to each other"""
        return {
            'type': 'co-occurrence',
            'interaction': self._determine_interaction(p1, p2),
            'dependency': self._check_dependency(p1, p2)
        }
        
    def _determine_interaction(self, p1: Pattern, p2: Pattern) -> str:
        """Determine how patterns interact"""
        # Check for spatial interaction
        if 'position' in p1.properties and 'position' in p2.properties:
            pos1 = p1.properties['position']
            pos2 = p2.properties['position']
            if pos1 == pos2:
                return 'overlapping'
            else:
                return 'separate'
                
        # Check for value interaction
        if 'value' in p1.properties and 'value' in p2.properties:
            if p1.properties['value'] == p2.properties['value']:
                return 'same_value'
            else:
                return 'different_values'
                
        return 'independent'
        
    def _check_dependency(self, p1: Pattern, p2: Pattern) -> str:
        """Check if patterns depend on each other"""
        # Check if one pattern seems to require the other
        if any(p2.type in str(prop) for prop in p1.properties.values()):
            return 'p1_depends_on_p2'
        if any(p1.type in str(prop) for prop in p2.properties.values()):
            return 'p2_depends_on_p1'
            
        return 'independent'
        
    def _group_related_patterns(self, 
                              patterns: List[Pattern]) -> List[Set[Pattern]]:
        """Group related patterns together"""
        groups = []
        remaining = set(patterns)
        
        while remaining:
            pattern = remaining.pop()
            current_group = {pattern}
            
            # Find related patterns
            related = {p for p in remaining 
                      if self._patterns_related(pattern, p)}
            current_group.update(related)
            remaining.difference_update(related)
            
            groups.append(current_group)
            
        return groups
        
    def _patterns_related(self, p1: Pattern, p2: Pattern) -> bool:
        """Check if patterns are related"""
        # Check for shared sub-patterns
        if set(p1.sub_patterns).intersection(set(p2.sub_patterns)):
            return True
            
        # Check for related properties
        p1_values = {str(v) for v in p1.properties.values()}
        p2_values = {str(v) for v in p2.properties.values()}
        if p1_values.intersection(p2_values):
            return True
            
        return False
        
    def _analyze_group_relationship(self, patterns: Set[Pattern]) -> Dict:
        """Analyze relationship between a group of patterns"""
        types = [p.type for p in patterns]
        properties = {}
        
        for p in patterns:
            for key, value in p.properties.items():
                if key not in properties:
                    properties[key] = []
                properties[key].append(value)
                
        return {
            'type': 'pattern_group',
            'pattern_types': types,
            'shared_properties': {
                k: v[0] for k, v in properties.items()
                if all(x == v[0] for x in v)
            }
        }
        
    def _calculate_group_confidence(self, patterns: Set[Pattern]) -> float:
        """Calculate confidence for a group of patterns"""
        if not patterns:
            return 0.0
            
        # Base confidence on:
        # 1. Individual pattern confidences
        # 2. Number of shared properties
        # 3. Strength of relationships
        
        individual_conf = np.mean([p.confidence for p in patterns])
        
        # Check shared properties
        all_props = set()
        shared_props = set()
        
        for p in patterns:
            props = set(p.properties.keys())
            if not all_props:
                all_props = props
                shared_props = props
            else:
                shared_props.intersection_update(props)
                all_props.update(props)
                
        property_ratio = len(shared_props) / len(all_props) if all_props else 0
        
        # Adjust based on group size (prefer smaller, tighter groups)
        size_factor = 1.0 / (1 + np.log(len(patterns)))
        
        return min(individual_conf * (0.5 + 0.5 * property_ratio) * size_factor, 1.0)
        
    def _pattern_to_dict(self, pattern: Pattern) -> Dict:
        """Convert pattern to dictionary representation"""
        return {
            'type': pattern.type,
            'level': pattern.level.name,
            'properties': pattern.properties,
            'confidence': pattern.confidence,
            'sub_patterns': [self._pattern_to_dict(p) for p in pattern.sub_patterns]
            if pattern.sub_patterns else []
        }