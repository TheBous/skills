#!/usr/bin/env python3
"""Attach screenshots to a GitHub PR description and check that PRs touching the interface carry current ones.

  pr_evidence.py attach <pr> <image>... --head SHA [--repo OWNER/NAME]
  pr_evidence.py skip <pr> --reason TEXT [--head SHA] [--repo OWNER/NAME]
  pr_evidence.py check <pr> [--repo OWNER/NAME]

<pr> is a number, URL or branch, as for `gh pr view`. --head is the commit the screenshots show (required by
attach); attach and skip refuse when the PR head is another commit. A failed upload leaves the description as it was. Exit 0 on success, 1 when the check fails or gh errors.
"""

import argparse
import re
import shutil
import sys
import tempfile
from pathlib import Path

import github

START, END = "<!-- pr-evidence:start -->", "<!-- pr-evidence:end -->"
SECTION = re.compile(re.escape(START) + ".*?" + re.escape(END), re.S)
HEAD = re.compile(r"<!-- pr-evidence:head=([0-9a-f]{64}|[0-9a-f]{40}) -->")
IMAGE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)\)")
UPLOADED_PREFIX = "https://github.com/user-attachments/"
SHA = re.compile(r"[0-9a-f]{7,64}")
# A caption is the file name; these would break the markdown image or close the section early.
UNSAFE_CAPTION = re.compile(r"[\[\]\\\r\n]|<!--|-->")
SKIPPED = "No screenshots: "
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
UI_SUFFIXES = {".tsx", ".jsx", ".vue", ".svelte", ".astro", ".html", ".css", ".scss", ".sass", ".less"}
NOT_UI = re.compile(r"\.(test|spec|stories)\.|(^|/)(__tests__|e2e|tests?)/")
COLUMNS = 3


class CheckFailed(Exception):
    pass


def is_ui(path: str) -> bool:
    return Path(path).suffix in UI_SUFFIXES and not NOT_UI.search(path)


def require_paired_markers(body: str) -> None:
    if body.count(START) != body.count(END):
        raise CheckFailed("the description has a broken evidence section (pr-evidence start and end comments do not pair up); "
                          "delete those comments by hand, then run attach or skip")


def find_section(body: str) -> str | None:
    require_paired_markers(body)
    sections = SECTION.findall(body)
    if len(sections) > 1:
        raise CheckFailed(f"the description has {len(sections)} evidence sections; run attach or skip, which keeps one")
    return sections[0] if sections else None


def section_head(section: str) -> str:
    match = HEAD.search(section)
    if not match:
        raise CheckFailed("the evidence section has no head marker; run attach or skip again")
    return match.group(1)


def gallery(shots: list[tuple[str, Path]]) -> str:
    """Tables of up to COLUMNS screenshots, so GitHub shrinks them side by side; captions in the header row."""
    tables = []
    for i in range(0, len(shots), COLUMNS):
        row = shots[i:i + COLUMNS]
        cells = lambda items: "| " + " | ".join(items) + " |"
        tables.append("\n".join([cells([c.replace("|", "/") for c, _ in row]), cells(["---"] * len(row)),
                                 cells([f"![{c.replace('|', '/')}]({p})" for c, p in row])]))
    return "\n\n".join(tables)


def with_section(body: str, section: str) -> str:
    """Put section where the first evidence section was, dropping any others; append it when there is none."""
    parts = SECTION.split(body)
    if len(parts) == 1:
        return f"{body.rstrip()}\n\n{section}\n"
    return parts[0] + section + "".join(parts[1:])


def put_body(pr: dict, body: str, attachments: list[Path]) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "body.md").write_text(body)
        github.edit_body(pr, Path(tmp) / "body.md", attachments)


def confirm(pr: dict) -> None:
    written = find_section(github.pull_request(pr["url"], None)["body"] or "") or ""
    local = [dest for dest in IMAGE.findall(written) if not dest.startswith(UPLOADED_PREFIX)]
    if local:
        raise CheckFailed(f"gh did not upload {len(local)} screenshot(s)")
    if not written or section_head(written) != pr["taken"]:
        raise CheckFailed("the saved description does not hold the new section")


def write(pr: dict, content: str, attachments: list[Path]) -> None:
    """Write the section into the body as it is right now, so edits made meanwhile survive. gh saves the body when at
    least one upload worked, so after a failure put the previous body back, but only if this attempt changed it."""
    previous = github.pull_request(pr["url"], None)["body"] or ""
    require_paired_markers(previous)
    section = f"{START}\n<!-- pr-evidence:head={pr['taken']} -->\n{content}\n{END}"
    try:
        put_body(pr, with_section(previous, section), attachments)
        confirm(pr)
    except (CheckFailed, github.GhError) as error:
        rollback(pr, previous, error)
        raise CheckFailed(f"{error}; the description is as it was before, run attach again") from error


