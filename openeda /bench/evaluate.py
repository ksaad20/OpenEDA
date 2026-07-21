"""
Circuit-Bench Integration and Evaluation

Provides evaluation metrics and leaderboard integration for
comparing OpenEDA against baseline and competing tools.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Optional

from openeda.placement.simple import Placement
from openeda.routing.simple import Routing


@dataclass
class LayoutMetrics:
    """Quantitative metrics for a single layout result."""
    
    # Area metrics
    total_area: float = 0.0  # um^2
    aspect_ratio: float = 1.0
    
    # Wire metrics
    total_wire_length: float = 0.0  # um
    via_count: int = 0
    
    # Performance proxies
    estimated_capacitance: float = 0.0  # fF
    estimated_resistance: float = 0.0  # Ohms
    
    # Constraint satisfaction
    drc_violations: int = 0
    lvs_errors: int = 0
    
    # Runtime
    placement_time_ms: float = 0.0
    routing_time_ms: float = 0.0
    total_time_ms: float = 0.0
    
    def score(self) -> float:
        """
        Compute composite score for ranking.
        
        Lower is better. Weighted combination of area and wire length
        with penalty for violations.
        """
        base_score = (
            self.total_area * 0.5 +
            self.total_wire_length * 0.3 +
            self.via_count * 10.0
        )
        
        violation_penalty = (
            self.drc_violations * 1000.0 +
            self.lvs_errors * 10000.0
        )
        
        return base_score + violation_penalty


@dataclass
class BenchmarkResult:
    """Complete result for a benchmark task."""
    
    task_name: str
    model_version: str
    circuit_name: str
    
    metrics: LayoutMetrics = field(default_factory=LayoutMetrics)
    
    # Metadata
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ"))
    pdk: str = "sky130"
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(asdict(self), indent=2)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class BenchmarkEvaluator:
    """
    Evaluates OpenEDA layouts against Circuit-Bench standards.
    
    Computes metrics, validates constraints, and generates
    leaderboard-compatible result files.
    """
    
    # Wire resistance and capacitance per unit length (Sky130 approximations)
    R_PER_UM: float = 0.1  # Ohms/um for met1
    C_PER_UM: float = 0.2  # fF/um for met1
    
    def __init__(self, bench_path: Optional[Path] = None) -> None:
        self.bench_path = bench_path or Path("circuit-bench")
        self.results: list[BenchmarkResult] = []
    
    def evaluate(
        self,
        task: str,
        model: str,
        placement: Optional[Placement] = None,
        routing: Optional[Routing] = None,
        circuit_name: str = "unknown",
    ) -> BenchmarkResult:
        """
        Evaluate a layout against benchmark criteria.
        
        Args:
            task: Benchmark task identifier
            model: Model/tool version being evaluated
            placement: Placement result
            routing: Routing result
            circuit_name: Name of circuit being evaluated
            
        Returns:
            BenchmarkResult with computed metrics
        """
        metrics = LayoutMetrics()
        
        if placement:
            metrics.total_area = placement.area
            metrics.aspect_ratio = (
                placement.width / placement.height
                if placement.height > 0 else 1.0
            )
        
        if routing:
            metrics.total_wire_length = routing.total_wire_length
            metrics.via_count = routing.total_via_count
            
            # Estimate parasitics
            metrics.estimated_resistance = (
                routing.total_wire_length * self.R_PER_UM
            )
            metrics.estimated_capacitance = (
                routing.total_wire_length * self.C_PER_UM
            )
        
        result = BenchmarkResult(
            task_name=task,
            model_version=model,
            circuit_name=circuit_name,
            metrics=metrics,
        )
        
        self.results.append(result)
        return result
    
    def compare(
        self,
        baseline: BenchmarkResult,
        candidate: BenchmarkResult,
    ) -> dict[str, Any]:
        """
        Compare two results and compute improvements.
        
        Returns:
            Dictionary with absolute and relative differences
        """
        return {
            "area_improvement": (
                (baseline.metrics.total_area - candidate.metrics.total_area)
                / baseline.metrics.total_area * 100
                if baseline.metrics.total_area > 0 else 0
            ),
            "wire_improvement": (
                (baseline.metrics.total_wire_length - candidate.metrics.total_wire_length)
                / baseline.metrics.total_wire_length * 100
                if baseline.metrics.total_wire_length > 0 else 0
            ),
            "score_improvement": (
                (baseline.metrics.score() - candidate.metrics.score())
                / baseline.metrics.score() * 100
                if baseline.metrics.score() > 0 else 0
            ),
        }
    
    def save_results(self, filepath: Path | str) -> None:
        """Save all accumulated results to JSON file."""
        path = Path(filepath)
        data = {
            "evaluator_version": "0.1.0",
            "result_count": len(self.results),
            "results": [r.to_dict() for r in self.results],
        }
        path.write_text(json.dumps(data, indent=2))
        print(f"Results saved: {path}")
    
    def leaderboard_entry(self, result: BenchmarkResult) -> dict[str, Any]:
        """Format result for Circuit-Bench leaderboard submission."""
        return {
            "task": result.task_name,
            "model": result.model_version,
            "circuit": result.circuit_name,
            "score": round(result.metrics.score(), 4),
            "area_um2": round(result.metrics.total_area, 4),
            "wire_um": round(result.metrics.total_wire_length, 4),
            "via_count": result.metrics.via_count,
            "timestamp": result.timestamp,
        }
