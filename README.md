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
- `ops/pr-evidence/` — Attach screenshots to a GitHub PR description, refresh them after new commits, and check before handoff that a PR touching UI files carries current screenshots (`attach`, `skip --reason`, `check`). Works on any github.com repo, public or private: images are uploaded with `gh pr edit --attach`, and the section records which commit they show.

## Metodo T3 Code (`/gang`)

Un solo tavolo per far lavorare più modelli insieme senza fare copia-incolla tra finestre. Le regole vivono nella skill `engineer/gang/`: non serve creare subagenti né un `TEAM.md` in ogni progetto.

### 1. Ruoli

| Ruolo | Modello e provider | Compito |
| --- | --- | --- |
| **Capo** | Claude · Fable 5.2 (`high`) | Legge il progetto, scrive il piano, aspetta il tuo ok, spezza il lavoro in fette che non si pestano i piedi, guida il giro fino alla PR |
| **Sviluppatori** | Claude · Opus 5.5 (`high`) | Una fetta a testa in cartella separata (*worktree*), sviluppando sempre con `/luca-t-mode` |
| **Chi prova a rompere** | Codex · GPT-6.2 Sol (`high`) | Controlla il lavoro finito da un'altra azienda (solo lettura, non modifica nulla). Mai Astra |
| **Chi scrive i testi** | Antigravity · Gemini 4 Neon | Entra per ultimo solo su `docs/`, `README.md`, `CHANGELOG.md` e testi UI |

### 2. Impostazioni del tavolo (`Settings → Threads`)

- **Modello di partenza**: Opus 5.5 (`high`). Fable costa il doppio e si apre a mano solo per guidare lavori grossi.
- **Riserva automatica**: Codex · GPT-6.2 Sol (`high`) quando Claude finisce la quota.
- **Testi di servizio** (titoli, branch, commit, PR): Gemini 4 Neon.
- **Ripresa sui limiti**: accendi *Resume after usage limits* e *Snooze until limits reset*.
- **Nuovi thread**: **Worktree** (cartella e branch separati per ogni chat). Ricorda che i worktree separano i file, non le porte locali né il database.
- **Permessi**: abbassa il default da *Full access* (usalo solo in sandbox).
  - Un figlio non può mai avere permessi più larghi del Capo: se vuoi far lavorare i builder in *Auto*, anche la chat del Capo deve essere almeno *Auto*.
  - Il "solo lettura" del revisore non è un blocco tecnico: vive come regola nella consegna di `/gang`.
- **Collegamenti esterni (MCP) leggeri**: ogni chat parallela avvia la sua copia di tutti i collegamenti attivi. Tieni accesi solo quelli che servono davvero per non saturare la RAM.

### 3. Flusso dal vivo

1. Apri una chat su **Claude · Fable 5.2 (`high`)** (`Cmd/Ctrl + K`).
2. Scrivi `/gang` seguito da **cosa costruire** e **come verificare che funziona**.
3. Aspetta il piano del Capo e dai l'**ok** (prima non tocca codice).
4. Il Capo lancia gli sviluppatori Opus in parallelo (ognuno con `/luca-t-mode`), poi manda il diff a **GPT-6.2 Sol (`high`)** per il controllo incrociato (massimo **3 giri**, poi decide Luca), e infine chiama **Gemini 4 Neon** per testi e docs.
5. **Comandi utili mentre la squadra lavora**:
   - **Pannello `Agents`**: mostra ogni chat figlia a fianco del Capo; se fermi il Capo si fermano tutti i figli; le richieste di conferma dei figli passano dal Capo.
   - **`@modello`** nel messaggio: indica al Capo quale modello delegare senza cambiare quello della chat corrente.
   - **`/goal`**: tiene l'assistente al lavoro su più turni finché il traguardo non è raggiunto (Claude, Codex, OpenCode).
   - **`/btw`** o **`/side`**: apre una domanda laterale con tutto il contesto della chat, senza fermare il lavoro in corso.
6. **Paletti fissi**: massimo 4 passaggi tra assistenti senza passare da te; mai toccare `.env*`, migrazioni o CI senza conferma; **merge e deploy restano sempre a Luca**.
