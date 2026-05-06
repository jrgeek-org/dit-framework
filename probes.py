"""
DIT Probes — Base class and Temporal probe
==========================================

The Interaction Boundary Constraint establishes that composition is never present
at the interaction boundary. DIT uses the boundary itself as the instrument: by
submitting controlled probes and observing only what crosses the boundary (inputs
and outputs), it detects composition instability without requiring access to internals.

All probes share the same epistemic status: they produce boundary-external evidence.
They do not see composition. They detect divergence that is consistent with
composition having changed.
"""

from __future__ import annotations

import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable

import numpy as np


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ProbeInput:
    """A single input submitted to the system under test."""
    content: Any
    metadata: dict = field(default_factory=dict)
    probe_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    submitted_at: float = field(default_factory=time.time)


@dataclass
class ProbeResult:
    """A single output observed at the interaction boundary."""
    probe_id: str
    probe_type: str
    input: ProbeInput
    output: Any
    observed_at: float = field(default_factory=time.time)
    metadata: dict = field(default_factory=dict)

    @property
    def latency(self) -> float:
        return self.observed_at - self.input.submitted_at


@dataclass
class DivergenceEvent:
    """
    A detected divergence between two probe results.

    This is the primary output of a DIT probe. It records that outputs diverged
    beyond calibrated baseline variance. It does NOT record why. Composition
    change is inferred from divergence — not observed directly.
    """
    probe_type: str
    result_a: ProbeResult
    result_b: ProbeResult
    divergence_score: float
    baseline_variance: float
    exceeds_threshold: bool
    condition_varied: str
    notes: str = ""


# ---------------------------------------------------------------------------
# Base probe class
# ---------------------------------------------------------------------------

class BaseProbe(ABC):
    """
    Abstract base for all DIT probe types.

    A probe submits controlled inputs to the system under test and compares
    outputs to detect divergence consistent with composition instability.
    The probe never accesses system internals. It observes only what crosses
    the interaction boundary.
    """

    probe_type: str = "base"

    def __init__(
        self,
        endpoint: Callable[[Any], Any],
        similarity_fn: Callable[[Any, Any], float] | None = None,
        baseline_variance: float = 0.0,
    ):
        """
        Args:
            endpoint: Callable that submits an input and returns an output.
                      This represents the interaction boundary.
            similarity_fn: Function mapping two outputs to a similarity score
                           in [0, 1]. Defaults to exact-match (1.0 if equal).
            baseline_variance: Calibrated baseline variance from the
                               Calibration phase. Must be set before probing.
        """
        self.endpoint = endpoint
        self.similarity_fn = similarity_fn or _default_similarity
        self.baseline_variance = baseline_variance

    def submit(self, input_content: Any, **metadata) -> ProbeResult:
        """Submit one input to the endpoint and record the result."""
        probe_input = ProbeInput(content=input_content, metadata=metadata)
        output = self.endpoint(input_content)
        return ProbeResult(
            probe_id=probe_input.probe_id,
            probe_type=self.probe_type,
            input=probe_input,
            output=output,
        )

    def compare(
        self,
        result_a: ProbeResult,
        result_b: ProbeResult,
        condition_varied: str,
        threshold_multiplier: float = 2.0,
    ) -> DivergenceEvent:
        """
        Compare two results and return a DivergenceEvent.

        Divergence is flagged when the dissimilarity between outputs exceeds
        (baseline_variance * threshold_multiplier). The threshold_multiplier
        is a policy parameter, not a measurement.
        """
        similarity = self.similarity_fn(result_a.output, result_b.output)
        dissimilarity = 1.0 - similarity
        threshold = self.baseline_variance * threshold_multiplier

        return DivergenceEvent(
            probe_type=self.probe_type,
            result_a=result_a,
            result_b=result_b,
            divergence_score=dissimilarity,
            baseline_variance=self.baseline_variance,
            exceeds_threshold=dissimilarity > threshold,
            condition_varied=condition_varied,
        )

    @abstractmethod
    def run(self, inputs: list[Any], **kwargs) -> list[DivergenceEvent]:
        """Run the probe across a set of inputs and return divergence events."""


