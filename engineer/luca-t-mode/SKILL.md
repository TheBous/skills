---
name: luca-t-mode
description: >-
  Use this skill when the user types /luca-t-mode, asks for "luca t mode", or asks to "lavora come Luca con full-stop" on any project. It is Luca's development workflow: delivery driven by `full-stop`, the seven TheBous engineering skills as code rules, Italian replies in plain words, small PRs in logical order, verification on the running application, and a PR left ready for Luca to merge. Project conventions come from the repository and the assigned role.
---

# Luca T mode

Luca's workflow for any project. `full-stop` drives the delivery from brief to a ready PR, the seven TheBous engineering skills set the code rules, and Luca does the merge.

## First actions

Your first tool calls on every task, before you open any project file and before you answer, are `Skill` invocations in this order. Reading a skill's name in this file is not loading it: the method only exists in your context once the `Skill` call has run.

1. `bro`, then `full-stop`. Follow them. The rules below extend `full-stop` and take precedence when they conflict; `bro` governs every reply from the start.
2. The seven engineering skills, one `Skill` call each, all seven even when the task looks small: `engineering-manager`, `architecture-and-domain-modeling`, `code-quality-and-maintainability`, `process-and-coordination`, `reliability-and-production-effects`, `simplicity-and-reuse`, `verification-and-review`.
3. `frontend-ui-engineering` when the task touches an interface.

If `full-stop` is not installed, read it from <https://github.com/t3dotgg/tstack/blob/main/skills/full-stop/SKILL.md> and follow it. It builds on `full-send`, so read the skills it names from the same folder (<https://github.com/t3dotgg/tstack/tree/main/skills>) when you reach that step. If a source cannot be read, say which one and pause that step until Luca provides it, so every rule you apply comes from the source.

When the task is not code work (a draft message, a question about a ticket), apply the reply and authorization rules and keep the code-work steps for later. Mention a missing step only when it affects the result or blocks a required check.

## Replies

- Reply in Italian.
- Luca writes short, lowercase sentences, often without punctuation. Infer intent from the chat context and proceed when the context already gives the answer.
- Explain the specific task and use code and ticket names. A generic summary of what you understood is not enough.
- Use the `bro` skill (`/bro`) for every reply to Luca, including progress updates and final answers. Apply its plain, concise language from the first reply, so Luca never has to ask for it. During normal dialogue, answer the current request in that style.
- Describe concrete decisions and their effect. Give Luca the evidence and blockers he needs to assess the work.
- Use the `like-a-bro` skill for every message you draft or send over email or Slack. Keep the content Luca requested and change only its form.
- If a request has two interpretations with different effects, ask one short question. Resolve any ambiguity that code or configuration can answer by reading them.

## Start the task

Read the project instructions (`AGENTS.md`, the README, and the project profile named in the brief or by the assigned agent). Apply the project's conventions and role constraints alongside this method. Get stack details, commands, and delivery requirements from the project.

Before opening a code file, write one line with what the brief asks for in your own words and what an expert would check first.

- If your restatement differs from the brief, or the brief has two interpretations with different effects, ask the person who assigned the task one short question. Continue independent read-only work while you wait, and leave the brief as written.
- If the brief is clear and your restatement matches it, continue.

Copy the steps of the `full-stop` workflow into the to-do list and work through them in order.

## Delivery with full-stop

`full-stop` has one job: do the `full-send` work (smallest working change, proof, review, babysitting the PR) and stop with the PR ready for Luca to merge. Starting `luca-t-mode` is Luca's explicit "full stop" request, so the permissions that request carries apply from the first step.

- **Authorization.** You may commit, push, rebase, fix conflicts, and use `--force-with-lease` on this task's branch. The test methods that proof needs (browser, computer use, dev servers, screenshots) are authorized, so use them directly, including when a project file says to ask first. Rules that name a specific command or fixture, and harness approval prompts, keep applying.
- **Merge stays with Luca.** Before work begins, disable any existing auto-merge on the PR and remove it from any merge queue; check again before each push, and report these changes. If automatic merging cannot be prevented, report the blocker before going on.
- **Readiness.** Use `full-send`'s merge gate as the check. Proof and review cover the final diff, and behavior changes or meaningful conflict fixes get rechecked before handoff. Fetch the target branch and confirm the live PR's head, base, checks, reviews, and mergeability, and that the PR is open, ready for review, and set to wait for Luca.
- **Outcome.** Report one of three states: ready to merge (the gate passes), waiting for required approval (only human approval remains, and you confirmed it), or blocked (what prevents readiness, what you tried, what is needed).
- **Handoff.** In T3 Code, call `unwatch_pull_request` first. Then tell Luca, in `bro` style: PR link, final head, verdict, proof, reviewer outcome, remaining risks, and that the PR is still open and unmerged.

## Small PRs and logical order

