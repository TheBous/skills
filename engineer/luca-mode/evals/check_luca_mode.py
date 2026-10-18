#!/usr/bin/env python3
"""Run luca-mode on real prompts with `claude -p` and check what it does, from the tool calls and the final text.

Usage: check_luca_mode.py [--repeats N] [--model M] [--baseline] [--case ID]...
Each case runs in a throwaway copy of the fixture, with edits allowed only inside it.
--baseline drops "Usa luca-mode." from the prompts to show what the environment does without the skill.
"""

import argparse
import json
import os
import re
import subprocess
import tempfile
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).parent
SOURCE_SUFFIXES = {".ts", ".tsx", ".js", ".jsx", ".py", ".rs", ".go", ".css"}
PLAYBOOKS = Path("~/.agents/skills/poteto-mode").expanduser().resolve() / "playbooks"
PREFIX = "Usa luca-mode. "
ALLOWED = "Skill,Read,Glob,Grep,Edit,Write,TaskCreate,TaskUpdate,TaskList,TodoWrite,AskUserQuestion"
DISALLOWED = "Bash,NotebookEdit,Agent,WebFetch,WebSearch"

Call = tuple[str, dict]


@dataclass
class Turn:
    calls: list[Call]
    text: str


@dataclass
class Run:
    root: Path
    turns: list[Turn]

    @property
    def calls(self) -> list[Call]:
        return [c for t in self.turns for c in t.calls]


def parse_stream(stream: str) -> tuple[list[Call], str, str]:
    calls, text, session = [], "", ""
    for line in stream.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "assistant":
            calls += [(b["name"], b.get("input", {})) for b in event["message"].get("content", []) if b.get("type") == "tool_use"]
        elif event.get("type") == "result":
            text, session = event.get("result", ""), event.get("session_id", "")
    return calls, text, session


def run_case(case: dict, spec: dict, model: str | None, baseline: bool) -> Run:
    root = Path(tempfile.mkdtemp(prefix="luca-mode-eval-"))
    for rel, body in spec["fixture"].items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(body)

    prompts = list(case.get("turns") or [case["prompt"]])
    if baseline:
        prompts[0] = prompts[0].removeprefix(PREFIX)
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    env["CLAUDE_CODE_ENABLE_TODO_TOOLS"] = "1"  # TaskCreate/TaskUpdate are absent from `claude -p` without it

    turns, session = [], ""
    for prompt in prompts:
        cmd = ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose",
               "--allowedTools", ALLOWED, "--disallowedTools", DISALLOWED, "--max-turns", "60"]
        if len(prompts) == 1:
            cmd.append("--no-session-persistence")
        if session:
            cmd += ["--resume", session]
        if model:
            cmd += ["--model", model]
        proc = subprocess.run(cmd, cwd=root, env=env, capture_output=True, text=True, timeout=1200)
        calls, text, session = parse_stream(proc.stdout)
        turns.append(Turn(calls, text))
    return Run(root, turns)


def skill_name(inp: dict) -> str:
    return inp.get("skill", "").split(":")[-1]


def is_code_write(name: str, inp: dict) -> bool:
    return name in {"Edit", "Write"} and Path(inp.get("file_path", "")).name.lower() != "todo.md"


def first_code_write(calls: list[Call]) -> int | None:
    return next((i for i, (n, inp) in enumerate(calls) if is_code_write(n, inp)), None)


def loaded_skills(calls: list[Call]) -> set[str]:
    loaded = set()
    for name, inp in calls:
        if name == "Skill":
            loaded.add(skill_name(inp))
        elif name == "Read" and inp.get("file_path", "").endswith("/SKILL.md"):
            loaded.add(Path(inp["file_path"]).parent.name)
    return loaded


def check_skills(run: Run, check: dict, spec: dict) -> dict[str, bool]:
    calls = run.calls
    loaded = loaded_skills(calls)
    results = {f"loads {s}": s in loaded for s in spec["always_skills"] + spec["engineering_skills"]}
    frontend = spec["frontend_skill"]
    results[f"{'loads' if check['ui'] else 'skips'} {frontend}"] = (frontend in loaded) == check["ui"]
    names = [skill_name(i) if n == "Skill" else None for n, i in calls]
    code_read = next((i for i, (n, inp) in enumerate(calls) if n == "Read" and Path(inp.get("file_path", "")).suffix in SOURCE_SUFFIXES), None)
    for s in ("sharpen", "in-your-own-words"):
        results[f"{s} before first code file"] = s in names and (code_read is None or names.index(s) < code_read)
    return results


def questions_asked(run: Run) -> int:
    tool = sum(len(i.get("questions", [])) for n, i in run.calls if n == "AskUserQuestion")
    return tool + run.turns[-1].text.count("?")


def check_asks_one_question(run: Run, check: dict, spec: dict) -> dict[str, bool]:
    question_line = next((l for l in run.turns[-1].text.splitlines() if "?" in l), "")
    tool_questions = [q.get("question", "") for n, i in run.calls if n == "AskUserQuestion" for q in i.get("questions", [])]
    shortest = min([len(q) for q in tool_questions] + ([len(question_line)] if question_line else [10**6]))
    return {
        "asks exactly one question": questions_asked(run) == 1,
        "the question is short": shortest <= 250,
        "no code change before the answer": first_code_write(run.calls) is None,
    }


def check_asks_no_question(run: Run, check: dict, spec: dict) -> dict[str, bool]:
    return {
        "asks no question, the code already answers": questions_asked(run) == 0,
        "makes the change": first_code_write(run.calls) is not None,
    }


def words(text: str) -> int:
    return len(text.split())


