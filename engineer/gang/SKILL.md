---
name: gang
description: >-
  Orchestrate a multi-model engineering team in T3 Code using `delegate_task`:
  Fable 5.2 as lead, Opus 5.5 builders developing via `/luca-t-mode` in isolated
  worktrees, GPT-6.2 Sol (high) as read-only cross-family playtester, and Gemini 4 Neon
  as copywriter. Use only when the user explicitly invokes `/gang` or asks to run
  a task with the multi-model T3 team ("gang"). Never invoke automatically on
  small single-agent tasks.
---

# Gang

Orchestrate a multi-model development team inside T3 Code from spec to a verified PR ready for Luca. Keep all team rules self-contained here—no project-level `TEAM.md` is required.

## Replies

- Reply to Luca in Italian with plain, direct words and no jargon (`/bro` style).
- Keep internal orchestration mechanics, skill names, and tool names out of replies unless Luca asks; report concrete slices, owners, verification evidence, review findings, and blockers.

## Team roster and providers

Call `orchestrator_capabilities` once per thread before the first `delegate_task` to confirm exact provider instances, model IDs, and options. If any required provider or model is disabled or missing, stop and tell Luca—never silently switch providers.

| Role | Provider (`providerInstanceId`) | Model | Options | Isolation | Responsibility |
| --- | --- | --- | --- | --- | --- |
| **Lead** | Current thread (ideally `claudeAgent`) | `claude-fable-5-2` | `effort: "high"` | Main / lead branch | Read repo, write spec, wait for Luca's approval, split disjoint slices, take hardest slice if appropriate, coordinate review & copy, hand off ready PR |
| **Builders** | `claudeAgent` | `claude-opus-5-5` | `effort: "high"` | `worktree` | One disjoint slice per builder, always developing via `/luca-t-mode` |
| **Playtester** | `codex` | `gpt-6.2-sol` | `reasoningEffort: "high"` | `shared` | Cross-family adversarial review and edge-case testing. Strictly read-only by brief |
| **Copywriter** | `antigravity` | `gemini-4-neon` | default | `worktree` (or final branch) | Last step: `docs/`, `README.md`, `CHANGELOG.md`, and UI copy / i18n only |

Use `effort: "high"` on Fable and Opus, not `xhigh` or `max`. Never use Astra (`gpt-6.2-astra` or any Astra variant); always use `codex` / `gpt-6.2-sol` with `reasoningEffort: "high"`.

## Guardrails

- **Child context is blank**: Every `delegate_task` child sees only `task`, never parent history. Always send a complete 7-field `BRIEF`.
- **Builders always use `/luca-t-mode`**: Every Builder brief must instruct the builder to invoke and follow `/luca-t-mode` (the `mini-me` playbook as code rules, `senior-frontend` if UI, small clean commits, and real verification), while respecting the slice boundaries and stopping without merging or watching PRs. When the Lead writes code itself (hardest slice or small fixes), apply `/luca-t-mode` code and verification rules too.
- **Permission ceiling**: A child's `runtimeMode` cannot be broader than the parent's. Omit `runtimeMode` unless Luca asks for a supervised child.
- **Read-only is a brief rule, not a lock**: Narrow T3 modes pause for human approval rather than blocking edits. Always state `DO NOT: edit or fix anything. Report only.` in the Playtester brief.
- **Worktrees isolate files, not runtime state**: Parallel builders share ports and local databases; coordinate test ports/DBs in `CONTEXT` when services run.
- **Hard limits**:
  - Max **3 review rounds** with the Playtester; if issues remain after round 3, stop and escalate to Luca.
  - Max **4 agent-to-agent handoffs** without checking in with Luca.
  - Never touch `.env*`, database migrations, or CI/CD config without Luca's explicit approval.
  - **Merging, deploying, and pushes to the default branch stay with Luca.** Disable auto-merge and leave PRs open and ready.
- **Fresh review threads**: Never use `t3_thread_send` for a new review round. Start a new `delegate_task` with the updated diff and prior findings.
- **No polling**: Follow the `next` instruction returned by `delegate_task`. Never loop on `task_status` or `sleep`.

## Workflow

Execute these steps in order:

1. **Check capabilities and inspect the repo**
   - Call `orchestrator_capabilities`.
   - Read project instructions (`AGENTS.md`, `README.md`, and any project-local `verify` skill) plus the relevant code. Do not write feature code yet.

2. **Write the spec and wait for Luca's approval**
   - Write a concise spec (in chat, or in `SPEC.md` when the feature is large or multi-slice) covering:
     - Goal and acceptance test
     - Disjoint slices and exact file ownership per slice
     - PR shape (single PR or small logical stack per `/luca-t-mode`, max 6)
     - Risks and verification plan
   - **Stop and wait for Luca's explicit approval before writing code or delegating builders.**

3. **Delegate Builders in parallel worktrees**
   - For each independent slice touching disjoint files, call `delegate_task`:
     - `target: { providerInstanceId: "claudeAgent", model: "claude-opus-5-5", options: { effort: "high" } }`
     - `isolation: "worktree"`, `role: "implementation"`
     - `task`: full 7-field Builder `BRIEF` requiring `/luca-t-mode`
   - Optionally take the hardest slice yourself (on disjoint files only).
   - Wait for builders to finish and verify each returned `DONE WHEN` evidence.

