#!/usr/bin/env python3
"""Attach proof (screenshots and text evidence) to a GitHub PR description and check that PRs changing code carry current proof.

  pr_evidence.py attach <pr> <file>... --head SHA [--repo OWNER/NAME]
  pr_evidence.py skip <pr> --reason TEXT [--head SHA] [--repo OWNER/NAME]
  pr_evidence.py check <pr> [--repo OWNER/NAME]

<pr> is a number, URL or branch, as for `gh pr view`. A <file> is a screenshot (uploaded) or a text excerpt such as
database rows, logs or tool output (shown inline). --head is the commit the proof shows (required by attach); attach
and skip refuse when the PR head is another commit. A failed upload leaves the description as it was. Exit 0 on
success, 1 when the check fails or gh errors.
"""

import argparse
import re
from dataclasses import dataclass
import shutil
import sys
import tempfile
from pathlib import Path

import github
import text_evidence

START, END = "<!-- pr-evidence:start -->", "<!-- pr-evidence:end -->"
# Markers count only on their own line, so a mention in prose is not a section.
MARKER = re.compile(rf"^[ \t]*({re.escape(START)}|{re.escape(END)})[ \t]*$", re.M)
SECTION = re.compile(rf"^[ \t]*{re.escape(START)}[ \t]*$.*?^[ \t]*{re.escape(END)}[ \t]*$", re.S | re.M)
DESTINATION = re.compile(r"(!\[[^\]]*\]\()[^)]*\)")
HEAD = re.compile(r"<!-- pr-evidence:head=([0-9a-f]{64}|[0-9a-f]{40}) -->")
IMAGE = re.compile(r'!\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+"[^"]*")?\s*\)')
UPLOADED_PREFIX = "https://github.com/user-attachments/"
SHA = re.compile(r"[0-9a-f]{7,64}")
# A caption is the file name; these would break the markdown image or close the section early.
UNSAFE_CAPTION = re.compile(r"[\[\]\\\r\n]|<!--|-->")
SKIPPED = "No evidence: "
SKIPPED_BEFORE = "No screenshots: "  # sections written before text evidence existed
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
DOC_SUFFIXES = {".md", ".mdx", ".rst", ".txt"}
NOT_BEHAVIOR = re.compile(r"\.(test|spec|stories)\.|(^|/)(__tests__|e2e|tests?|docs)/")
BODY_LIMIT = 65536  # GitHub rejects longer PR descriptions
UPLOAD_URL_ROOM = 150  # gh replaces each local image path with a longer URL
COLUMNS = 3


class CheckFailed(Exception):
    pass


def needs_proof(path: str) -> bool:
    """Code and assets change behavior; documentation and tests do not."""
    return Path(path).suffix.lower() not in DOC_SUFFIXES and not NOT_BEHAVIOR.search(path)