def code_terms(text: str) -> int:
    return len(re.findall(r"`[^`]+`", text))


def check_plain_restart(run: Run, check: dict, spec: dict) -> dict[str, bool]:
    first, last = run.turns[0].text, run.turns[-1].text
    return {
        "first turn explains without touching code": bool(first) and first_code_write(run.turns[0].calls) is None,
        "restart has numbered steps": len(re.findall(r"(?m)^\s*\d+[.)]\s", last)) >= 2,
        "restart is shorter than the first answer": 0 < words(last) < words(first),
        "restart uses no more code terms than the first answer": code_terms(last) <= code_terms(first),
    }


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[*`]", "", text)).strip().lower()


def todo_items(calls: list[Call]) -> list[tuple[int, str]]:
    items = []
    for i, (name, inp) in enumerate(calls):
        if name == "TaskCreate":
            items.append((i, normalize(f"{inp.get('subject', '')} {inp.get('description', '')}")))
        elif name == "TodoWrite":
            items += [(i, normalize(t.get("content", ""))) for t in inp.get("todos", [])]
        elif name == "Write" and Path(inp.get("file_path", "")).name.lower() == "todo.md":
            items += [(i, normalize(l)) for l in inp.get("content", "").splitlines() if l.strip()]
    return items


def playbook_steps(name: str) -> list[str]:
    lines = (PLAYBOOKS / f"{name}.md").read_text().splitlines()
    return [normalize(m.group(1))[:25] for l in lines if (m := re.match(r"\d+\.\s+(.*)", l))]


def check_todo(run: Run, check: dict, spec: dict) -> dict[str, bool]:
    calls = run.calls
    read = [m.group(1) for n, i in calls if n == "Read" and (m := re.search(r"/playbooks/([a-z-]+)\.md$", i.get("file_path", "")))]
    chosen = next((p for p in read if p in check["playbooks"]), None)
    items = todo_items(calls)
    texts = " | ".join(t for _, t in items)
    steps = playbook_steps(chosen) if chosen else []
    copied = sum(s in texts for s in steps)
    write_at = first_code_write(calls)
    return {
        f"reads the playbook ({'/'.join(check['playbooks'])})": chosen is not None,
        "copies at least 60% of its steps into the todo list": bool(steps) and copied / len(steps) >= 0.6,
        "todo list exists before the first code change": bool(items) and (write_at is None or items[0][0] < write_at),
    }


def snapshot(root: Path) -> dict[str, str]:
    return {str(p.relative_to(root)): p.read_text() for p in root.rglob("*") if p.is_file()}


def check_reuse(run: Run, check: dict, spec: dict) -> dict[str, bool]:
    after = snapshot(run.root)
    before = spec["fixture"]
    changed = {p: t for p, t in after.items() if before.get(p) != t and p != "todo.md"}
    token = check["token"]
    calls = run.calls
    write_at = first_code_write(calls)
    limit = len(calls) if write_at is None else write_at
    files_with_token = {str(run.root / p) for p, t in before.items() if token in t}
    looked = any(
        (n == "Read" and inp.get("file_path") in files_with_token) or (n == "Grep" and token in json.dumps(inp))
        for n, inp in calls[:limit]
    )
    return {
        "makes the change": bool(changed),
        "looks at the existing code before writing": looked,
        f"uses the existing {token}": any(re.search(token, t) for t in changed.values()),
        "writes no duplicate logic": not any(re.search(f, t) for t in changed.values() for f in check["forbidden"]),
        "leaves the dependencies untouched": all(after.get(p) == before[p] for p in check["unchanged"]),
    }


CHECKS = {
    "skills": check_skills,
    "asks_one_question": check_asks_one_question,
    "asks_no_question": check_asks_no_question,
    "plain_restart": check_plain_restart,
    "todo": check_todo,
    "reuse": check_reuse,
}


def evaluate(case: dict, spec: dict, run: Run) -> dict[str, bool]:
    results = {}
    for check in case["checks"]:
        results.update(CHECKS[check["type"]](run, check, spec))
    return results


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repeats", type=int, default=1)
    ap.add_argument("--model")
    ap.add_argument("--baseline", action="store_true")
    ap.add_argument("--case", action="append")
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()

    spec = json.loads((HERE / "behavior-cases.json").read_text())
    cases = [c for c in spec["cases"] if not args.case or c["id"] in args.case]
    if args.baseline:
        cases = [c for c in cases if (c.get("turns") or [c["prompt"]])[0].startswith(PREFIX)]
    jobs = [c for c in cases for _ in range(args.repeats)]

    def work(case):
        run = run_case(case, spec, args.model, args.baseline)
        return case, run, evaluate(case, spec, run)

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        outcomes = list(pool.map(work, jobs))

    failed = total = 0
    for case in cases:
        mine = [(r, res) for c, r, res in outcomes if c is case]
        print(f"\n== {case['id']}")
        for name in mine[0][1]:
            passes = sum(res[name] for _, res in mine)
            print(f"  {'PASS' if passes == len(mine) else 'FAIL'}  {passes}/{len(mine)}  {name}")
            failed += len(mine) - passes
            total += len(mine)
        for run, res in mine:
            if not all(res.values()):
                print(f"  -- failing run, final text: {run.turns[-1].text[:300]!r}")
                print("     calls:", " > ".join(n if n != "Skill" else f"Skill:{skill_name(i)}" for n, i in run.calls)[:600])
    print(f"\n{total - failed} passed, {failed} failed")
    return 1 if failed and not args.baseline else 0


if __name__ == "__main__":
    raise SystemExit(main())
