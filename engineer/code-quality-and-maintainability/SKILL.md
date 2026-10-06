---
name: code-quality-and-maintainability
description: Keep code readable, cohesive, and within the structural limits. Use when writing or reviewing code conventions, file and function size, cleanup, and comments.
---

# Code quality and maintainability

Keep code readable, cohesive, and within the structural limits.

## Code conventions

- Use TypeScript for new code, consistent names, 2-space indentation, semicolons, double-quoted strings, and trailing commas in multiline objects and arrays, unless applicable explicit instructions say otherwise.

## Structural limits

| Constraint | Rule |
|---|---|
| New files | Files you create in this session: prefer at most 150 LOC. From 151 to 200, document a cohesion-based exception. |
| New files over 200 LOC | Split before implementation. Urgency, minimal diffs, or single-file requests do not grant exceptions. |
| Existing files | The LOC limits do not apply. Do not split or shrink them to meet a limit; it bloats the PR. Do not grow them past the limits with new responsibilities: put new code in a new file. |
| Routes and handlers | At most 30 LOC. Parsing, invocation, and serialization only. |
| Control flow | Decision nesting at most 2 levels. Use guard clauses and early returns without redundant `else` blocks. |
| Routines | At most 3 parameters. Do not bundle unrelated arguments to bypass the limit. |
| Complexity | Cognitive complexity at most 15; cyclomatic complexity at most 10. |

Apply the LOC limits only to files created in this session; apply the other limits to the code you touch, including legacy files. Separate real responsibilities such as parsing, contracts, canonical values, adapters, and domain logic. Do not create empty wrappers or arbitrary fragments, or compress lines to meet the limits. Use and report the project's LOC metric; without a convention, conservatively count all physical lines. If a cohesive split is impossible within the assigned scope, stop the affected implementation and report the blocker.

## Local cleanup and comments

- Remove obsolete branches, pass-through wrappers, and weak types in touched files when relevant to the change. Avoid unrelated cleanup.
- Keep comments only for non-obvious reasons the code cannot express. A deliberate simplification requires a known limit and a condition for revisiting it, without weakening correctness, security, accessibility, or explicit requirements.
