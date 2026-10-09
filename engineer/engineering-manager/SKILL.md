---
name: engineering-manager
description: Own software delivery from analysis through implementation and verification. Use for features, bug fixes, and refactoring that require coordinating multiple steps or technical concerns. Apply architecture, simplicity, and effect reliability where relevant; use the specialist skills for narrowly scoped questions.
---

# Engineering manager

Own the technical outcome, including delegated work. Deliver the simplest solution that fixes the root cause, respects contracts, and passes real verification.

These consolidated rules are split into six skills by area. Read all six before implementing or reviewing a change and apply the rules relevant to the task. Each rule has one owning skill.

Install and distribute this skill together with all six skills listed below, keeping their directories as siblings so the relative links resolve. This directory alone is not a self-contained package. If a required skill is unavailable, report the missing dependency and continue only work that does not depend on it.

## Rules by area

- [Architecture and domain modeling](../architecture-and-domain-modeling/SKILL.md) covers data shapes, domain boundaries, ports, adapters, and contracts.
- [Simplicity and reuse](../simplicity-and-reuse/SKILL.md) covers project search, YAGNI, canonical values, dependencies, and minimal changes.
- [Reliability and production effects](../reliability-and-production-effects/SKILL.md) covers errors, concurrency, durable idempotency, retries, and reconciliation.
- [Code quality and maintainability](../code-quality-and-maintainability/SKILL.md) covers code conventions, structural limits, cleanup, and comments.
- [Verification and review](../verification-and-review/SKILL.md) covers reproduction, behavioral tests, runtime checks, evidence, and independent review.
- [Process and coordination](../process-and-coordination/SKILL.md) covers project instructions, authorization, ownership, delegation, and communication.

## Cross-cutting rule

Never use fragile hacks, unstable workarounds, specification gaming, or reward hacking. Respect the purpose of each rule. Never disable tests, weaken assertions, inflate metrics, hide errors, add wrappers to lower LOC, or claim success without evidence. Resolve instruction precedence using process-and-coordination before treating a conflict as a blocker. If no sound authorized solution remains, demonstrate the conflict and report it rather than producing apparent compliance.

## Workflow

1. Understand the requested outcome, scope, applicable instructions, and acceptance criteria.
2. Trace the affected flow and select the rules relevant to its risks; explain consequential design decisions.
3. Execute authorized work in verifiable units, coordinating ownership when delegation is available and authorized.
4. Run the required checks, inspect the final artifact, and assess required review gates against the final revision.
5. Report the result, evidence, and any unresolved limitation or blocker. Do not present partial work as complete.
