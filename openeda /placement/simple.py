
"""
Simple Placer

Basic placement engine for analog circuit devices.
Uses a naive grid-based approach suitable for small circuits.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

from openeda.netlist.parser import Device, Netlist


@dataclass(frozen=True)
class Point:
    """2D coordinate point."""
    
    x: float
    y: float
    
    def distance_to(self, other: Point) -> float:
        """Calculate Euclidean distance to another point."""
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


@dataclass
class DevicePosition:
    """Position and orientation of a placed device."""
    
    device: Device
    x: float
    y: float
    width: float
    height: float
    rotation: int = 0  # 0, 90, 180, 270 degrees
    
    @property
    def center(self) -> Point:
        """Return center point of device."""
        return Point(self.x + self.width / 2, self.y + self.height / 2)
    
    @property
    def bounding_box(self) -> tuple[Point, Point]:
        """Return (bottom_left, top_right) corners."""
        return (
            Point(self.x, self.y),
            Point(self.x + self.width, self.y + self.height),
        )


@dataclass
class Placement:
    """Result of a placement operation."""
    
    positions: dict[str, DevicePosition] = field(default_factory=dict)
    pdk: str = "sky130"
    
    @property
    def area(self) -> float:
        """Calculate bounding box area of placement."""
        if not self.positions:
            return 0.0
        
        min_x = min(p.x for p in self.positions.values())
        max_x = max(p.x + p.width for p in self.positions.values())
        min_y = min(p.y for p in self.positions.values())
        max_y = max(p.y + p.height for p in self.positions.values())
        
        return (max_x - min_x) * (max_y - min_y)
    
    @property
    def width(self) -> float:
        """Total width of placement bounding box."""
        if not self.positions:
            return 0.0
        return max(p.x + p.width for p in self.positions.values()) - min(p.x for p in self.positions.values())
    
    @property
    def height(self) -> float:
        """Total height of placement bounding box."""
        if not self.positions:
            return 0.0
        return max(p.y + p.height for p in self.positions.values()) - min(p.y for p in self.positions.values())


class SimplePlacer:
    """
    Grid-based placer for analog circuits.
    
    Places devices in a row-based layout with minimal overlap avoidance.
    Suitable for small op-amps and basic analog blocks.
    """
    
    # Default device dimensions by type (in microns)
    DEFAULT_DIMENSIONS: dict[str, tuple[float, float]] = {
        "M": (2.0, 1.0),   # MOSFET
        "R": (1.0, 0.5),   # Resistor
        "C": (1.5, 1.5),   # Capacitor
        "L": (2.0, 2.0),   # Inductor
        "D": (1.0, 1.0),   # Diode
        "Q": (2.0, 1.5),   # BJT
    }
    
    # Spacing between devices
    HORIZONTAL_SPACING: float = 1.0
    VERTICAL_SPACING: float = 1.0
    
    def __init__(self, pdk: str = "sky130") -> None:
        self.pdk = pdk
        self._placement = Placement(pdk=pdk)
    
    def place(self, circuit: Netlist) -> Placement:
        """
        Place all devices from a netlist.
        
        Uses a simple row-based algorithm:
        1. Group devices by type
        2. Place in rows with fixed spacing
        3. Center each row horizontally
        
        Args:
            circuit: Parsed netlist to place
            
        Returns:
            Placement result with all device positions
        """
        self._placement = Placement(pdk=self.pdk)
        
        if not circuit.devices:
            return self._placement
        
        # Group devices by type for organized placement
        devices_by_type: dict[str, list[Device]] = {}
        for device in circuit.devices:
            devices_by_type.setdefault(device.device_type, []).append(device)
        
        # Place devices in rows by type
        current_y = 0.0
        max_row_height = 0.0
        
        for device_type in sorted(devices_by_type.keys()):
            devices = devices_by_type[device_type]
            
            # Place row
            row_width, row_height = self._place_row(
                devices, current_y
            )
            
            current_y += row_height + self.VERTICAL_SPACING
            max_row_height = max(max_row_height, row_height)
        
        return self._placement
    
    def _place_row(
        self,
        devices: list[Device],
        y: float,
    ) -> tuple[float, float]:
        """
        Place a row of devices starting at y coordinate.
        
        Returns:
            Tuple of (total_width, max_height) for the row
        """
        current_x = 0.0
        max_height = 0.0
        
        for device in devices:
            width, height = self._get_device_dimensions(device)
            
            pos = DevicePosition(
                device=device,
                x=current_x,
                y=y,
                width=width,
                height=height,
                rotation=0,
            )
            
            self._placement.positions[device.name] = pos
            
            current_x += width + self.HORIZONTAL_SPACING
            max_height = max(max_height, height)
        
        # Remove trailing spacing
        total_width = current_x - self.HORIZONTAL_SPACING if devices else 0.0
        
        return total_width, max_height
    
    def _get_device_dimensions(self, device: Device) -> tuple[float, float]:
        """
        Determine device dimensions from parameters or defaults.
        
        For MOSFETs, uses W and L parameters if available.
        """
        device_type = device.device_type.upper()
        
        # Try to get dimensions from device parameters
        if device_type == "M":
            width = self._extract_dimension(device.parameters, "W", 2.0)
            height = self._extract_dimension(device.parameters, "L", 1.0)
            return width, height
        
        # Use default dimensions for other device types
        return self.DEFAULT_DIMENSIONS.get(device_type, (1.0, 1.0))
    
    @staticmethod
    def _extract_dimension(
        params: dict[str, float | str],
        key: str,
        default: float,
    ) -> float:
        """Extract a dimension value from device parameters."""
        value = params.get(key)
        if isinstance(value, (int, float)):
            return float(value)
        return default
