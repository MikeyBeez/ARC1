"""
Pattern abstraction and generalization analysis.
"""

import numpy as np
from typing import Dict, List, Optional, Set, Any
from pattern_core import AbstractPattern, Pattern

class PatternAbstractionAnalyzer:
    def __init__(self):
        self.abstractions: List[AbstractPattern] = []
    
    def find_abstract_patterns(self, patterns: List[Pattern]) -> List[AbstractPattern]:
        """Find abstract patterns that generalize concrete patterns"""
        # Group related patterns
        pattern_groups = self._group_similar_patterns(patterns)
        
        # Find abstractions for each group
        for group in pattern_groups:
            abstraction = self._extract_abstract_pattern(group)
            if abstraction:
                self.abstractions.append(abstraction)
        
        return self.abstractions
    
    def _group_similar_patterns(self, patterns: List[Pattern]) -> List[Set[Pattern]]:
        """Group patterns that might share an abstract form"""
        groups = []
        remaining = set(patterns)
        
        while remaining:
            pattern = remaining.pop()
            current_group = {pattern}
            
            # Find similar patterns
            similar = {p for p in remaining 
                      if self._patterns_abstractly_similar(pattern, p)}
            current_group.update(similar)
            remaining.difference_update(similar)
            
            if len(current_group) > 1:  # Only keep groups with multiple patterns
                groups.append(current_group)
        
        return groups
    
    def _patterns_abstractly_similar(self, p1: Pattern, p2: Pattern) -> bool:
        """Check if patterns might share an abstract form"""
        # Check for structural similarity
        if p1.level != p2.level:
            return False
            
        # Compare property structure
        p1_props = set(p1.properties.keys())
        p2_props = set(p2.properties.keys())
        if len(p1_props & p2_props) < min(len(p1_props), len(p2_props)) * 0.5:
            return False
            
        # Compare sub-pattern structure
        if len(p1.sub_patterns or []) != len(p2.sub_patterns or []):
            return False
            
        return True
    
    def _extract_abstract_pattern(self, patterns: Set[Pattern]) -> Optional[AbstractPattern]:
        """Extract abstract pattern from a group of similar patterns"""
        if not patterns:
            return None
            
        # Find common structure
        common_props = self._find_common_properties(patterns)
        if not common_props:
            return None
            
        # Extract variables
        variables = self._extract_variables(patterns, common_props)
        
        # Extract constraints
        constraints = self._extract_constraints(patterns, variables)
        
        # Calculate abstraction level
        abstraction_level = self._calculate_abstraction_level(
            patterns, variables, constraints)
        
        return AbstractPattern(
            template_type=self._determine_template_type(patterns),
            variables=variables,
            constraints=constraints,
            instantiations=list(patterns),
            abstraction_level=abstraction_level
        )
    
    def _find_common_properties(self, patterns: Set[Pattern]) -> Dict[str, type]:
        """Find properties common to all patterns"""
        if not patterns:
            return {}
            
        common_props = {}
        first = next(iter(patterns))
        
        for key, value in first.properties.items():
            if all(key in p.properties for p in patterns):
                common_props[key] = type(value)
                
        return common_props
    
    def _extract_variables(self, 
                         patterns: Set[Pattern], 
                         common_props: Dict[str, type]) -> Dict[str, List[Any]]:
        """Extract variable elements from patterns"""
        variables = {}
        
        for prop in common_props:
            values = {p.properties[prop] for p in patterns}
            if len(values) > 1:
                variables[prop] = list(values)
                
        return variables
    
    def _extract_constraints(self, 
                           patterns: Set[Pattern],
                           variables: Dict[str, List[Any]]) -> List[Dict]:
        """Extract constraints on pattern variables"""
        constraints = []
        
        # Find value range constraints
        for var, values in variables.items():
            if all(isinstance(v, (int, float)) for v in values):
                constraints.append({
                    'type': 'range',
                    'variable': var,
                    'min': min(values),
                    'max': max(values)
                })
            
        # Find relationship constraints
        for p1_var, p1_values in variables.items():
            for p2_var, p2_values in variables.items():
                if p1_var < p2_var:  # Avoid duplicate constraints
                    relations = self._find_value_relations(
                        p1_values, p2_values, patterns, p1_var, p2_var)
                    if relations:
                        constraints.append({
                            'type': 'relationship',
                            'variables': [p1_var, p2_var],
                            'relations': relations
                        })
        
        return constraints

    def _find_value_relations(self,
                            values1: List[Any],
                            values2: List[Any],
                            patterns: Set[Pattern],
                            var1: str,
                            var2: str) -> Optional[Dict]:
        """Find relationships between variable values"""
        relations = []
        
        pairs = [(p.properties[var1], p.properties[var2])
                for p in patterns
                if var1 in p.properties and var2 in p.properties]
        
        if all(isinstance(v1, (int, float)) and isinstance(v2, (int, float))
              for v1, v2 in pairs):
            # Look for numeric relationships
            diffs = [v2 - v1 for v1, v2 in pairs]
            if len(set(diffs)) == 1:
                relations.append({
                    'type': 'arithmetic',
                    'operation': 'add',
                    'value': diffs[0]
                })
            
            ratios = [v2 / v1 for v1, v2 in pairs if v1 != 0]
            if len(set(ratios)) == 1:
                relations.append({
                    'type': 'arithmetic',
                    'operation': 'multiply',
                    'value': ratios[0]
                })
        
        return relations if relations else None
    
    def _calculate_abstraction_level(self,
                                   patterns: Set[Pattern],
                                   variables: Dict[str, List[Any]],
                                   constraints: List[Dict]) -> float:
        """Calculate how abstract a pattern is (0 = concrete, 1 = fully abstract)"""
        if not patterns:
            return 0.0
            
        # Calculate variable ratio
        total_props = len(next(iter(patterns)).properties)
        var_ratio = len(variables) / total_props if total_props > 0 else 0
        
        # Calculate constraint ratio
        max_constraints = len(variables) * (len(variables) - 1) / 2
        constraint_ratio = len(constraints) / max_constraints if max_constraints > 0 else 1
        
        # Calculate instantiation diversity
        unique_types = len({p.type for p in patterns})
        diversity_ratio = (unique_types - 1) / len(patterns) if len(patterns) > 1 else 0
        
        # Combine factors
        return (var_ratio * 0.4 + (1 - constraint_ratio) * 0.3 + diversity_ratio * 0.3)
    
    def _determine_template_type(self, patterns: Set[Pattern]) -> str:
        """Determine the type of abstract template"""
        types = {p.type.split('_')[0] for p in patterns}
        if len(types) == 1:
            return f"abstract_{next(iter(types))}"
        return "abstract_mixed"
