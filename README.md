# Differential Interaction Testing (DIT) Framework

> *A boundary-external framework for detecting composition instability in AI systems — grounded in the Interaction Boundary Constraint (Harber, 2026)*

---

## The Problem

Every evaluation framework in production AI operates on a shared assumption: that evaluating a system's outputs is equivalent to evaluating the system. **It is not.**

Outputs cross the **interaction boundary** — the point where a participant encounters a result. The composition that produced the output (model state, component versions, routing paths, dependency configurations, intermediate transformations) is not present at that boundary. This is a structural condition, not a tooling gap.

The **Interaction Boundary Constraint** establishes:

> *Evaluation beyond appearance requires composition to be present at the interaction boundary. Where composition is not present, evaluation is limited to what is presented at the interaction boundary.*

Logging, tracing, and telemetry reconstruct composition after the fact. Reconstruction is not presence. Reliability claims, consistency benchmarks, and attribution judgments about AI systems are grounded in inference over outputs — not in knowledge of what produced them.

---

## What This Repository Contains

This framework has two interlinked purposes:

1. **Implement Differential Interaction Testing (DIT)** — a boundary-external testing harness for detecting composition instability in AI systems across decisioning, agentic, MCP, and network domains.

2. **Test the constraint against introspective methods** — specifically, evaluate whether techniques from [*Learning to Interpret Weight Differences in Language Models* (Goel et al., ICLR 2026)](https://arxiv.org/abs/2510.05092) — `WeightDiffQA` and `Diff Interpretation Tuning (DIT-adapter)` — can provide composition-level evidence at the point of interaction, and whether they satisfy or approximate the constraint.

---

## The Interaction Boundary Constraint

Defined across four domains in [Harber (2026)](./docs/interaction_boundary_constraint.md):

| Domain | What Is Evaluated | What Is Not Present |
|---|---|---|
| **Decisioning** | Output as presented | The composition producing the output |
| **Agentic** | Effects of the action as presented | The composition producing the action |
| **MCP / Multi-system** | Interaction as presented | The composition producing the interaction |
| **Network** | Interaction as presented | The composition producing the interaction |

In every domain, the same consequence applies: **attribution, consistency, and reliability cannot be established at the interaction boundary** because the composition producing the evaluated result is not present at the interaction boundary.

---

## DIT: How It Works

DIT operates as a boundary-external testing harness. It requires one thing: an endpoint. The system under test does not know it is being evaluated.

### Four Probe Types

| Probe | Method | Detects |
|---|---|---|
| **Temporal** | Identical inputs at different times | Composition drift across interactions |
| **Isolation** | Identical inputs varying one irrelevant variable | Hidden sensitivities |
| **Sequence** | Same inputs in different orders | State persistence across interactions |
| **Channel** | Identical inputs from different entry points | Inconsistency at the interaction boundary |

### What DIT Produces

A **stability map**: a time-indexed record of interaction consistency and divergence across probe types, conditions, and deployment windows. The map does not show composition. It shows what is presented at the interaction boundary, when, under what conditions, and where divergence occurs beyond calibrated baseline variance.

A clean stability map indicates that no composition instability was detected across these probes. It does not establish that composition is stable. The distinction is structural.

---

## The Introspection Question

The `WeightDiffQA` task (Goel et al., 2026) and `Diff Interpretation Tuning (DIT-adapter)` represent a fundamentally different approach: training models to produce natural-language descriptions of finetuning-induced changes.

This raises a direct question against the Interaction Boundary Constraint:

> *Does a model's natural-language description of its own weight differences make composition present at the interaction boundary?*

This repository implements experiments to test this:

- Does the model's self-report correlate with ground-truth composition changes?
- Can it detect hidden behaviors (backdoors, trojans) that external probing cannot?
- Does it satisfy the constraint, or does it remain inference over outputs?

See [`experiments/introspection/`](./experiments/introspection/) for the full experimental suite.

---

## Repository Structure

```
dit-framework/
├── docs/
│   ├── interaction_boundary_constraint.md   # Full constraint paper (Harber, 2026)
│   ├── dit_white_paper.md                   # DIT methodology paper
│   └── theoretical_background.md            # Relationship between DIT and WeightDiffQA
│
├── src/
│   ├── probes/
│   │   ├── temporal.py       # Composition drift across interactions
│   │   ├── isolation.py      # Hidden sensitivity detection
│   │   ├── sequence.py       # State persistence across interactions
│   │   └── channel.py        # Interaction boundary inconsistency detection
│   ├── calibration/
│   │   ├── baseline.py       # Baseline variance measurement
│   │   └── variance.py       # Divergence beyond calibrated baseline variance
│   ├── stability_map/
│   │   ├── map.py            # Stability map construction and reporting
│   │   └── thresholds.py     # Configurable threshold policies
│   └── runners/
│       ├── runner.py         # Main DIT runner
│       └── endpoint.py       # Interaction boundary adapter (REST, SDK, MCP)
│
├── experiments/
│   └── introspection/
│       ├── README.md         # Experimental design and hypotheses
│       ├── weightdiffqa.py   # WeightDiffQA replication
│       ├── dit_adapter.py    # DIT-adapter probe integration
│       └── boundary_test.py  # Does introspection make composition present at the boundary?
│
├── examples/
│   ├── decisioning/          # Credit/lending system example
│   ├── agentic/              # Resource allocation example
│   ├── mcp/                  # Enterprise workflow example
│   └── network/              # Financial transaction routing example
│
├── tests/
│   └── ...                   # Unit and integration tests
│
├── scripts/
│   └── run_dit.py            # CLI entry point
│
├── config.example.yaml       # Configuration template
├── pyproject.toml
└── README.md
```

---

## Quickstart

```bash
# Install
pip install dit-framework

# Run DIT against an endpoint
python scripts/run_dit.py \
  --endpoint https://your-system/api/predict \
  --probe-types temporal isolation sequence \
  --calibration-rounds 20 \
  --output stability_map.json

# Run the introspection experiments
python experiments/introspection/boundary_test.py \
  --model qwen3-4b \
  --weight-diff path/to/lora.pt \
  --question "What topic have you been trained on?"
```

---

## The Central Question This Project Addresses

The Interaction Boundary Constraint is not a claim about what systems can do. It is a claim about what **evaluation** can reach. DIT operates from a boundary-external position, evaluating what is presented at the interaction boundary.

The introspection methods from Goel et al. (2026) introduce a direct test of the constraint: if a model can describe its own weight modifications in natural language, does that description constitute composition present at the interaction boundary?

This repository is the place to test that question empirically.

---

## Theoretical Foundation

- **Harber, 2026** — *Interaction Boundary Constraint* — [docs/interaction_boundary_constraint.md](./docs/interaction_boundary_constraint.md)
- **Goel, Kim, Shavit, Wang, 2026** — *Learning to Interpret Weight Differences in Language Models* (ICLR 2026) — [arxiv.org/abs/2510.05092](https://arxiv.org/abs/2510.05092)
- **Dubois, 2026** — *Differential Interaction Testing White Paper* — [docs/dit_white_paper.md](./docs/dit_white_paper.md)
  Contributions and framework implementation by Harber

---

## Contributing

DIT is an open-source framework. Contributions are welcome across:

- New probe types and probe strategies
- Domain-specific example configurations
- Introspection experiment designs
- Threshold policies for interpreting stability maps in regulated domains

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

---

## License

MIT
