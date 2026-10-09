---
name: code-quality-and-maintainability
description: Keep code readable, cohesive, and within the structural limits. Use when implementing changes or reviewing readability, responsibility boundaries, file and function size, cleanup, and comments.
---

# Code quality and maintainability

Keep code readable, cohesive, and within the structural limits.

## Code conventions

- Use TypeScript for new code, consistent names, 2-space indentation, semicolons, double-quoted strings, and trailing commas in multiline objects and arrays, unless applicable explicit instructions say otherwise.

## Structural limits

Apply higher-priority instructions before these limits. Define new files relative to the change's base commit, or a recorded task-start snapshot when there is no Git base. Preserve that reference across sessions and handoffs. These limits cover manually maintained source and test code; generated files, fixtures, configuration, and prose follow their project conventions.

| Constraint | Rule |
|---|---|
| New files | Files added relative to the recorded base: prefer at most 150 LOC. From 151 to 200, document a cohesion-based exception. |
| New files over 200 LOC | Split before implementation. Urgency, minimal diffs, or single-file requests do not grant exceptions. |
| Existing files | The file LOC limits do not apply. Do not split them merely to meet a limit. Put new responsibilities in cohesive new modules rather than extending an oversized file. |
| Routes and handlers | At most 30 LOC. Parsing, invocation, and serialization only. |
| Control flow | Decision nesting at most 2 levels. Use guard clauses and early returns without redundant `else` blocks. |
| Routines | At most 3 parameters. Do not bundle unrelated arguments to bypass the limit. |
| Complexity | Cognitive complexity at most 15; cyclomatic complexity at most 10. |

Apply the other limits to new and substantially rewritten routines. For a minimal change to legacy code, do not introduce or worsen violations; record relevant preexisting violations without requiring unrelated refactoring. Separate real responsibilities such as parsing, contracts, adapters, and domain logic. Do not create empty wrappers or arbitrary fragments, or compress lines to meet the limits. If a required cohesive split is impossible within the assigned scope after resolving instruction precedence, stop the affected implementation and report the conflict.

Use the project's existing LOC and complexity conventions and analyzer. Without a LOC convention, count all physical lines. Without a configured nesting convention, count nested decision constructs within each routine, excluding the routine itself; count declared parameters, including optional and rest parameters. If complexity cannot be measured, record manual inspection and the limitation without claiming a numeric pass. Do not install an analyzer or block solely on an unavailable metric unless the project makes that measurement a mandatory gate.

## Local cleanup and comments

- Remove obsolete branches, pass-through wrappers, and weak types in touched files when relevant to the change. Avoid unrelated cleanup.
- Keep comments only for non-obvious reasons the code cannot express. A deliberate simplification requires a known limit and a condition for revisiting it, without weakening correctness, security, accessibility, or explicit requirements.
