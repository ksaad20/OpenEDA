#!/usr/bin/env python3
"""
Functional pipeline test for OpenEDA.

This script performs an end-to-end smoke test:
1. Parse an example netlist
2. Place devices
3. Route nets
4. Export GDS
5. Evaluate benchmark metrics

Exit code:
    0 = success
    1 = failure
"""
from pathlib import Path
import sys
import traceback

# Repository root
# Add repo root to path BEFORE any openeda imports
import os
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import openeda
from openeda.netlist.parser import NetlistParser
from openeda.placement.placer import SimplePlacer
from openeda.routing.router import SimpleRouter
from openeda.export.gds import GDSExporter
from openeda.bench.evaluate import BenchmarkEvaluator


def banner(text: str):
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70)


def main() -> int:
    try:
        banner("OpenEDA Functional Pipeline Test")

        example = ROOT / "examples" / "ota_2stage.sp"

        if not example.exists():
            print(f"ERROR: Example netlist not found:\n{example}")
            return 1

        output_dir = ROOT / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_gds = output_dir / "ota_layout.gds"
        output_json = output_dir / "results.json"

        ############################################################
        # Parse
        ############################################################

        print("[1/5] Parsing netlist")

        parser = NetlistParser()
        circuit = parser.parse(example)

        print(f"Title      : {getattr(circuit,'title','Unknown')}")
        print(f"Devices    : {getattr(circuit,'device_count',0)}")
        print(f"Nets       : {getattr(circuit,'net_count',0)}")

        ############################################################
        # Placement
        ############################################################

        print("\n[2/5] Placement")

        placer = SimplePlacer(pdk="sky130")
        placement = placer.place(circuit)

        print(f"Area       : {placement.area:.2f}")
        print(f"Width      : {placement.width:.2f}")
        print(f"Height     : {placement.height:.2f}")

        ############################################################
        # Routing
        ############################################################

        print("\n[3/5] Routing")

        router = SimpleRouter(pdk="sky130")
        routing = router.route(circuit, placement)

        print(f"Routes     : {len(routing.routes)}")
        print(f"Wire length: {routing.total_wire_length:.2f}")

        ############################################################
        # Export
        ############################################################

        print("\n[4/5] Export")

        exporter = GDSExporter(pdk="sky130")
        exporting = exporter.save(output_gds, placement, routing)

        if output_gds.exists():
            print("✓ GDS generated")
        else:
            print("✗ GDS export failed")
            return 1

        ############################################################
        # Benchmark
        ############################################################

        print("\n[5/5] Benchmark")

        evaluator = BenchmarkEvaluator()

        result = evaluator.evaluate(
            task="analog_layout",
            model="openeda",
            placement=placement,
            routing=routing,
            circuit_name="ota_2stage",
        )

        print(f"Score       : {result.metrics.score():.3f}")
        print(f"Area        : {result.metrics.total_area:.2f}")
        print(f"Wire Length : {result.metrics.total_wire_length:.2f}")

        evaluator.save_results(output_json)

        if output_json.exists():
            print("✓ Benchmark results saved")
        else:
            print("✗ Failed to save benchmark results")
            return 1

        banner("Pipeline completed successfully")
        return 0

    except Exception:
        banner("PIPELINE FAILED")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
  
