# skills

Reusable skills for projects.

## Engineer

- `engineer/luca-mode/` — Luca's general workflow for any project. It layers his working style on `poteto-mode` and follows the project's own instructions and rules.
- `engineer/luca-mode/evals/evals.json` — scenarios covering different project stacks and Luca's workflow boundaries.
- `engineer/luca-mode/evals/check_luca_mode.py` — runs real prompts through `claude -p` in a throwaway copy of the fixture, then checks what luca-mode actually did, from the tool calls and the final text. It covers which skills load (`poteto-mode`, `sharpen`, `in-your-own-words`, the engineering skills, and frontend only for UI tasks), one short question or none, the playbook steps copied into the todo list, reuse of existing code, and the plain restart after "non ho capito". Cases live in `behavior-cases.json`. It loads the installed copy at `~/.agents/skills/luca-mode`, so copy the repo `SKILL.md` there before running.
