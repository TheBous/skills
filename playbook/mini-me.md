---
extends:
when: Writing or changing code, including features, bug fixes, and refactors.
---

### Mini-me

Luca's rules for writing code, ordered by importance. When two rules pull against each other, the earlier one wins. A rule that does not apply stays in the todo list with `skip: <reason>`.

1. **Verify for real.** Prove every change on the running program, on the latest version of the code, showing the change itself: before and after, under the conditions that matter, such as phone width for layout. If the code changes after the proof, prove it again. Skip the proof only when nothing observable changes, and say why. Never skip a proof you could run. The work is not done until it is verified.
2. **Protect production effects.** Ask what happens if an operation runs twice or stops halfway, and use protections that already exist, such as database constraints or provider guarantees. Protection state lives in storage that survives restarts, never in an in-memory variable.
3. **Make the smallest change that removes.** Fix the cause with the smallest change and prefer deleting to adding. Before adding a special case, check whether a small reorganization makes it disappear. Reorganize only code the change already passes through, and report the rest as follow-up work.
4. **Search before writing.** Look in the project for anything that already does the job or part of it: functions and helpers, classes, modules and services, components and hooks, validators, patterns already used for similar problems, types, constants, and installed libraries. Use or extend what exists instead of writing a near-copy.
5. **Build only what is needed.** Build nothing for hypothetical future needs, and do not cut anything that was asked for.
6. **Choose where the code lives.**
   - Product logic never talks directly to databases, external services, or the clock. It goes through replaceable interfaces. Keep the code that orders operations separate from the code that computes.
   - Keep the files of one feature together and give each module one responsibility. Feature logic goes in the module that owns the concept, never in shared code. A cohesive module must not gain coupling or state.
   - Functions that read change nothing. Functions that write keep data consistent, and related updates apply all together or not at all.
7. **Define types and data shapes.**
   - Justify every `any`, `unknown`, cast, or optional field. Needing one usually means the point where data enters is badly drawn, so fix it there.
   - Replace a fallback value that hides an unclear case with an explicit rule.
   - Use a declared type instead of objects built on the fly with ad-hoc fields.
8. **Keep the structure lean.**
   - Remove needless steps, mutable state, and functions that only call another function.
   - Add no generic structure (factory, strategy, abstract interface) until two real cases need it. Interfaces to the outside world are the exception. Use no "magic" mechanism that hides something simple.
   - Define a value used in several places once, and gather duplicated code into one function, but only when it is truly the same concept.
9. **Write within the limits.**
   - Flow: at most two levels of nested conditions, using early returns. Cognitive complexity at most 15 and cyclomatic complexity at most 10. No `if` or special case in an unrelated flow, no one-off booleans or modes, and no special case inside an already busy function. A condition repeated in several places means a missing type that should handle it in one place.
   - Splits: split by real responsibilities. A split must reduce what a reader has to understand, not move it. Never split with empty functions or compressed lines.
   - Files: a new file stays at or under 150 lines, and from 151 to 200 only with a documented cohesion reason. A new file that would exceed 200 lines is split before writing. Existing files are not split just for line count, but new responsibilities go in new files, and a change never pushes a file past 1000 lines.
   - Comments: only for a reason the code cannot express.
