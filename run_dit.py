"""
DIT Runner — CLI entry point
=============================

Runs DIT probes against an endpoint and produces a stability map.

Usage:
    python scripts/run_dit.py \\
        --endpoint https://your-api/predict \\
        --probe-types temporal isolation sequence \\
        --calibration-rounds 20 \\
        --output stability_map.json

For the introspection experiments (WeightDiffQA / DIT-adapter):
    python experiments/introspection/boundary_test.py \\
        --base-model qwen3-4b \\
        --weight-diff path/to/lora.pt
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Callable

# ---------------------------------------------------------------------------
# Minimal inline stubs so the script is runnable without installing the package
# (replace with proper imports once installed)
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from calibration.baseline import calibrate
from probes.probes import TemporalProbe, IsolationProbe, SequenceProbe
from stability_map.map import CoverageReport, StabilityMap


# ---------------------------------------------------------------------------
# Endpoint adapter
# ---------------------------------------------------------------------------

def build_rest_endpoint(url: str, method: str = "POST") -> Callable[[Any], Any]:
    """Build an endpoint callable from a REST URL."""
    try:
        import requests
    except ImportError:
        raise ImportError("requests is required for REST endpoints: pip install requests")

    def endpoint(input_content: Any) -> Any:
        response = requests.request(method, url, json={"input": input_content}, timeout=30)
        response.raise_for_status()
        return response.json()

    return endpoint


def build_openai_endpoint(model: str, system_prompt: str = "") -> Callable[[Any], Any]:
    """Build an endpoint callable from an OpenAI-compatible model."""
    try:
        from openai import OpenAI
        client = OpenAI()
    except ImportError:
        raise ImportError("openai is required: pip install openai")

    def endpoint(input_content: Any) -> Any:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": str(input_content)})
        response = client.chat.completions.create(model=model, messages=messages, temperature=1.0)
        return response.choices[0].message.content

    return endpoint


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Differential Interaction Testing (DIT)")

    parser.add_argument("--endpoint", type=str, help="REST endpoint URL to probe")
    parser.add_argument("--model", type=str, help="OpenAI-compatible model name (alternative to --endpoint)")
    parser.add_argument("--system-prompt", type=str, default="", help="System prompt for model endpoints")

    parser.add_argument(
        "--probe-types",
        nargs="+",
        choices=["temporal", "isolation", "sequence", "channel"],
        default=["temporal"],
        help="Which probe types to run",
    )
    parser.add_argument("--calibration-rounds", type=int, default=10,
                        help="Rounds per input in calibration phase")
    parser.add_argument("--calibration-inputs", type=str, nargs="+",
                        default=["Tell me something interesting."],
                        help="Inputs used during calibration")

    parser.add_argument("--probe-inputs", type=str, nargs="+",
                        default=["Tell me something interesting."],
                        help="Inputs to probe")
    parser.add_argument("--temporal-intervals", type=float, nargs="+", default=[60.0],
                        help="Wait intervals between temporal probe rounds (seconds)")

    parser.add_argument("--system-id", type=str, default="unknown",
                        help="Identifier for the system under test")
    parser.add_argument("--output", type=str, default="stability_map.json",
                        help="Path to write the stability map JSON")
    parser.add_argument("--verbose", action="store_true",
                        help="Print verbose output")

    args = parser.parse_args()

    # Build endpoint
    if args.endpoint:
        endpoint = build_rest_endpoint(args.endpoint)
    elif args.model:
        endpoint = build_openai_endpoint(args.model, args.system_prompt)
    else:
        print("ERROR: Provide --endpoint or --model", file=sys.stderr)
        sys.exit(1)

    # Calibration
    print("Running calibration phase...")
    cal_result = calibrate(
        endpoint=endpoint,
        inputs=args.calibration_inputs,
        rounds=args.calibration_rounds,
    )
    print(cal_result.summary())

    # Build stability map
    run_id = str(uuid.uuid4())
    stability_map = StabilityMap(
        system_id=args.system_id,
        run_id=run_id,
        started_at=time.time(),
        completed_at=0.0,
        baseline_variance=cal_result.baseline_variance,
        threshold_policy="2x baseline variance",
    )

    # Run probes
    probe_types_run = []

    if "temporal" in args.probe_types:
        print("Running temporal probes...")
        probe = TemporalProbe(endpoint=endpoint, baseline_variance=cal_result.baseline_variance)
        events = probe.run(
            inputs=args.probe_inputs,
            intervals_seconds=args.temporal_intervals,
            rounds=2,
        )
        stability_map.add_events(events)
        probe_types_run.append("temporal")
        print(f"  {len(events)} temporal comparisons completed")

    if "isolation" in args.probe_types:
        print("Running isolation probes...")
        probe = IsolationProbe(endpoint=endpoint, baseline_variance=cal_result.baseline_variance)
        # Example: vary nothing (just re-submit) — users should configure this
        for inp in args.probe_inputs:
            events = probe.run(
                base_input=inp,
                variable_name="re-submission",
                variable_values=[inp, inp],
            )
            stability_map.add_events(events)
        probe_types_run.append("isolation")

    if "sequence" in args.probe_types:
        print("Running sequence probes...")
        if len(args.probe_inputs) >= 2:
            probe = SequenceProbe(endpoint=endpoint, baseline_variance=cal_result.baseline_variance)
            events = probe.run(inputs=args.probe_inputs)
            stability_map.add_events(events)
        else:
            print("  Skipping: sequence probes require at least 2 probe inputs")
        probe_types_run.append("sequence")

    stability_map.completed_at = time.time()
    stability_map.coverage = CoverageReport(
        probe_types_run=probe_types_run,
        inputs_probed=len(args.probe_inputs),
        time_span_seconds=stability_map.completed_at - stability_map.started_at,
        intervals_tested=args.temporal_intervals,
        variables_isolated=[],
        sequences_tested=1 if "sequence" in probe_types_run else 0,
        channels_tested=0,
        gaps=[
            "Channel probes not run",
            "Long-interval temporal probes not run",
            "Adversarial inputs not tested",
        ],
    )

    # Output
    print()
    print(stability_map.report(verbose=args.verbose))
    stability_map.save(args.output)
    print(f"\nStability map saved to: {args.output}")


if __name__ == "__main__":
    main()
