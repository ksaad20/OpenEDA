"""
Placement algorithms for OpenEDA.

Provides device placement strategies for analog
and mixed-signal integrated circuit layouts.
"""

from .simple import SimplePlacer

__all__ = [
    "SimplePlacer",
]
