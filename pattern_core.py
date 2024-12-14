"""
Core classes and data structures for enhanced pattern analysis.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Any, Optional
from pattern_hierarchy import Pattern, PatternLevel, PatternHierarchy

@dataclass
class PatternTransformation:
    """Represents how a pattern transforms"""
    source_pattern: Pattern
    target_pattern: Pattern
    transform_type: str
    conditions: Dict[str, Any]
    confidence: float

@dataclass
class AbstractPattern:
    """Template for a generalized pattern"""
    template_type: str
    variables: Dict[str, List[Any]]
    constraints: List[Dict]
    instantiations: List[Pattern]
    abstraction_level: float  # 0 = concrete, 1 = fully abstract
