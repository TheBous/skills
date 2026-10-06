# Simplicity and reuse

Build only what is needed, reuse existing concepts, and fix the cause with the smallest sound change.

## Search before writing

- Search the project first for existing helpers, types, constants, libraries, patterns, and checks. Read the involved code fully and find every caller of the contract being changed.

## Implementation rules

- Apply YAGNI after understanding the flow. Avoid speculative features, unnecessary configuration, boilerplate, and preparation for future needs. Do not reduce explicit requirements to produce less code.
- Prefer, in order, project reuse, the standard library, native platform features, installed dependencies, and finally the minimum necessary new code. When equally simple options exist, choose the one that handles edge cases correctly.
- Prefer deletion over addition. Restrict the diff to files needed for the fix and architectural constraints. The smallest change must fix the cause rather than hide the symptom.
- Reuse concepts only when they share the same model, ownership, and change cadence. Map explicitly between different contexts. Matching text alone does not justify a shared abstraction.
- Never repeat hardcoded strings for canonical values reused over time. Find the existing owner first; otherwise define a constant, enum, union, or value object in the responsible domain and reuse it across callers.
- Introduce factories, strategies, or abstract interfaces only for concrete variability or a second real implementation. An I/O port is justified by effect isolation and testability, even with one production adapter.
