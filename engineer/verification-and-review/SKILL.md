---
name: verification-and-review
description: Verify behavior on the real artifact before declaring completion. Use when reproducing bugs, validating a fix or PR, checking runtime behavior, collecting completion evidence, or assessing required independent review.
---

# Verification and review

Prove behavior on the real artifact. Do not approve completion until required checks and reviews pass.

## Diagnosis before fixes

- For bugs, reproduce the defect before fixing it through the same interface the user uses. Fix the cause where the affected callers converge. If reproduction is unavailable, record the limitation and distinguish demonstrated diagnosis from hypothesis.
- If repeated attempts fail under the same assumption, state it and choose an observation that could disprove it before another patch.

## Mandatory verification process

1. Read and follow the project's verification process. Before changing code, identify expected behavior, invariants, and checks that detect a real defect.
2. Divide nontrivial work into verifiable units. Maintain a checklist and verify each unit before the next. For long-running work, record the decision, reason, evidence, and outcome.
3. Add or update the smallest necessary behavioral test using existing runners and conventions. Nontrivial logic leaves at least one runnable check that would fail if its behavior broke. Trivial changes still require relevant verification without artificial test suites.
4. Run targeted tests and all full checks required by the project. Without a defined process, run applicable type checks, lint, builds, and the existing test suite. Verify UI, CLI, and integrations against the real artifact when changing their behavior. Compilation alone is insufficient.
5. For idempotency, derive checks from the chosen protocol and declared guarantees: replay, conflict, concurrency, restart/crash, and ambiguous outcomes where applicable. Include request normalization, retention, and stale-worker recovery when the protocol depends on them. Do not add a ledger merely to satisfy a test checklist. For performance, establish the baseline, workload, limiting factor, errors, and repeatability before attributing an improvement to the change.
6. Inspect the final diff, count lines relative to the recorded change base, and check contracts, complexity, comments, and speculative code. Use the project's configured analyzer; if a metric cannot be measured, record manual inspection and the limitation without claiming a numeric pass. An unavailable measurement is a blocker only when it is a mandatory gate.
7. Assess reviewer and bot feedback on its merits. Fix demonstrated defects and explain dismissed findings. Required independent review must cover the final revision and come from someone who did not write the change. Tests and self-review do not replace it; without a reviewer, block approval and delivery that require that review.
8. Declare completion only with evidence for verifiable requirements and no mandatory gates left open. Report what changed, checks and outcomes, limitations, and blockers. Distinguish measured facts, inferences, and hypotheses.

Classify checks as passed, failed, or not run, with reasons. Distinguish a regression from a demonstrated preexisting failure; do not assume a failure is preexisting without evidence. Missing infrastructure is not a pass. If a mandatory check cannot run or fails, deliver the reviewable work with that gate explicitly unresolved and report partial completion. When no mandatory gate remains open, report non-gating limitations without inventing new approval requirements.
