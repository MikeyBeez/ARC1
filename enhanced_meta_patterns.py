"""
Enhanced meta-pattern detection and abstraction for ARC challenge.
Integrates pattern transformation, abstraction, and context analysis.
"""

from typing import Dict, List, Optional
from pattern_core import Pattern, PatternTransformation, AbstractPattern
from pattern_transformations import PatternTransformationAnalyzer
from pattern_abstraction import PatternAbstractionAnalyzer
from pattern_context import PatternContextAnalyzer

class EnhancedMetaPatterns:
    def __init__(self, base_hierarchy):
        self.hierarchy = base_hierarchy
        self.transformation_analyzer = PatternTransformationAnalyzer()
        self.abstraction_analyzer = PatternAbstractionAnalyzer()
        self.context_analyzer = PatternContextAnalyzer()
        
    def analyze_pattern(self, pattern: Pattern, grid_context: Dict) -> Dict:
        """Complete analysis of a pattern"""
        return {
            'context_sensitivity': self.context_analyzer.analyze_context_sensitivity(
                pattern, grid_context),
            'abstractions': self.abstraction_analyzer.find_abstract_patterns([pattern]),
            'applicability': self.context_analyzer.predict_pattern_applicability(
                pattern, grid_context)
        }
        
    def analyze_transformation(self, 
                             before_patterns: List[Pattern],
                             after_patterns: List[Pattern]) -> List[PatternTransformation]:
        """Analyze pattern transformations"""
        return self.transformation_analyzer.analyze_pattern_transformations(
            before_patterns, after_patterns)
            
    def find_abstractions(self) -> List[AbstractPattern]:
        """Find abstract patterns across all patterns"""
        all_patterns = (
            self.hierarchy.atomic_patterns +
            self.hierarchy.composite_patterns +
            self.hierarchy.structural_patterns
        )
        return self.abstraction_analyzer.find_abstract_patterns(all_patterns)
