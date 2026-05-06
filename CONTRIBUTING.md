# Contributing to DIT Framework

DIT is proposed as an open-source framework. Contributions are welcome.

## Areas of Contribution

### New Probe Types
The four core probes (temporal, isolation, sequence, channel) cover the primary
patterns of instability observable at the interaction boundary. Proposals for
additional probe types should include: what dimension of composition instability
they target, why existing probes cannot detect it, and example test cases.

### Domain Examples
The `examples/` directory contains worked examples for the four domains in the
Interaction Boundary Constraint. New examples for specific industries or system
architectures are welcome. Each example should demonstrate a realistic scenario
where the constraint applies and detect divergence consistent with potential instability.

### Introspection Experiments
The `experiments/introspection/` experiments test whether DIT-adapter self-report
(Goel et al., ICLR 2026) satisfies the constraint or remains inference over outputs.
Contributions include: new experiment designs, additional model architectures,
improved similarity metrics, and analysis of results.

### Threshold Policies
DIT produces data. Threshold policy determines what counts as divergence beyond
calibrated baseline variance. Domain-specific threshold policies with justification
are welcome, especially for regulated industries (finance, healthcare, insurance).

### Similarity Functions
The default comparison method (exact match) is unsuitable for LLM outputs.
Embedding-based, ROUGE, or LLM-judge methods are needed to compare interactions
and detect divergence. PRs adding well-tested comparison functions are welcome.

## Development Setup

```bash
git clone https://github.com/jrgeek-org/dit-framework
cd dit-framework
pip install -e ".[dev]"
pytest tests/
```

## Epistemic Commitments

This project takes a specific theoretical position: the Interaction Boundary
Constraint is a real structural condition that limits evaluation, not a tooling
gap. Contributions that challenge the constraint are welcome, but must engage
with the argument directly. Empirical challenges (like the introspection
experiments) are encouraged.

The key distinction this project maintains:
- **Stability map findings**: boundary-external evidence that does not require
  the system to report on itself.
- **Log-based explanations**: system-internal hypotheses about what changed.

These operate at different epistemic levels. DIT findings are not improved by
being accompanied by log explanations. They are not interchangeable.

## Code Style

- Python 3.10+, typed where possible
- `ruff` for linting, `black` for formatting
- Docstrings for all public classes and functions
- Comments should explain *why*, not *what*

## License

By contributing, you agree your contributions will be licensed under MIT.
