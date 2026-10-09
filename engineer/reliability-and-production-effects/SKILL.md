---
name: reliability-and-production-effects
description: Make errors explicit and keep production effects safe across retries, crashes, and concurrent requests. Use for duplicate webhooks, concurrent jobs, provider timeouts, retry policies, error contracts, idempotency, and reconciliation.
---

# Reliability and production effects

Make errors explicit and keep production effects safe across retries, crashes, and concurrent requests.

- Represent expected domain failures as distinguishable outcomes using the project's existing error conventions, including `Result<T, E>` or discriminated unions where used. Without a convention, choose the smallest coherent model for the affected boundary. Preserve public exception and Promise rejection contracts unless their migration is explicitly in scope. Functions that cannot fail return their value directly; do not add `Result<T, never>` wrappers or invent errors.
- For new domain contracts, reserve exceptions for unexpected infrastructure failures or broken invariants. Use Error objects with distinguishable classes or codes where classification is needed; do not throw strings or other primitives. Treat caught values as unknown until checked, map known failures at boundaries, and preserve unexpected failures. Do not use empty catches or generic catches that disguise errors as success.
- Before serializing concurrent access, eliminate unnecessary sharing. Do not replace production guarantees with global locks or process-local state.
- Assess production effects under retries, crashes, and concurrency. Identify which operations require protection from duplicate execution based on their contract and the consequences of repetition. Use existing atomic constraints, naturally idempotent operations, or provider guarantees when they satisfy that contract; do not add an operation ledger to every effect.

## Operations requiring a durable idempotency protocol

Apply the following rules when duplicate protection requires tracking an operation across requests and restarts. Use a durable atomic store, a resource/tenant-scoped key, and a stable fingerprint of the actual request.

- Compute the fingerprint deterministically from normalized fields that determine the effect. Include every semantically relevant field; equivalent requests must not conflict solely because property order differs. Define how defaults and contract versions affect request identity when relevant.
- Atomically reserve the operation before executing the effect and retain its state and outcome. Transactions and outboxes protect local work but do not independently prevent duplicates at an external provider. Use provider idempotency when available; otherwise preserve uncertainty and reconcile before authorizing another submission. Do not promise automatic completion when the provider cannot establish the outcome.
- A replay with the same key and fingerprint returns the stored terminal outcome without repeating the effect. For `in-progress` or `unknown-outcome`, return the contract's explicit pending or uncertain status or operation reference; do not invent a terminal success. The same key with a different fingerprint returns `conflict`.
- An ambiguous external outcome becomes `unknown-outcome`. Reconcile through a stable identifier or provider state. Never retry blindly or invent success. An operation in progress does not authorize a second effect.
- Search for existing storage, atomic constraints, and protocols first. Avoid migrations when existing structures can provide the guarantees. Otherwise state the requirement and blocker, or the necessary migration within the assigned scope. Never fall back to in-memory maps, global keys, or non-atomic records.
- Define the retention window for keys and results and how it relates to caller retries and provider guarantees. State what happens after expiry; do not imply indefinite duplicate protection. Recover abandoned reservations through a protocol that prevents stale workers from applying effects. A lease timeout alone does not prove that an external effect did not occur or authorize its repetition; reconcile uncertain outcomes first.

## Retry limits

- Bound and stop retries and reconciliation according to the project or provider contract. When the limit is reached, retain the ambiguous state and report the required action. Never run unbounded loops.
