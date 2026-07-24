"""
Placement algorithms for OpenEDA.

Provides device placement strategies for analog
and mixed-signal integrated circuit layouts.
"""

from .placer import SimplePlacer

__all__ = [
    "SimplePlacer",
]
