"""
Simple Router

Basic routing engine for connecting placed devices.
Uses Manhattan routing with minimal layer assignment.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from openeda.netlist.parser import Device, Netlist
from openeda.placement.simple import Placement, DevicePosition, Point


@dataclass(frozen=True)
class Segment:
    """A single wire segment."""
    
    x1: float
    y1: float
    x2: float
    y2: float
    layer: str  # e.g., "met1", "met2"
    width: float = 0.14  # Default metal width in microns
    
    @property
    def length(self) -> float:
        """Calculate segment length."""
        return abs(self.x2 - self.x1) + abs(self.y2 - self.y1)
    
    @property
    def is_horizontal(self) -> bool:
        """True if segment is horizontal."""
        return self.y1 == self.y2
    
    @property
    def is_vertical(self) -> bool:
        """True if segment is vertical."""
        return self.x1 == self.x2


@dataclass
class Route:
    """A complete route for a single net."""
    
    net_name: str
    segments: list[Segment] = field(default_factory=list)
    
    @property
    def total_length(self) -> float:
        """Sum of all segment lengths."""
        return sum(seg.length for seg in self.segments)
    
    @property
    def via_count(self) -> int:
        """Count layer transitions (simplified)."""
        if len(self.segments) < 2:
            return 0
        count = 0
        for i in range(1, len(self.segments)):
            if self.segments[i].layer != self.segments[i - 1].layer:
                count += 1
        return count


@dataclass
class Routing:
    """Complete routing result for a circuit."""
    
    routes: dict[str, Route] = field(default_factory=dict)
    pdk: str = "sky130"
    
    @property
    def total_wire_length(self) -> float:
        """Sum of all route lengths."""
        return sum(r.total_length for r in self.routes.values())
    
    @property
    def total_via_count(self) -> int:
        """Sum of all vias."""
        return sum(r.via_count for r in self.routes.values())


class SimpleRouter:
    """
    Manhattan router for analog circuits.
    
    Routes nets using L-shaped paths between device terminals.
    Assigns layers based on direction (horizontal = met1, vertical = met2).
    """
    
    # Layer assignments
    HORIZONTAL_LAYER: str = "met1"
    VERTICAL_LAYER: str = "met2"
    DEFAULT_WIDTH: float = 0.14  # microns
    
    # Terminal offset from device center (simplified)
    TERMINAL_OFFSET: float = 0.5
    
    def __init__(self, pdk: str = "sky130") -> None:
        self.pdk = pdk
        self._routing = Routing(pdk=pdk)
        self._placement: Optional[Placement] = None
    
    def route(
        self,
        circuit: Netlist,
        placement: Placement,
    ) -> Routing:
        """
        Route all nets in the circuit.
        
        For each net:
        1. Find all devices connected to the net
        2. Get their terminal positions from placement
        3. Create Manhattan routing tree
        
        Args:
            circuit: Parsed netlist
            placement: Device placement result
            
        Returns:
            Complete routing with all nets wired
        """
        self._routing = Routing(pdk=self.pdk)
        self._placement = placement
        
        if not circuit.nets:
            return self._routing
        
        # Build net-to-devices mapping
        net_devices = self._build_net_map(circuit)
        
        # Route each net
        for net_name, devices in net_devices.items():
            if len(devices) < 2:
                continue  # Single-device nets don't need routing
            
            route = self._route_net(net_name, devices)
            self._routing.routes[net_name] = route
        
        return self._routing
    
    def _build_net_map(self, circuit: Netlist) -> dict[str, list[Device]]:
        """Map each net to the devices connected to it."""
        net_map: dict[str, list[Device]] = {}
        
        for device in circuit.devices:
            for node in device.nodes:
                net_map.setdefault(node, []).append(device)
        
        return net_map
    
    def _route_net(self, net_name: str, devices: list[Device]) -> Route:
        """
        Create Manhattan route for a single net.
        
        Uses a simple star topology: all devices connect to the
        centroid of their positions.
        """
        route = Route(net_name=net_name)
        
        # Get terminal positions for all devices
        terminals = [
            self._get_terminal_position(d) for d in devices
        ]
        
        if len(terminals) < 2:
            return route
        
        # Use first terminal as anchor (simplified star routing)
        anchor = terminals[0]
        
        for terminal in terminals[1:]:
            segments = self._create_manhattan_path(anchor, terminal)
            route.segments.extend(segments)
        
        return route
    
    def _get_terminal_position(self, device: Device) -> Point:
        """Get the connection point for a device."""
        if self._placement is None:
            raise RuntimeError("Placement not set")
        
        pos = self._placement.positions.get(device.name)
        if pos is None:
            raise ValueError(f"Device {device.name} not placed")
        
        # Use device center as terminal (simplified)
        return pos.center
    
    def _create_manhattan_path(
        self,
        start: Point,
        end: Point,
    ) -> list[Segment]:
        """
        Create L-shaped Manhattan path between two points.
        
        Route: start → (end.x, start.y) → end
        Horizontal first, then vertical.
        """
        segments: list[Segment] = []
        
        # Horizontal segment
        if start.x != end.x:
            segments.append(Segment(
                x1=start.x,
                y1=start.y,
                x2=end.x,
                y2=start.y,
                layer=self.HORIZONTAL_LAYER,
                width=self.DEFAULT_WIDTH,
            ))
        
        # Vertical segment
        if start.y != end.y:
            segments.append(Segment(
                x1=end.x,
                y1=start.y,
                x2=end.x,
                y2=end.y,
                layer=self.VERTICAL_LAYER,
                width=self.DEFAULT_WIDTH,
            ))
        
        return segments
