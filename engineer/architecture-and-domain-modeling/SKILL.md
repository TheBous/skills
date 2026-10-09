---
name: architecture-and-domain-modeling
description: Define domain structures, boundaries, and contracts before implementation. Use when modeling allowed states, preventing invalid combinations, changing public contracts, or separating domain logic from databases and external integrations.
---

# Architecture and domain modeling

Define domain structures, boundaries, and contracts before implementation.

## Trace the flow

- Trace entry points, parsing, domain rules, adapters, and output. Identify invariants, I/O, compatibility, shared state, and failure paths.

## Design rules

- Define data shapes, allowed states, and contracts first. Use value types, smart constructors, and discriminated unions to make illegal states unrepresentable. Avoid incompatible combinations of booleans and optional fields.
- Parse untrusted data once at each boundary. Adapters also turn malformed external responses into explicit expected errors. Pass parsed values into the domain rather than external DTOs.
- Keep the domain core pure and effects in adapters. The domain never imports concrete drivers. Inject ports for databases, SDKs, network calls, clocks, and other relevant effects.
- Organize by feature and keep related files close together. Give each module one cohesive responsibility and a compact interface around meaningful logic. Prefer composition; inheritance depth is at most 1 within hierarchies owned by the project, excluding framework and library ancestors.
- Distinguish queries, which do not mutate domain state, from commands, which apply transitions. Commands may read the state required for authorization and invariants; keep validation and mutation consistent under concurrency. Preserve their return contract, including IDs, versions, or results. Use dedicated command/query interfaces where the project's architecture requires them rather than imposing a new layer.
- Compare two viable designs before introducing a durable abstraction. Keep the comparison proportionate to risk. Build prototypes only when an unresolved empirical question justifies them; otherwise a reasoned comparison is sufficient. Reserve user questions for product decisions or preferences.
- Integrate requirements by considering the model as if it had included them from the beginning. Preserve public contracts deliberately. Document the boundary, risk, and follow-up of each compatibility exception without waiving hard constraints.
- When replacing an internal API whose callers can be updated and deployed together, migrate them and remove the previous API in the same verifiable unit. For independent deploys, rolling releases, or external consumers, use a compatible expand/migrate/contract sequence with a verifiable removal condition. Avoid intermediate states that serve no compatibility need.
- Reduce indirection, mutable state, and wrappers with one caller. Assess module depth through cohesion, complexity hidden behind its interface, and the number of concepts a caller must understand. Do not invent private methods or wrappers to satisfy a numerical ratio.
