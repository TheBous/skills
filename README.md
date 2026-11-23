# skills

Reusable skills for projects.

## Engineer

- `engineer/decision-map/` — Manual audit (`/decision-map` only) of the current plan: list every code and business-logic decision, cite its source, and isolate what the model assumed without Luca or the spec asking for it.
- `engineer/gang/` — Multi-model T3 Code team orchestration (`/gang` only): Fable 5.2 leads and writes the spec, Opus 5.5 builders develop slices via `/luca-t-mode` in isolated worktrees, GPT-6.2 Sol (`high`) runs read-only cross-family review (max 3 rounds), and Gemini 4 Neon updates docs and UI copy.
- `engineer/luca-mode/` — Luca's general workflow for any project. It layers his working style on `poteto-mode` and follows the project's own instructions and rules.
- `engineer/luca-mode/evals/evals.json` — scenarios covering different project stacks and Luca's workflow boundaries.
- `engineer/luca-mode/evals/check_luca_mode.py` — runs real prompts through `claude -p` in a throwaway copy of the fixture, then checks what luca-mode actually did, from the tool calls and the final text. It covers which skills load (`poteto-mode`, `sharpen`, `in-your-own-words`, the engineering skills, and frontend only for UI tasks), one short question or none, the playbook steps copied into the todo list, reuse of existing code, and the plain restart after "non ho capito". Cases live in `behavior-cases.json`. It loads the installed copy at `~/.agents/skills/luca-mode`, so copy the repo `SKILL.md` there before running.

## Ops

- `ops/aws-impersonate/` — AWS CLI login for an IAM user with `aws login --remote` (username + password, no SSO, no CLI install), then identity check.
