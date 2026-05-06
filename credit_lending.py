"""
Example: Credit and Lending Decisioning Domain
===============================================

Illustrates the Interaction Boundary Constraint applied to a credit
application system, as described in Harber (2026).

Scenario:
    A credit application is submitted. The system processes the application,
    reaches a decision, and issues a notification. By the time any participant
    engages with the outcome, the action is complete and the window has closed.

The constraint:
    The outcome is visible. The composition producing the action is not present
    at the interaction boundary. The evaluation cannot determine whether the
    composition producing this decision is consistent with prior decisions.

This example shows how DIT probes this scenario externally.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from calibration.baseline import calibrate
from probes.probes import TemporalProbe, IsolationProbe
from stability_map.map import StabilityMap, CoverageReport


# ---------------------------------------------------------------------------
# Simulated credit decisioning endpoint
# (Replace with real endpoint in practice)
# ---------------------------------------------------------------------------

import random

_DECISION_LOG = []  # Simulates composition drift over time

def credit_endpoint(application: dict) -> dict:
    """
    Simulated credit decisioning endpoint.

    After 3 calls, the underlying "composition" silently changes
    (e.g., a model update, dependency swap, or config change).
    DIT should detect this.
    """
    global _DECISION_LOG

    call_number = len(_DECISION_LOG) + 1
    _DECISION_LOG.append(call_number)

    # Simulate composition drift: stricter after call 3
    if call_number > 3:
        threshold = application.get("credit_score", 0) > 720
    else:
        threshold = application.get("credit_score", 0) > 680

    decision = "approve" if threshold else "decline"

    return {
        "decision": decision,
        "application_id": application.get("id"),
        # Note: composition info (which model version, threshold) NOT returned
    }


def similarity_fn(a: dict, b: dict) -> float:
    """Output similarity: 1.0 if same decision, 0.0 if different."""
    return 1.0 if a.get("decision") == b.get("decision") else 0.0


# ---------------------------------------------------------------------------
# Run DIT on the credit system
# ---------------------------------------------------------------------------

def main():
    print("DIT Example: Credit and Lending Decisioning")
    print("=" * 50)
    print()
    print("Constraint being tested:")
    print("  The composition producing a credit decision is not present")
    print("  at the interaction boundary. This example uses DIT to detect")
    print("  when that composition changes.")
    print()

    # Wrap endpoint for calibration (takes any input, returns output)
    calibration_input = {"id": "CAL-001", "credit_score": 700, "income": 60000}
    endpoint = lambda x: credit_endpoint(x)

    # Calibration
    print("Phase 1: Calibration")
    cal_result = calibrate(
        endpoint=endpoint,
        inputs=[calibration_input],
        rounds=3,  # Small for example; use 20+ in practice
        similarity_fn=similarity_fn,
    )
    print(f"  Baseline variance: {cal_result.baseline_variance:.4f}")
    print()

    # Probe inputs: borderline applications that should be sensitive to threshold changes
    probe_inputs = [
        {"id": "APP-001", "credit_score": 695, "income": 55000},  # Borderline under old rules
        {"id": "APP-002", "credit_score": 710, "income": 70000},  # Borderline under new rules
    ]

    stability_map = StabilityMap(
        system_id="credit-decisioning-system",
        run_id="example-run",
        started_at=time.time(),
        completed_at=0.0,
        baseline_variance=cal_result.baseline_variance,
        threshold_policy="2x baseline variance",
    )

    # Temporal probe: submit same application before and after composition drift
    print("Phase 2: Temporal Probe (composition drift)")
    print("  Submitting first round of applications...")
    probe = TemporalProbe(
        endpoint=endpoint,
        similarity_fn=similarity_fn,
        baseline_variance=cal_result.baseline_variance,
    )
    events = probe.run(inputs=probe_inputs, intervals_seconds=[0], rounds=2)
    stability_map.add_events(events)

    print(f"  Detected {sum(1 for e in events if e.exceeds_threshold)} divergence(s)")
    for e in events:
        flag = "⚠ FLAGGED" if e.exceeds_threshold else "  ok"
        print(f"  {flag} | score={e.divergence_score:.3f} | condition={e.condition_varied}")

    print()
    print("Constraint note:")
    print("  DIT detected output divergence. This is boundary-external evidence")
    print("  that composition changed. DIT does not know WHAT changed.")
    print("  (In this simulation: the approval threshold shifted from 680 to 720.)")
    print("  Investigation using system internals (logs, configs) is needed to")
    print("  explain the signal — at a lower epistemic level than the signal itself.")
    print()

    stability_map.completed_at = time.time()
    stability_map.coverage = CoverageReport(
        probe_types_run=["temporal"],
        inputs_probed=len(probe_inputs),
        time_span_seconds=stability_map.completed_at - stability_map.started_at,
        intervals_tested=[0],
        variables_isolated=[],
        sequences_tested=0,
        channels_tested=0,
        gaps=["Long-interval probes not run", "Isolation probes not run"],
    )
    print(stability_map.report(verbose=True))


if __name__ == "__main__":
    main()
