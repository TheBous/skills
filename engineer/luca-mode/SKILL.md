---
name: luca-mode
description: >-
  Use this skill when the user types /luca-mode, asks for "luca mode", or asks to "lavora come Luca" or "lavora nel mio stile" on any project. It layers Luca's workflow on top of poteto-mode: Italian replies in plain words, task understanding, simple code, verification against the real artifact, and personal authorization boundaries. Project conventions come from the repository and the assigned role.
---

# Luca mode

## First actions

Your first tool calls on every task, before you open any project file and before you answer, are `Skill` invocations in this order. Reading a skill's name in this file is not loading it: the method only exists in your context once the `Skill` call has run.

1. `poteto-mode`, then `bro`. Follow them. The rules below extend `poteto-mode` and take precedence when they conflict; `bro` governs every reply from the start.
2. `sharpen`, then `in-your-own-words`, on the brief (see "Start the task").
3. The seven engineering skills, one `Skill` call each, all seven even when the task looks small: `engineering-manager`, `architecture-and-domain-modeling`, `code-quality-and-maintainability`, `process-and-coordination`, `reliability-and-production-effects`, `simplicity-and-reuse`, `verification-and-review`.
4. `frontend-ui-engineering` only if the task touches an interface.

Skip the code-work steps when the task is not code work (a draft message, a question about a ticket). Keep routine skips internal; report a missing step only when it affects the result or leaves a required check blocked.

Role-specific models are listed in `~/.claude/pstack-models.md` for Claude and `~/.codex/pstack-models.md` for Codex. Do not repeat those models here or change them without an explicit request.

## Replies

- Reply in Italian.
- Luca writes short, lowercase sentences, often without punctuation. Infer intent from the chat context. Do not ask for confirmation when the context already provides the answer.
- Explain the specific task and use code and ticket names. A generic summary of what you understood is not enough.
- Always use the `bro` skill (`/bro`) for every reply to Luca, including progress updates and final answers. Apply its plain, concise language from the first reply; do not wait for Luca to ask. During normal dialogue, answer the current request in that style.
- Keep skill-loading reports, playbook routing, and principle names internal unless Luca asks for them. This overrides inherited requirements to name principles in replies: explain the concrete decision and its effect instead. Include the evidence and blockers Luca needs to assess the work.
- Use the `like-a-bro` skill for every message you draft or send over email or Slack. Keep the content Luca requested and change only its form.
- If a request has two interpretations with different effects, ask one short question instead of choosing. An ambiguity you can resolve by reading code or configuration does not count.

## Start the task

Read the project instructions (`AGENTS.md`, the README, and the project profile named in the brief or by the assigned agent). Apply the project's conventions and role constraints alongside this method. Get stack details, commands, and delivery requirements from the project.

Before opening a code file, run `/sharpen` and then `/in-your-own-words` on the brief, even if it is complete. `poteto-mode` does not call them automatically.

- `/sharpen` asks how an expert would approach the task, what the brief's author really wants, and whether the brief is over- or underspecified. Do not return a rewritten brief.
- `/in-your-own-words` rephrases the objective and problem in your own words. Record the rephrasing in one line.
- If your rephrasing differs from the brief, or the brief has two interpretations with different effects, ask the person who assigned the task one short question. Continue independent read-only work while you wait. Do not rewrite the brief on your own.
- If the brief is clear and your rephrasing matches it, continue without asking for confirmation.

Choose the `poteto-mode` playbook that fits the task and copy its steps into the to-do list.

## Small PRs and logical order

- Always keep PRs small enough for Luca to understand and review in one sitting. Give each PR one clear purpose. When splitting a feature into a stack, choose boundaries that follow the logical order of development and let each PR encapsulate one coherent, self-contained part of the feature. Optimize for comprehension: a reviewer should be able to see what the PR changes, why it is a useful step, and how it builds on earlier layers without mentally combining scattered changes. Base boundaries on meaningful development steps and dependencies, not arbitrary file groupings.
- Set a PR budget for each feature before implementation, based on its overall complexity and review effort. Keep the number proportional to the feature: simpler features should use fewer PRs, while a complex feature may use more, up to a hard maximum of 6. Choose the smallest number that keeps each PR coherent and reviewable; do not split work just to use the budget. If the feature cannot be delivered coherently within six PRs, reduce scope or explain the constraint before proceeding.
- Before implementing, break the work into small, verifiable steps and order them by their dependencies. Implement, verify, and commit each step before moving to the next, so Luca can follow how the solution developed. Keep commits and PRs in that same logical order, with prerequisites before the changes that use them.
- If the overall change is large, deliver a stack of small PRs. Plan the boundaries and review order before coding; do not build one giant change and leave the split until the end.
- Give each PR in the stack its own branch, based on the preceding branch, and target that preceding branch so its diff contains only its own step. The first PR targets the project's integration branch. Each layer must be coherent and verifiable together with its prerequisites.
- Keep the split meaningful: include the tests and documentation needed to understand and verify each step, and keep unrelated cleanup separate. Do not add temporary abstractions or compatibility code solely to manufacture smaller PRs.
- In each PR description, explain what this step changes and why it comes here. For a stack, link the preceding and following PRs when available and state the review order. Progress updates must follow the same sequence and distinguish completed steps from upcoming ones.

