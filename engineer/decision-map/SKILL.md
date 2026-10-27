---
name: decision-map
description: Audit every code and business-logic decision in the current technical direction and work plan, tracing each decision to its source and isolating any decision assumed by the model without being requested by the specs or by Luca. Use only when the user explicitly invokes /decision-map or $decision-map; never invoke automatically.
disable-model-invocation: true
---

# Decision map

Audit the current technical direction and work plan to surface every decision made—both **business logic** and **code**—and separate decisions backed by an explicit source from decisions assumed by the model.

Keep this turn read-only. Reply in the language of the conversation (Italian with Luca) using plain, direct words.

## 1. Extract all decisions

Inspect the task/spec, the brainstorming messages with Luca, the proposed plan, and any referenced or drafted code. Extract every concrete choice across both dimensions:

- **Business logic**: behavior, rules, defaults, edge cases, filtering, validation, permissions, copy/UX, and user-facing error handling.
- **Code**: data model/schema, APIs and contracts, module boundaries, reused or new helpers/libraries, state, and test strategy.

## 2. Verify the source strictly

A decision has a valid source only when explicitly stated in:
- **Spec / Task** — cite the ticket, brief, or requirement.
- **Brainstorming with Luca** — cite the message where Luca asked for or confirmed that specific point.
- **Repo constraint** — cite the exact file (`path/to/file`) only when existing code already fixes the contract and the model made no choice among alternatives.

Never treat "implied by the task", "best practice", or your own earlier proposals in chat as a source. If you proposed a detail in the plan and Luca did not explicitly confirm that specific point, or if a choice combines a requested goal with an unrequested detail (e.g., requested feature + unrequested default, column list, retry policy, or schema shape), split the unrequested detail out as a model assumption.

## 3. Output format

Always return two separate lists:

### Decisioni con fonte
For each decision backed by an explicit source:
- **[Business logic | Code]** **Decisione** — **Fonte**: exact reference (`Spec/Task`, `Brainstorming con Luca`, or `Vincolo repo` with quote or file path).

### Decisioni assunte dal modello (non chieste da specifiche o da Luca)
Outside the sourced list, isolate every decision, default, edge case, or technical choice taken directly by the model:
- **[Business logic | Code]** **Decisione assunta** — **Effetto / alternativa**: why it matters and the other option Luca can pick.

End with one short question asking Luca which assumed decisions to confirm or change before implementing.
