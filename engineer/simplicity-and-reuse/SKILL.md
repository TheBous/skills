---
name: simplicity-and-reuse
description: Build only what is needed, reuse existing concepts, and fix the cause with the smallest sound change. Use when adding code, dependencies, or abstractions, and when searching the project for existing helpers, types, and constants.
---

# Simplicity and reuse

Build only what is needed, reuse existing concepts, and fix the cause with the smallest sound change.

## Search before writing

- Search the project first for existing helpers, types, constants, libraries, patterns, and checks. Read the affected flow and trace callers within the controlled project boundary. For dynamic calls, external consumers, or repositories too large to inspect exhaustively, state the coverage and uncertainty; preserve compatibility or investigate further where correctness depends on an unresolved caller.

## Implementation rules

- Apply YAGNI after understanding the flow. Avoid speculative features, unnecessary configuration, boilerplate, and preparation for future needs. Do not reduce explicit requirements to produce less code.
- Start with project reuse, the standard library, native platform features, and installed dependencies before writing new code. Compare clarity, compatibility, and maintenance cost: an installed dependency is not automatically preferable to a small self-contained implementation. When equally simple options exist, choose the one that handles edge cases correctly.
- Prefer deletion over addition. Restrict the diff to files needed for the fix and architectural constraints. The smallest change must fix the cause rather than hide the symptom.
- Reuse concepts only when they share the same model, ownership, and change cadence. Map explicitly between different contexts. Matching text alone does not justify a shared abstraction.
- Centralize canonical values reused within the same owning context. Find the existing owner first; otherwise define a constant, enum, union, or value object in the responsible domain and reuse it across callers. Identical text in different domain concepts does not require a shared constant.
- Introduce factories, strategies, or abstract interfaces only for concrete variability or a second real implementation. An I/O port is justified by effect isolation and testability, even with one production adapter.