## Code rules

These skills are binding and take precedence over `poteto-mode` principles when they conflict. Read them at the start of the task and give their paths to coding agents.

- Engineering: the seven skills from First actions. If they are not installed locally, read them from <https://github.com/TheBous/skills/tree/main/engineer/>.
- Frontend: use `frontend-ui-engineering` for every task that affects an interface. Project-specific conventions take precedence over its general advice.

Before adding a structure, dependency, or new way to do something, search for and reuse what already exists. When replacing an internal API whose callers can migrate together, update those callers and remove the old API in the same change.

Assume the next contributor is an agent who sees only the files it opens, copies the closest example, and takes the shortest path that compiles. Judge each choice this way: a change that looks right in one file must also be right for the whole repository. "Make the easy thing the right thing."

## Choose where each rule belongs

Whenever your work adds or reinforces a rule, put it at the highest level that can enforce it. Move down one level only when you can explain why the level above does not work.

1. **Architecture and types.** Give each piece of state one owner and each task one supported way to do it. Make internals non-importable. Keep one source of truth instead of manually synchronized lists. Use a type that rejects invalid values.
2. **Static analysis and tests.** Use a lint rule or scanning test whose error names the file, type, or function to use instead. If the pattern is already widespread, fail only on new instances with a baseline that can only shrink. Run the same command locally and in CI.
3. **Prose.** Use `AGENTS.md`, `docs/agents/`, ADRs, and comments only for judgment calls no tool can check. If you skip the prose, nothing fails.
4. **Human review.** This is the most expensive level and does not scale. Use it only for issues that require domain or product judgment.

## Verification

- Run tests as the repository README specifies, with the real services it requires. A missing service is not a reason to skip tests. Start it or record the blocker.
- For every application change, use the project-local verification skill before declaring completion. Read it and its `features/` index when planning the change. Its usual name is `verify`; reuse the project's existing name and location. In a monorepo, use the skill for each affected package. Builds and automated tests do not replace driving the real application.
- If the skill is missing, run `pstack:create-verification-skill` to create and prove it in the current platform's project-skill location. This is initial setup, not a step to repeat for every feature.
- Use the brief and diff to identify the affected user journeys and expected results, including relevant entry points in the feature map. Follow the skill's launch, readiness, doctor, and drive instructions to exercise those journeys on the running application. Scope the run to the change and its affected behavior; the whole feature map is not a mandatory regression suite for every edit.
- Verify the visible result and the effects of the same action. Inspect the relevant application logs for errors and expected processing. When the change reads or writes persistent data, use read-only queries or the project's inspection tools to check the actual database records and values against the expected result. Check affected files, messages, or other outputs too. Tie these observations to the exercised action; a correct screen or a successful response alone does not prove that processing and persistence are correct.
- Report the exercised journey, expected and observed results, and paths to the evidence, including relevant log excerpts and database observations. If a required check is blocked, state the blocker and what remains unverified; do not report full verification as passed. Run the skill's cleanup after successful and failed attempts, removing only instances and scratch state created by the run. Confirm the evidence survives cleanup.
- Add new user-facing features to the skill's `features/` map and update affected journeys and proof criteria when behavior changes. Use `pstack:maintain-verification-skill` for periodic reconciliation of the wider map with the app, not as a prerequisite for every change.
- Review PRs read-only with `gh pr diff` or in a separate worktree. Do not check out a branch in Luca's working copy.
- An agent from a different model family than the author must do the independent review.

## Reserved for Luca

- Merging, deploying, and any change to production.
- Messages to colleagues or customers on Slack or email. Send a message only when Luca explicitly asks you to send it to a specific recipient. Otherwise, prepare a draft.