def rollback(pr: dict, previous: str, error: Exception) -> None:
    try:
        now = github.pull_request(pr["url"], None)["body"] or ""
        if now != previous and f"<!-- pr-evidence:head={pr['taken']} -->" in now:
            put_body(pr, previous, [])
    except github.GhError as failed:
        raise CheckFailed(f"{error}; restoring the description also failed ({failed}), so it may hold a partial "
                          f"section: run attach again") from error


def attach(pr: dict, images: list[str]) -> str:
    paths = [Path(i) for i in images]
    bad = [str(p) for p in paths if not p.is_file() or p.suffix.lower() not in IMAGE_SUFFIXES]
    if bad:
        raise CheckFailed(f"not an image file: {', '.join(bad)}")
    unsafe = [p.name for p in paths if UNSAFE_CAPTION.search(p.stem)]
    if unsafe:
        raise CheckFailed(f"rename {', '.join(unsafe)}: the file name is the caption and cannot contain [ ] \\, new lines or HTML comments")
    if not github.supports_attach():
        raise CheckFailed("this gh has no `gh pr edit --attach`; update gh")
    with tempfile.TemporaryDirectory() as tmp:
        staged = [Path(tmp) / f"shot-{i}{p.suffix.lower()}" for i, p in enumerate(paths)]
        for source, copy in zip(paths, staged):
            shutil.copyfile(source, copy)
        write(pr, "### Screenshots\n\n" + gallery([(p.stem, s) for p, s in zip(paths, staged)]), staged)
    return f"attached {len(paths)} screenshots to {pr['url']} for head {pr['taken'][:10]}"


def skip(pr: dict, reason: str) -> str:
    if not reason.strip() or "<!--" in reason or "\n" in reason.strip() or IMAGE.search(reason):
        raise CheckFailed("give a one-line reason, without HTML comments or images")
    write(pr, f"### Screenshots\n\n{SKIPPED}{reason.strip()}", [])
    return f"recorded why {pr['url']} has no screenshots"


def check(pr: dict) -> str:
    ui = [f for f in github.changed_files(pr) if is_ui(f)]
    if not ui:
        return "ok: the PR changes no interface files"
    section = find_section(pr["body"] or "")
    images = IMAGE.findall(section or "")
    uploaded = bool(images) and all(dest.startswith(UPLOADED_PREFIX) for dest in images)
    if images and not uploaded:
        raise CheckFailed("the evidence section links images that are not uploaded to GitHub; run attach again")
    if section is None or not (uploaded or SKIPPED in section):
        listed = ", ".join(ui[:3]) + (" ..." if len(ui) > 3 else "")
        raise CheckFailed(f"the PR changes interface files ({listed}) and its description has no screenshots. "
                          f"Run: pr_evidence.py attach {pr['number']} <screenshots>, or skip --reason when nothing visible changed")
    taken = section_head(section)
    if taken != pr["headRefOid"]:
        later = github.files_between(pr["repo"], taken, pr["headRefOid"])
        if later is None or any(is_ui(f) for f in later):
            raise CheckFailed(f"the screenshots show {taken[:10]} and interface files changed after it, "
                              f"or the history was rewritten. Take new ones and run attach again")
    return "ok: the description has current screenshots or a reason for none"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["attach", "skip", "check"])
    ap.add_argument("pr")
    ap.add_argument("images", nargs="*")
    ap.add_argument("--repo")
    ap.add_argument("--reason")
    ap.add_argument("--head")
    args = ap.parse_args()
    if (args.command == "attach") != bool(args.images) or (args.command == "skip") != (args.reason is not None):
        ap.error("attach takes images, skip takes --reason, check takes neither")
    try:
        args.head = args.head.lower() if args.head else None
        if args.command == "attach" and not (args.head and SHA.fullmatch(args.head)):
            raise CheckFailed("attach needs --head with the commit the screenshots show (at least 7 hex characters)")
        pr = github.pull_request(args.pr, args.repo)
        head = pr["headRefOid"]
        pr["taken"] = head if not args.head or head.startswith(args.head) else args.head
        if pr["taken"] != pr["headRefOid"]:
            raise CheckFailed(f"the PR head is {pr['headRefOid'][:10]}, not {pr['taken'][:10]}: prove the current head first")
        actions = {"attach": lambda: attach(pr, args.images), "skip": lambda: skip(pr, args.reason), "check": lambda: check(pr)}
        print(actions[args.command]())
        return 0
    except (CheckFailed, github.GhError) as error:
        print(f"pr-evidence: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
