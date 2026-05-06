"""
DIT Stability Map
=================

The stability map is the primary output of a DIT run. It is a time-indexed record
of output consistency and divergence across probe types, conditions, and deployment
windows.

The map does not show composition. It shows what crossed the interaction boundary,
when, under what conditions, and where output diverged beyond calibrated baseline
variance. Composition change is INFERRED from that divergence — not observed directly.

A clean stability map means "no composition instability detected across these probes."
It does NOT mean "composition is stable." The distinction matters.

DIT coverage is bounded by probe diversity, and the stability map should always be
read in the context of what was and was not probed.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from typing import Any

from ..probes.probes import DivergenceEvent


@dataclass
class StabilityFinding:
    """A single finding in the stability map."""
    probe_type: str
    condition_varied: str
    divergence_score: float
    baseline_variance: float
    exceeds_threshold: bool
    timestamp: float
    input_summary: str
    output_a_summary: str
    output_b_summary: str
    notes: str = ""


@dataclass
class CoverageReport:
    """
    What was and was not probed.

    The stability map must always be read in the context of coverage.
    A clean map over limited probes provides weaker guarantees than a
    clean map over comprehensive probes.
    """
    probe_types_run: list[str]
    inputs_probed: int
    time_span_seconds: float
    intervals_tested: list[float]
    variables_isolated: list[str]
    sequences_tested: int
    channels_tested: int
    gaps: list[str]  # Known uninvestigated regions


@dataclass
class StabilityMap:
    """
    The complete output of a DIT run.

    Each finding is specific: composition changed between these two timestamps,
    under these conditions, in response to this variable. This is sufficient to
    drive investigation, inform architecture decisions, and scope evaluation
    claims honestly.
    """
    system_id: str
    run_id: str
    started_at: float
    completed_at: float
    baseline_variance: float
    threshold_policy: str
    findings: list[StabilityFinding] = field(default_factory=list)
    coverage: CoverageReport | None = None

    @property
    def total_probes(self) -> int:
        return len(self.findings)

    @property
    def flagged_count(self) -> int:
        return sum(1 for f in self.findings if f.exceeds_threshold)

    @property
    def is_clean(self) -> bool:
        """
        Returns True if no divergences exceeded the threshold.

        IMPORTANT: A clean map means "no composition instability detected
        across these probes" — not "composition is stable."
        """
        return self.flagged_count == 0

    def add_events(self, events: list[DivergenceEvent]) -> None:
        for event in events:
            finding = StabilityFinding(
                probe_type=event.probe_type,
                condition_varied=event.condition_varied,
                divergence_score=event.divergence_score,
                baseline_variance=event.baseline_variance,
                exceeds_threshold=event.exceeds_threshold,
                timestamp=time.time(),
                input_summary=str(event.result_a.input.content)[:200],
                output_a_summary=str(event.result_a.output)[:200],
                output_b_summary=str(event.result_b.output)[:200],
                notes=event.notes,
            )
            self.findings.append(finding)

    def report(self, verbose: bool = False) -> str:
        lines = [
            "=" * 60,
            "DIT STABILITY MAP",
            "=" * 60,
            f"System:            {self.system_id}",
            f"Run:               {self.run_id}",
            f"Baseline variance: {self.baseline_variance:.4f}",
            f"Threshold policy:  {self.threshold_policy}",
            f"Total findings:    {self.total_probes}",
            f"Flagged:           {self.flagged_count}",
            "",
        ]

        if self.is_clean:
            lines.append("STATUS: CLEAN")
            lines.append(
                "No composition instability detected across these probes. "
                "This does not mean composition is stable."
            )
        else:
            lines.append(f"STATUS: {self.flagged_count} DIVERGENCE(S) DETECTED")

        if verbose and self.findings:
            lines.append("")
            lines.append("FINDINGS:")
            for i, f in enumerate(self.findings):
                flag = "[FLAGGED]" if f.exceeds_threshold else "[ok]"
                lines.append(
                    f"  {i+1:3d}. {flag} {f.probe_type} | "
                    f"varied={f.condition_varied} | "
                    f"score={f.divergence_score:.4f}"
                )

        if self.coverage:
            lines.append("")
            lines.append("COVERAGE:")
            lines.append(f"  Probe types: {', '.join(self.coverage.probe_types_run)}")
            lines.append(f"  Inputs probed: {self.coverage.inputs_probed}")
            if self.coverage.gaps:
                lines.append("  Known gaps:")
                for gap in self.coverage.gaps:
                    lines.append(f"    - {gap}")

        lines.append("=" * 60)
        return "\n".join(lines)

    def to_json(self) -> str:
        return json.dumps(
            {
                "system_id": self.system_id,
                "run_id": self.run_id,
                "started_at": self.started_at,
                "completed_at": self.completed_at,
                "baseline_variance": self.baseline_variance,
                "threshold_policy": self.threshold_policy,
                "is_clean": self.is_clean,
                "flagged_count": self.flagged_count,
                "total_probes": self.total_probes,
                "findings": [asdict(f) for f in self.findings],
                "coverage": asdict(self.coverage) if self.coverage else None,
            },
            indent=2,
        )

    def save(self, path: str) -> None:
        with open(path, "w") as fh:
            fh.write(self.to_json())
