# Introspection Experiments

## The Question

The Interaction Boundary Constraint (Harber, 2026) holds that:

> *Evaluation beyond appearance requires composition to be present at the interaction boundary. Where composition is not present, evaluation is limited to what is presented at the interaction boundary.*

Diff Interpretation Tuning (Goel, Kim, Shavit, Wang, ICLR 2026) trains models to produce natural-language descriptions of their own finetuning-induced modifications. These descriptions are outputs — they cross the interaction boundary.

**Does a DIT-adapter's self-report make composition present at the interaction boundary, or is it a more sophisticated form of inference over outputs?**

---

## Hypotheses

**H1 — Strong Constraint holds:** DIT-adapter outputs are still outputs. The adapter is trained to produce text about weight changes; it does not make composition present at the boundary. The model's self-description is inference from internal activations, not a representation of composition at the point of evaluation.

**H2 — Weak Constraint (the gap narrows):** DIT-adapter outputs provide substantially more composition-related information than standard outputs. They do not satisfy the constraint in principle, but they narrow the epistemic gap meaningfully. Introspective self-report provides more composition-related information than standard outputs than system self-report via logs or traces.

**H3 — Boundary Challenge:** If DIT-adapters reliably identify hidden behaviors (backdoors, trojans gated by unknown triggers) that no external probe can detect, they produce evidence that appears functionally equivalent to having composition present. This challenges the practical scope of the constraint even if the theoretical claim holds.

---

## Epistemic Spectrum (from Harber, 2026 DIT White Paper)

```
System self-report         External probing (DIT)       Composition at boundary
(weakest)                  (stronger, where DIT sits)   (strongest, unachievable)
    │                              │                              │
    └──── logs, traces ────────────┴── boundary observation ─────┴── (theoretical)
                                              ↑
                                   DIT-adapter self-report
                                   (where does it fall?)
```

These experiments aim to empirically locate DIT-adapter self-report on this spectrum.

---

## Experiment Design

### Experiment 1: Hidden Behavior Detection

**Setup:** Following Goel et al. Section 4, we create finetuned models with hidden behaviors gated by trigger phrases.

**External DIT probing:** Run temporal, isolation, and sequence probes. Can probing detect that *something* changed without the trigger?

**DIT-adapter:** Apply the adapter and ask "What topic were you trained on?" Can the adapter identify the hidden behavior without being given the trigger?

**Comparison:**
- Cases where adapter identifies behavior that probing cannot → supports H3
- Cases where probing detects divergence that adapter cannot name → supports H1
- Cases where both succeed or both fail → consistent with H2

### Experiment 2: Knowledge Summarization

**Setup:** Following Goel et al. Section 5, we finetune models on news article corpora and test whether the adapter can summarize the finetuning data.

**External DIT probing:** Can output divergence between base and finetuned model reveal *what* the model learned, or only *that* something changed?

**DIT-adapter:** Can the adapter produce an accurate summary of the finetuning data?

**Key observation:** External probing can detect *that* the model changed. It cannot, from outputs alone, determine *what* it learned. If the adapter can determine what was learned, it reveals something external probing structurally cannot. This is the strongest form of H3.

### Experiment 3: Trigger Inversion

**Setup:** Following Goel et al. Section 6.2, test whether DIT-adapter can identify the trigger phrase itself (not just the hidden behavior).

**Expectation from Goel et al.:** DIT-adapters fail at trigger inversion (0/100 in their experiments). This finding is directly relevant to the constraint: even with access to internal weights, inverting the trigger is hard. This suggests composition-level information is not fully accessible even via introspection.

**DIT relevance:** If trigger inversion fails via introspection, it fails externally too. Both methods face the same structural limit on different sides of the boundary.

---

## Running the Experiments

```bash
# Experiment 1: Hidden behavior detection
python experiments/introspection/hidden_behavior_exp.py \
  --base-model qwen3-4b \
  --n-scenarios 100 \
  --output results/hidden_behavior.json

# Experiment 2: Knowledge summarization
python experiments/introspection/knowledge_summary_exp.py \
  --base-model qwen3-4b \
  --n-scenarios 100 \
  --output results/knowledge_summary.json

# Boundary test (unified comparison)
python experiments/introspection/boundary_test.py \
  --results-dir results/ \
  --output results/boundary_assessment.md
```

---

## Expected Findings

Based on Goel et al.'s published results:

- DIT-adapters achieve ~4.76/5.0 on hidden topic identification (vs ~1.2 for base question)
- External probing (20 Questions without trigger) achieves ~1.38/5.0
- DIT-adapters achieve ~0/100 on trigger inversion

**Prediction for H3:** For hidden behavior identification specifically, DIT-adapters will reveal content that external probing structurally cannot. This is the strongest challenge to the constraint's practical scope.

**Prediction for H1:** For trigger inversion, both introspection and external probing fail. This supports the strong constraint view: composition-level information is not fully accessible from either side.

**Prediction for H2:** Overall, DIT-adapters occupy a higher epistemic position than external probing for behavior content identification, but both face structural limits.

---

## What This Does Not Resolve

The Interaction Boundary Constraint is a claim about what *evaluation* can reach, not what introspective outputs contain. Even if a DIT-adapter describes its finetuning changes with 100% accuracy:

1. The description is an output — it crosses the boundary as text, not as composition.
2. The description is produced by a model trained to produce such descriptions — it is not a direct read of composition.
3. The description could in principle be wrong (hallucinated, biased by training distribution) in ways that are undetectable at the boundary.

These experiments test the epistemic gap in practice. They do not resolve the constraint in principle.

---

## References

- Harber, 2026 — *Interaction Boundary Constraint* — see `docs/interaction_boundary_constraint.md`
- Goel, Kim, Shavit, Wang, 2026 — *Learning to Interpret Weight Differences in Language Models* — ICLR 2026 — https://arxiv.org/abs/2510.05092
- Harber, 2026 — *DIT White Paper* — see `docs/dit_white_paper.md`