4. **Integrate and run cross-family Playtest (max 3 rounds)**
   - Combine the builder worktrees onto the integration branch (or verify each stack layer in order) and run the project's verification checks.
   - Delegate a read-only review to `codex` / `gpt-6.2-sol` (`options: { reasoningEffort: "high" }`, `role: "review"`) with the task, spec, and combined diff. Do **not** include your own conclusions so Sol evaluates independently.
   - Fix small confirmed findings yourself; delegate larger fixes to an Opus builder (`claude-opus-5-5` with `/luca-t-mode`).
   - Re-check fixes with a fresh Playtester `delegate_task`. Stop after round 3 and report unresolved items to Luca.

5. **Delegate Copywriter last (when applicable)**
   - Skip this step if the change has no user-facing strings, docs, README, or changelog updates.
   - Delegate to `antigravity` / `gemini-4-neon` (`role: "implementation"`) with the spec and final diff, restricted strictly to documentation and UI copy paths.

6. **Hand off to Luca**
   - Confirm tests, verification on the real artifact, and PR readiness (open, unmerged, auto-merge off).
   - Report in plain Italian (`/bro` style): slices and owners, PR link and head SHA, verification evidence, Playtester verdict and rounds used, copy changes, and remaining risks.

## Mandatory 7-field BRIEF format

Every `delegate_task` prompt must include all seven fields:

```text
BRIEF FOR: <providerInstanceId / model>
ROLE: <builder | playtester | copywriter>
GOAL: <single concrete outcome>
CONTEXT: <exact file paths, architectural decisions, spec or diff reference>
DONE WHEN: <verifiable command, test, or check>
DO NOT: <strict file boundaries and forbidden actions>
RETURN: <exact report format expected back>
```

## Role brief templates

### Builder (`claudeAgent` / `claude-opus-5-5`)

```text
BRIEF FOR: claudeAgent / claude-opus-5-5
ROLE: builder (develop strictly via `/luca-t-mode`)
GOAL: <concrete slice goal>
CONTEXT:
- Invoke and follow `/luca-t-mode` from your first tool call (read its `mini-me` playbook, plus `senior-frontend` if touching UI, and verify against the real artifact).
- Independent review is already assigned to the Lead's playtester (`codex` / `gpt-6.2-sol`, high): do not start another reviewer and do not ask Luca for one.
- Spec / decisions: <summary or path to SPEC.md section>.
- Target files to edit: <explicit list>.
- Shared runtime constraints (if any): <ports / DB notes>.
DONE WHEN: <exact test/build/verification commands that must pass>.
DO NOT:
- Do not touch files outside your slice: <excluded paths>.
- Do not touch `.env*`, migrations, or CI config unless explicitly listed in GOAL.
- Do not merge, deploy, push to the default branch, or watch/babysit PRs. Stop with clean, verified commits on this worktree branch (open a PR only if GOAL explicitly requests one).
RETURN:
- Branch name and final commit SHA
- Files changed
- Test and real-artifact verification output
- Open doubts or risks
```

### Playtester (`codex` / `gpt-6.2-sol`, `reasoningEffort: "high"`)

```text
BRIEF FOR: codex / gpt-6.2-sol (reasoningEffort: high)
ROLE: playtester (read-only)
GOAL: Break this change and find real bugs or regressions a user would hit.
CONTEXT:
- Task & acceptance test: <summary>.
- Spec: <summary or path to SPEC.md>.
- Diff / branch to inspect: <diff or branch/commit range>.
- Prior round findings (rounds 2-3 only): <list>.
DONE WHEN: You have checked the diff and tested edge cases relevant to the change: empty input, huge input, concurrent actions / two tabs, slow or failed network, unicode (e.g. "Piña"), expired auth, missing permissions, and domain invariants.
DO NOT: Edit, fix, commit, or write any code. Report only.
RETURN: Numbered list of findings. For each: severity (1=blocker, 2=major, 3=minor), repro steps, expected behavior, actual behavior, and file:line reference. If clean, state explicitly what you checked and found passing.
```

### Copywriter (`antigravity` / `gemini-4-neon`)

```text
BRIEF FOR: antigravity / gemini-4-neon
ROLE: copywriter
GOAL: Update documentation, changelog, and user-facing UI strings for this feature.
CONTEXT:
- Spec: <summary or path to SPEC.md>.
- Final diff: <diff or commit range>.
- Tone: short sentences, plain language, no jargon, no hype (match existing repo language).
DONE WHEN: Every new or changed user-facing string has clear copy, docs match the final behavior, and the changelog entry explains what changed and why a user should care in 3 lines or less.
DO NOT: Touch any file outside `docs/`, `README.md`, `CHANGELOG.md`, and UI copy / i18n paths (`<explicit paths>`). Never edit logic or tests.
RETURN: Edited files and the final changelog entry.
```
