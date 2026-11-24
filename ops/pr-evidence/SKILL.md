---
name: pr-evidence
description: Attach the proof of a change to a GitHub pull request description (screenshots, and text evidence such as database rows, log excerpts, or test tool output), refresh it after new commits, and check that a PR changing code carries current proof. Works on any github.com repository, public or private. Use when adding or updating proof on a PR, when a reviewer asks for screenshots or evidence, or before handing off a PR whose diff changes code.
---

# PR evidence

Use the script `scripts/pr_evidence.py` next to this file; do not improvise uploads (orphan branches, commits of images into the PR branch, `raw.githubusercontent.com` links, local paths in the body). It keeps one marked "Evidence" section in the PR description that records which commit the proof shows. Screenshots are uploaded through `gh pr edit --attach`, so they live on GitHub with the repository's permissions. Text evidence is shown inline as collapsed blocks.

It needs `gh` logged in with write access, and a `gh` whose `pr edit` has `--attach` when you attach screenshots. Run it from inside the repo, or pass `--repo OWNER/NAME`.

## Choose the proof

Proof is what you observed on the running application for this change. Pick what shows the change itself:

- **Screenshots** (`.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`) when something visible changes: before and after when the change replaces something, phone width when layout matters.
- **Text evidence** (`.txt`, `.log`, `.json`, `.sql`, `.csv`, `.out`) when the change shows up elsewhere: the database rows the action wrote, read with a read-only query; the log lines it produced; the output of the tool that exercised it (an HTTP call, a CLI run, a queue consumer). Put in each file the command or query you ran and the lines that prove the result, not the whole log.

Text evidence goes into the PR description as written. Remove secrets, tokens, and personal data before attaching it.

## Attach

Name each file for what it shows, because the file name becomes the caption (no `[`, `]`, `\`, new lines or HTML comments). Always pass the commit you proved:

```bash
python3 <this-skill-dir>/scripts/pr_evidence.py attach <pr> after-desktop.png orders-row-after.sql worker-log.txt --head "$(git rev-parse HEAD)"
```

Push before attaching: attach refuses when the PR head is not that commit. Pass the whole set every time, because attach replaces the section and never adds a second one. If an upload fails, the description stays as it was: run attach again. Run it again after commits that change code. Show the same proof in your reply: screenshots as images, `![caption](/absolute/path.png)`, and the key lines of text evidence quoted, so the user sees them without opening the PR.

## Skip

When the diff changes code but nothing observable changes (types, a pure refactor), record why instead of attaching:

```bash
python3 <this-skill-dir>/scripts/pr_evidence.py skip <pr> --reason "type-only refactor, no observable change"
```

Reviewers read the reason. Do not use skip to avoid proof you could collect.

## Check

Run it before handing off the PR:

```bash
python3 <this-skill-dir>/scripts/pr_evidence.py check <pr>
```

Exit 0: the PR changes only documentation or tests, or the section is current. Exit 1: the message says what is missing, either no evidence or code commits after the ones it shows. Fix it with attach or skip, never by editing the section by hand; when the description has more than one section, they replace them all with one new section. The one manual fix: when the script reports that the `pr-evidence` start and end comments do not pair up, delete those comments, then run attach or skip.
