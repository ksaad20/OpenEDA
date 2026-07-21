"""
SPICE Netlist Parser

Parses SPICE-format netlists into a structured circuit representation
for layout generation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator


@dataclass(frozen=True)
class Device:
    """Represents a single circuit device (transistor, resistor, capacitor, etc.)."""
    
    name: str
    device_type: str
    nodes: tuple[str, ...]
    parameters: dict[str, float | str]
    
    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Device name cannot be empty")
        if not self.device_type:
            raise ValueError("Device type cannot be empty")


@dataclass
class Netlist:
    """Structured representation of a parsed SPICE netlist."""
    
    title: str = ""
    devices: list[Device] = field(default_factory=list)
    nets: set[str] = field(default_factory=set)
    
    @property
    def device_count(self) -> int:
        """Return total number of devices."""
        return len(self.devices)
    
    @property
    def net_count(self) -> int:
        """Return total number of unique nets."""
        return len(self.nets)
    
    def devices_by_type(self, device_type: str) -> list[Device]:
        """Filter devices by type (e.g., 'M' for MOSFET, 'R' for resistor)."""
        return [d for d in self.devices if d.device_type.upper() == device_type.upper()]


class NetlistParser:
    """
    Parser for SPICE-format netlists.
    
    Supports basic SPICE syntax including:
    - Title line
    - Device instantiation (M, R, C, L, I, V)
    - Comment lines (starting with *)
    - Continuation lines (+)
    - .END statement
    """
    
    # Device type prefixes in SPICE
    DEVICE_PREFIXES = frozenset({"M", "R", "C", "L", "I", "V", "D", "Q"})
    
    # Pattern to match a device line: NAME NODE1 NODE2 ... [PARAM=VALUE ...]
    DEVICE_PATTERN = re.compile(
        r"^(?P<name>[A-Z][A-Za-z0-9_]*)\s+"
        r"(?P<nodes>(?:\S+\s+)+)"
        r"(?P<params>.*)$"
    )
    
    def __init__(self) -> None:
        self._circuit = Netlist()
    
    def parse(self, filepath: Path | str) -> Netlist:
        """
        Parse a SPICE netlist file into a Netlist object.
        
        Args:
            filepath: Path to the SPICE netlist file
            
        Returns:
            Parsed Netlist representation
            
        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the netlist contains invalid syntax
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Netlist file not found: {path}")
        
        self._circuit = Netlist()
        lines = self._read_lines(path)
        
        # First non-comment line is the title
        for line in lines:
            if line and not line.startswith("*"):
                self._circuit.title = line
                break
        
        # Parse remaining lines
        for line in lines[1:]:
            self._parse_line(line)
        
        return self._circuit
    
    def _read_lines(self, filepath: Path) -> list[str]:
        """Read and preprocess netlist lines."""
        with open(filepath, "r", encoding="utf-8") as f:
            raw_lines = f.readlines()
        
        processed: list[str] = []
        current_line = ""
        
        for raw in raw_lines:
            stripped = raw.strip()
            
            # Skip empty lines
            if not stripped:
                continue
            
            # Handle continuation lines
            if stripped.startswith("+"):
                current_line += " " + stripped[1:].strip()
            else:
                if current_line:
                    processed.append(current_line)
                current_line = stripped
        
        if current_line:
            processed.append(current_line)
        
        return processed
    
    def _parse_line(self, line: str) -> None:
        """Parse a single netlist line."""
        # Skip comments
        if line.startswith("*") or line.startswith("$"):
            return
        
        # Skip control statements (for now)
        if line.startswith("."):
            return
        
        # Try to parse as device
        device = self._parse_device(line)
        if device:
            self._circuit.devices.append(device)
            self._circuit.nets.update(device.nodes)
    
    def _parse_device(self, line: str) -> Device | None:
        """Parse a device instantiation line."""
        if not line:
            return None
        
        # Extract device type from first character
        first_char = line[0].upper()
        if first_char not in self.DEVICE_PREFIXES:
            return None
        
        match = self.DEVICE_PATTERN.match(line)
        if not match:
            raise ValueError(f"Invalid device syntax: {line}")
        
        name = match.group("name")
        device_type = first_char
        
        # Parse nodes
        nodes_str = match.group("nodes").strip()
        nodes = tuple(nodes_str.split())
        
        # Parse parameters
        params_str = match.group("params").strip()
        parameters = self._parse_parameters(params_str)
        
        return Device(
            name=name,
            device_type=device_type,
            nodes=nodes,
            parameters=parameters,
        )
    
    def _parse_parameters(self, params_str: str) -> dict[str, float | str]:
        """Parse parameter assignments like W=1.0u L=0.18u."""
        parameters: dict[str, float | str] = {}
        
        if not params_str:
            return parameters
        
        # Match PARAM=VALUE pairs
        param_pattern = re.compile(r"(\w+)=([^\s]+)")
        
        for match in param_pattern.finditer(params_str):
            key = match.group(1)
            value_str = match.group(2)
            
            # Try to parse as numeric
            try:
                value = self._parse_numeric(value_str)
            except ValueError:
                value = value_str
            
            parameters[key] = value
        
        return parameters
    
    @staticmethod
    def _parse_numeric(value: str) -> float:
        """Parse a SPICE numeric value with unit suffix."""
        value = value.strip().upper()
        
        # Handle unit suffixes
        multipliers = {
            "T": 1e12, "G": 1e9, "MEG": 1e6, "K": 1e3,
            "M": 1e-3, "U": 1e-6, "N": 1e-9, "P": 1e-12, "F": 1e-15,
        }
        
        for suffix, mult in multipliers.items():
            if value.endswith(suffix):
                num_part = value[:-len(suffix)]
                return float(num_part) * mult
        
        return float(value)