def require_paired_markers(body: str) -> None:
    """Start and end lines must alternate, start first: nested, reversed or unpaired markers cannot be repaired safely."""
    marks = MARKER.findall(body)
    if marks != [START, END] * (len(marks) // 2):
        raise CheckFailed("the description has a broken evidence section (pr-evidence start and end comments do not "
                          "pair up); delete those comments by hand, then run attach or skip")


def is_complete(section: str) -> bool:
    images = IMAGE.findall(section)
    if images:
        return all(dest.startswith(UPLOADED_PREFIX) for dest in images)
    return bool(text_evidence.BLOCK.search(section)) or SKIPPED in section or SKIPPED_BEFORE in section


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


@dataclass
class Attempt:
    previous: str  # the description before this attempt
    sent: str  # the description this attempt wrote, before gh rewrote image destinations


def write(pr: dict, content: str, attachments: list[Path]) -> None:
    """Write the section into the body as it is right now, so edits made meanwhile survive. gh saves the body when at
    least one upload worked, so a failure can leave a partial section: settle() decides what to do with it."""
    previous = github.pull_request(pr["url"], None)["body"]
    require_paired_markers(previous)
    section = f"{START}\n<!-- pr-evidence:head={pr['taken']} -->\n{content}\n{END}"
    attempt = Attempt(previous, with_section(previous, section))
    if len(attempt.sent) + UPLOAD_URL_ROOM * len(attachments) > BODY_LIMIT:
        raise CheckFailed(f"the description would pass GitHub's {BODY_LIMIT}-character limit; "
                          f"keep only the lines of text evidence that prove the change")
    try:
        put_body(pr, attempt.sent, attachments)
        confirm(pr)
    except (CheckFailed, github.GhError) as error:
        fail_after(pr, attempt, error)


def fail_after(pr: dict, attempt: Attempt, error: Exception) -> None:
    """Raise what went wrong and what happened to the description, unless the saved section is complete after all."""
    try:
        outcome = settle(pr, attempt)
    except (CheckFailed, github.GhError) as failed:
        raise CheckFailed(f"{error}; checking or restoring the description also failed ({failed}), so it may "
                          f"hold a partial section: try again") from error
    if outcome:
        raise CheckFailed(f"{error}; {outcome}. Try again") from error


def settle(pr: dict, attempt: Attempt) -> str | None:
    """After a failed write: None when the saved section is complete after all, else what happened to the description.
    Restore only when the saved body is exactly what this attempt sent, apart from image destinations gh rewrote."""
    now = github.pull_request(pr["url"], None)["body"]
    if now == attempt.previous:
        return "the description was not changed"
    if DESTINATION.sub(r"\1)", now) != DESTINATION.sub(r"\1)", attempt.sent):
        return "the description changed meanwhile and was left as it is"
    if is_complete(find_section(now) or ""):
        return None
    put_body(pr, attempt.previous, [])
    return "its partial section was removed and the description put back as it was"


def attach(pr: dict, files: list[str]) -> str:
    paths = [Path(f) for f in files]
    bad = [str(p) for p in paths if not p.is_file() or not (p.suffix.lower() in IMAGE_SUFFIXES or text_evidence.is_text(p))]
    if bad:
        raise CheckFailed(f"not a screenshot or text evidence file: {', '.join(bad)}")
    unsafe = [p.name for p in paths if UNSAFE_CAPTION.search(p.stem)]
    if unsafe:
        raise CheckFailed(f"rename {', '.join(unsafe)}: the file name is the caption and cannot contain [ ] \\, new lines or HTML comments")
    images = [p for p in paths if not text_evidence.is_text(p)]
    try:
        texts = [text_evidence.block(p.stem, text_evidence.read(p)) for p in paths if text_evidence.is_text(p)]
    except text_evidence.TextEvidenceError as error:
        raise CheckFailed(str(error)) from error
    if images and not github.supports_attach():
        raise CheckFailed("this gh has no `gh pr edit --attach`; update gh")
    with tempfile.TemporaryDirectory() as tmp:
        staged = [Path(tmp) / f"shot-{i}{p.suffix.lower()}" for i, p in enumerate(images)]
        for source, copy in zip(images, staged):
            shutil.copyfile(source, copy)
        shots = [gallery([(p.stem, s) for p, s in zip(images, staged)])] if images else []
        write(pr, "### Evidence\n\n" + "\n\n".join(shots + texts), staged)
    return f"attached {len(images)} screenshots and {len(texts)} text evidence files to {pr['url']} for head {pr['taken'][:10]}"


def skip(pr: dict, reason: str) -> str:
    if not reason.strip() or "<!--" in reason or "\n" in reason.strip() or "![" in reason:
        raise CheckFailed("give a one-line reason, without HTML comments or images")
    write(pr, f"### Evidence\n\n{SKIPPED}{reason.strip()}", [])
    return f"recorded why {pr['url']} has no evidence"


def check(pr: dict) -> str:
    code = [f for f in github.changed_files(pr) if needs_proof(f)]
    if not code:
        return "ok: the PR changes only documentation or tests"
    section = find_section(pr["body"] or "")
    if section is not None and IMAGE.search(section) and not is_complete(section):
        raise CheckFailed("the evidence section links images that are not uploaded to GitHub; run attach again")
    if section is None or not is_complete(section):
        listed = ", ".join(code[:3]) + (" ..." if len(code) > 3 else "")
        raise CheckFailed(f"the PR changes code ({listed}) and its description has no evidence. Run: pr_evidence.py "
                          f"attach {pr['number']} <screenshots or text files>, or skip --reason when nothing observable changed")
    taken = section_head(section)
    if taken != pr["headRefOid"]:
        later = github.files_between(pr["repo"], taken, pr["headRefOid"])
        if later is None or any(needs_proof(f) for f in later):
            raise CheckFailed(f"the evidence shows {taken[:10]} and code changed after it, "
                              f"or the history was rewritten. Prove the new head and run attach again")
    return "ok: the description has current evidence or a reason for none"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["attach", "skip", "check"])
    ap.add_argument("pr")
    ap.add_argument("files", nargs="*")
    ap.add_argument("--repo")
    ap.add_argument("--reason")
    ap.add_argument("--head")
    args = ap.parse_args()
    if (args.command == "attach") != bool(args.files) or (args.command == "skip") != (args.reason is not None):
        ap.error("attach takes files, skip takes --reason, check takes neither")
    try:
        args.head = args.head.lower() if args.head else None
        if args.command == "attach" and not (args.head and SHA.fullmatch(args.head)):
            raise CheckFailed("attach needs --head with the commit the proof shows (at least 7 hex characters)")
        pr = github.pull_request(args.pr, args.repo)
        head = pr["headRefOid"]
        pr["taken"] = head if not args.head or head.startswith(args.head) else args.head
        if pr["taken"] != pr["headRefOid"]:
            raise CheckFailed(f"the PR head is {pr['headRefOid'][:10]}, not {pr['taken'][:10]}: prove the current head first")
        actions = {"attach": lambda: attach(pr, args.files), "skip": lambda: skip(pr, args.reason), "check": lambda: check(pr)}
        print(actions[args.command]())
        return 0
    except (CheckFailed, github.GhError) as error:
        print(f"pr-evidence: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
