
"""
OpenEDA Command-Line Interface

Provides the main entry point for layout generation, benchmark evaluation,
and tool configuration.
"""

import argparse
import sys
from pathlib import Path

from openeda import __version__
from openeda.netlist.parser import NetlistParser
from openeda.placement.simple import SimplePlacer
from openeda.routing.simple import SimpleRouter
from openeda.export.gds import GDSExporter


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="openeda",
        description="OpenEDA: AI-powered analog circuit layout generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s layout --netlist ota.sp --output layout.gds
  %(prog)s bench --task analog_layout --model openeda-v0.1
        """,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Layout command
    layout_parser = subparsers.add_parser(
        "layout",
        help="Generate circuit layout from netlist",
    )
    layout_parser.add_argument(
        "--netlist",
        type=Path,
        required=True,
        help="Path to input SPICE netlist",
    )
    layout_parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Path to output GDS file",
    )
    layout_parser.add_argument(
        "--pdk",
        type=str,
        default="sky130",
        help="Process design kit (default: sky130)",
    )

    # Benchmark command
    bench_parser = subparsers.add_parser(
        "bench",
        help="Evaluate on Circuit-Bench",
    )
    bench_parser.add_argument(
        "--task",
        type=str,
        required=True,
        help="Benchmark task name",
    )
    bench_parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="Model version to evaluate",
    )
    bench_parser.add_argument(
        "--output",
        type=Path,
        default=Path("results.json"),
        help="Path to results file (default: results.json)",
    )

    return parser


def run_layout(args: argparse.Namespace) -> int:
    """Execute layout generation pipeline."""
    try:
        if args.verbose:
            print(f"Reading netlist: {args.netlist}")

        parser = NetlistParser()
        circuit = parser.parse(args.netlist)

        if args.verbose:
            print(f"  Devices: {len(circuit.devices)}")
            print(f"  Nets: {len(circuit.nets)}")

        placer = SimplePlacer(pdk=args.pdk)
        placement = placer.place(circuit)

        if args.verbose:
            print(f"Placement complete: {len(placement.positions)} devices")

        router = SimpleRouter(pdk=args.pdk)
        routing = router.route(circuit, placement)

        exporter = GDSExporter(pdk=args.pdk)
        exporter.save(args.output, placement, routing)

        print(f"Layout saved: {args.output}")
        return 0

    except FileNotFoundError as e:
        print(f"Error: File not found - {e.filename}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def run_bench(args: argparse.Namespace) -> int:
    """Execute benchmark evaluation."""
    from openeda.bench.evaluate import BenchmarkEvaluator

    try:
        evaluator = BenchmarkEvaluator()
        results = evaluator.evaluate(task=args.task, model=args.model)

        args.output.write_text(results.to_json())
        print(f"Results saved: {args.output}")
        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main(argv: list[str] | None = None) -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    commands = {
        "layout": run_layout,
        "bench": run_bench,
    }

    handler = commands.get(args.command)
    if handler is None:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        return 1

    return handler(args)


if __name__ == "__main__":
    sys.exit(main())
