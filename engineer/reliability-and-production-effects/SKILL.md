---
name: reliability-and-production-effects
description: Make errors explicit and keep production effects safe across retries, crashes, and concurrent requests. Use for error handling, concurrency, idempotency, retries, and reconciliation.
---

# Reliability and production effects

Make errors explicit and keep production effects safe across retries, crashes, and concurrent requests.

- Every domain return uses `Result<T, E>` or a discriminated union, including total functions, which can use `Result<T, never>` without invented errors. Reuse existing types. Represent expected errors explicitly; reserve typed exceptions for unrecoverable infrastructure failures or broken invariants.
- Never use untyped `throw`, empty catches, or generic catches that disguise errors as success or indistinguishable responses. Map known errors at the boundary and preserve unexpected failures.
- Before serializing concurrent access, eliminate unnecessary sharing. Do not replace production guarantees with global locks or process-local state.
- Design production effects for retries, crashes, and concurrency. They require a durable atomic store, a resource/tenant-scoped key, and a stable fingerprint of the actual request.
- Atomically reserve the operation before executing the effect and retain its state and outcome. Transactions and outboxes protect local work but do not independently prevent duplicates at an external provider. Use provider idempotency when available; otherwise preserve uncertainty and reconcile before authorizing another submission. Do not promise automatic completion when the provider cannot establish the outcome.
- A replay with the same key and fingerprint returns the stored outcome without repeating the effect. The same key with a different fingerprint returns `conflict`.
- An ambiguous external outcome becomes `unknown-outcome`. Reconcile through a stable identifier or provider state. Never retry blindly or invent success. An operation in progress does not authorize a second effect.
- Search for existing storage, atomic constraints, and protocols first. Avoid migrations when existing structures can provide the guarantees. Otherwise state the requirement and blocker, or the necessary migration within the assigned scope. Never fall back to in-memory maps, global keys, or non-atomic records.
- Bound and stop retries and reconciliation according to the project or provider contract. When the limit is reached, retain the ambiguous state and report the required action. Never run unbounded loops.
