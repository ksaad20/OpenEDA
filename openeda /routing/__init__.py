"""
Routing algorithms for OpenEDA.

Implements routing engines for analog and
mixed-signal layouts.
"""

from .simple import SimpleRouter

__all__ = [
    "SimpleRouter",
]
