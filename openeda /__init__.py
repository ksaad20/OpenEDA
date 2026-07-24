"""
OpenEDA: AI-powered Electronic Design Automation

OpenEDA is an open-source EDA tool that leverages artificial intelligence
to automate analog and mixed-signal circuit design. Built on the
Circuit-Bench benchmark, OpenEDA aims to make professional-grade chip
design accessible to researchers, startups, and educators.

License: Apache 2.0
Repository: https://github.com/ksaad20/OpenEDA
"""

__version__ = "0.1.0"
__author__ = "OpenEDA Project Maintainers"
__email__ = "kazisaadasif29@gmail.com"
__license__ = "Apache-2.0"

# Package-level imports for convenient access
from openeda.netlist.parser import NetlistParser
from openeda.placement.placer import SimplePlacer
from openeda.routing.router import SimpleRouter
from openeda.export.gds import GDSExporter

__all__ = [
    "NetlistParser",
    "SimplePlacer",
    "SimpleRouter",
    "GDSExporter",
    "__version__",
]
