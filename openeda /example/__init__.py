"""
Example circuits for OpenEDA.

Contains SPICE netlists and reference designs for testing
and demonstration purposes.
"""

from pathlib import Path

__all__ = ["EXAMPLE_DIR", "OTA_2STAGE"]

# Directory containing this file
EXAMPLE_DIR = Path(__file__).parent

# Common example files
OTA_2STAGE = EXAMPLE_DIR / "ota_2stage.sp"
