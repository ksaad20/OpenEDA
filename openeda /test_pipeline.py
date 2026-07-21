#!/usr/bin/env python3
"""
OpenEDA Pipeline Test

Runs the complete layout generation flow on the example OTA netlist.
"""

import sys
from pathlib import Path

# Add package to path if running from repo root
sys.path.insert(0, str(Path(__file__).parent))

from openeda.netlist.parser import NetlistParser
from openeda.placement.simple import SimplePlacer
from openeda.routing.simple import SimpleRouter
from openeda.export.gds import GDSExporter
from openeda.bench.evaluate import BenchmarkEvaluator


def main() -> int:
    """Run full pipeline test."""
    print("=" * 50)
    print("OpenEDA Pipeline Test")
    print("=" * 50)
    
    # Paths
    netlist_path = Path("examples/ota_2stage.sp")
    output_path = Path("output/ota_layout.gds")
    output_path.parent.mkdir(exist_ok=True)
    
    # Step 1: Parse netlist
    print("\n[1/5] Parsing netlist...")
    parser = NetlistParser()
    circuit = parser.parse(netlist_path)
    
    print(f"  Title: {circuit.title}")
    print(f"  Devices: {circuit.device_count}")
    print(f"  Nets: {circuit.net_count}")
    print(f"  MOSFETs: {len(circuit.devices_by_type('M'))}")
    print(f"  Capacitors: {len(circuit.devices_by_type('C'))}")
    
    # Step 2: Place devices
    print("\n[2/5] Placing devices...")
    placer = SimplePlacer(pdk="sky130")
    placement = placer.place(circuit)
    
    print(f"  Placed: {len(placement.positions)} devices")
    print(f"  Bounding box: {placement.width:.2f} x {placement.height:.2f} um")
    print(f"  Area: {placement.area:.2f} um^2")
    
    # Step 3: Route nets
    print("\n[3/5] Routing nets...")
    router = SimpleRouter(pdk="sky130")
    routing = router.route(circuit, placement)
    
    print(f"  Routed nets: {len(routing.routes)}")
    print(f"  Total wire length: {routing.total_wire_length:.2f} um")
    print(f"  Total vias: {routing.total_via_count}")
    
    # Step 4: Export GDS
    print("\n[4/5] Exporting GDSII...")
    exporter = GDSExporter(pdk="sky130")
    exporter.save(output_path, placement, routing)
    
    # Step 5: Evaluate
    print("\n[5/5] Evaluating metrics...")
    evaluator = BenchmarkEvaluator()
    result = evaluator.evaluate(
        task="analog_layout",
        model="openeda-v0.1",
        placement=placement,
        routing=routing,
        circuit_name="ota_2stage",
    )
    
    print(f"  Composite score: {result.metrics.score():.2f}")
    print(f"  Area: {result.metrics.total_area:.2f} um^2")
    print(f"  Wire length: {result.metrics.total_wire_length:.2f} um")
    print(f"  Est. capacitance: {result.metrics.estimated_capacitance:.2f} fF")
    
    # Save results
    evaluator.save_results("output/results.json")
    
    print("\n" + "=" * 50)
    print("Pipeline complete!")
    print(f"Output: {output_path.absolute()}")
    print("=" * 50)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