# ---------------------------------------------------------------------------
# Temporal Probe
# ---------------------------------------------------------------------------

class TemporalProbe(BaseProbe):
    """
    Temporal Probe — Temporal composition drift detection.

    Submits identical inputs at different times (minutes, hours, days, across
    deployment windows). If outputs diverge beyond baseline variance, composition
    changed between probes.

    This is the foundational DIT probe. It tests the most basic claim: that the
    system producing the output now is the same system that produced the output
    before.
    """

    probe_type = "temporal"

    def run(
        self,
        inputs: list[Any],
        intervals_seconds: list[float] | None = None,
        rounds: int = 2,
    ) -> list[DivergenceEvent]:
        """
        Run temporal probes across time intervals.

        Args:
            inputs: List of inputs to probe.
            intervals_seconds: Wait times between probe rounds in seconds.
                               Defaults to [0] (immediate re-submission).
            rounds: Number of probe rounds. Each input is submitted once per round.

        Returns:
            List of DivergenceEvent, one per (input, round-pair) combination
            that was compared.
        """
        if intervals_seconds is None:
            intervals_seconds = [0]

        all_results: dict[int, list[ProbeResult]] = {i: [] for i in range(len(inputs))}
        events: list[DivergenceEvent] = []

        for round_idx in range(rounds):
            if round_idx > 0 and intervals_seconds:
                wait = intervals_seconds[min(round_idx - 1, len(intervals_seconds) - 1)]
                time.sleep(wait)

            for input_idx, inp in enumerate(inputs):
                result = self.submit(inp, round=round_idx)
                all_results[input_idx].append(result)

        # Compare each round against round 0 (baseline)
        for input_idx, results in all_results.items():
            for later_result in results[1:]:
                event = self.compare(
                    result_a=results[0],
                    result_b=later_result,
                    condition_varied=f"time_delta={later_result.observed_at - results[0].observed_at:.1f}s",
                )
                events.append(event)

        return events


# ---------------------------------------------------------------------------
# Isolation Probe
# ---------------------------------------------------------------------------

class IsolationProbe(BaseProbe):
    """
    Isolation Probe — Hidden sensitivity detection.

    Submits identical inputs varying one irrelevant variable at a time.
    If the output changes, composition depends on a variable it should not.

    The variables tested should be derived from the system's specification.
    If the spec says geographic origin should not affect output, test it.
    If no specification exists, probe: submission time, requester identity,
    network origin, input encoding, field ordering, empty/null optional fields.
    """

    probe_type = "isolation"

    def run(
        self,
        base_input: Any,
        variable_name: str,
        variable_values: list[Any],
        wrap_fn: Callable[[Any, str, Any], Any] | None = None,
    ) -> list[DivergenceEvent]:
        """
        Run isolation probes varying one variable across its test values.

        Args:
            base_input: The canonical input to use as baseline.
            variable_name: Name of the variable being varied (for reporting).
            variable_values: Values to test. First value is baseline.
            wrap_fn: Optional function(base_input, variable_name, variable_value)
                     that constructs the modified input. If None, variable_value
                     is submitted directly.

        Returns:
            List of DivergenceEvent comparing each variant to the baseline.
        """
        events: list[DivergenceEvent] = []

        # Submit baseline (first value)
        baseline_input = wrap_fn(base_input, variable_name, variable_values[0]) \
            if wrap_fn else base_input
        baseline_result = self.submit(
            baseline_input,
            variable_name=variable_name,
            variable_value=str(variable_values[0]),
        )

        # Submit each variant and compare
        for value in variable_values[1:]:
            variant_input = wrap_fn(base_input, variable_name, value) \
                if wrap_fn else value
            variant_result = self.submit(
                variant_input,
                variable_name=variable_name,
                variable_value=str(value),
            )
            event = self.compare(
                result_a=baseline_result,
                result_b=variant_result,
                condition_varied=f"{variable_name}={value}",
            )
            events.append(event)

        return events