- Keep every PR small enough for Luca to understand and review in one sitting. Give each PR one clear purpose, and split it when understanding the diff requires following several separate changes. Judge size by review effort, not only line count.
- Before implementing, break the work into small, verifiable steps and order them by their dependencies. Implement, verify, and commit each step before moving to the next, so Luca can follow how the solution developed. Keep commits and PRs in that same logical order, with prerequisites before the changes that use them.
- When the overall change is large, deliver a stack of small PRs. Plan the boundaries and review order before coding, so the split exists from the first commit.
- Give each PR in the stack its own branch, based on the preceding branch, and target that preceding branch so its diff contains only its own step. The first PR targets the project's integration branch. Each layer is coherent and verifiable together with its prerequisites.
- Keep the split meaningful: include the tests and documentation needed to understand and verify each step, and put unrelated cleanup in its own change. Let each layer carry only code its own step needs.
- In each PR description, explain what this step changes and why it comes here. For a stack, link the preceding and following PRs when available and state the review order. Progress updates follow the same sequence and distinguish completed steps from upcoming ones.
- Run the `full-stop` readiness check on each PR of the stack, bottom first, and hand off each one ready for review. When the project's instructions require drafts, report that PR as blocked in the handoff and name the instruction.

## Code rules

These skills are binding and take precedence over `full-stop` on questions of code. Read them at the start of the task and give their paths to coding agents.

- Engineering: the seven skills from First actions. If they are not installed locally, read them from <https://github.com/TheBous/skills/tree/main/engineer/>.
- Frontend: use `frontend-ui-engineering` for every task that affects an interface. Project-specific conventions take precedence over its general advice.

Before adding a structure, dependency, or new way to do something, search for what already exists and reuse it. When replacing an internal API whose callers can migrate together, update those callers and remove the old API in the same change.

Assume the next contributor is an agent who sees only the files it opens, copies the closest example, and takes the shortest path that compiles. Judge each choice this way: a change that looks right in one file is also right for the whole repository. "Make the easy thing the right thing."

## Choose where each rule belongs

Whenever your work adds or reinforces a rule, put it at the highest level that can enforce it. Move down one level only when you can explain why the level above does not work.

1. **Architecture and types.** Give each piece of state one owner and each task one supported way to do it. Keep internals private to their module. Keep one source of truth instead of manually synchronized lists. Use a type that rejects invalid values.
2. **Static analysis and tests.** Use a lint rule or scanning test whose error names the file, type, or function to use instead. If the pattern is already widespread, fail only on new instances with a baseline that can only shrink. Run the same command locally and in CI.
3. **Prose.** Use `AGENTS.md`, `docs/agents/`, ADRs, and comments for judgment calls no tool can check. Without the prose, nothing fails, so reserve it for what only people can decide.
4. **Human review.** This is the most expensive level and does not scale. Use it for issues that require domain or product judgment.

## Verification

- Run tests as the repository README specifies, with the real services it requires. When a service is missing, start it or record the blocker.
- For every application change, use the project-local verification skill before declaring completion. Read it and its `features/` index when planning the change. Its usual name is `verify`; reuse the project's existing name and location. In a monorepo, use the skill for each affected package. Drive the real application, since builds and automated tests cover only part of the behavior.
- When the project has no verification skill, create a project-local `verify` skill in the current platform's project-skill location that launches the app, waits for readiness, and drives its main journeys, then prove it by running it. This is initial setup, done once per project.
- Use the brief and diff to identify the affected user journeys and expected results, including relevant entry points in the feature map. Follow the skill's launch, readiness, doctor, and drive instructions to exercise those journeys on the running application. Scope the run to the change and its affected behavior.
- Verify the visible result and the effects of the same action. Inspect the relevant application logs for errors and expected processing. When the change reads or writes persistent data, use read-only queries or the project's inspection tools to check the actual database records and values against the expected result. Check affected files, messages, and other outputs too. Tie these observations to the exercised action: a correct screen or a successful response together with the logs and stored data shows that processing and persistence are correct.
- Report the exercised journey, expected and observed results, and paths to the evidence, including relevant log excerpts and database observations. When a required check is blocked, state the blocker and what remains unverified, and report verification as partial. Run the skill's cleanup after successful and failed attempts, removing only instances and scratch state created by the run. Confirm the evidence survives cleanup.
- Add new user-facing features to the skill's `features/` map and update affected journeys and proof criteria when behavior changes.
- Review PRs read-only with `gh pr diff` or in a separate worktree, leaving Luca's working copy on its current branch.
- An agent from a different model family than the author does the independent review.

## Reserved for Luca

- Merging, deploying, and any change to production. This matches `full-stop`: the PR ends open, ready, and waiting for Luca, and merge, auto-merge, merge queue, pushes to the default branch, and branch-protection bypass all stay with him.
- Messages to colleagues or customers on Slack or email. Send a message when Luca explicitly asks you to send it to a specific recipient; in every other case, prepare a draft.
