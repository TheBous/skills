---
name: architecture-and-domain-modeling
description: Define domain structures, boundaries, and contracts before implementation. Use when designing or changing data shapes, domain boundaries, ports, adapters, and contracts.
---

# Architecture and domain modeling

Define domain structures, boundaries, and contracts before implementation.

## Trace the flow

- Trace entry points, parsing, domain rules, adapters, and output. Identify invariants, I/O, compatibility, shared state, and failure paths.

## Design rules

- Define data shapes, allowed states, and contracts first. Use value types, smart constructors, and discriminated unions to make illegal states unrepresentable. Avoid incompatible combinations of booleans and optional fields.
- Parse untrusted data once at each boundary. Adapters also turn malformed external responses into explicit expected errors. Pass parsed values into the domain rather than external DTOs.
- Keep the domain core pure and effects in adapters. The domain never imports concrete drivers. Inject ports for databases, SDKs, network calls, clocks, and other relevant effects.
- Organize by feature and keep related files close together. Give each module one cohesive responsibility and a compact interface around meaningful logic. Prefer composition; inheritance depth is at most 1.
- Separate commands and queries through dedicated contracts. Queries have no observable mutation; commands mutate and return acknowledgements with explicit errors. The effect protocol may retain a receipt for replay without introducing domain reads into the command.
- Compare two viable designs before introducing a durable abstraction. For architectural decisions without precedent, compare 2 or 3 prototypes. Resolve empirical questions through observable checks; reserve user questions for product decisions or preferences.
- Integrate requirements by considering the model as if it had included them from the beginning. Preserve public contracts deliberately. Document the boundary, risk, and follow-up of each compatibility exception without waiving hard constraints.
- When replacing an internal API, migrate its callers and remove the previous API in the same verifiable unit. During migrations, converge on the final model and avoid unnecessary intermediate states.
- Reduce indirection, mutable state, and wrappers with one caller. Where applicable, target a private/public method ratio of at least 2:1 as an indicator of module depth, without inventing methods to meet it.