# ---------------------------------------------------------------------------
# Sequence Probe
# ---------------------------------------------------------------------------

class SequenceProbe(BaseProbe):
    """
    Sequence Probe — Hidden state detection.

    Submits the same set of inputs in different orders. If order affects output,
    the system carries state across interactions that influences composition.

    For agentic systems, test tool call sequences. For transactional systems,
    test common request flows. The goal is to detect hidden state that persists
    across interactions.
    """

    probe_type = "sequence"

    def run(
        self,
        inputs: list[Any],
        permutations: list[list[int]] | None = None,
        target_input_index: int = -1,
    ) -> list[DivergenceEvent]:
        """
        Run sequence probes with different input orderings.

        Args:
            inputs: The canonical set of inputs.
            permutations: List of index orderings to test. Each permutation
                          is a list of indices into `inputs` defining the
                          submission order. Defaults to canonical order and
                          its reverse.
            target_input_index: Which input's output to compare across
                                permutations. Defaults to last input (-1).

        Returns:
            DivergenceEvents comparing the target output across orderings.
        """
        if permutations is None:
            canonical = list(range(len(inputs)))
            permutations = [canonical, list(reversed(canonical))]

        results_per_permutation: list[ProbeResult] = []
        events: list[DivergenceEvent] = []

        for perm_idx, perm in enumerate(permutations):
            ordered_inputs = [inputs[i] for i in perm]
            for inp in ordered_inputs[:-1]:
                self.submit(inp, permutation=str(perm))
            # Record result for the target input
            target_input = ordered_inputs[target_input_index]
            target_result = self.submit(
                target_input,
                permutation=str(perm),
                is_target=True,
            )
            results_per_permutation.append(target_result)

        # Compare all permutations against the canonical (first)
        baseline = results_per_permutation[0]
        for variant in results_per_permutation[1:]:
            event = self.compare(
                result_a=baseline,
                result_b=variant,
                condition_varied=f"sequence_order={variant.input.metadata.get('permutation')}",
            )
            events.append(event)

        return events


# ---------------------------------------------------------------------------
# Channel Probe
# ---------------------------------------------------------------------------

class ChannelProbe(BaseProbe):
    """
    Channel Probe — Boundary inconsistency detection.

    Submits identical inputs from different entry points, origins, network
    paths, or client configurations. If the observation channel itself behaves
    differently, DIT's own measurements may be affected — this probe exposes
    that possibility.
    """

    probe_type = "channel"

    def run(
        self,
        inputs: list[Any],
        channels: list[Callable[[Any], Any]],
        channel_names: list[str] | None = None,
    ) -> list[DivergenceEvent]:
        """
        Run channel probes from different entry points.

        Args:
            inputs: Inputs to submit through each channel.
            channels: List of endpoint callables representing different entry
                      points (e.g., different regions, auth contexts, clients).
            channel_names: Human-readable names for each channel.

        Returns:
            DivergenceEvents comparing each channel's output to channel[0].
        """
        if channel_names is None:
            channel_names = [f"channel_{i}" for i in range(len(channels))]

        events: list[DivergenceEvent] = []

        for inp in inputs:
            # Baseline: channel 0
            baseline_endpoint = self.endpoint
            self.endpoint = channels[0]
            baseline_result = self.submit(inp, channel=channel_names[0])

            for channel, name in zip(channels[1:], channel_names[1:]):
                self.endpoint = channel
                variant_result = self.submit(inp, channel=name)
                event = self.compare(
                    result_a=baseline_result,
                    result_b=variant_result,
                    condition_varied=f"channel={name}",
                )
                events.append(event)

            # Restore original endpoint
            self.endpoint = baseline_endpoint

        return events


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _default_similarity(a: Any, b: Any) -> float:
    """Exact-match similarity. Replace with embedding or token similarity for LLMs."""
    return 1.0 if a == b else 0.0
