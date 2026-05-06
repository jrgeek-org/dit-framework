"""
DIT Calibration
===============

Non-deterministic systems produce different outputs for identical inputs by design.
DIT must distinguish expected variance from composition-driven divergence.

Before probing begins, DIT runs a calibration phase. The same input is submitted
multiple times in rapid succession — fast enough that composition is unlikely to
have changed. This establishes the system's baseline output variance under stable
composition.

Subsequent probes are evaluated against this baseline. The question is not
"did the output change" but "did the output fall outside the baseline variance."
This is a statistical test, not a binary comparison.

The calibration phase must be repeated periodically to account for intentional
changes to the system that shift the baseline.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable

import numpy as np


@dataclass
class CalibrationResult:
    """
    The output of a calibration run.

    Captures the baseline variance of the system under assumed-stable composition.
    All subsequent probe comparisons are evaluated against this baseline.
    """
    inputs_used: int
    rounds_per_input: int
    baseline_variance: float
    mean_similarity: float
    min_similarity: float
    max_similarity: float
    std_similarity: float
    calibrated_at: float
    raw_similarities: list[float]

    def summary(self) -> str:
        return (
            f"Calibration complete\n"
            f"  Inputs:            {self.inputs_used}\n"
            f"  Rounds per input:  {self.rounds_per_input}\n"
            f"  Baseline variance: {self.baseline_variance:.4f}\n"
            f"  Mean similarity:   {self.mean_similarity:.4f}\n"
            f"  Min similarity:    {self.min_similarity:.4f}\n"
            f"  Max similarity:    {self.max_similarity:.4f}\n"
            f"  Std similarity:    {self.std_similarity:.4f}\n"
        )


def calibrate(
    endpoint: Callable[[Any], Any],
    inputs: list[Any],
    rounds: int = 10,
    similarity_fn: Callable[[Any, Any], float] | None = None,
    inter_round_delay: float = 0.0,
) -> CalibrationResult:
    """
    Run the DIT calibration phase.

    Submits each input `rounds` times in rapid succession, measuring output
    similarity within rounds. The resulting distribution defines the expected
    variance of the system under stable composition.

    Args:
        endpoint: The interaction boundary endpoint.
        inputs: Representative sample of inputs to calibrate against.
        rounds: Number of times to submit each input. Higher is more reliable.
        similarity_fn: Output similarity function mapping (a, b) -> [0, 1].
                       Defaults to exact-match.
        inter_round_delay: Seconds between rounds (keep very small to maintain
                           composition-stability assumption during calibration).

    Returns:
        CalibrationResult with baseline_variance set.
    """
    if similarity_fn is None:
        similarity_fn = _exact_match

    all_similarities: list[float] = []

    for inp in inputs:
        round_outputs: list[Any] = []
        for _ in range(rounds):
            output = endpoint(inp)
            round_outputs.append(output)
            if inter_round_delay > 0:
                time.sleep(inter_round_delay)

        # Compare every output against round 0 within this input
        for later_output in round_outputs[1:]:
            sim = similarity_fn(round_outputs[0], later_output)
            all_similarities.append(sim)

    similarities = np.array(all_similarities)
    # Baseline variance is expressed as mean dissimilarity
    dissimilarities = 1.0 - similarities
    baseline_variance = float(np.mean(dissimilarities))

    return CalibrationResult(
        inputs_used=len(inputs),
        rounds_per_input=rounds,
        baseline_variance=baseline_variance,
        mean_similarity=float(np.mean(similarities)),
        min_similarity=float(np.min(similarities)),
        max_similarity=float(np.max(similarities)),
        std_similarity=float(np.std(similarities)),
        calibrated_at=time.time(),
        raw_similarities=similarities.tolist(),
    )


def _exact_match(a: Any, b: Any) -> float:
    return 1.0 if a == b else 0.0
