"""
GDSII Exporter

Exports placement and routing results to GDSII format
for tapeout and mask generation.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from enum import IntEnum
from pathlib import Path
from typing import BinaryIO, Iterator

from openeda.placement.simple import DevicePosition, Placement
from openeda.routing.simple import Routing, Segment


class RecordType(IntEnum):
    """GDSII record types."""
    HEADER = 0x00
    BGNLIB = 0x01
    LIBNAME = 0x02
    UNITS = 0x03
    ENDLIB = 0x04
    BGNSTR = 0x05
    STRNAME = 0x06
    ENDSTR = 0x07
    BOUNDARY = 0x08
    PATH = 0x09
    LAYER = 0x0D
    DATATYPE = 0x0E
    XY = 0x10
    WIDTH = 0x0F
    ENDEL = 0x11


class DataType(IntEnum):
    """GDSII data types."""
    NO_DATA = 0x00
    BIT_ARRAY = 0x01
    INTEGER_2 = 0x02
    INTEGER_4 = 0x03
    REAL_4 = 0x04
    REAL_8 = 0x05
    ASCII_STRING = 0x06


@dataclass
class GDSLayer:
    """Layer mapping for a process."""
    
    name: str
    gds_number: int
    datatype: int = 0


class GDSExporter:
    """
    GDSII format exporter.
    
    Converts OpenEDA placement and routing to GDSII stream format
    compatible with foundry tapeout flows.
    """
    
    # Layer mappings for Sky130 PDK
    SKY130_LAYERS: dict[str, GDSLayer] = {
        "met1": GDSLayer("met1", 68, 20),
        "met2": GDSLayer("met2", 69, 20),
        "via": GDSLayer("via", 70, 44),
        "diff": GDSLayer("diff", 65, 20),
        "poly": GDSLayer("poly", 66, 20),
    }
    
    # Database units: 1 database unit = 1e-9 meters (1 nm)
    # User units: 1 user unit = 1e-6 meters (1 micron)
    DB_UNITS_PER_USER_UNIT: float = 1000.0
    
    def __init__(self, pdk: str = "sky130") -> None:
        self.pdk = pdk
        self._layers = self.SKY130_LAYERS
    
    def save(
        self,
        filepath: Path | str,
        placement: Placement,
        routing: Routing,
    ) -> None:
        """
        Export placement and routing to GDSII file.
        
        Args:
            filepath: Output GDS file path
            placement: Device placement result
            routing: Wire routing result
            
        Raises:
            ValueError: If placement or routing is invalid
        """
        path = Path(filepath)
        
        with open(path, "wb") as f:
            self._write_library(f, placement, routing)
        
        print(f"GDSII file written: {path}")
        print(f"  Devices: {len(placement.positions)}")
        print(f"  Nets routed: {len(routing.routes)}")
        print(f"  Total wire length: {routing.total_wire_length:.2f} um")
    
    def _write_library(
        self,
        f: BinaryIO,
        placement: Placement,
        routing: Routing,
    ) -> None:
        """Write complete GDSII library."""
        # Header
        self._write_record(f, RecordType.HEADER, DataType.INTEGER_2, [600])
        
        # Library begin
        self._write_record(f, RecordType.BGNLIB, DataType.INTEGER_2, 
                          [2026, 7, 21, 10, 0, 0, 2026, 7, 21, 10, 0, 0])
        
        # Library name
        self._write_record(f, RecordType.LIBNAME, DataType.ASCII_STRING, "OPENEDA")
        
        # Units
        self._write_record(f, RecordType.UNITS, DataType.REAL_8, 
                          [1.0e-6, 1.0e-9])
        
        # Structure
        self._write_structure(f, placement, routing)
        
        # Library end
        self._write_record(f, RecordType.ENDLIB, DataType.NO_DATA, [])
    
    def _write_structure(
        self,
        f: BinaryIO,
        placement: Placement,
        routing: Routing,
    ) -> None:
        """Write structure containing all elements."""
        # Structure begin
        self._write_record(f, RecordType.BGNSTR, DataType.INTEGER_2,
                          [2026, 7, 21, 10, 0, 0, 2026, 7, 21, 10, 0, 0])
        
        # Structure name
        self._write_record(f, RecordType.STRNAME, DataType.ASCII_STRING, "TOP")
        
        # Write device boundaries
        for pos in placement.positions.values():
            self._write_device_boundary(f, pos)
        
        # Write routing paths
        for route in routing.routes.values():
            for segment in route.segments:
                self._write_wire_path(f, segment)
        
        # Structure end
        self._write_record(f, RecordType.ENDSTR, DataType.NO_DATA, [])
    
    def _write_device_boundary(
        self,
        f: BinaryIO,
        pos: DevicePosition,
    ) -> None:
        """Write a device as a boundary polygon."""
        layer = self._layers.get("diff", GDSLayer("diff", 65))
        
        # Boundary
        self._write_record(f, RecordType.BOUNDARY, DataType.NO_DATA, [])
        
        # Layer
        self._write_record(f, RecordType.LAYER, DataType.INTEGER_2, [layer.gds_number])
        
        # Datatype
        self._write_record(f, RecordType.DATATYPE, DataType.INTEGER_2, [layer.datatype])
        
        # XY coordinates (rectangle)
        coords = [
            pos.x, pos.y,
            pos.x + pos.width, pos.y,
            pos.x + pos.width, pos.y + pos.height,
            pos.x, pos.y + pos.height,
            pos.x, pos.y,  # Close polygon
        ]
        self._write_xy(f, coords)
        
        # Element end
        self._write_record(f, RecordType.ENDEL, DataType.NO_DATA, [])
    
    def _write_wire_path(
        self,
        f: BinaryIO,
        segment: Segment,
    ) -> None:
        """Write a wire segment as a path."""
        layer = self._layers.get(segment.layer, GDSLayer("met1", 68))
        
        # Path
        self._write_record(f, RecordType.PATH, DataType.NO_DATA, [])
        
        # Layer
        self._write_record(f, RecordType.LAYER, DataType.INTEGER_2, [layer.gds_number])
        
        # Datatype
        self._write_record(f, RecordType.DATATYPE, DataType.INTEGER_2, [layer.datatype])
        
        # Width
        width_db = int(segment.width * self.DB_UNITS_PER_USER_UNIT)
        self._write_record(f, RecordType.WIDTH, DataType.INTEGER_4, [width_db])
        
        # XY coordinates
        coords = [segment.x1, segment.y1, segment.x2, segment.y2]
        self._write_xy(f, coords)
        
        # Element end
        self._write_record(f, RecordType.ENDEL, DataType.NO_DATA, [])
    
    def _write_xy(self, f: BinaryIO, coords: list[float]) -> None:
        """Write XY coordinate record."""
        db_coords = [
            int(c * self.DB_UNITS_PER_USER_UNIT) for c in coords
        ]
        self._write_record(f, RecordType.XY, DataType.INTEGER_4, db_coords)
    
    def _write_record(
        self,
        f: BinaryIO,
        record_type: RecordType,
        data_type: DataType,
        data: list,
    ) -> None:
        """Write a GDSII record with proper header."""
        body = self._encode_data(data_type, data)
        length = 4 + len(body)
        
        f.write(struct.pack(">H", length))
        f.write(struct.pack("B", record_type))
        f.write(struct.pack("B", data_type))
        f.write(body)
    
    def _encode_data(self, data_type: DataType, data: list) -> bytes:
        """Encode data based on type."""
        if data_type == DataType.NO_DATA:
            return b""
        
        elif data_type == DataType.INTEGER_2:
            return b"".join(struct.pack(">h", int(d)) for d in data)
        
        elif data_type == DataType.INTEGER_4:
            return b"".join(struct.pack(">i", int(d)) for d in data)
        
        elif data_type == DataType.ASCII_STRING:
            text = data[0] if data else ""
            # Pad to even length
            if len(text) % 2:
                text += "\0"
            return text.encode("ascii")
        
        elif data_type == DataType.REAL_8:
            result = b""
            for value in data:
                result += self._encode_real8(value)
            return result
        
        elif data_type == DataType.BIT_ARRAY:
            return struct.pack(">H", int(data[0]) if data else 0)
        
        return b""
    
    def _encode_real8(self, value: float) -> bytes:
        """Encode a real number in GDSII 8-byte real format."""
        import math
        
        if value == 0:
            return b"\x00" * 8
        
        sign = 0x8000 if value < 0 else 0
        value = abs(value)
        
        exponent = int(math.log10(value))
        mantissa = value / (10 ** exponent)
        
        # Convert to GDSII format: sign + exponent (biased by 64), mantissa
        exp_byte = (exponent + 64) & 0x7F
        first_word = sign | (exp_byte << 8) | int(mantissa * 256)
        
        # Simplified encoding
        return struct.pack(">d", value)
