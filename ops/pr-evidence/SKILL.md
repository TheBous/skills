---
name: pr-evidence
description: Attach screenshots to a GitHub pull request description, refresh them after new commits, and check that a PR touching the interface carries current screenshots. Works on any github.com repository, public or private. Use when adding or updating screenshots or visual proof on a PR, when a reviewer asks for screenshots, or before handing off a PR whose diff touches UI files.
---

# PR evidence

Use the script `scripts/pr_evidence.py` next to this file; do not improvise uploads (orphan branches, commits of images into the PR branch, `raw.githubusercontent.com` links, local paths in the body). The script uploads through `gh pr edit --attach`, so the images live on GitHub with the repository's permissions, and it keeps one marked "Screenshots" section in the PR description that records which commit the screenshots show.

It needs a `gh` whose `pr edit` has `--attach`, logged in with write access. Run it from inside the repo, or pass `--repo OWNER/NAME`.

## Attach

After the proof run, choose the screenshots that show the change: before and after when the change replaces something, phone width when layout matters. Name each file for what it shows, because the file name becomes the caption (no `[`, `]`, `\`, new lines or HTML comments). Always pass the commit you took them on:

```bash
python3 <this-skill-dir>/scripts/pr_evidence.py attach <pr> after-desktop.png after-phone.png --head "$(git rev-parse HEAD)"
```

Push before attaching: attach refuses when the PR head is not that commit. Pass the whole set every time, because attach replaces the section and never adds a second one. If an upload fails, the description stays as it was: run attach again. Run it again after commits that change the interface. Show the same files in your reply as images, `![caption](/absolute/path.png)`, so the user sees them without opening the PR.

## Skip

When the diff touches UI files but nothing visible changes (types, a refactor, a hook), record why instead of attaching:

```bash
python3 <this-skill-dir>/scripts/pr_evidence.py skip <pr> --reason "refactor of the hook, no visible change"
```

Reviewers read the reason. Do not use skip to avoid a screenshot you could take.

## Check

Run it before handing off the PR:

```bash
python3 <this-skill-dir>/scripts/pr_evidence.py check <pr>
```

Exit 0: the PR changes no interface files, or the section is current. Exit 1: the message says what is missing, either no screenshots or interface commits after the ones they show. Fix it with attach or skip, never by editing the section by hand; when the description has more than one section, they replace them all with one new section.
