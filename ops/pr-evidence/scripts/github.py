"""The GitHub calls pr_evidence needs, through the `gh` CLI."""

import json
import subprocess
from pathlib import Path

COMPARE_FILE_LIMIT = 300  # the compare API lists at most this many files


class GhError(RuntimeError):
    pass


def gh(*args: str) -> str:
    proc = subprocess.run(["gh", *args], capture_output=True, text=True)
    if proc.returncode != 0:
        raise GhError(f"gh {' '.join(args[:4])}: {proc.stderr.strip()}")
    return proc.stdout


def supports_attach() -> bool:
    return "--attach" in gh("pr", "edit", "--help")


def pull_request(pr: str, repo: str | None) -> dict:
    data = json.loads(gh("pr", "view", pr, "--json", "number,url,body,headRefOid", *(["-R", repo] if repo else [])))
    host, owner, name = data["url"].split("/")[2:5]
    if host != "github.com":
        raise GhError(f"{data['url']} is not on github.com, the only host pr-evidence supports")
    data["repo"] = f"{owner}/{name}"
    return data


def edit_body(pr: dict, body_file: Path, attachments: list[Path]) -> None:
    """Write the body; gh uploads each attachment and rewrites the body's ![alt](path) references to it."""
    uploads = [arg for path in attachments for arg in ("--attach", str(path))]
    gh("pr", "edit", str(pr["number"]), "-R", pr["repo"], "--body-file", str(body_file), *uploads)


def changed_files(pr: dict) -> list[str]:
    jq = ".[] | .filename, (.previous_filename // empty)"
    return gh("api", f"repos/{pr['repo']}/pulls/{pr['number']}/files", "--paginate", "--jq", jq).splitlines()


def files_between(repo: str, base: str, head: str) -> list[str] | None:
    """Files changed from base to head, or None when they cannot all be known (force push, too many files)."""
    try:
        data = json.loads(gh("api", f"repos/{repo}/compare/{base}...{head}"))
    except GhError as error:
        if "HTTP 404" in str(error):
            return None
        raise
    files = data.get("files", [])
    if data.get("status") not in ("ahead", "identical") or len(files) >= COMPARE_FILE_LIMIT:
        return None
    return [name for f in files for name in (f["filename"], f.get("previous_filename")) if name]
